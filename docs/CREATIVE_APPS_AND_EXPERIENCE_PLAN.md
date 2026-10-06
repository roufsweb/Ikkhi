# Master Implementation Plan: Universal Creative App Mastery & Experiential Mistake Learning

## 1. Executive Summary & Architectural Motivation

While early iterations of Ikkhi registered DaVinci Resolve as a discrete hardcoded macro module (`src/ikkhi/automation/apps/davinci.py`), a truly intelligent desktop sidekick must **transcend application-specific silos**. 

Professional creators operate across an expansive ecosystem of creative software—spanning Non-Linear Video Editors (DaVinci Resolve, Premiere Pro), 3D & VFX suites (Blender, After Effects, Unreal Engine), Digital Audio Workstations (Ableton Live, FL Studio), and Graphic Design engines (Photoshop, Illustrator, Figma).

Furthermore, static hardcoding fails to account for custom user keybindings, UI layout alterations, or execution failures. Ikkhi must incorporate a **continuous experiential feedback loop**:
1. **Application-Agnostic Semantic Action Normalization:** Resolves high-level creative intents (e.g. *cut clip*, *render*, *ripple delete*, *add marker*, *toggle snapping*) to the appropriate active foreground application.
2. **Mistake Detection & Negative Confidence Penalization:** Detects runtime failures and negative human feedback (e.g. *"no"*, *"undo"*, *"wrong"*), dynamically degrading flawed strategies.
3. **Adaptive Experiential Memory (`storage/memory/experience.jsonl`):** Maintains an ultra-compact, resource-friendly experiential ledger (<500 KB, capped ring buffer) that ranks strategies by empirical historical reliability.
4. **Autonomous Convergence toward 0-Token Fast-Paths:** When a visual or UIA strategy is validated after user correction, it is permanently synthesized into the active application's profile, saving cloud API tokens on all future invocations.

---

## 2. System Architecture & Information Flow

```
                                  [ User Utterance ]
                                          │
                                          ▼
                            [ Active Window Introspection ]
                      (Detects Process: resolve, blender, premiere, etc.)
                                          │
                                          ▼
                     ┌─────────────────────────────────────────┐
                     │   Experiential Memory & Mistake Learner │
                     │   (Consults Historical Confidence Log)  │
                     └────────────────────┬────────────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
         [ Proven High Confidence ]                      [ Unknown / Sub-optimal ]
      (Historical success rate >= 75%)                 (Mistake logged or untried)
                  │                                               │
                  ▼                                               ▼
      [ Tier 0 Fast-Path Dispatch ]                  [ Tier 0.5 UIA & Tier 1 Gemini ]
   (App-specific hotkey / cached UIA)               (Live discovery & screen parsing)
                  │                                               │
                  └───────────────────────┬───────────────────────┘
                                          │
                                          ▼
                                 [ Execution Attempt ]
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    ▼                                           ▼
             [ Action Succeeded ]                       [ Action Failed / Corrected ]
     • Record success in Experience Log         • Log mistake & increment failure count
     • Boost strategy confidence score          • Penalize strategy confidence score
     • Update app profile (<2ms write)          • Attempt fallback / await user feedback
```

---

## 3. Core Component Design Specifications

### 3.1 The Creative Application Catalog (`src/ikkhi/automation/creative/`)
Pre-seeds canonical cross-app semantic intents for major creative application families:
- **Video & NLE:** DaVinci Resolve (`resolve.exe`), Adobe Premiere Pro (`premiere.exe`), CapCut (`capcut.exe`).
- **3D & VFX:** Blender (`blender.exe`), Adobe After Effects (`afterfx.exe`), Cinema 4D (`cinema 4d.exe`).
- **Image & Vector:** Adobe Photoshop (`photoshop.exe`), Illustrator (`illustrator.exe`), Figma (`figma.exe`).
- **Digital Audio Workstations:** Ableton Live (`ableton live`), FL Studio (`fl64.exe`), Reaper (`reaper.exe`).
- **Code & IDE:** VS Code (`code.exe`), Cursor (`cursor.exe`).

### 3.2 The Experiential Memory Engine (`src/ikkhi/automation/experience.py`)
- **Data Models:**
  - `ActionOutcome`: Encapsulates timestamp, application identifier, intent phrase, strategy (`hotkey`, `uia_control`, `visual_coordinate`), payload, success boolean, and execution latency.
  - `StrategyStats`: Tracks cumulative successes, failures, and calculates an empirical Bayesian reliability score:
    $$\text{Confidence} = \frac{\text{Successes} + 1}{\text{Successes} + \text{Failures} + 2}$$
- **Mistake Learning:**
  - Explicit execution exceptions immediately log failure events.
  - Explicit user rollback phrases (*"undo that"*, *"no, wrong button"*, *"cancel"*) automatically penalize the immediately preceding action.
- **Resource Consciousness:**
  - In-memory dictionary cache for $\mathcal{O}(1)$ lookups (<0.1ms).
  - Compact append-only JSON Lines file (`storage/memory/experience.jsonl`) with automated compaction/rotation capped at 5,000 entries (~500 KB).

---

## 4. Phase Schedule & Task Breakdown

| Task ID | Component Name | Deliverable | Status |
| :--- | :--- | :--- | :--- |
| `EXP-01` | Master Architectural Blueprint | `docs/CREATIVE_APPS_AND_EXPERIENCE_PLAN.md` | 🟢 Completed |
| `EXP-02` | Experiential Memory & Mistake Learner | `src/ikkhi/automation/experience.py` | ⚪ Queued |
| `EXP-03` | Universal Creative Application Catalog | `src/ikkhi/automation/creative/` | ⚪ Queued |
| `EXP-04` | Orchestrator & Universal Engine Integration | `src/ikkhi/automation/universal.py` & `orchestrator.py` | ⚪ Queued |
| `EXP-05` | Comprehensive Unit Test Suite | `tests/unit/test_experience.py` & `test_creative.py` | ⚪ Queued |
| `EXP-06` | Project Governance & Context Synchronization | `CONTEXT.md`, `PROGRESS.md`, `PROJECT_MAP.md` | ⚪ Queued |
