---
name: ikkhi-ui
description: Autonomous UI engineering, opulent aesthetic design guidelines, and design system governance inspired by Cloudflare, Apple, Google, Microsoft Fluent 2, and OpenClaw for the Ikkhi desktop companion.
---

# Ikkhi Autonomous UI Engineering & Design Governance Protocol
### *Curated by 10-Year Principal UI/UX & Spatial HCI Design Heuristics*

This skill dictates the aesthetic philosophy, cognitive architecture, design tokens, and autonomous implementation rules for crafting the graphical interfaces of **Ikkhi**.

---

## 1. Design Philosophy: The 10-Year Veteran Manifesto

Designing an AI desktop companion is fundamentally different from designing a standard SaaS web app. An intelligent desktop assistant lives alongside the user's high-cognitive-load creative workflows (video editing in DaVinci Resolve, 3D modeling in Blender, programming in VS Code). 

### The Five Inviolable Design Pillars
1. **Peripheral Calm, Zero Cognitive Intrusion:**
   - The UI must never fight for focal attention. It exists in the user's peripheral awareness until summoned.
   - It must **never steal OS window focus** (`Qt.WidgetAttribute.WA_ShowWithoutActivating = True`). Creative tools must never drop key inputs or timeline scrubbing because an assistant overlay appeared.
2. **Deterministic Transparency over AI Mysticism:**
   - Never show a generic "AI is thinking" spinning wheel without intent.
   - Ground the user immediately: Show *which app* is being targeted (e.g. `🎬 DaVinci Resolve`), *which tier* handled the command (`⚡ 0ms • $0.00` Local vs. `☁️ Gemini Flash` Cloud), and *what latency* occurred.
3. **Visceral Acoustic-Visual Feedback:**
   - When a user speaks, sound waves are physical energy. A static circle or flat bar fails to communicate that the system heard them.
   - Visual waveforms must utilize **harmonic formant weighting** (center-weighted bell curves), scaling organically with real-time decibel RMS values at 40+ FPS.
4. **Spatial Continuity (The "Dynamic Island" Morphology):**
   - Avoid abrupt popups, modal flashes, or jarring window appearances.
   - The companion HUD is a single cohesive organic pill that fluidly expands, morphs its internal anatomy, and contracts back to idle resting state.
5. **The Doherty Threshold (<400ms Feedback Loop):**
   - In HCI, productivity skyrockets when human and computer interact at a pace that ensures neither has to wait.
   - Instant visual response (<16ms) on keydown or wake-word detection, followed by deterministic sub-100ms local execution.

---

## 2. Aesthetic DNA & Inspiration Synthesis

| Design Influence | Core Aesthetics | Translation into Ikkhi's UI Architecture |
| :--- | :--- | :--- |
| **Apple (macOS / visionOS / Dynamic Island)** | Frosted glassmorphism, dynamic spring physics, organic rounded pill geometries (16px–24px radius), soft ambient drop-shadows, subtle depth layering. | Applied to the **Floating Companion HUD Overlay** (`FloatingCompanionOverlay`), state transitions, and smooth expansion/contraction. |
| **Cloudflare** | High data density, monospace telemetry, technical elegance, ultra-fine 1px borders (`rgba(255,255,255,0.08)`), crisp contrast, latency readouts. | Applied to the **Analytics Dashboard**, live event logs, execution tier classification, and token economy counters. |
| **Linear / OpenClaw / Vercel** | Obsidian cosmic dark mode (`#07090e`, `#0b0f17`), neon electric cyan (`#00e5ff`) & cyber violet (`#a855f7`) gradients, tactile keycap badges (`kbd`). | Applied to brand identity, the glowing Bengali monogram ("ই"), and visual attention highlights. |
| **Microsoft Fluent 2 / Mica** | Windows 11 desktop integration, layered material elevations, Segoe UI Variable typography, acrylic translucency. | Applied to system tray applets, context menus, and native Windows shell harmonization. |
| **HeyClicky (Spatial Grounding)** | Non-disruptive visual target beacon ripples, crosshair reticles, cursor trajectory awareness. | Applied to `CursorTargetBeacon`, showing exact coordinate targets when Ikkhi points or acts on the canvas. |

---

## 3. Hard Design Tokens & Color Palette

All UI components MUST adhere strictly to the standardized token dictionary:

### 3.1 Obsidian Canvas & Glass Layering
```css
--canvas-base:       #07090e; /* Cosmic obsidian black */
--surface-card:      #0d121d; /* Elevated dark card container */
--surface-glass:     rgba(13, 18, 29, 0.78); /* Frosted glassmorphic backdrop */
--border-subtle:     rgba(255, 255, 255, 0.08); /* 1px hairline border */
--border-focus:      rgba(0, 229, 255, 0.40); /* Active accent border */
--surface-hover:     rgba(255, 255, 255, 0.04);
--surface-active:    rgba(255, 255, 255, 0.08);
```

### 3.2 Semantic State & Accent Palette
- **Primary / Listening Accent:** `#00e5ff` (Electric Cyan) — signals active auditory capture and microphone receptivity.
- **Neural / Processing Accent:** `#a855f7` (Cyber Violet) — signals Whisper GPU inference or orchestrator reasoning.
- **Success / Speaking Accent:** `#10b981` (Emerald Green) — signals deterministic action execution and TTS voice response.
- **Warning / Ambiguity Accent:** `#f59e0b` (Amber Flame) — signals fuzzy fallbacks or low confidence actions.
- **Muted / Error Accent:** `#ef4444` (Crimson Red) — signals microphone mute or hardware access barriers.

### 3.3 Typography & Readability (WCAG AAA Compliance)
- **Primary Label:** `#f8fafc` (Clean crisp slate white, 100% opacity, 600 weight)
- **Secondary Detail:** `#94a3b8` (Muted technical slate, 400 weight)
- **Tertiary / Subtext:** `#64748b` (Subtle metadata, 400 weight)
- **Interface Font Stack:** `"Segoe UI Variable", "Inter", -apple-system, BlinkMacSystemFont, sans-serif`
- **Monospace Telemetry Stack:** `"JetBrains Mono", "Cascadia Code", "Consolas", monospace`

---

## 4. Complex Logic to Intuitive UI: Architectural Mappings

### 4.1 Live Voice Waveform Physics (Harmonic Formants)
Do not draw random or linear audio bars. Human voice resonance concentrates in the middle speech frequencies (formants F1–F3).
- Implement a center-weighted harmonic bell curve for the 7 visualizer bars:
  $$\text{weight}_i = \max\left(0.45, 1.0 - \left(\frac{|i - \text{center}|}{\text{center} + 1}\right)^{1.3}\right)$$
- Modulate height with sinusoidal phase offset:
  $$\text{bar\_height} = \text{base\_height} + (\text{max\_amp} \times \text{normalized\_rms} \times \text{weight}_i \times (0.7 + 0.3 \sin(\text{phase} + i \times 0.85)))$$
- Paint each bar with a vertical linear gradient from `#00e5ff` to `#a855f7` with smooth rounded caps (`QPainter.drawRoundedRect`).

### 4.2 Dynamic Island State Machine
The companion overlay transitions smoothly across 4 discrete states:
1. **Idle State (`idle`):**
   - Monogram: Subtle slate glow (`#64748b`).
   - Title: "Ikkhi Companion".
   - Subtitle: "Hold Ctrl+Alt+Space to speak" (or "Hey Ikkhi").
   - Waveform: Dormant flat bars (height 4px).
   - Badges: Active app chip visible (`🎬 DaVinci Resolve`), Tier badge hidden.
2. **Listening State (`listening`):**
   - Monogram: Vibrant Electric Cyan (`#00e5ff`).
   - Title: "Listening...".
   - Subtitle: "Capture active".
   - Waveform: Animated harmonic bars pulsating in real-time to microphone RMS.
3. **Processing State (`processing`):**
   - Monogram: Cyber Violet (`#a855f7`).
   - Title: "Processing...".
   - Subtitle: "Whisper CUDA transcription & intent routing".
   - Indeterminate progress bar sweeps across the container.
4. **Speaking / Done State (`speaking`):**
   - Monogram: Emerald Green (`#10b981`).
   - Title: Recognized utterance.
   - Subtitle: Deterministic action feedback / TTS utterance.
   - Tier badge flashes: `⚡ 0ms • $0.00` (Local) or `☁️ Gemini Flash` (Cloud).
   - Auto-reverts to `idle` after 3.8 seconds without user friction.

### 4.3 HeyClicky Visual Target Beacon (`CursorTargetBeacon`)
When the assistant points to or clicks a UI element on screen:
- Instantiate a frameless, transparent top-level canvas at the target coordinates.
- Animate 2 concentric radar rings radiating outward over 600ms with ease-out cubic decay:
  - Ring 1 (Inner): Neon Cyan (`#00e5ff`) with glowing pulse.
  - Ring 2 (Outer): Cyber Violet (`#a855f7`) with decaying alpha.
  - Reticle: Crosshair ticks and center dot indicating exact click target.
- Automatically destroys itself upon animation completion.

---

## 5. Strict Engineering Invariants & Checklist

When building or modifying any UI component in `src/ikkhi/ui/`, rigorously satisfy this checklist:

- [ ] **Focus Invariant:** Is `WA_ShowWithoutActivating = True` set on all overlay windows?
- [ ] **Frame Rate Invariant:** Are UI repaints bounded by 25ms timers (40 FPS)? Is CPU overhead strictly < 1% during animation?
- [ ] **Thread Safety Invariant:** Are all heavy compute operations (Whisper STT, LLM queries, OS automation) offloaded to `QThread` and bridged back via Qt Signals?
- [ ] **Contrast & Accessibility:** Does primary text achieve >= 7:1 contrast ratio against the glassmorphic background?
- [ ] **Multi-Monitor DPI:** Does the positioning logic respect multi-monitor geometry and screen DPI scaling?
- [ ] **Graceful Degradation:** Does the UI function seamlessly even if system fonts (JetBrains Mono) are missing by falling back to standard system sans-serif and monospace stacks?
