# Boundaries & Safety Guardrails: Ikkhi

## 1. Privacy & Cloud AI Cost Guardrails
- **Zero Continuous Cloud Streaming:** Audio input and camera feeds are NEVER continuously streamed to the cloud. Audio is always transcribed locally via `faster-whisper`.
- **Selective Google AI Studio (Gemini) Usage:** 
  - Standard commands (cuts, clicks, shortcuts, app navigation) must be handled 100% locally with 0 API calls.
  - The Gemini API is only called on-demand when:
    1. The user explicitly asks a visual question about the screen ("What is this button?", "Explain this error").
    2. Local intent classification fails to match any registered macro.
- **Credit & Token Optimization Mandate:**
  - Before sending a screenshot to Gemini, the screen indexer must crop to the active window or target region, downscale where appropriate, and check if the screen state has changed.
  - Never send raw 4K uncompressed screenshots when a targeted 720p crop is sufficient.
- **Local Fallback:** The user can disable cloud AI entirely at any time and run 100% offline.

---

## 2. Execution Safety Boundaries (No AI Hallucination)
- **Deterministic Action Contract:** The LLM's output is restricted to choosing from a catalog of known, registered Python functions with validated type-safe arguments (e.g. via Pydantic or structured tool calling).
- **No Arbitrary Code Execution:** The LLM is **never** permitted to generate raw Python code, PowerShell commands, or shell scripts on the fly and execute them directly without explicit user review.
- **No Blind Visual Clicks:** Coordinates are never hallucinated by an LLM guessing pixel positions. All visual clicks must be derived from:
  1. Identified Windows UI Automation element bounding boxes, OR
  2. OpenCV template matching / pixel search with a minimum confidence threshold (e.g. >= 0.85), OR
  3. Pre-calibrated, resolution-normalized button coordinates recorded in config files.
- **Destructive Action Confirmation:** Commands that can delete data, close unsaved work, or terminate critical processes must require audible or visual confirmation before triggering.

---

## 3. Resource & Performance Limits
- **Idle State CPU Budget:** Under 1.5% CPU when in passive wake-word listening mode.
- **Memory Footprint:** Under 1.5 GB RAM during active state when models are loaded (using quantized models like Whisper `tiny`/`base` int8, and small SLMs or rule-based matching where possible).
- **Background Daemon Behavior:** Low thread priority so heavy foreground applications (video rendering, compiling, gaming) are never starved of compute.
