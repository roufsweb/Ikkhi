# Project Vision & Goals: Ikkhi

## 1. Project Vision
**Ikkhi** (ইক্ষি — meaning "vision/sight" in Bengali) is a lightweight, local-first, voice-controlled Windows desktop assistant designed to automate complex desktop workflows hands-free.

Ikkhi acts as a fast, reliable desktop companion that bridges the gap between natural speech and complex desktop software (such as DaVinci Resolve, VS Code, Blender, Adobe Premiere, browser workflows, and general OS management).

---

## 2. Core Pillars & Architecture

```
                                  [ Microphone Input ]
                                            │
               ┌────────────────────────────┴────────────────────────────┐
               ▼ (Push-to-Talk Hotkey)                                    ▼ (Wake Word: "Hey Ikkhi")
      [ 0% Idle CPU Mode ]                                        [ openWakeWord - <1% CPU ]
               │                                                          │
               └────────────────────────────┬────────────────────────────┘
                                            ▼
                             [ Silero VAD + faster-whisper ]
                                 (Local GPU Transcription)
                                            │
                                  [ Local Transcript ]
                                            │
                        ┌───────────────────┴───────────────────┐
                        ▼                                       ▼
             [ Tier 0: Local Fast Path ]             [ Tier 1: Smart Cloud AI Path ]
             • Exact & Fuzzy Regex Macros            • Google AI Studio (Gemini Flash)
             • Windows UIA Element Cache             • ONLY triggered for:
             • 0ms API Latency, 0 Credits              - Screen-reading / Visual Q&A
             • Covers 90% of routine actions           - Ambiguous/Conversational queries
                        │                                       │
                        │                            [ Smart Screen Indexer ]
                        │                            • Crops active window only
                        │                            • Diffs screen changes
                        │                            • Minimum token resolution
                        │                                       │
                        └───────────────────┬───────────────────┘
                                            ▼
                             [ Hybrid Execution Engine ]
                ├── Native App API (DaVinci Resolve Script, VS Code CLI)
                ├── Windows UI Automation (pywinauto / uiautomation)
                ├── Visual Cursor Pointer (Moves mouse to visually highlight UI)
                └── Visual Fallback (pyautogui + OpenCV Template Match)
                                            │
                                            ▼
                               [ Audio / Visual Feedback ]
                      (Subtle chime sound effect or Piper TTS)
```

---

## 3. Key Milestones

- **Milestone 1: Project Skeleton & Environment Setup**
  - Python virtual environment with dependencies (`faster-whisper`, `openwakeword`, `pywinauto`, `pyautogui`, `opencv-python`, `sounddevice`).
  - Structured modular directory layout (`core/`, `actions/`, `audio/`, `vision/`, `config/`).

- **Milestone 2: Voice Pipeline Prototype (Wake Word -> STT -> Print)**
  - Local wake word listener using `openwakeword` (runs continuously with minimal CPU).
  - On wake word: record voice command until silence (Silero VAD), transcribe via `faster-whisper` (`tiny.en` / `base.en`).

- **Milestone 3: Intent Router & Macro Registry**
  - Deterministic router: pattern matching for immediate commands (e.g., "mute audio", "cut clip", "open terminal").
  - LLM parser fallback (via Ollama or local small GGUF model) with strict JSON schema output.

- **Milestone 4: Hybrid Desktop Automation Engine**
  - Window focus, keystroke injection, Windows UI element navigation (`pywinauto`).
  - Screen coordinate vision matcher (`OpenCV` + `pyautogui`) for canvas elements.
  - Dedicated plugin for target software (e.g. DaVinci Resolve timeline actions).

- **Milestone 5: Persona & Feedback**
  - Non-intrusive sound cues or ultra-fast local TTS (`piper-tts`).
  - System tray icon / minimal overlay status indicator.
