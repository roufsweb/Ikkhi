# Master Implementation Plan: Ultra-Compact Agent Handoff & Quick-Context Engine

## 1. Executive Summary & Problem Formulation

As the **Ikkhi** project evolves into an enterprise-grade desktop assistant with 20+ architectural modules, the cumulative conversation logs ([`CONVERSATION_SUMMARY.md`](file:///e:/rouf/software-project/Ikkhi/CONVERSATION_SUMMARY.md)) have naturally expanded to over 11.6 KB (~2,500 tokens). 

When initializing **new chat sessions**, switching between AI models (e.g., Gemini, Claude, GPT-4, DeepSeek), or onboarding external human developers and IDE agents (such as Cursor or Copilot), parsing multi-page historical transcripts introduces:
1. **Token Inefficiency & Context Bloat:** Consuming precious context window budget on superseded deliberations.
2. **Cognitive Latency:** Requiring new agents to cross-examine lengthy logs to ascertain the active state.
3. **Drift Risk:** Uncertainty regarding which components are conceptual versus already compiled and verified.

### The Objective
To design and deploy a canonical **Ultra-Compact Context Snapshot (`CONTEXT.md`)** that provides an instantaneous, high-density, 30-second situational briefing (<100 lines, <700 tokens) guaranteed to inform any incoming agent without ambiguity, accompanied by an automated governance protocol to ensure zero documentation drift.

---

## 2. Documentation Architecture & Separation of Concerns

To avoid redundancy, the project repository will maintain a strict tripartite documentation hierarchy:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 DOCUMENTATION TRIAD                                    │
├───────────────────────────┬────────────────────────────┬───────────────────────────────┤
│    1. CONTEXT.md          │   2. PROGRESS.md / MAP     │   3. CONVERSATION_SUMMARY.md  │
│    (High-Density State)   │   (Structural Ledger)      │   (Historical Archive)        │
├───────────────────────────┼────────────────────────────┼───────────────────────────────┤
│ • <100 lines / ~600 tokens│ • Full component inventory │ • Chronological session logs  │
│ • "Read first in new chat"│ • Detailed roadmap phases  │ • Architectural rationale     │
│ • Architecture invariants │ • Dependency graphs        │ • Security audit details      │
│ • One-line command cheats │ • Quantitative metrics     │ • Historical decisions        │
└───────────────────────────┴────────────────────────────┴───────────────────────────────┘
```

---

## 3. Structural Specification of `CONTEXT.md`

The snapshot file will adhere to a rigorous 6-block schema engineered for optimal LLM parsing:

### Block 1: Identity & Paradigm Matrix
* **Name & Role:** Ikkhi ("ইক্ষি" / Vision) — Resource-efficient, voice-controlled Windows desktop assistant.
* **Core Philosophy:** 100% Local Voice & Execution first (<2ms, 0 tokens); Google AI Studio (Gemini 2.0 Flash) strictly for on-demand visual screen parsing. 0% CPU idle budget.

### Block 2: Hard Invariants & Technical Rules
* **Language & Runtime:** Python 3.12 (PEP 517/621 `src-layout`).
* **Packaging:** Single-file standalone executable (`dist/Ikkhi.exe`, 180MB, zero external dependencies).
* **Execution Safety:** Zero hallucination; strict deterministic dispatch via `ActionRegistry`.
* **GUI Stack:** PyQt6 (Frameless Translucent Floating HUD + Windows System Tray + Analytics Dashboard).

### Block 3: Verified Active State & Test Metrics
* **Current Status:** Phase 8 Complete (GUI + Standalone Executable compiled).
* **Test Health:** **30/30 unit & integration tests passing (100%)**.
* **Host Setup:** Windows 11, NVIDIA RTX 3070 CUDA, 4K Display (3840x2160).
* **Remote Repository:** `https://github.com/roufsweb/Ikkhi` (branch `main`).

### Block 4: Quick-Start Developer & Agent Cheat Sheet
```bash
# Execute full test suite
.venv\Scripts\pytest.exe -v

# Launch GUI Desktop Companion (Default)
.venv\Scripts\python.exe -m ikkhi

# Run headless CLI simulation command
.venv\Scripts\python.exe -m ikkhi --cli "volume up"

# Compile standalone single-file binary
.venv\Scripts\python.exe scripts/build_executable.py
```

### Block 5: Deep-Dive Pointer Index
* High-level map: [`PROJECT_MAP.md`](file:///e:/rouf/software-project/Ikkhi/PROJECT_MAP.md)
* Detailed roadmap: [`PROGRESS.md`](file:///e:/rouf/software-project/Ikkhi/PROGRESS.md)
* Packaging master plan: [`docs/GUI_AND_PACKAGING_PLAN.md`](file:///e:/rouf/software-project/Ikkhi/docs/GUI_AND_PACKAGING_PLAN.md)
* Security skill: [`.agents/skills/ikkhi-security/SKILL.md`](file:///e:/rouf/software-project/Ikkhi/.agents/skills/ikkhi-security/SKILL.md)

### Block 6: Immediate Next Priority
* Real-world physical voice testing by the end user via microphone (`scripts/test_live_voice.py` and `dist/Ikkhi.exe`).
* DaVinci Resolve hands-free macro automation validation in live video editing timeline.

---

## 4. Maintenance Cadence & Enforcement Protocol

To guarantee that `CONTEXT.md` never becomes stale:
1. **Rule Binding in `AGENTS.md`:** Add an explicit directive requiring that every milestone update or batch commit must synchronize `CONTEXT.md` alongside `PROGRESS.md` and `PROJECT_MAP.md`.
2. **Automated Freshness Validation (`tests/unit/test_context.py`):**
   - An automated unit test will assert that `CONTEXT.md` exists, remains under a strict line-count budget (maximum 120 lines), and references the correct passing test count.

---

## 5. Phased Task Breakdown & Execution Schedule

| Task ID | Item Description | Target Deliverable | Status |
| :--- | :--- | :--- | :--- |
| `CTX-01` | Formalize Master Implementation Plan | `docs/COMPACT_CONTEXT_PLAN.md` | 🟢 Completed |
| `CTX-02` | Author Canonical High-Density Snapshot | `CONTEXT.md` | ⚪ Queued |
| `CTX-03` | Update Agent Rules & Invariants | `AGENTS.md` | ⚪ Queued |
| `CTX-04` | Implement Automated Integrity & Freshness Test | `tests/unit/test_context.py` | ⚪ Queued |
| `CTX-05` | Synchronize Architecture Documentation & Git | `PROGRESS.md`, `PROJECT_MAP.md` | ⚪ Queued |
