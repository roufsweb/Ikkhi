"""
Interactive Wake-Word & Live Voice Command Testing Script for Ikkhi.
Monitors the physical microphone in real time, visualizes RMS audio energy levels,
and logs every activation when you say: "Hey Ikkhi" (or use Push-to-Talk Ctrl+Alt+Space).
Logs are streamed to console and persistently appended to storage/live_test.log.
"""

import sys
import os
import time
import logging
from pathlib import Path

# Force unbuffered output so logs appear instantly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(line_buffering=True)

# Ensure src is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Create storage dir if not present
os.makedirs("storage", exist_ok=True)
log_file = Path("storage/live_test.log")

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(log_file), mode="w", encoding="utf-8")
    ]
)
logger = logging.getLogger("live_test")

import sounddevice as sd
from ikkhi.core.config import AppConfig
from ikkhi.core.orchestrator import IkkhiOrchestrator
from ikkhi.audio.capture import AudioCaptureEngine
from ikkhi.audio.stt import WhisperSTTEngine
from ikkhi.audio.hotkey import PushToTalkListener
from ikkhi.audio.wakeword import WakeWordListener


def run_live_test():
    logger.info("=" * 65)
    logger.info("      IKKHI INTERACTIVE LIVE WAKE-WORD & VOICE TESTING CONSOLE")
    logger.info("=" * 65)
    
    config = AppConfig.load_from_yaml("config.yaml")

    try:
        from ikkhi.audio.capture import resolve_optimal_device_params, resolve_optimal_output_device
        in_idx, in_sr, in_ch, in_name = resolve_optimal_device_params(config.audio.input_device)
        out_idx, out_sr, out_ch, out_name = resolve_optimal_output_device(getattr(config.audio, "output_device", None))
        logger.info("Active Mic:     [%s] %s (%dHz, %dch)", in_idx, in_name, in_sr, in_ch)
        logger.info("Active Audio:   [%s] %s (%dHz, %dch)", out_idx, out_name, out_sr, out_ch)
    except Exception as exc:
        logger.warning("Could not query sound devices: %s", exc)

    logger.info("Wake Word:      Say 'HEY IKKHI' aloud into your microphone")
    logger.info("Hotkey Trigger: [%s] (Push-and-Hold)", config.audio.push_to_talk_key.upper())
    logger.info("STT Engine:     faster-whisper [%s] on %s", config.audio.whisper_model, config.audio.whisper_device.upper())
    logger.info("=" * 65)
    logger.info("Initializing neural audio engines...")

    orchestrator = IkkhiOrchestrator(config)
    capture = AudioCaptureEngine(config.audio)
    stt_engine = WhisperSTTEngine(config.audio, config.network)

    try:
        stt_engine.load_model()
        logger.info("faster-whisper CUDA model loaded successfully and pre-warmed.")
    except Exception as exc:
        logger.warning("Whisper pre-warm deferred: %s", exc)

    is_processing = False

    def on_wake_detected(trigger_name: str, direct_cmd: str | None):
        nonlocal is_processing
        if is_processing:
            return
        is_processing = True

        logger.info("*" * 55)
        logger.info(">>> [WAKE DETECTED!] Wake word recognized via: '%s' <<<", trigger_name)
        logger.info("*" * 55)

        if direct_cmd:
            logger.info("Direct command identified: \"%s\"", direct_cmd)
            logger.info("Executing deterministic action...")
            res = orchestrator.process_transcript(direct_cmd)
            logger.info(">>> Execution Result: %s", res)
            is_processing = False
        else:
            logger.info("Assistant awakened! Awaiting voice command...")
            orchestrator.speech_engine.speak("I'm listening.")
            logger.info(">>> SPEAK YOUR COMMAND NOW (e.g., 'volume up', 'read text', 'cut') <<<")
            capture.start_recording()
            time.sleep(3.0)
            audio = capture.stop_recording()

            if len(audio) > 0:
                logger.info("Transcribing speech on CUDA...")
                transcript, _ = stt_engine.transcribe(audio)
                clean = transcript.strip()
                if clean:
                    logger.info(">>> Spoken Command: \"%s\"", clean)
                    res = orchestrator.process_transcript(clean)
                    logger.info(">>> Execution Result: %s", res)
                else:
                    logger.info("No speech detected in audio segment.")
            else:
                logger.info("Audio buffer empty.")
            is_processing = False

    # Start Wake Word Listener
    wake_listener = WakeWordListener(
        settings=config.audio,
        on_wake=on_wake_detected,
        stt_engine=stt_engine
    )
    wake_listener.start()

    # Start Push-to-Talk Listener
    def on_ptt_start():
        logger.info("[Push-to-Talk Active] Recording speech...")
        capture.start_recording()

    def on_ptt_stop():
        logger.info("[Push-to-Talk Released] Transcribing on CUDA...")
        audio = capture.stop_recording()
        if len(audio) > 0:
            transcript, _ = stt_engine.transcribe(audio)
            clean = transcript.strip()
            if clean:
                logger.info(">>> Spoken: \"%s\"", clean)
                res = orchestrator.process_transcript(clean)
                logger.info(">>> Execution Result: %s", res)

    ptt_listener = PushToTalkListener(
        settings=config.audio,
        on_start=on_ptt_start,
        on_stop=on_ptt_stop
    )
    ptt_listener.start()

    logger.info("=" * 65)
    logger.info(">>> READY & LISTENING LIVE! Say 'Hey Ikkhi' or hold Ctrl+Alt+Space.")
    logger.info(">>> Log file path: storage/live_test.log")
    logger.info("=" * 65)

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        logger.info("Stopping listeners and shutting down...")
        wake_listener.stop()
        ptt_listener.stop()
        capture.close()
        orchestrator.speech_engine.stop()
        logger.info("Ikkhi test console exited cleanly.")


if __name__ == "__main__":
    run_live_test()
