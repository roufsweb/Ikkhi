"""
Interactive Wake-Word & Live Voice Command Testing Script for Ikkhi.
Monitors the physical microphone in real time, visualizes RMS audio energy levels,
and logs every activation when you say: "Hey Ikkhi" (or use Push-to-Talk Ctrl+Alt+Space).
Logs are streamed to console and persistently appended to storage/live_test.log.
"""

import sys
import os
import time
import threading
import logging
from typing import Optional, Tuple
from pathlib import Path
import numpy as np

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

    is_session_active = False
    session_lock = threading.Lock()

    FAREWELL_KEYWORDS = [
        "bye", "goodbye", "stop", "cancel", "thank you", "thanks", "go to sleep",
        "exit", "quit", "never mind", "that's all", "that is all"
    ]

    def record_natural_utterance(max_wait_seconds: float = 12.0) -> Optional[np.ndarray]:
        """
        Dynamically records user speech using Voice Activity Detection (VAD).
        Waits until the user speaks, captures until they pause for ~0.75s, then returns the audio.
        """
        capture.start_recording()
        t_start = time.time()
        in_speech = False
        silence_start = 0.0
        speech_started_at = 0.0

        while time.time() - t_start < max_wait_seconds:
            time.sleep(0.06)
            rms = capture.get_live_rms()
            threshold = 0.0018  # Conversational speech threshold

            if rms >= threshold:
                if not in_speech:
                    in_speech = True
                    speech_started_at = time.time()
                    logger.info("  [Voice Activity] (RMS: %.5f) User speaking...", rms)
                silence_start = 0.0
            else:
                if in_speech:
                    if silence_start == 0.0:
                        silence_start = time.time()
                    elif (time.time() - silence_start >= 0.75) and (time.time() - speech_started_at >= 0.4):
                        break

        audio = capture.stop_recording()
        if in_speech and len(audio) > 8000:
            return audio
        return None

    def run_conversation_standby(initial_cmd: Optional[str] = None):
        """
        Multi-turn conversational standby session (Gemini style).
        Keeps listening for follow-up questions/commands without requiring the wake word again.
        """
        nonlocal is_session_active
        with session_lock:
            if is_session_active:
                return
            is_session_active = True

        logger.info("=" * 65)
        logger.info(">>> [CONVERSATION STANDBY ACTIVE] Multi-turn dialog online <<<")
        logger.info(">>> Speak your command or follow-up freely. Say 'bye' or 'thank you' to exit. <<<")
        logger.info("=" * 65)

        # 1. Handle initial command if uttered with wake word, otherwise give warm prompt
        if initial_cmd:
            logger.info("Executing initial intent: \"%s\"", initial_cmd)
            res = orchestrator.process_transcript(initial_cmd)
            logger.info(">>> Response: %s", res)
            orchestrator.speech_engine.speak(res, wait=True)
        else:
            orchestrator.speech_engine.speak("I'm listening, go ahead.", wait=True)

        # 2. Continuous Standby Conversation Loop
        timeout_seconds = getattr(config.audio, "conversation_timeout_seconds", 15)

        while True:
            logger.info("[STANDBY] Listening for speech (Session Timeout: %ds)...", timeout_seconds)
            audio = record_natural_utterance(max_wait_seconds=timeout_seconds)

            if audio is None or len(audio) == 0:
                logger.info("[STANDBY TIMEOUT] 15s of silence elapsed. Exiting conversation.")
                orchestrator.speech_engine.speak("Standing by whenever you need me.", wait=False)
                break

            logger.info("Transcribing conversational turn on CUDA...")
            transcript, _ = stt_engine.transcribe(audio)
            clean = transcript.strip()

            if not clean or clean in (".", "...", ". . . ."):
                logger.info("Acoustic blip ignored. Continuing standby.")
                continue

            logger.info(">>> User: \"%s\"", clean)
            clean_lower = clean.lower().strip(" ,.!?")

            # Check for farewell or exit keywords
            if any(fw in clean_lower for fw in FAREWELL_KEYWORDS):
                logger.info("Farewell keyword recognized: '%s'. Closing conversation session.", clean)
                orchestrator.speech_engine.speak("You're welcome! Going to sleep.", wait=True)
                break

            # Execute user action / Gemini query and speak reply
            res = orchestrator.process_transcript(clean)
            logger.info(">>> Assistant: %s", res)
            orchestrator.speech_engine.speak(res, wait=True)

        with session_lock:
            is_session_active = False

        logger.info("=" * 65)
        logger.info(">>> Returned to low-power idle wake-word monitoring (0%% GPU) <<<")
        logger.info("=" * 65)

    def on_wake_detected(trigger_name: str, direct_cmd: str | None):
        if is_session_active:
            return

        logger.info("*" * 55)
        logger.info(">>> [WAKE DETECTED!] Wake word recognized via: '%s' <<<", trigger_name)
        logger.info("*" * 55)

        # Launch conversational standby session in background worker
        threading.Thread(
            target=run_conversation_standby,
            args=(direct_cmd,),
            daemon=True,
            name="Ikkhi-Conversation-Session"
        ).start()

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
                threading.Thread(
                    target=run_conversation_standby,
                    args=(clean,),
                    daemon=True,
                    name="Ikkhi-PTT-Conversation-Session"
                ).start()

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
