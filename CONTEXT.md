# Ikkhi — Quick-Context & AI Agent Handoff Snapshot

> **For New Chats & External AI Agents:** Read this file first. It contains the complete active project state, architecture invariants, and essential workflows in under 700 tokens.

---

## 1. Project Identity & Core Philosophy
- **Name:** **Ikkhi** (Bengali "ইক্ষি" / Vision / Sight)
- **Mission:** A resource-efficient, voice-controlled, local-first Windows desktop assistant that navigates heavy desktop applications (DaVinci Resolve, VS Code, Chrome) completely hands-free.
- **Dual-Tier Execution Paradigm:**
  - **Tier 0 (Local Fast-Path, <2ms, 0 tokens, $0.00):** Deterministic regex/hotkey macros and cached Windows UI Automation (UIA) controls.
  - **Tier 1 (On-Demand Cloud Multimodal):** Google AI Studio (`gemini-2.0-flash`) invoked *only* for ambiguous visual queries or unindexed screen coordinates. Configured safely via local `.env` (strictly Git-ignored).
- **Resource Budget:** Idle CPU $\approx$ 0.0% (Push-to-Talk `Ctrl+Alt+Space` with zero continuous Whisper streaming).

---

## 2. Technical Stack & Invariants
- **Language & Runtime:** Python 3.12 (PEP 517/621 `src-layout` with `pyproject.toml`).
- **Visual Screen Guidance:** Assistive locator (HeyClicky-style beacon reticle + bezier cursor) with WebP compression (<80KB payload, <260 tokens, clamped 768px), local UIA text fast-path (<25ms, 0 tokens), and credential manager privacy shield.
- **Local Audio & Voice:** `sounddevice` + `faster-whisper` (RTX 3070 CUDA conversational STT + CPU int8 wake spotter with 0.0% GPU idle) + Edge Neural TTS (`en-US-AvaNeural`, Google Assistant style) + dynamic energy VAD standby session.
- **Dynamic AI Model Orchestration:** Reasoned model selection (`router_model.py`) with `gemini-3.5-flash` primary model, task-aware routing, and multi-model fallback across active models.
- **GUI Desktop Companion:** PyQt6 frameless translucent floating HUD overlay with reactive multi-bar RMS waveform, Windows system tray applet, and dark-mode settings/token analytics dashboard.
- **Persistent Logging & Correlation:** Dual output console + rotating `storage/ikkhi.log` capturing every hardware key, window change, audio RMS, Whisper STT, and action execution.
- **Standalone Distribution:** Single-file standalone Windows executable (`dist/Ikkhi.exe`, 181.51 MB) compiled via PyInstaller with zero client dependencies.

---

## 3. Current Verification State & Metrics
| Metric | Value | Verification Status |
| :--- | :--- | :--- |
| **Active Milestones** | 21 of 21 Phases Completed | 100% Complete |
| **Automated Test Suite** | 57 / 57 Tests Passing | 100% Pass Rate (12.14s) |
| **Standalone Binary** | `dist/Ikkhi.exe` (181.51 MB) | Compiled & Verified |
| **Hardware Grounding** | Windows 11, RTX 3070 CUDA, 4K Display, USB Mic + Headphones | Auto-Detected & Wired |
| **Remote Repository** | `https://github.com/roufsweb/Ikkhi` | Synced on `main` |

---

## 4. Developer & AI Agent Command Cheat Sheet
```powershell
# Run full automated test suite (57 unit & integration tests)
.venv\Scripts\pytest.exe -v

# Run Standalone Visual Navigation Tester (UIA fast-path, WebP telemetry, beacon)
.venv\Scripts\python.exe scripts/test_visual_navigation.py --find "close"
# Or interactive launcher:
launch_visual_tester.bat

# Launch Desktop GUI Companion (Floating HUD + Tray + Dashboard)
.venv\Scripts\python.exe -m ikkhi

# Run Headless Background Daemon (Console mode)
.venv\Scripts\python.exe -m ikkhi --headless
```

---

## 5. Architectural Directory Map
- [`src/ikkhi/core/`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/core/): `config.py` (Pydantic), `logger.py` (InputCorrelationTracker & persistent log), `paths.py`, `router.py`, `orchestrator.py`.
- [`src/ikkhi/audio/`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/audio/): `capture.py` (RMS buffer + physical mic resolver), `hotkey.py` (pynput + correlation), `stt.py` (Whisper CUDA), `tts.py` (Google Assistant style Neural TTS + SAPI), `wakeword.py` (adaptive acoustic spotter).
- [`src/ikkhi/ai/`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/ai/): `router_model.py` (Reasoned Model Orchestrator & Fallback Chain), `gemini.py` (Visual grounding client).
- [`src/ikkhi/automation/`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/automation/): `reader.py` (screen TTS reader), `experience.py` (mistake learner), `creative/` (catalog), `universal.py`, `inspector.py`, `profiles.py`, `registry.py`, `windows.py`, `apps/davinci.py`.
- [`src/ikkhi/vision/`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/vision/): `monitors.py` (multi-display normalizer), `indexer.py` (crop/downsample), `pointer.py` (bezier cursor).
- [`src/ikkhi/ui/`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/ui/): `theme.py` (obsidian QSS), `overlay.py` (HUD + waveform), `beacon.py` (HeyClicky ripple), `tray.py`, `dashboard.py`, `app.py`.
- [`dist/Ikkhi.exe`](file:///e:/rouf/software-project/Ikkhi/dist/Ikkhi.exe): Standalone single-file binary.

---

## 6. Deep Documentation References
- Detailed Roadmap & Checklist: [`PROGRESS.md`](file:///e:/rouf/software-project/Ikkhi/PROGRESS.md)
- Master Project Map & Dossier: [`PROJECT_MAP.md`](file:///e:/rouf/software-project/Ikkhi/PROJECT_MAP.md) (Governed by [`ikkhi-map`](file:///e:/rouf/software-project/Ikkhi/.agents/skills/ikkhi-map/SKILL.md))
- DeepSeek Architectural Innovations: [`docs/DEEPSEEK_AND_AGENT_INNOVATIONS.md`](file:///e:/rouf/software-project/Ikkhi/docs/DEEPSEEK_AND_AGENT_INNOVATIONS.md)
- OpenClaw Comparative Analysis: [`docs/COMPARISON_OPENCLAW.md`](file:///e:/rouf/software-project/Ikkhi/docs/COMPARISON_OPENCLAW.md)
- Creative Apps & Experience Engine Plan: [`docs/CREATIVE_APPS_AND_EXPERIENCE_PLAN.md`](file:///e:/rouf/software-project/Ikkhi/docs/CREATIVE_APPS_AND_EXPERIENCE_PLAN.md)
- Full Historical Conversation Log: [`CONVERSATION_SUMMARY.md`](file:///e:/rouf/software-project/Ikkhi/CONVERSATION_SUMMARY.md)
