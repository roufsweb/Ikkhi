"""
Ikkhi Visual Navigation & Screen Guidance Tester.
Validates high-efficiency active window capture, WebP token optimization (<80KB, <260 tokens),
local UIA fast-path control discovery (<25ms, 0 tokens), and cursor beacon guidance.
"""

import sys
import time
import argparse
import logging
from typing import Optional
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from PyQt6.QtWidgets import QApplication
from ikkhi.core.config import AppConfig
from ikkhi.core.exceptions import ScreenSecurityViolation
from ikkhi.vision.indexer import ScreenIndexer
from ikkhi.vision.pointer import CursorPointer
from ikkhi.automation.inspector import UniversalUIInspector
from ikkhi.ai.gemini import GeminiVisualClient
from ikkhi.audio.tts import LocalSpeechEngine
from ikkhi.ui.beacon import CursorTargetBeacon

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("visual_nav_tester")


def test_visual_locate(query: str, config: AppConfig, qt_app: QApplication, speak: bool = True) -> None:
    """Tests the full multi-tier visual locating pipeline for a given query."""
    inspector = UniversalUIInspector()
    pointer = CursorPointer(config.pointer)
    indexer = ScreenIndexer(config.screen_indexing)
    tts = LocalSpeechEngine(config.audio) if speak else None

    print("\n" + "=" * 65)
    print(f"Visual Navigation Test: '{query}'")
    print("=" * 65)

    # 1. Inspect Foreground Window Context
    context = inspector.get_foreground_context()
    if not context:
        print("[!] No active foreground window detected.")
        return

    print(f"[*] Foreground Application: {context.process_name} (PID: {context.pid})")
    print(f"[*] Window Title:           '{context.title}'")
    print(f"[*] Window Geometry:        Left={context.bounding_box[0]}, Top={context.bounding_box[1]}, "
          f"Right={context.bounding_box[2]}, Bottom={context.bounding_box[3]} "
          f"({context.bounding_box[2] - context.bounding_box[0]}x{context.bounding_box[3] - context.bounding_box[1]} px)")

    # 2. Check Local UIA Accessibility Tree Fast-Path (<25ms, 0 tokens)
    start_time = time.perf_counter()
    local_ctrl = inspector.find_control_by_label(context.hwnd, query)
    uia_latency_ms = (time.perf_counter() - start_time) * 1000

    if local_ctrl:
        box = local_ctrl.bounding_box
        target_x = (box[0] + box[2]) // 2
        target_y = (box[1] + box[3]) // 2
        print(f"\n[+] TIER 1.0 LOCAL UIA FAST-PATH MATCH!")
        print(f"    - Control Name:   '{local_ctrl.name}'")
        print(f"    - Control Type:   {local_ctrl.control_type}")
        print(f"    - Target Pixels:  ({target_x}, {target_y})")
        print(f"    - Resolution:     0 API TOKENS ($0.00 cost, 100% private)")
        print(f"    - Search Latency: {uia_latency_ms:.2f} ms")

        # Glide cursor & pulse beacon
        print(f"[*] Gliding cursor to ({target_x}, {target_y}) and pulsing beacon reticle...")
        beacon = CursorTargetBeacon(size=84)
        beacon.trigger_at(target_x, target_y, duration_seconds=1.5)
        pointer.point_to(target_x, target_y)

        # Process Qt events so beacon animates smoothly
        for _ in range(60):
            qt_app.processEvents()
            time.sleep(0.025)

        if tts:
            tts.speak(f"Located {local_ctrl.name} on screen.")
        return

    print(f"[-] Local UIA did not match '{query}' in {uia_latency_ms:.2f} ms.")
    print("    Proceeding to Tier 1.1 WebP Active Window Multimodal Grounding...")

    # 3. Capture Active Window with WebP Compression & Security Shield
    try:
        cap_start = time.perf_counter()
        screen = indexer.capture_active_window()
        cap_latency_ms = (time.perf_counter() - cap_start) * 1000

        print(f"\n[*] Screen Indexer Payload Telemetry:")
        print(f"    - Capture Latency:  {cap_latency_ms:.2f} ms")
        print(f"    - Scaled Geometry:  {screen.scaled_dimensions[0]}x{screen.scaled_dimensions[1]} px")
        print(f"    - Image Encoding:   {screen.mime_type}")
        print(f"    - Payload Size:     {screen.payload_kb:.1f} KB (<80 KB optimal target)")
        print(f"    - Estimated Tokens: {screen.estimated_tokens} vision tokens (<260 tokens)")

    except ScreenSecurityViolation as sec_err:
        print(f"\n[!] SECURITY SHIELD BLOCKED CAPTURE: {sec_err}")
        if tts:
            tts.speak("Visual capture is blocked to protect your private credentials.")
        return
    except Exception as exc:
        print(f"\n[!] Screen capture failed: {exc}")
        return

    # 4. Multimodal Cloud Vision Grounding via Gemini
    if not config.ai_tier.gemini_api_key:
        print("\n[!] GEMINI_API_KEY is not configured in .env. Skipping multimodal cloud grounding.")
        return

    client = GeminiVisualClient(config.ai_tier)
    print(f"[*] Querying Gemini multimodal vision client...")
    cloud_start = time.perf_counter()
    res = client.query_visual_target(query, screen)
    cloud_latency_ms = (time.perf_counter() - cloud_start) * 1000

    print(f"\n[+] Multimodal Vision Result ({cloud_latency_ms:.2f} ms):")
    print(f"    - Target Found: {res.target_found}")
    print(f"    - Explanation:  '{res.response_text}'")

    if res.target_found and res.coordinates:
        norm_x, norm_y = res.coordinates
        abs_x, abs_y = screen.map_to_screen_coordinates(norm_x, norm_y)
        print(f"    - Coordinates:  Normalized=({norm_x:.3f}, {norm_y:.3f}) -> Screen=({abs_x}, {abs_y})")

        print(f"[*] Gliding cursor to ({abs_x}, {abs_y}) and pulsing beacon reticle...")
        beacon = CursorTargetBeacon(size=84)
        beacon.trigger_at(abs_x, abs_y, duration_seconds=1.5)
        pointer.point_to(abs_x, abs_y)

        # Process Qt events so beacon animates smoothly
        for _ in range(60):
            qt_app.processEvents()
            time.sleep(0.025)

    if tts and res.response_text:
        tts.speak(res.response_text)


def interactive_mode(config: AppConfig, qt_app: QApplication) -> None:
    """Interactive command-line loop allowing live queries."""
    print("\n" + "=" * 65)
    print("Ikkhi Interactive Visual Guidance Console")
    print("Type a UI element to find, or 'exit' / 'q' to quit.")
    print("Examples: 'close button', 'file menu', 'terminal', 'save'")
    print("=" * 65)

    while True:
        try:
            query = input("\n[ikkhi-nav] > ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit", "q"):
                print("Exiting visual navigation tester.")
                break
            test_visual_locate(query, config, qt_app, speak=True)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


def main():
    parser = argparse.ArgumentParser(description="Ikkhi Visual Navigation Tester")
    parser.add_argument("--find", "-f", type=str, help="Target UI element to locate (e.g. 'close button', 'file menu')")
    parser.add_argument("--no-tts", action="store_true", help="Disable text-to-speech spoken guidance")
    args = parser.parse_args()

    config = AppConfig.load_from_yaml()
    qt_app = QApplication.instance() or QApplication(sys.argv)

    if args.find:
        test_visual_locate(args.find, config, qt_app, speak=not args.no_tts)
    else:
        interactive_mode(config, qt_app)


if __name__ == "__main__":
    main()
