---
name: ikkhi-ui
description: Autonomous UI engineering, opulent aesthetic design guidelines, and design system governance inspired by Cloudflare, Apple, Google, Microsoft Fluent 2, and OpenClaw for the Ikkhi desktop companion.
---

# Ikkhi Autonomous UI Engineering & Design Governance Protocol

This skill dictates the aesthetic, architectural, and behavioral rules for crafting and autonomously polishing the graphical interfaces of **Ikkhi**.

---

## 1. Aesthetic DNA & Inspiration Matrix

The Ikkhi desktop companion synthesizes the design languages of five industry-leading design systems:

| Design Influence | Core Aesthetics | Implementation in Ikkhi |
| :--- | :--- | :--- |
| **Cloudflare** | Precision telemetry, high data density, ultra-subtle 1px borders (`rgba(255,255,255,0.08)`), monospace metric readouts, clean tabular structures. | Applied to the **Analytics Dashboard**, live event logs, token economy metrics, and latency counters. |
| **Apple (macOS / visionOS)** | Frosted glassmorphism, dynamic spring physics, soft ambient dropshadows, rounded pills (12–16px), organic micro-animations. | Applied to the **Floating Companion HUD Overlay**, status state changes, and audio waveform fluid motion. |
| **Microsoft Fluent 2 / Mica** | Windows 11 desktop integration, layered material elevations, Segoe UI Variable typography, acrylic translucency. | Applied to native shell menus, window borders, and system tray applets. |
| **Google Material You** | Expressive contextual states, reactive color chips, clear contrast boundaries, touch/cursor accessibility. | Applied to interactive buttons, status pills, and settings toggles. |
| **OpenClaw / Linear / Vercel** | Obsidian deep-space dark mode (`#07090e`, `#0b0f17`), neon electric cyan (`#00e5ff`) and violet (`#a855f7`) gradients, shortcut keycap badges (`kbd`). | Applied to brand identity, the glowing Bengali monogram ("ই"), and visual attention highlights. |

---

## 2. Hard Design Tokens & Color Palette

All UI components MUST adhere strictly to the standardized token dictionary:

### 2.1 Surfaces & Canvas (Obsidian Layering)
- **Base Canvas (Level 0):** `#07090e` (Deep cosmic black)
- **Card Background (Level 1):** `#0d121d` (Elevated dark container)
- **Border / Divider:** `rgba(255, 255, 255, 0.08)` / `#1e2638` (Ultra-fine 1px hair-line)
- **Glassmorphic Fill:** `rgba(13, 18, 29, 0.78)` with `backdrop-filter: blur(24px)`
- **Hover Surface:** `rgba(255, 255, 255, 0.04)`
- **Active Surface:** `rgba(255, 255, 255, 0.08)`

### 2.2 Brand & Semantic Accents
- **Electric Cyan (Primary / Listening):** `#00e5ff` (RGB: `0, 229, 255`)
- **Cyber Violet (Processing / Neural):** `#a855f7` (RGB: `168, 85, 247`)
- **Emerald Green (Speaking / Success):** `#10b981` (RGB: `16, 185, 129`)
- **Amber Flame (Warning / Fallback):** `#f59e0b` (RGB: `245, 158, 11`)
- **Crimson Red (Error / Muted):** `#ef4444` (RGB: `239, 68, 68`)

### 2.3 Typography & Readability (WCAG AAA)
- **Primary Text:** `#f8fafc` (Clean crisp white, 100% opacity)
- **Secondary Text:** `#94a3b8` (Muted technical slate)
- **Tertiary / Subtext:** `#64748b` (Subtle metadata)
- **Font Stack:** `"Segoe UI Variable", "Inter", -apple-system, BlinkMacSystemFont, sans-serif`
- **Monospace Stack (Data / Logs):** `"JetBrains Mono", "Cascadia Code", "Consolas", monospace`

---

## 3. Strict Rules & Regulations for Autonomous UI Engineering

### Rule 1: Zero Visual Stutter & 60 FPS Event Loop Guarantee
- Never execute file I/O, network requests, audio transcription, or heavy processing on the Qt GUI main thread.
- Always delegate asynchronous compute to `QThread` or non-blocking timers (`QTimer.singleShot`).
- Waveform visualizers and animations must execute under a 25ms timer (40–60 FPS) with smooth anti-aliased interpolation.

### Rule 2: Non-Intrusive Desktop Behavior
- The floating companion overlay must **never steal focus** from active creative applications (DaVinci Resolve, Blender, VS Code).
- Configure overlay window flags with:
  `Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool`
  and attribute `Qt.WidgetAttribute.WA_ShowWithoutActivating = True`.

### Rule 3: High-Density Telemetry & Monospace Precision
- All metrics cards (Tokens Saved, Fast-Path Actions, Latency, VRAM usage) must format numbers clearly with thousands separators (`1,800`).
- Use monospace font styling for timestamps, memory numbers, and shortcut badges.

### Rule 4: Keyboard-First Micro-Interactions & Shortcut Keycaps
- Every actionable item or command shortcut must be visually rendered with a tactile keycap badge:
  `<kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>Space</kbd>`
  featuring subtle top-bevel highlights (`rgba(255,255,255,0.12)`) and bottom shadows.

### Rule 5: Double-Buffered Custom Painting
- All custom `paintEvent` implementations (`AudioWaveformVisualizer`, `IkkhiTrayIcon`, custom meters) MUST enable:
  `painter.setRenderHint(QPainter.RenderHint.Antialiasing)`
  and utilize vector math rather than hardcoded pixel offsets to remain flawless across 1080p, 1440p, and 4K displays.

---

## 4. Autonomous UI Polishing Checklist

Whenever creating or modifying a UI component in `src/ikkhi/ui/`, verify the following:

- [ ] **Contrast Check:** Does text contrast against background surface meet >= 4.5:1 ratio?
- [ ] **State Transition:** Does the component visually indicate `idle`, `listening`, `processing`, and `speaking` states with color cues and micro-animations?
- [ ] **DPI Scaling:** Are coordinate dimensions relative or scaled to screen DPI?
- [ ] **Glow & Drop Shadow:** Is there an ambient drop shadow (`QGraphicsDropShadowEffect`, blur radius >= 20, opacity 0.5-0.7)?
- [ ] **Hover Polish:** Do buttons have a distinct hover transition (`background-color`, border brightness increase)?
- [ ] **Tray Integration:** Can the window be summoned or dismissed smoothly from the Windows system tray?
