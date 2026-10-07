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
- **Local Audio Pipeline:** `sounddevice` (16kHz zero-copy buffer) + `faster-whisper` (RTX 3070 CUDA float16) + native Win32 SAPI (zero-token TTS).
- **GUI Desktop Companion:** PyQt6 frameless translucent floating HUD overlay with reactive multi-bar RMS waveform, Windows system tray applet, and dark-mode settings/token analytics dashboard.
- **Standalone Distribution:** Single-file standalone Windows executable (`dist/Ikkhi.exe`, 180MB) compiled via PyInstaller with zero client dependencies.
- **Code & Test Rigor:** 100% typing, no arbitrary code execution without validation, strict path traversal mitigations in `ProfileManager`.

---

## 3. Current Verification State & Metrics
| Metric | Value | Verification Status |
| :--- | :--- | :--- |
| **Active Milestones** | 10 of 10 Core Phases Completed | 🟢 100% Complete |
| **Automated Test Suite** | 46 / 46 Tests Passing | 🟢 100% Pass Rate (3.49s) |
| **Standalone Binary** | `dist/Ikkhi.exe` (180.28 MB) | 🟢 Compiled & Verified |
| **Hardware Grounding** | Windows 11, RTX 3070 CUDA, 4K Display | 🟢 Verified & Calibrated |
| **Remote Repository** | `https://github.com/roufsweb/Ikkhi` | 🟢 Synced on `main` |

---

## 4. Developer & AI Agent Command Cheat Sheet
```powershell
# Run full automated test suite (46 unit & integration tests)
.venv\Scripts\pytest.exe -v

# Launch Desktop GUI Companion (Floating HUD + Tray + Dashboard)
.venv\Scripts\python.exe -m ikkhi

# Run Headless Background Daemon (Console mode)
.venv\Scripts\python.exe -m ikkhi --headless

# Execute simulated single command (fast-path test)
.venv\Scripts\python.exe -m ikkhi --cli "volume up"

# Recompile standalone single-file binary (dist/Ikkhi.exe)
.venv\Scripts\python.exe scripts/build_executable.py

# Launch interactive microphone voice calibration tool
.venv\Scripts\python.exe scripts/test_live_voice.py
```

---

## 5. Architectural Directory Map
- [`src/ikkhi/core/`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/core/): `config.py` (Pydantic), `paths.py` (frozen runtime paths), `router.py` (Tier 0 vs 1), `orchestrator.py`.
- [`src/ikkhi/audio/`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/audio/): `capture.py` (RMS buffer), `hotkey.py` (pynput), `stt.py` (Whisper CUDA), `tts.py` (local SAPI).
- [`src/ikkhi/automation/`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/automation/): `reader.py` (screen TTS reader), `experience.py` (mistake learner), `creative/` (catalog), `universal.py`, `inspector.py`, `profiles.py`, `registry.py`, `windows.py`, `apps/davinci.py`.
- [`src/ikkhi/vision/`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/vision/): `monitors.py` (multi-display normalizer), `indexer.py` (crop/downsample), `pointer.py` (bezier cursor).
- [`src/ikkhi/ui/`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/ui/): `theme.py` (obsidian QSS), `overlay.py` (HUD + waveform), `tray.py` (vector tray), `dashboard.py` (token meter), `app.py`.
- [`dist/Ikkhi.exe`](file:///e:/rouf/software-project/Ikkhi/dist/Ikkhi.exe): Standalone single-file binary.

---

## 6. Deep Documentation References
- Detailed Roadmap & Checklist: [`PROGRESS.md`](file:///e:/rouf/software-project/Ikkhi/PROGRESS.md)
- Master Project Map & Dossier: [`PROJECT_MAP.md`](file:///e:/rouf/software-project/Ikkhi/PROJECT_MAP.md) (Governed by [`ikkhi-map`](file:///e:/rouf/software-project/Ikkhi/.agents/skills/ikkhi-map/SKILL.md))
- DeepSeek Architectural Innovations: [`docs/DEEPSEEK_AND_AGENT_INNOVATIONS.md`](file:///e:/rouf/software-project/Ikkhi/docs/DEEPSEEK_AND_AGENT_INNOVATIONS.md)
- OpenClaw Comparative Analysis: [`docs/COMPARISON_OPENCLAW.md`](file:///e:/rouf/software-project/Ikkhi/docs/COMPARISON_OPENCLAW.md)
- Creative Apps & Experience Engine Plan: [`docs/CREATIVE_APPS_AND_EXPERIENCE_PLAN.md`](file:///e:/rouf/software-project/Ikkhi/docs/CREATIVE_APPS_AND_EXPERIENCE_PLAN.md)
- Full Historical Conversation Log: [`CONVERSATION_SUMMARY.md`](file:///e:/rouf/software-project/Ikkhi/CONVERSATION_SUMMARY.md)
