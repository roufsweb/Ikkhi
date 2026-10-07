---
name: ikkhi-ui
description: UI design guidelines for Ikkhi focused on a clean, responsive hobby project aesthetic. Eliminates AI clichés, emoji spam, and corporate SaaS bloat in favor of honest developer utility.
---

# Ikkhi UI Guidelines: The Hacker / Hobbyist Standard

This document defines the interface design rules for **Ikkhi**. Its purpose is to keep the project feeling like a fast, responsive, well-crafted **personal hacker / hobbyist tool** rather than a bloated, venture-backed enterprise AI product.

---

## 1. The "AI Model / Corporate UI" Cliché Inventory (Excluded from Ikkhi)

Every time an AI model or corporate designer builds an interface or writes documentation, they default to a predictable set of tropes. **All of the following are explicitly banned from Ikkhi:**

| AI Model / Corporate Cliché | What AI Models Typically Do | Why It's Excluded & How Ikkhi Replaces It |
| :--- | :--- | :--- |
| **Emoji Spam Everywhere** | Slapping emojis onto every single button, header, badge, tab, and log line (`⚡`, `🚀`, `🤖`, `✨`, `🔥`, `🎬`, `☁️`, `🟢`, `📁`, `⚙️`). | Looks like a crypto bot or cheap landing page. **Ikkhi rule:** Zero emojis in UI components, tab headers, or operational badges. Use clean plain text (`local`, `cloud`, `Activity`, `Settings`). |
| **Enterprise SaaS Pretense** | Pretending a personal Python desktop automation script is a B2B SaaS startup with "Release Readiness Gates", "RICE Prioritization", and "Enterprise SLAs". | Adds bureaucratic weight without value. **Ikkhi rule:** Treat Ikkhi as a fun, hackable desktop tool that solves real automation problems for its author. |
| **Vanity Telemetry Cards** | Flashing exaggerated metrics ("Tokens Saved: 1,800!", "ROI Savings: $0.0018", "Enterprise Efficiency: 98%"). | Vanity numbers clutter the screen. **Ikkhi rule:** Show simple, useful stats: how many commands ran locally vs. routed to the cloud, and the live log of what was executed. |
| **Theatrical "AI is Thinking" Delays** | Glowing neon rainbow spinners, mysterious pulsing purple clouds, or fake delays to make the AI look "deep". | Distracting and slow. **Ikkhi rule:** Instant response. Sub-millisecond local execution. If something is processing, show a minimal, subtle line or state change and finish immediately. |
| **Jargon Overload** | Filling docs with corporate buzzwords like "multimodal spatial substrate", "neuro-symbolic orchestration", "material elevation hierarchies". | Obscures how the code actually works. **Ikkhi rule:** Speak plainly. It's a local Faster-Whisper listener, a regex router, and Windows UI automation / hotkey triggers. |
| **Complex Pricing / Tier Badges** | Slapping "⚡ 0ms • $0.00" or "TIER 0 DETERMINISTIC VIP" chips onto the UI. | Overcomplicated. **Ikkhi rule:** Minimal tags. Just `local` or `cloud`. |
| **Focus-Stealing Windows** | Popping up dialogs or overlays that take focus away from what the user is doing. | Destroys video editing, 3D work, or coding flow. **Ikkhi rule:** Strict `WA_ShowWithoutActivating` and `WindowType.Tool`. Never steal OS window focus. |

---

## 2. The Hobbyist / Hacker Design Philosophy

A great developer hobby project has distinct virtues:
1. **Lightweight & Fast:** Under 1% CPU when idle. No lag, no bloated frameworks, no stuttering animations.
2. **Clean & Dark:** A subtle, clean dark theme (`#07090e`, `#0d121d`) that sits quietly on a secondary monitor or top of screen without glaring bright colors.
3. **Glanceable & Honest:**
   - In idle state: Small, quiet HUD pill.
   - When listening: Simple, organic audio bars showing your voice is actually hitting the microphone.
   - When executed: Plain text showing what ran (`local` macro or `cloud` query).
4. **Non-Intrusive:** The companion sits at the top of the screen or in the system tray. It never interrupts your work.

---

## 3. UI Tokens & Styling Rules

Keep the stylesheet simple, legible, and unpretentious:

### Surfaces
- Base background: `#07090e` (Cosmic black)
- Card / panel background: `#0d121d`
- Borders: `rgba(255, 255, 255, 0.08)` (1px subtle border)
- Text color: `#f8fafc` (Primary), `#94a3b8` (Muted)

### Status Indicators (Plain Text, No Emojis)
- Local macro executed: small green tag `local` (`#34d399`, border `rgba(16, 185, 129, 0.35)`)
- Cloud query executed: small purple tag `cloud` (`#c084fc`, border `rgba(168, 85, 247, 0.35)`)
- Active app context: small subtle badge with clean process name (e.g., `DaVinci Resolve`, `VS Code`, `Blender`)

### Typography
- Primary UI: System default sans-serif (`Segoe UI Variable`, `Inter`, `system-ui`)
- Monospace (logs, timestamps, badges): `JetBrains Mono`, `Consolas`, `monospace`

---

## 4. UI Checklist for New Features

When writing or updating any UI component in `src/ikkhi/ui/`:

- [ ] Does it have zero emojis in tab names, buttons, badges, and titles?
- [ ] Does it run without blocking the Qt event loop?
- [ ] Is it free of fake corporate metrics and marketing jargon?
- [ ] Does it avoid stealing window focus from active creative tools?
- [ ] Is the code easy to read, modify, and hack on?
