# Project Conversation Summary & Status Log: Ikkhi

> **Note:** This document is maintained by the AI Assistant to log key conversation highlights, decisions made, requirements identified, and pending questions across all sessions.

---

## Session: Kickoff & Requirements Analysis (Current Session)

### 1. Context & Origin
- **Initial Prompt Origin:** The user provided an AI-generated initial specification prompt for a project named **Ikkhi** ("vision/sight" in Bengali).
- **User Clarification:** The user noted they have not fully read the entire AI-generated prompt and asked for:
  1. A clear, human-understandable summary of what the prompt actually proposes.
  2. Setting up project files, skills, boundaries, and analyzing existing solutions.
  3. Formulating specific, actionable questions to help the user define their true requirements and preferences.
  4. Keeping this summary file up-to-date across conversations.

### 2. Core Decisions & Artifacts Initialized
- [x] Initialized [AGENTS.md](file:///e:/rouf/software-project/Ikkhi/AGENTS.md) establishing agent persona, hard privacy bounds, deterministic action execution, and priority-tier automation hierarchy.
- [x] Initialized [PROJECT_GOALS.md](file:///e:/rouf/software-project/Ikkhi/PROJECT_GOALS.md) with 5-stage architecture (Wake Word -> VAD/STT -> Intent Router -> Hybrid Execution -> Feedback) and phased milestones.
- [x] Initialized [BOUNDARIES.md](file:///e:/rouf/software-project/Ikkhi/BOUNDARIES.md) locking in privacy (100% local, no cloud audio/screens), safety (no hallucinated clicks, no arbitrary code execution), and resource budgets (<1.5% CPU idle).
- [x] Initialized [EXISTING_SOLUTIONS.md](file:///e:/rouf/software-project/Ikkhi/EXISTING_SOLUTIONS.md) cataloging Talon Voice, Microsoft UFO, `faster-whisper`, `openWakeWord`, `Silero VAD`, and `pywinauto`.
- [x] Restructured repository layout into an enterprise-grade, canonical PEP 517/621 `src/ikkhi` architecture with `pyproject.toml`, `.gitignore`, `README.md`, and typed package marker (`py.typed`).
- [x] Implemented core domain packages: `core/` (config, router, orchestrator, exceptions), `automation/` (registry, windows, davinci), `vision/` (indexer, pointer), and `ai/` (token-conscious Gemini client).
- [x] Implemented **Universal Dynamic Automation & Adaptive Indexing Engine**:
  - `src/ikkhi/automation/inspector.py`: Universal UI tree crawler enumerating buttons, menus, and controls across any active Windows application.
  - `src/ikkhi/automation/profiles.py`: Adaptive JSON knowledge profiles (`storage/profiles/{app_name}.json`) storing learned controls, hotkeys, and coordinate offsets.
  - `src/ikkhi/automation/universal.py`: Dynamic execution engine that prioritizes past learned interactions $\rightarrow$ cached controls $\rightarrow$ live UIA traversal $\rightarrow$ Gemini multimodal learning.
  - Integrated permanent learning loop: whenever Gemini locates an element on screen, it is memorized in the active application's profile, eliminating future credit expenditure for that query.
- [x] Configured authenticated SOCKS5 proxy (`socks5://02:1234@27.147.152.33:5645`) within `config.yaml` and `AppConfig` for resilient model and asset downloads.
- [x] Initialized Git repository on branch `main` and executed initial commits.
- [x] Automated unit test suite executed via `pytest`: **8 out of 8 tests passed successfully** in 1.45s.
- [x] Enforced strict rules in [AGENTS.md](file:///e:/rouf/software-project/Ikkhi/AGENTS.md) to continually maintain `PROGRESS.md`, `PROJECT_MAP.md`, and `CONVERSATION_SUMMARY.md` after every batch of changes.
- [x] Created [PROGRESS.md](file:///e:/rouf/software-project/Ikkhi/PROGRESS.md) with full project schedule, milestones, and task checklists.
- [x] Created [PROJECT_MAP.md](file:///e:/rouf/software-project/Ikkhi/PROJECT_MAP.md) detailing the codebase hierarchy, module flow, and component responsibilities.
- [x] Created [IMPLEMENTATION_PLAN.md](file:///e:/rouf/software-project/Ikkhi/IMPLEMENTATION_PLAN.md) with component designs, risk mitigation, and validation routine matrix.
- [x] Created and executed [scripts/validate_environment.py](file:///e:/rouf/software-project/Ikkhi/scripts/validate_environment.py) to validate the implementation plan against the physical machine:
  - **Python 3.12.10** on Windows 11 AMD64 verified.
  - **NVIDIA GeForce RTX 3070 8GB** detected with CUDA capability.
  - **4K Primary Display (3840x2160)** detected: Validated Windows Per-Monitor V2 DPI awareness. Highlighted the vital need for the Smart Screen Indexer's active window cropping & token downsampling to prevent high API credit consumption.
- [x] Successfully initialized Python virtual environment [`.venv`](file:///e:/rouf/software-project/Ikkhi/.venv).
- [x] Adopted IELTS Band 8 linguistic standard across all user communications and documentation.

### 3. User Requirements & Clarifications (From Session)
- **Hardware Profile:** Dedicated NVIDIA RTX GPU (6GB+ VRAM) available. Can run GPU-accelerated local STT (`faster-whisper`), local embeddings, and local vision models.
- **Activation Mode:** Dual mode — Push-to-Talk hotkey (default, 0% CPU, 0 accidental triggers) + Hands-free wake word ("Hey Ikkhi").
- **Smart Cloud AI Tier (Google AI Studio / Gemini):**
  - Use Google AI Studio (Gemini 1.5/2.0 Flash) for complex intent parsing and visual screen understanding.
  - **Credit & Token Efficiency Rule:** Only call the API when strictly necessary.
  - **Local Pre-Processing / Filter:** Simple commands ("cut clip", "pause", "save", "open VS Code") are handled 100% locally via local speech-to-text and local macro registry (0 API credits used).
  - Only route to Gemini when an intent is ambiguous, conversational, or asks to parse screen content.
- **Visual Cursor Pointer & Screen Grounding:**
  - When asked about something on the screen, Ikkhi should be able to analyze the screen, locate the target UI element, and physically move the mouse cursor to point it out / highlight it for the user.
  - **Smart Screen Indexing:** Super-efficient screen indexing/caching algorithm (cropping active window, diffing changes, caching UI accessibility tree) to avoid sending heavy redundant images and wasting credits.
- **Full Input Control:** Seamless mouse and keyboard control (clicks, hotkeys, text entry).
- **Project Tracking Directives:**
  - Mandatory rules in `AGENTS.md` to continuously update `PROGRESS.md`, `PROJECT_MAP.md`, and `CONVERSATION_SUMMARY.md`.
  - Maintain a live schedule, detailed implementation plan, and run validation routines.
