# Master Implementation Plan: Final Audio Pipeline & Live Voice Daemon

## 1. Overview & Objective
This plan governs the execution of the final **18% of the Ikkhi architecture**, transitioning the system from a simulated CLI tool into a fully operational, live voice-interactive background assistant. Upon completion of this plan, the user will be able to speak into their physical microphone, trigger deterministic actions across any Windows application, point out UI controls across multi-monitor setups, and receive instantaneous local voice feedback.

---

## 2. Granular Work Breakdown Structure (WBS)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 6: LIVE AUDIO & INTERACTIVE DAEMON                        │
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
     ┌──────────────────────────────┼──────────────────────────────┐
     ▼                              ▼                              ▼
[ 6.1 Audio Ingestion ]    [ 6.2 Whisper CUDA ]          [ 6.3 Hotkey Daemon ]
• sounddevice capture      • faster-whisper float16      • pynput low-level hook
• NumPy ring buffer        • RTX 3070 CUDA cores         • Push-to-Talk debouncer
• RMS voice activity       • Model caching & proxy       • 0% idle CPU overhead
     │                              │                              │
     └──────────────────────────────┼──────────────────────────────┘
                                    ▼
                     [ 6.4 Daemon Orchestration Loop ]
                     • Non-blocking event dispatcher
                     • End-to-end audio-to-speech loop
                     • Graceful shutdown & signal handling
                                    │
                                    ▼
                     [ 6.5 User Diagnostic Utility ]
                     • scripts/test_live_voice.py
                     • Interactive mic check & audio benchmark
```

---

### Step 6.1: Zero-Copy Audio Buffer Engine ([`src/ikkhi/audio/capture.py`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/audio/capture.py))
* **Objective:** Stream audio directly from the host workstation's physical input device at 16,000 Hz (mono, float32) into a contiguous memory structure.
* **Technical Details:**
  * Uses `sounddevice.InputStream` with a callback architecture.
  * Accumulates raw chunks into a `queue.Queue[np.ndarray]`.
  * Computes Root-Mean-Square (RMS) amplitude per chunk to enable local Voice Activity Detection (VAD) and silence trimming.
  * Exports audio buffers directly as float32 NumPy arrays normalized to $[-1.0, 1.0]$, perfectly matching Whisper input expectations without disk I/O.

---

### Step 6.2: Global Asynchronous Hotkey Daemon ([`src/ikkhi/audio/hotkey.py`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/audio/hotkey.py))
* **Objective:** Intercept the Push-to-Talk trigger (`Ctrl+Alt+Space` or custom key) globally across Windows without requiring window focus.
* **Technical Details:**
  * Implemented using `pynput.keyboard.Listener` in a dedicated background daemon thread.
  * Tracks key press and release events with atomic booleans.
  * Dispatches `on_recording_start()` on key press and `on_recording_stop()` on key release.
  * Consumes **0% CPU in the idle state**, completely sleeping until hardware interrupts are signaled.

---

### Step 6.3: GPU-Accelerated Whisper STT Engine ([`src/ikkhi/audio/stt.py`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/audio/stt.py))
* **Objective:** Perform ultra-fast, local transcription on the workstation's NVIDIA GeForce RTX 3070.
* **Technical Details:**
  * Uses `faster-whisper.WhisperModel` configured for `device="cuda"`, `compute_type="float16"`.
  * Model Selection: Default `base.en` (~140MB memory footprint, ~150ms inference latency) or `small.en` for high vocabulary accuracy.
  * Ingests contiguous float32 NumPy arrays in-memory.
  * Network Resiliency: Routes initial model downloads through our authenticated SOCKS5 proxy (`socks5://02:1234@27.147.152.33:5645`) if configured.

---

### Step 6.4: Interactive Daemon & Orchestrator Integration ([`src/ikkhi/__main__.py`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/__main__.py))
* **Objective:** Unify all components into a seamless, always-available background assistant.
* **Execution Flow:**
  1. User holds `Ctrl+Alt+Space`.
  2. `AudioCapture` begins recording 16kHz audio stream.
  3. User speaks command (*e.g.*, *"blade cut"*, *"where is the render queue"*, *"volume down"*).
  4. User releases hotkey.
  5. Audio buffer is passed to `stt.py` $\rightarrow$ transcribed in ~180ms on CUDA.
  6. Transcript enters `IkkhiOrchestrator.process_transcript()`:
     - If local macro: executes immediately via Win32/UIA (0 tokens, <2ms).
     - If universal app control: resolved via adaptive profile or live UI tree inspection.
     - If visual query: active window is cropped, downsampled, sent to Gemini Flash; mouse cursor points to target coordinate via cubic bezier curve; explanation is spoken aloud via local zero-token TTS.

---

### Step 6.5: User Verification & Diagnostic Script ([`scripts/test_live_voice.py`](file:///e:/rouf/software-project/Ikkhi/scripts/test_live_voice.py))
* **Objective:** Provide a friendly, step-by-step diagnostic CLI tool for the user to test hardware compatibility prior to continuous background operation.
* **Verification Routine:**
  1. Detects and prints all available physical microphone input devices.
  2. Records a 3-second audio sample from the user.
  3. Transcribes the sample using the local CUDA Whisper model and prints the text.
  4. Speaks back confirmation through workstation speakers using the local speech synthesizer.

---

## 3. Timeline, Resource Budget & Acceptance Criteria

| Workstream | Estimated Duration | Resource Allocation | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Dependency Provisioning** | 5 mins | Network Proxy / Pip | `sounddevice`, `numpy`, `faster-whisper` installed in `.venv` |
| **Audio Capture (`capture.py`)** | 10 mins | CPU < 0.5% | Streams 16kHz mono audio cleanly without buffer underruns |
| **Hotkey Daemon (`hotkey.py`)** | 10 mins | CPU 0.0% idle | Fires start/stop events accurately on `Ctrl+Alt+Space` |
| **Whisper CUDA (`stt.py`)** | 15 mins | ~600MB VRAM | Transcribes spoken audio on RTX 3070 in <250ms |
| **Daemon Assembly & Testing** | 15 mins | System Integration | Live voice input triggers actions and spoken feedback |
| **Total Estimated Time** | **~55 minutes** | Workstation Native | **System 100% Ready for Live Hands-Free User Testing** |
