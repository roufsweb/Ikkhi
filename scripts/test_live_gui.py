"""
Interactive Visual GUI Testing Launcher for Ikkhi Desktop Assistant.
Boots the full graphical user interface (HUD Overlay + System Tray + Control Panel)
with real-time microphone diagnostics, CUDA acceleration, and Google AI Studio visual grounding.
"""

import sys
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import sounddevice as sd
from ikkhi.core.config import AppConfig
from ikkhi.ui.app import IkkhiApplication

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ikkhi.test_gui")


def main() -> None:
    print("\n" + "=" * 70)
    print("        IKKHI DESKTOP COMPANION — LIVE VISUAL TEST LAUNCHER")
    print("=" * 70)

    config = AppConfig.load_from_yaml("config.yaml")

    # Enumerate Audio Hardware
    try:
        in_dev = sd.query_devices(kind="input")
        out_dev = sd.query_devices(kind="output")
        print(f"  • Microphone:          {in_dev['name']}")
        print(f"  • Audio Speakers:      {out_dev['name']}")
    except Exception as exc:
        print(f"  • Audio Device Note:   {exc}")

    print(f"  • Wake Word:           Say '{config.audio.wake_word.upper()}' into your microphone")
    print(f"  • Hotkey Trigger:      [{config.audio.push_to_talk_key.upper()}] (Push-and-Hold to speak)")
    print(f"  • STT Neural Engine:   faster-whisper [{config.audio.whisper_model}] on {config.audio.whisper_device.upper()}")
    has_gemini = bool(config.ai_tier.gemini_api_key)
    print(f"  • Google AI Studio:    {'Configured (.env)' if has_gemini else 'Disabled (No Key)'}")
    if config.ai_tier.gemini_project_id:
        print(f"  • Project ID:          {config.ai_tier.gemini_project_id}")
    print("=" * 70)
    print("\n[Visual Testing Checklist]")
    print("  1. Look at the top center of your primary screen for the Floating HUD Pill.")
    print("  2. Hold [Ctrl+Alt+Space] and speak — the cyan-to-violet waveform will dynamically pulse!")
    print("  3. Say 'Hey Ikkhi' — the HUD pill will switch to listening mode automatically.")
    print("  4. Check your Windows System Tray (near the clock) for the glowing Ikkhi tray icon.")
    print("  5. Explore the Control Panel window for real-time Token Analytics & Settings.")
    print("\nLaunching Desktop GUI now...\n")

    app = IkkhiApplication(config)
    app.start()
    sys.exit(app.app.exec())


if __name__ == "__main__":
    main()
