---
name: ikkhi-product
description: Product management governance, user value economics, feature lifecycle, release gates, and competitive benchmarking for the Ikkhi desktop companion.
---

# Ikkhi Product Management & Strategic Roadmap Governance Protocol

This skill dictates product strategy, feature prioritization, token economics, and release gate standards for **Ikkhi**.

---

## 1. Product Vision & Value Proposition

**Ikkhi** (ইক্ষি / Vision) is an open-source, resource-conscious, voice-controlled Windows desktop companion designed for creative professionals and power users (DaVinci Resolve, Blender, Premiere, VS Code, Ableton).

### Core Differentiators vs. Competing Solutions:
1. **Vs. HeyClicky:** HeyClicky is macOS-only, cloud-tethered (streaming every screen to Claude/AssemblyAI/ElevenLabs at high API cost and 3-4s latency). Ikkhi is Windows 11-native, 100% local-first (<250ms latency, $0.00 for routine tasks), and invokes Google AI Studio strictly on-demand.
2. **Vs. OpenClaw / Computer-Use:** OpenClaw executes slow multi-turn agentic visual loops (taking 15-30s per task and hundreds of tokens). Ikkhi uses a **Tier 0 Deterministic Fast-Path** (<2ms, 0 tokens) via Windows UI Automation (UIA) and shortcuts, falling back to CV only when necessary.

---

## 2. Token & Resource Economic Invariants

Every feature proposed or built for Ikkhi MUST satisfy the **Zero-Token First Economic Rule**:

| Interaction Tier | Target Frequency | Cost per Action | Latency Target | Execution Method |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 0: Local Fast-Path** | $\ge 95\%$ of all interactions | **$0.00** (0 tokens) | $<2$ ms | Deterministic regex, UIA accessibility cache, hotkeys |
| **Tier 1: On-Demand Multimodal** | $\le 5\%$ of all interactions | $<1,800$ input tokens | $<1.5$ s | Google AI Studio (`gemini-2.0-flash`), window crop downsampled |

### Golden Metrics (Product KPIs):
- **Local-First Ratio:** $\ge 95\%$ of daily commands handled completely offline.
- **Idle CPU/GPU Budget:** $<1.0\%$ CPU, $0.0\%$ GPU when waiting for push-to-talk or wake-word.
- **Hardware Footprint:** VRAM $<2.5$ GB (leaving $>5.5$ GB free on an RTX 3070 for creative video rendering).

---

## 3. Feature Prioritization Matrix (RICE-R)

Features are scored using the **RICE-R Framework** (Reach, Impact, Confidence, Effort, and Resource Cost):

$$\text{Priority Score} = \frac{\text{Reach} \times \text{Impact} \times \text{Confidence}}{\text{Effort} \times \text{Resource Cost}}$$

1. **Reach (1–10):** How many creative applications or workflows benefit?
2. **Impact (1–10):** Does it eliminate tedious mouse clicks or complex multi-key shortcuts?
3. **Confidence (1–10):** Can it be executed deterministically without hallucination?
4. **Effort (1–10):** Engineering complexity and development hours.
5. **Resource Cost (1–10):** Does it introduce continuous background compute or cloud API calls? (Lower cost = higher priority).

---

## 4. Product Lifecycle & Release Gates

Before any milestone or version release is signed off, it must pass all 6 **Product Quality Gates**:

- [ ] **Gate 1: Zero-Exposure Privacy Gate:** No credentials or tokens hardcoded in Git (`.gitignore:36` verified).
- [ ] **Gate 2: Deterministic Safety Gate:** Actions validate active window context; no arbitrary coordinate clicking without boundary verification.
- [ ] **Gate 3: Automated Test Gate:** 100% test pass rate across unit and integration suites (`pytest`).
- [ ] **Gate 4: Standalone Binary Gate:** Builds cleanly into a self-contained single executable (`dist/Ikkhi.exe`) via PyInstaller.
- [ ] **Gate 5: Non-Intrusive UX Gate:** Overlays must never steal window focus from active creative software (`WA_ShowWithoutActivating = True`).
- [ ] **Gate 6: Living Docs Gate:** [`CONTEXT.md`](file:///e:/rouf/software-project/Ikkhi/CONTEXT.md), [`PROGRESS.md`](file:///e:/rouf/software-project/Ikkhi/PROGRESS.md), and [`PROJECT_MAP.md`](file:///e:/rouf/software-project/Ikkhi/PROJECT_MAP.md) synchronized.
