---
name: ikkhi-product
description: Lightweight task planning and feature ideas for Ikkhi as a personal hobby automation project, free of corporate SaaS frameworks.
---

# Ikkhi Developer & Hobby Task Protocol

This document replaces corporate product management bloat with practical, developer-friendly planning for **Ikkhi** as a personal automation project.

---

## 1. Project Character: A Real Hacker Tool, Not a Commercial Product

Ikkhi is a personal desktop helper for automating Windows workflows (video editing in DaVinci Resolve, 3D shortcuts in Blender, audio commands, screen reading) using voice and local models.

It is **not** a SaaS startup, not an enterprise B2B product, and not an investor pitch.

### What We Care About:
- Does it work when I press the key or say the wake word?
- Does it run fast and stay completely offline for routine macros?
- Does it stay out of the way and use almost zero CPU/GPU when idle?
- Is the code clean, modular, and fun to hack on?

### What We Do Not Care About:
- Corporate prioritization frameworks (RICE, MoSCoW, OKRs).
- Monetization, commercial pricing tiers, or enterprise compliance gates.
- Vanity marketing stats or corporate slide decks.

---

## 2. Feature Idea Checklist (Hacker Pragmatism)

When thinking about adding a new voice command or feature:

1. **Practical Utility:** Is this something you actually want to use while editing a video, writing code, or working on your desktop?
2. **Local-First Speed:** Can it be done locally with a fast hotkey, regex pattern, or Windows UI Automation before touching any cloud API?
3. **No Lag:** Does it respond in under 300ms without freezing the desktop?
4. **Clean Implementation:** Is it a clean Python function registered in the action registry or a straightforward PyQt widget?

---

## 3. Working Checklist for Upcoming Tweaks

- [ ] Add more application shortcuts (e.g. specialized macros for your favorite tools).
- [ ] Keep the UI minimal, quiet, and responsive.
- [ ] Keep all unit tests passing (`pytest tests/`).
- [ ] Keep dependencies lean and locally runnable.
