"""
Primary entry point and application launcher for the Ikkhi desktop ecosystem.
Supports full Graphical User Interface (default), Headless Daemon, and CLI Command modes.
"""

import sys
import time
import signal
import logging
from ikkhi.core.config import AppConfig
from ikkhi.core.orchestrator import IkkhiOrchestrator

logger = logging.getLogger("ikkhi")


def run_headless_daemon(config: AppConfig) -> None:
    """Launch headless background daemon without Qt GUI dependencies."""
    from ikkhi.audio.capture import AudioCaptureEngine
    from ikkhi.audio.stt import WhisperSTTEngine
    from ikkhi.audio.hotkey import PushToTalkListener
    from ikkhi.audio.wakeword import WakeWordListener

    orchestrator = IkkhiOrchestrator(config)

    print("\n" + "=" * 65)
    print("      IKKHI VOICE-CONTROLLED DESKTOP ASSISTANT DAEMON")
    print("=" * 65)
    print(f"  • Wake Word:           Say '{config.audio.wake_word.upper()}' aloud")
    print(f"  • Trigger Hotkey:      [{config.audio.push_to_talk_key.upper()}] (Push-and-Hold to speak)")
    print(f"  • STT Model:           faster-whisper [{config.audio.whisper_model}] on {config.audio.whisper_device.upper()}")
    print(f"  • Universal Indexing:  Active ({config.universal_automation.profiles_directory})")
    print(f"  • Idle CPU Budget:     <1.0%")
    print("=" * 65)
    print(f"Ready and listening in background. Say '{config.audio.wake_word}' or hold hotkey.\n")

    capture = AudioCaptureEngine(config.audio)
    stt_engine = WhisperSTTEngine(config.audio, config.network)

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

    def on_wake_detected(trigger_name: str, optional_command: Optional[str]):
        print(f"\n>>> [WAKE DETECTED] Wake phrase recognized via '{trigger_name}'!")
        if optional_command:
            print(f">>> Direct Command: \"{optional_command}\"")
            response = orchestrator.process_transcript(optional_command)
            print(f">>> Response: {response}\n")
        else:
            print(">>> Assistant awakened! Speak your command into the microphone...")
            orchestrator.speech_engine.speak("I'm listening.")
            capture.start_recording()
            time.sleep(3.0)
            audio = capture.stop_recording()
            if len(audio) > 0:
                try:
                    transcript, _ = stt_engine.transcribe(audio)
                    if transcript.strip():
                        print(f">>> Spoken Command: \"{transcript}\"")
                        response = orchestrator.process_transcript(transcript)
                        print(f">>> Response: {response}\n")
                except Exception as exc:
                    logger.error("Error processing wake command: %s", exc)

    hotkey_listener = PushToTalkListener(
        settings=config.audio,
        on_start=on_recording_start,
        on_stop=on_recording_stop
    )
    hotkey_listener.start()

    wakeword_listener: Optional[WakeWordListener] = None
    if config.audio.activation_mode in ("both", "wake_word"):
        wakeword_listener = WakeWordListener(
            settings=config.audio,
            on_wake=on_wake_detected,
            stt_engine=stt_engine
        )
        wakeword_listener.start()

    running = True

    def sig_handler(sig, frame):
        nonlocal running
        print("\nShutting down Ikkhi daemon gracefully...")
        running = False
        hotkey_listener.stop()
        if wakeword_listener:
            wakeword_listener.stop()
        capture.close()
        orchestrator.speech_engine.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)

    try:
        while running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        sig_handler(None, None)


def main() -> None:
    """Initialize system configuration and route to GUI, Headless, or CLI modes."""
    config = AppConfig.load_from_yaml("config.yaml")

    from ikkhi.core.logger import setup_logging
    setup_logging(debug=config.system.debug)


    # Mode 1: Explicit Headless Daemon
    if "--headless" in sys.argv:
        run_headless_daemon(config)
        return

    # Mode 2: Direct CLI Simulation Command
    if "--cli" in sys.argv:
        cli_args = [arg for arg in sys.argv[1:] if arg != "--cli"]
        test_command = " ".join(cli_args)
        orchestrator = IkkhiOrchestrator(config)
        logger.info("Executing simulated CLI command: '%s'", test_command)
        result = orchestrator.process_transcript(test_command)
        print(f"\nResult: {result}")
        return

    # Mode 3: Desktop Graphical User Interface (Default)
    from ikkhi.ui.app import launch_gui
    sys.exit(launch_gui(config))


if __name__ == "__main__":
    main()
