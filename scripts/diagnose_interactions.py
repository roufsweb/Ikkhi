"""
Interactive User Input & System Correlation Diagnostic Tool for Ikkhi.
Monitors all computer user inputs (keyboard, active window, audio RMS), correlates them
to Ikkhi's activation state, verifies TTS neural voice, and checks available Gemini models.
"""

import sys
import time
import argparse
import numpy as np
from pathlib import Path
from pynput import keyboard

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ikkhi.core.config import AppConfig
from ikkhi.core.logger import setup_logging, InputCorrelationTracker
from ikkhi.core.orchestrator import IkkhiOrchestrator
from ikkhi.audio.capture import AudioCaptureEngine
from ikkhi.audio.stt import WhisperSTTEngine
from ikkhi.ai.gemini import GeminiVisualClient


def print_banner(title: str) -> None:
    print("\n" + "=" * 70)
    print(f" {title.center(68)} ")
    print("=" * 70)


def check_audio_devices(config: AppConfig) -> None:
    print_banner("1. AUDIO HARDWARE AUTO-DETECTION & DRIVER ROUTING")
    import sounddevice as sd
    from ikkhi.audio.capture import (
        resolve_optimal_device_params,
        resolve_optimal_output_device,
        get_audio_hardware_report
    )

    report = get_audio_hardware_report()

    # 1. Host Audio APIs
    print("Available Host Audio APIs / Drivers on Windows:")
    for i, api in enumerate(report["host_apis"]):
        print(f"  [{i}] {api}")

    # 2. Windows CoreAudio Physical Endpoint Status
    print("\nWindows Physical Jack / Endpoint Status (CoreAudio Registry):")
    if report["core_audio_endpoints"]:
        for ep in report["core_audio_endpoints"]:
            print(f"  - {ep['name']} ({ep['desc']}): {ep['status']}")
    else:
        print("  (No CoreAudio MMDevice endpoints enumerated)")

    # 3. Input Device Auto-Detection
    dev_idx, native_sr, native_ch, dev_name = resolve_optimal_device_params(config.audio.input_device)
    print("\n[ACTIVE MICROPHONE (INPUT)]")
    print(f"  • Windows Default Input Index: [{report['default_devices'][0]}]")
    print(f"  • Configured Input Device:     [{config.audio.input_device}]")
    print(f"  • Auto-Resolved Input Device:  [{dev_idx}] '{dev_name}'")
    print(f"  • Operating Format:            {native_sr} Hz, {native_ch} Channel(s)")

    # 4. Output Device Auto-Detection
    out_idx, out_sr, out_ch, out_name = resolve_optimal_output_device(getattr(config.audio, "output_device", None))
    print("\n[ACTIVE SPEAKERS / HEADPHONES (OUTPUT)]")
    print(f"  • Windows Default Output Index: [{report['default_devices'][1]}]")
    print(f"  • Configured Output Device:     [{getattr(config.audio, 'output_device', None)}]")
    print(f"  • Auto-Resolved Output Device:  [{out_idx}] '{out_name}'")
    print(f"  • Operating Format:             {out_sr} Hz, {out_ch} Channel(s)")

    # 5. Live 0.3-second stream responsiveness test
    print("\nTesting 0.3s live audio capture from active microphone...")
    try:
        from ikkhi.audio.capture import AudioCaptureEngine
        eng = AudioCaptureEngine(config.audio)
        eng.start_recording()
        time.sleep(0.3)
        buf = eng.stop_recording()
        rms = eng.compute_rms(buf)
        status_note = "Audible signal detected" if rms > 0.005 else "SILENT STREAM (RMS < 0.005)"
        print(f">>> Capture Result: {len(buf)} samples at 16kHz | RMS: {rms:.6f} ({status_note})")
        eng.close()
    except Exception as exc:
        import traceback
        print(f">>> Capture stream failed: {exc}")
        traceback.print_exc()


def check_tts_voice(config: AppConfig) -> None:
    print_banner("2. VOICE SYNTHESIS (TTS) STATUS")
    print(f"Configured TTS Engine: {config.audio.tts_engine}")
    print(f"Configured Neural Voice: {config.audio.tts_voice} (Google Assistant style)")
    try:
        from ikkhi.audio.tts import LocalSpeechEngine
        engine = LocalSpeechEngine(config.audio)
        print("Testing audio playback via neural engine...")
        engine.speak("Ikkhi voice synthesis is verified and online.", wait=True)
        print(">>> Neural voice synthesis succeeded!")
    except Exception as exc:
        print(f">>> TTS test encountered error: {exc}")


def check_gemini_models(config: AppConfig) -> None:
    print_banner("3. GEMINI API & REASONED MODEL ORCHESTRATION")
    from ikkhi.ai.router_model import ReasonedModelOrchestrator

    orch = ReasonedModelOrchestrator(config.ai_tier.gemini_api_key)
    if not orch.client:
        print("Notice: No GEMINI_API_KEY configured in .env. Cloud fallback is disabled.")
        return

    try:
        available_models = orch.list_available_models(force_refresh=True)
        print(f"Connected to Google AI Studio. Found {len(available_models)} active generative models.")

        # Show categorized breakdown
        flash_models = [m.name for m in available_models if m.is_flash]
        pro_models = [m.name for m in available_models if m.is_pro]
        print(f"  • Fast Vision/Flash Models ({len(flash_models)}): {flash_models[:4]}...")
        print(f"  • Deep Reasoning/Pro Models ({len(pro_models)}):  {pro_models[:4]}...")

        # Demonstrate Task Reasoning 1: Visual screen grounding
        vis_model, vis_reason, vis_chain = orch.select_reasoned_model(
            user_prompt="Click the export button in DaVinci Resolve",
            has_image=True,
            preferred_model=config.ai_tier.model_name
        )
        print("\n  [Task 1: Desktop Visual Grounding]")
        print(f"    -> Reasoned Selection: {vis_model}")
        print(f"    -> Rationale:          {vis_reason}")
        print(f"    -> Fallback Hierarchy: {vis_chain}")

        # Demonstrate Task Reasoning 2: Deep logic / troubleshooting
        comp_model, comp_reason, comp_chain = orch.select_reasoned_model(
            user_prompt="Why does the audio buffer underrun when switching audio device? Debug and explain code.",
            has_image=False
        )
        print("\n  [Task 2: Deep System Diagnostic & Logic]")
        print(f"    -> Reasoned Selection: {comp_model}")
        print(f"    -> Rationale:          {comp_reason}")
        print(f"    -> Fallback Hierarchy: {comp_chain}")
    except Exception as exc:
        print(f"Error querying Gemini API: {exc}")


def run_interactive_monitor(config: AppConfig) -> None:
    print_banner("4. LIVE USER INPUT & SYSTEM CORRELATION MONITOR")
    print("Press ANY keys on your keyboard to test detection.")
    print(f"Hold [{config.audio.push_to_talk_key.upper()}] to record speech.")
    print("Release to transcribe via CUDA faster-whisper and execute intent.")
    print("Switch application windows to verify active context tracking.")
    print("Press Ctrl+C to terminate the monitor.\n")

    tracker = InputCorrelationTracker()
    orchestrator = IkkhiOrchestrator(config)
    capture = AudioCaptureEngine(config.audio)
    stt = WhisperSTTEngine(config.audio, config.network)

    try:
        stt.load_model()
    except Exception as exc:
        print(f"Notice: Whisper prewarm: {exc}")

    active_keys = set()
    is_recording = False
    rec_start_time = 0.0

    target_tokens = set(config.audio.push_to_talk_key.lower().replace(" ", "").split("+"))

    def normalize(key):
        if isinstance(key, keyboard.Key):
            if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                return "ctrl"
            if key in (keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
                return "alt"
            if key in (keyboard.Key.shift_l, keyboard.Key.shift_r):
                return "shift"
            if key == keyboard.Key.space:
                return "space"
            return key.name.lower()
        elif hasattr(key, "char") and key.char:
            return key.char.lower()
        return str(key).lower()

    def get_active_window_title():
        try:
            import win32gui
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                return win32gui.GetWindowText(hwnd).strip() or "Desktop"
        except Exception:
            pass
        return "Unknown"

    last_window = get_active_window_title()

    def on_press(key):
        nonlocal is_recording, rec_start_time
        k_str = normalize(key)
        active_keys.add(k_str)

        is_match = target_tokens.issubset(active_keys)
        relation = "MATCH -> [IKKHI TRIGGER ACTIVATED!]" if is_match else ("PARTIAL COMBO" if active_keys.intersection(target_tokens) else "UNRELATED KEY")

        print(f"\r[KEY DOWN] {k_str:<10} | Held: {str(sorted(list(active_keys))):<25} | Relation: {relation:<32}", flush=True)

        if is_match and not is_recording:
            is_recording = True
            rec_start_time = time.time()
            capture.start_recording()
            print("\n  >>> [RECORDING STARTED] Speak into microphone now...")

    def on_release(key):
        nonlocal is_recording
        k_str = normalize(key)
        is_match = target_tokens.issubset(active_keys)

        if is_recording and not is_match:
            is_recording = False
            duration = time.time() - rec_start_time
            print(f"\n  >>> [RECORDING STOPPED] Held for {duration:.2f}s. Finalizing buffer...")
            audio = capture.stop_recording()
            rms = float(np.sqrt(np.mean(audio**2))) if len(audio) > 0 else 0.0
            print(f"  >>> Audio Energy RMS: {rms:.6f} {'[AUDIBLE SPEECH]' if rms > 0.0005 else '[SILENCE/EMPTY MIC]'}")

            if len(audio) > 0 and rms > 0.0001:
                print("  >>> Transcribing via CUDA faster-whisper...")
                t0 = time.time()
                transcript, _ = stt.transcribe(audio)
                elapsed = time.time() - t0
                print(f"  >>> Transcript ({elapsed:.2f}s): \"{transcript}\"")
                if transcript.strip():
                    response = orchestrator.process_transcript(transcript)
                    print(f"  >>> Orchestrator Action Response: {response}")
            else:
                print("  >>> Notice: Buffer empty or silent. Check microphone setting.")

        active_keys.discard(k_str)

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.daemon = True
    listener.start()

    try:
        while True:
            time.sleep(1.0)
            curr_window = get_active_window_title()
            if curr_window != last_window:
                print(f"\n[WINDOW SWITCH] Focused Window: '{curr_window}'")
                last_window = curr_window
    except KeyboardInterrupt:
        print("\nExiting monitor. Shutting down cleanly.")
        listener.stop()
        capture.close()


def main():
    parser = argparse.ArgumentParser(description="Ikkhi Live Input & System Diagnostic Tool")
    parser.add_argument("--test-only", action="store_true", help="Run automated checks without interactive monitor")
    args = parser.parse_args()

    config = AppConfig.load_from_yaml("config.yaml")
    setup_logging(debug=True)

    print("\n" + "#" * 70)
    print("      IKKHI SYSTEM HEALTH & INPUT CORRELATION DIAGNOSTIC SUITE")
    print("#" * 70)

    check_audio_devices(config)
    check_tts_voice(config)
    check_gemini_models(config)

    if not args.test_only:
        run_interactive_monitor(config)


if __name__ == "__main__":
    main()
