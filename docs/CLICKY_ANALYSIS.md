# Architectural Deconstruction: HeyClicky vs. Ikkhi

## 1. Executive Summary

This document presents a comprehensive technical deconstruction of **HeyClicky** (formerly the viral open-source project *Clicky*, created by Farza Majeed) and benchmarks it against **Ikkhi**. 

Following Clicky's pivot from an open-source prototype into a closed-source, hosted SaaS commercial product ("HeyClicky"), its architectural dependencies have rendered it **cloud-tethered, token-extravagant, latency-heavy, and platform-constrained to macOS**. 

Our mandate for **Ikkhi** is to match and surpass HeyClicky’s companion experience while pioneering an **ultra-efficient, multi-monitor, local-first architecture** that reduces multimodal cloud token consumption by more than **95%**.

---

## 2. Anatomy of HeyClicky: How It Works & Where It Fails

### 2.1 The HeyClicky Pipeline
HeyClicky functions as an on-screen "buddy" that sits adjacent to the mouse cursor, providing visual and verbal guidance:

```
[ Push-to-Talk / Shortcut ]
            │
            ▼
[ macOS ScreenCaptureKit ] ──> Takes full uncompressed screen capture
            │
            ▼
[ AssemblyAI Cloud API ]   ──> Streams microphone audio for transcription ($)
            │
            ▼
[ Anthropic Claude 3.5 ]   ──> Multimodal Vision Model receives full image + prompt ($$)
            │                  Returns explanation text + normalized coordinates
            ▼
[ ElevenLabs Cloud API ]   ──> Generates neural voice audio stream ($$$)
            │
            ▼
[ Floating Cursor Overlay] ──> Draws glowing pointer indicator; plays spoken audio
```

### 2.2 Critical Vulnerabilities of HeyClicky

| Dimension | HeyClicky Flaw | Ikkhi Solution |
| :--- | :--- | :--- |
| **Monetary & Token Cost** | Every single interaction streams raw screenshots and audio to three distinct paid cloud APIs (AssemblyAI + Claude + ElevenLabs). High ongoing costs. | **Hybrid Local-First:** Local GPU Whisper (STT) + Local Piper (TTS) + Tier 0 Regex/UIA cache = **$0.00 for routine tasks**. Gemini Flash called strictly on-demand. |
| **Response Latency** | Tri-API serial waterfall introduces **2.5 to 4.5 seconds** of round-trip latency per interaction. | **Sub-second loop:** Local STT (<250ms) + Local Fast-Path (<2ms) + Local TTS (<150ms) yields near-instant response times. |
| **Data Privacy** | Sensitive desktop screens (code, banking, private messages) are continuously transmitted to third-party endpoints. | **100% Local Privacy Boundary:** Audio and screens remain strictly on the host machine. Cloud vision is opt-in, window-cropped, and downsampled. |
| **Platform Lock-In** | Implemented natively in Swift for macOS; Windows workstations are unsupported. | **Native Windows 11 Optimization:** Direct Windows UI Automation (UIA), Win32 API, and NVIDIA CUDA RTX 3070 hardware acceleration. |
| **Multi-Monitor Handling**| Naive full-desktop captures degrade on multi-screen setups, distorting aspect ratios and inflating image token costs. | **Multi-Monitor Coordinate Normalizer:** Automatically isolates the active display, crops to active window, and maps virtual multi-screen coordinates. |
| **System Memory** | Stateless: Asks the cloud model repeatedly for identical buttons across sessions. | **Adaptive Knowledge Profiles (`storage/profiles/`):** Memorizes button locations upon discovery; subsequent runs are 100% local. |

---

## 3. Gap Analysis: Where Ikkhi Currently Stands vs. HeyClicky

```
                                FEATURE MATURITY RADAR
                                
                             Universal UI Inspection
                                      100%
                                       │
                Multi-Monitor 50% ────┼──── 90% Token Efficiency
                                       │
                     Cursor Guidance  ─┼─  Voice Output (TTS)
                           80%         │        20%
                                  Wake Word (STT)
                                       60%
```

### Gap 1: Local Voice Synthesis (Text-to-Speech)
* **HeyClicky:** Streams answers back using ElevenLabs cloud neural voice.
* **Ikkhi Status:** Architecture supports audio feedback, but local TTS engine is not yet hooked into the runtime.
* **Remedy:** Integrate **Piper TTS** (or Kokoro ONNX) into `src/ikkhi/audio/tts.py`. Runs in under 150ms on CPU/GPU with zero token costs and natural human intonation.

### Gap 2: Multi-Monitor Coordinate & Screen Management
* **HeyClicky:** Bounded to single macOS screen buffers.
* **Ikkhi Status:** Single 4K display verified, but needs virtual multi-monitor bounding box resolution and monitor switching logic.
* **Remedy:** Implement `src/ikkhi/vision/monitors.py` utilizing Win32 `EnumDisplayMonitors` and `GetSystemMetrics(SM_XVIRTUALSCREEN)` to seamlessly support arbitrary multi-display grids.

### Gap 3: Cursor-Adjacent Floating HUD Companion
* **HeyClicky:** Features an animated on-screen "buddy" glyph adjacent to the mouse cursor.
* **Ikkhi Status:** Cursor pointer moves smoothly to target coordinates with radial highlight pulse, but lacks a persistent transparent overlay widget.
* **Remedy:** Build a non-stealing, lightweight transparent overlay HUD (`src/ikkhi/vision/companion.py`) using PyQt6 / PySide6 or Win32 Layered Windows.

### Gap 4: Local Wake-Word & Continuous Audio Loop
* **HeyClicky:** Push-to-talk hotkey only.
* **Ikkhi Status:** Architecture designed for dual mode (Push-to-Talk + "Hey Ikkhi" wake-word); needs live background thread loop assembled.
* **Remedy:** Connect `openwakeword` + `faster-whisper` CUDA into `src/ikkhi/audio/engine.py`.

---

## 4. Architectural Roadmap to Surpass HeyClicky

1. **Sprint 1: Multi-Monitor Management & Screen Isolation**
   - Win32 Virtual Desktop geometry resolver.
   - Cursor-proximity monitor detection (determines which screen the user is focusing on).
2. **Sprint 2: Local Neural TTS Engine (Piper TTS)**
   - Zero-token, high-speed speech synthesizer for spoken answers.
3. **Sprint 3: Cursor-Adjacent Transparent Overlay HUD**
   - Translucent glowing indicator and interactive companion hovering near the mouse.
4. **Sprint 4: Live Audio Ingestion Daemon**
   - Push-to-talk + Wake-word listener running continuously on RTX 3070 CUDA cores.
