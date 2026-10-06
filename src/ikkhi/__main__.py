"""
CLI entry point and background daemon for the Ikkhi desktop assistant.
"""

import sys
import time
import signal
import logging
from ikkhi.core.config import AppConfig
from ikkhi.core.orchestrator import IkkhiOrchestrator
from ikkhi.audio.capture import AudioCaptureEngine
from ikkhi.audio.stt import WhisperSTTEngine
from ikkhi.audio.hotkey import PushToTalkListener

logger = logging.getLogger("ikkhi")


def main() -> None:
    """Initialize system configuration and launch orchestrator daemon."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    config = AppConfig.load_from_yaml("config.yaml")
    orchestrator = IkkhiOrchestrator(config)

    # Mode A: Direct CLI argument simulation (for testing & scripts)
    if len(sys.argv) > 1:
        test_command = " ".join(sys.argv[1:])
        logger.info("Executing simulated CLI command: '%s'", test_command)
        result = orchestrator.process_transcript(test_command)
        print(f"\nResult: {result}")
        return

    # Mode B: Live Background Assistant Daemon
    print("\n" + "=" * 65)
    print("      IKKHI VOICE-CONTROLLED DESKTOP ASSISTANT DAEMON")
    print("=" * 65)
    print(f"  • Trigger Hotkey:      [{config.audio.push_to_talk_key.upper()}] (Push-and-Hold to speak)")
    print(f"  • STT Model:           faster-whisper [{config.audio.whisper_model}] on {config.audio.whisper_device.upper()}")
    print(f"  • Universal Indexing:  Active ({config.universal_automation.profiles_directory})")
    print(f"  • Idle CPU Budget:     0.0%")
    print("=" * 65)
    print("Ready and listening in background. Hold hotkey, speak, and release.\n")

    capture = AudioCaptureEngine(config.audio)
    stt_engine = WhisperSTTEngine(config.audio, config.network)
    
    # Warm up Whisper model in background
    logger.info("Pre-warming local Whisper model on CUDA...")
    try:
        stt_engine.load_model()
    except Exception as exc:
        logger.warning("Whisper pre-warm deferred: %s", exc)

    def on_recording_start():
        print("\n[Listening...] Speaking into microphone...", end="\r", flush=True)
        capture.start_recording()

    def on_recording_stop():
        print("\n[Processing...] Transcribing speech on CUDA...", end="\r", flush=True)
        audio = capture.stop_recording()
        if len(audio) == 0:
            print("\n[Warning] No audio recorded.")
            return

        try:
            transcript, _ = stt_engine.transcribe(audio)
            if not transcript.strip():
                print("\n[Notice] No clear speech detected.")
                return

            print(f"\n>>> Spoken: \"{transcript}\"")
            response = orchestrator.process_transcript(transcript)
            print(f">>> Response: {response}\n")
        except Exception as exc:
            logger.error("Error during live speech handling: %s", exc)

    hotkey_listener = PushToTalkListener(
        settings=config.audio,
        on_start=on_recording_start,
        on_stop=on_recording_stop
    )
    hotkey_listener.start()

    # Graceful shutdown handler
    running = True

    def sig_handler(sig, frame):
        nonlocal running
        print("\nShutting down Ikkhi daemon gracefully...")
        running = False
        hotkey_listener.stop()
        capture.close()
        orchestrator.speech_engine.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)

    try:
        while running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        sig_handler(None, None)


if __name__ == "__main__":
    main()
