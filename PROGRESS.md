# Project Schedule & Progress Tracker: Ikkhi

> **Status Legend:**
> - 🟢 **Done** — Implemented and validated
> - 🟡 **In Progress** — Currently actively being developed or tested
> - ⚪ **Pending** — Queued for subsequent phase

---

## Overall Roadmap & Milestones

| Phase | Milestone Name | Status | Estimated Duration | Target Completion |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 0** | Project Blueprint, Documentation & Rules | 🟢 Done | 1 Session | 2026-10-04 |
| **Phase 1** | Virtual Environment & Hardware Validation | 🟡 In Progress | 1 Day | 2026-10-04 |
| **Phase 2** | Local Audio Pipeline (Push-to-Talk + Whisper CUDA) | ⚪ Pending | 2 Days | 2026-10-06 |
| **Phase 3** | Local Macro Engine & Fast-Path Intent Router | ⚪ Pending | 2 Days | 2026-10-08 |
| **Phase 4** | Screen Indexer & Credit-Saving Token Compressor | ⚪ Pending | 2 Days | 2026-10-10 |
| **Phase 5** | Visual Cursor Pointer & Screen Grounding | ⚪ Pending | 2 Days | 2026-10-12 |
| **Phase 6** | DaVinci Resolve & Windows Automation Suite | ⚪ Pending | 3 Days | 2026-10-15 |
| **Phase 7** | System Integration & End-to-End Validation Routine | ⚪ Pending | 2 Days | 2026-10-17 |

---

## Detailed Task Breakdown

### Phase 0: Project Blueprint & Foundation 🟢
- [x] Create core guidelines and rules ([AGENTS.md](file:///e:/rouf/software-project/Ikkhi/AGENTS.md))
- [x] Establish vision, architecture, and goals ([PROJECT_GOALS.md](file:///e:/rouf/software-project/Ikkhi/PROJECT_GOALS.md))
- [x] Formalize safety guardrails and token budget rules ([BOUNDARIES.md](file:///e:/rouf/software-project/Ikkhi/BOUNDARIES.md))
- [x] Research and document existing solutions ([EXISTING_SOLUTIONS.md](file:///e:/rouf/software-project/Ikkhi/EXISTING_SOLUTIONS.md))
- [x] Create living conversation summary ([CONVERSATION_SUMMARY.md](file:///e:/rouf/software-project/Ikkhi/CONVERSATION_SUMMARY.md))
- [x] Create project map and architecture blueprint ([PROJECT_MAP.md](file:///e:/rouf/software-project/Ikkhi/PROJECT_MAP.md))
- [x] Define automation extension skill ([SKILL.md](file:///e:/rouf/software-project/Ikkhi/.agents/skills/ikkhi-automation/SKILL.md))
- [x] Structure project under canonical PEP 517/621 `src/ikkhi` layout
- [x] Configure production `pyproject.toml`, `.gitignore`, and `README.md`
- [x] Setup `requirements.txt`, `config.yaml`, and `.env.example`
- [x] Implement Tier 0 / Tier 1 intent routing in `src/ikkhi/core/router.py`
- [x] Implement deterministic Action Registry in `src/ikkhi/automation/registry.py`
- [x] Implement Credit-Saving Screen Indexer in `src/ikkhi/vision/indexer.py`
- [x] Implement DPI-Aware Visual Cursor Pointer in `src/ikkhi/vision/pointer.py`
- [x] Implement token-conscious Gemini client in `src/ikkhi/ai/gemini.py`
- [x] Implement Universal UI Inspector in `src/ikkhi/automation/inspector.py`
- [x] Implement Adaptive Per-App Knowledge Profiles in `src/ikkhi/automation/profiles.py`
- [x] Implement Universal Dynamic Execution Engine in `src/ikkhi/automation/universal.py`
- [x] Integrate authenticated SOCKS5 proxy configuration for heavy model downloads
- [x] Initialize Git repository on branch `main`
- [x] Successfully create and publish public GitHub repository: [https://github.com/roufsweb/Ikkhi](https://github.com/roufsweb/Ikkhi)
- [x] Deep research & architectural deconstruction of HeyClicky ([docs/CLICKY_ANALYSIS.md](file:///e:/rouf/software-project/Ikkhi/docs/CLICKY_ANALYSIS.md))
- [x] Implement Multi-Monitor topology & virtual coordinate normalizer (`src/ikkhi/vision/monitors.py`)
- [x] Implement 100% offline, zero-token local speech synthesis (`src/ikkhi/audio/tts.py`)
- [x] Formulate and execute comprehensive unit test suite under `tests/unit/` (11/11 tests passing)

### Phase 1: Environment & Hardware Validation 🟡
- [x] Verify Python installation (Python 3.12.10 detected on Windows 11 AMD64)
- [x] Verify GPU & CUDA driver (NVIDIA GeForce RTX 3070 8GB, Driver 616.56, CUDA confirmed)
- [x] Verify Display & DPI Scaling (Detected 3840x2160 4K primary display with Per-Monitor V2 DPI awareness)
- [x] Execute validation routine script (`scripts/validate_environment.py` passed all checks)
- [x] Initialize Python virtual environment (`.venv`)
- [ ] Install core dependencies and verify CUDA acceleration in PyTorch / CTranslate2
- [ ] Test audio input capture via microphone with `sounddevice`

### Phase 2: Local Audio Pipeline (Push-to-Talk & STT) ⚪
- [ ] Implement `audio/hotkey_listener.py` for global Push-to-Talk (`Ctrl+Alt+Space`)
- [ ] Implement `audio/recorder.py` for dynamic silence/VAD audio buffer capture
- [ ] Implement `audio/stt_engine.py` using `faster-whisper` (`base.en` on CUDA)
- [ ] Benchmark local transcription latency (< 300ms target on RTX 3070)

### Phase 3: Local Fast-Path Macro Router ⚪
- [ ] Implement `actions/registry.py` with type-safe action schema decorator
- [ ] Implement `core/intent_router.py` pattern matching (instant regex/fuzzy matching)
- [ ] Implement basic Windows OS actions (`actions/os_actions.py`: volume, media, app focus)
- [ ] Validate 0-cost, 0-API-token execution for registered commands

### Phase 4: Smart Screen Indexer (Credit Saver) ⚪
- [ ] Implement `vision/screen_indexer.py`:
  - Active window detection and dynamic boundary cropping
  - Image downsampling to 1024px maximum dimension
  - Fast perceptual hashing / pixel diffing (avoid sending duplicate screenshots)
- [ ] Implement `ai_tier/gemini_client.py` using official `google-genai` SDK
- [ ] Enforce strict prompt token economy (system prompt optimized for coordinates + concise response)

### Phase 5: Visual Cursor Pointer & Grounding ⚪
- [ ] Implement `vision/cursor_pointer.py`:
  - Normalized coordinate converter (API coordinate space $\rightarrow$ screen pixel coordinates)
  - Human-like smooth cursor interpolation (e.g. cubic bezier / ease-out)
  - Visual pulse/circle indicator around target element using a lightweight transparent overlay
- [ ] Test screen pointing accuracy on multi-monitor / varied resolution setups

### Phase 6: DaVinci Resolve & App Automation ⚪
- [ ] Build `actions/davinci_actions.py` (blade tool / cut, ripple delete, play/pause, add marker, render queue)
- [ ] Connect hybrid automation: DaVinci scripting API $\rightarrow$ keyboard shortcuts $\rightarrow$ OpenCV template match fallback
- [ ] Add VS Code quick actions (open terminal, git commit, switch file)

### Phase 7: End-to-End Validation Routine ⚪
- [ ] Automated regression suite testing all registered local macros
- [ ] Latency and VRAM memory profiling under active video editing load
- [ ] Final user acceptance testing
