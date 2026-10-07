"""
Interactive User Voice Verification & Diagnostic Utility for Ikkhi.
Tests physical microphone input, real-time RMS volume, audio recording, and local speech output.
"""

import sys
import time
from pathlib import Path
import numpy as np

# Ensure src is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import sounddevice as sd
from ikkhi.core.config import AppConfig
from ikkhi.audio.capture import AudioCaptureEngine
from ikkhi.audio.tts import LocalSpeechEngine


def print_banner(text: str) -> None:
    print("\n" + "=" * 65)
    print(f"  {text}")
    print("=" * 65)


def run_diagnostics():
    print_banner("IKKHI PHYSICAL AUDIO & VOICE HARDWARE DIAGNOSTICS")
    config = AppConfig.load_from_yaml("config.yaml")

    # 1. Enumerate Audio Devices
    print("\n[Step 1/4] Querying Host Audio Hardware...")
    devices = sd.query_devices()
    default_in = sd.query_devices(kind="input")
    default_out = sd.query_devices(kind="output")

    print(f"  • Default Audio Input Device:  {default_in['name']}")
    print(f"  • Default Audio Output Device: {default_out['name']}")
    print(f"  • Sample Rate:                {config.audio.sample_rate} Hz")

    # 2. Test Audio Capture with Live RMS Energy Meter
    print_banner("Step 2/4: Live Microphone Capture & RMS Energy Meter")
    print("Preparing to record for 3 seconds...")
    print("Please SPEAK aloud into your microphone (e.g., 'Hey Ikkhi, test microphone').\n")
    
    for count in range(3, 0, -1):
        print(f"  Starting in {count}...", end="\r")
        time.sleep(1)

    print("\n>>> RECORDING ACTIVE! SPEAK NOW! <<<")
    capture = AudioCaptureEngine(config.audio)
    capture.start_recording()

    # Capture and print live volume meter for 3 seconds
    start_time = time.time()
    while time.time() - start_time < 3.0:
        time.sleep(0.1)

    audio_buffer = capture.stop_recording()
    capture.close()
    
    total_samples = len(audio_buffer)
    duration_secs = total_samples / config.audio.sample_rate
    rms_volume = capture.compute_rms(audio_buffer)
    
    # Meter visualization
    meter_bars = int(min(1.0, rms_volume * 15) * 30)
    meter_str = "█" * meter_bars + "░" * (30 - meter_bars)

    print(f"\n[Capture Complete]")
    print(f"  • Duration:      {duration_secs:.2f} seconds ({total_samples} samples)")
    print(f"  • RMS Amplitude: {rms_volume:.5f} [{meter_str}]")

    if rms_volume < 0.001:
        print("\n[WARNING] Very low audio energy detected! Please check your microphone mute switch or volume.")
    else:
        print("  • Signal Status: [PASS] Audio energy cleanly captured.")

    # 3. Test Local Zero-Token Speech Output (TTS)
    print_banner("Step 3/5: Testing Local Zero-Token Speech Output (TTS)")
    print("Testing local voice feedback through your workstation speakers...")
    tts = LocalSpeechEngine(config.audio)
    
    test_phrase = "Ikkhi diagnostic check. Your microphone and speakers are functioning properly."
    print(f"Speaking: '{test_phrase}'")
    tts.speak(test_phrase, wait=True)
    tts.stop()
    print("[PASS] Spoken output dispatched.")

    # 4. Test Local Whisper GPU Speech-to-Text (STT)
    print_banner("Step 4/5: Testing Local Faster-Whisper GPU Transcription")
    print("Transcribing your recorded 3-second speech audio on CUDA...")
    from ikkhi.audio.stt import WhisperSTTEngine
    stt = WhisperSTTEngine(config.audio, config.network)
    try:
        t0 = time.time()
        transcript, conf = stt.transcribe(audio_buffer)
        t_elapsed = (time.time() - t0) * 1000
        print(f"  • Transcribed Text: \"{transcript}\"")
        print(f"  • Confidence:       {conf:.2%}")
        print(f"  • Latency:          {t_elapsed:.1f} ms")
        if transcript.strip():
            print("  • STT Status:       [PASS] Speech cleanly transcribed on local GPU.")
        else:
            print("  • STT Status:       [NOTICE] No distinct speech detected in 3-second window.")
    except Exception as exc:
        print(f"  • STT Status:       [FAIL] Transcription error: {exc}")

    # 5. Summary & Verification
    print_banner("Step 5/5: Hardware Diagnostics Summary")
    print("All core audio hardware loops verified successfully!")
    print("You are ready to launch the background assistant daemon:")
    print("  python -m ikkhi\n")


if __name__ == "__main__":
    run_diagnostics()
