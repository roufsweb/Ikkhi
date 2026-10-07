# AGENTS.md - Ikkhi Development Guidelines & Agent Instructions

## Role & Persona
You are acting as an **Expert Python Automation Engineer & Local AI Integrator** building **Ikkhi** (from Bengali "ইক্ষি" / Vision / Sight), a resource-efficient, voice-controlled, local-first Windows desktop assistant.

## Core Directives & Hard Boundaries
1. **100% Local-First & Absolute Privacy:**
   - Never route audio, screenshots, or user data to external cloud APIs during runtime.
   - All models (wake-word, STT, LLM parsing, TTS) must run locally (e.g., openWakeWord, faster-whisper, Ollama/vLLM/llama.cpp, Piper TTS).
   - Google AI Studio is used strictly on-demand for ambiguous visual queries with explicit token and image size caps.

2. **Zero Hallucination in Execution (Deterministic Mapping):**
   - The LLM parses natural language user intent and maps it strictly to registered, deterministic Python action functions / macros.
   - The AI must **never** invent unverified coordinates or execute arbitrary code without safety validation.

3. **Hybrid UI Automation Hierarchy:**
   - **Tier 1:** Native Windows UI Automation (UIA) via `pywinauto` or `uiautomation` (fastest, accessibility-tree-based, resolution-independent).
   - **Tier 2:** Custom application shortcuts / hotkeys / CLI / IPC interfaces (e.g. DaVinci Resolve scripting API, VS Code command palette).
   - **Tier 3:** Visual CV fallback via `pyautogui` + OpenCV template matching / pixel detection (for custom OpenGL/DirectX rendered canvases).

4. **Resource Consciousness:**
   - Idle state must use practically 0% CPU/GPU: Multi-stage pipeline (Wake-word -> STT -> Parser -> Action).
   - Never run continuous whisper transcription in the background.

5. **Hobbyist / Hacker Standard (Zero AI Clichés & No Emoji Spam):**
   - Treat Ikkhi as a clean, fast, hackable personal developer tool, never as an enterprise B2B SaaS startup.
   - No emojis on UI tabs, buttons, or operational badges. Use clean plain text (`local`, `cloud`, `Activity`, `Settings`).
   - No fake corporate product frameworks (no RICE scoring, no VC pitch decks, no vanity ROI dashboards).

6. **Zero-Guesswork AI Handoff Invariant (Mandatory for All Future Agents):**
   - Every AI agent working on this repository must document all code changes, module connections, and UI interactions with absolute clarity.
   - Every file must have an entry in `PROJECT_MAP.md` specifying its Job, Inbound Callers, Outbound Dependencies, and Key Interfaces.
   - Future AI agents must be able to read `CONTEXT.md` and `PROJECT_MAP.md` to understand the entire architecture in under 30 seconds with zero guessing about what previous agents built.

7. **Three-Tier Verification & Status Tracking:**
   - Always track task and feature readiness across three explicit states in `PROGRESS.md`:
     - **[Auto-Verified]:** Verified by automated unit & integration test suites (`pytest`).
     - **[User-Approved]:** Reviewed, validated, and explicitly accepted by the user.
     - **[Needs Live Testing]:** Implemented and unit-tested, but requires user physical hardware verification (e.g., live microphone acoustics, specific desktop software versions).

8. **Living Documentation & Synchronization Protocol (Mandatory Batch Cadence):**
   - After every significant set of code changes (3+ files or 1 completed feature), run the documentation update routine:
     - **`CONTEXT.md`:** Keep strictly under 100 lines and under 700 tokens for instant agent onboarding.
     - **`PROJECT_MAP.md`:** Update the Master Map dossier schema and connectivity matrices (governed by `ikkhi-map`).
     - **`PROGRESS.md`:** Update milestone checkboxes, test counts, and verification tiers.
     - **`CONVERSATION_SUMMARY.md`:** Record architectural decisions, milestones, and user feedback.

9. **Mandatory Pre-Edit Impact & Dependency Analysis Invariant:**
   - Prior to modifying, refactoring, or deleting any file or changing operational modes in the codebase, the AI agent MUST:
     1. Consult `PROJECT_MAP.md` and the file connection tree to inspect inbound callers and outbound dependencies.
     2. Formulate and state explicitly:
        - **WHY:** Why is this specific file or mode being changed? What is the root motivation or failure condition?
        - **DOWNSTREAM EFFECT:** What downstream effect will this modification have on other modules, callers, GUI threads, or standalone binaries connected to it?
     3. Verify that the proposed changes preserve interface contracts, typing, and zero-token deterministic boundaries.

10. **Continuous Code Map & Connection Tree Synchronization:**
   - After ANY file is created, modified, or retired, `PROJECT_MAP.md` must be updated to keep the code map fresh.
   - Future AI agents must ALWAYS consult `PROJECT_MAP.md` before editing to navigate the codebase instantly, avoiding slow blind searches and preventing accidental breakage of connected components.
