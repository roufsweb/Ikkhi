# Ikkhi (ইক্ষি) — Local-First Voice Desktop Assistant

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OS: Windows](https://img.shields.io/badge/platform-Windows%2011-blue.svg)](https://www.microsoft.com/windows)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**Ikkhi** (*ইক্ষি*, Bengali for *vision/sight*) is an enterprise-grade, resource-efficient Windows desktop assistant engineered for hands-free workflow automation. Built upon a hybrid execution model, Ikkhi empowers creators and developers to operate demanding creative suites (such as DaVinci Resolve) and development environments without manual keystrokes or mouse navigation.

---

## Key Architectural Highlights

* **100% Local Voice Pipeline:** Accelerated speech-to-text powered by `faster-whisper` running locally on NVIDIA CUDA hardware (<250ms latency), ensuring complete auditory privacy.
* **Two-Tier Intent Routing:**
  * **Tier 0 (Deterministic Local Fast-Path):** Executes standard keyboard shortcuts, macro sequences, and Windows UI automation locally with **0ms cloud latency and zero API cost**.
  * **Tier 1 (Smart Multimodal Fallback):** Engages Google AI Studio (Gemini 2.0 Flash) strictly on-demand for semantic reasoning and screen comprehension.
* **Credit-Conscious Screen Indexer:** Intelligently captures only the active foreground window and compresses image dimensions ($\le$ 1024px JPEG) to reduce multimodal token expenditure by up to 90% on high-DPI (4K) displays.
* **Visual Cursor Guidance:** Converts normalized bounding coordinates into hardware-accurate physical pixels, animating the system cursor along an ergonomic ease-out curve to physically highlight target UI controls.

---

## System Architecture

```
                                [ Microphone Input ]
                                          │
             ┌────────────────────────────┴────────────────────────────┐
             ▼ (Push-to-Talk: Ctrl+Alt+Space)                          ▼ (Wake Word: "Hey Ikkhi")
     [ 0% Idle CPU Mode ]                                      [ openWakeWord Engine ]
             │                                                         │
             └────────────────────────────┬────────────────────────────┘
                                          ▼
                           [ Silero VAD + faster-whisper ]
                              (Local RTX 3070 CUDA STT)
                                          │
                                [ Local Transcript ]
                                          │
                      ┌───────────────────┴───────────────────┐
                      ▼                                       ▼
           [ Tier 0: Local Fast-Path ]             [ Tier 1: Multimodal AI ]
           • Compiled Regex & Exact Match          • Google AI Studio (Gemini Flash)
           • Windows & DaVinci Macros              • Active Window Crop & Indexing
           • 0 Tokens / $0.00 Cost                 • Token-Capped Bounding Box Detection
                      │                                       │
                      └───────────────────┬───────────────────┘
                                          ▼
                           [ Hybrid Execution Engine ]
              ├── Native Windows UI Automation (pywinauto)
              ├── Deterministic Hotkeys (pyautogui / OS VK)
              └── Visual Cursor Pointer (DPI-Aware Physical Guidance)
```

---

## Directory Structure (PEP 621 Standard)

```
Ikkhi/
├── .agents/                    # Agent directives and skill specifications
├── docs/                       # Architectural documentation & project tracking
├── src/
│   └── ikkhi/                  # Core package root
│       ├── __init__.py
│       ├── __main__.py         # CLI entry point
│       ├── py.typed            # PEP 561 static typing marker
│       ├── core/               # Configuration, router, and orchestrator
│       ├── audio/              # Voice capture, VAD, and local STT
│       ├── vision/             # Active window indexer and cursor pointer
│       ├── automation/         # Deterministic action registry and app macros
│       └── ai/                 # Multimodal Gemini integration
├── tests/                      # Pytest unit and integration test suites
├── scripts/                    # Hardware validation & diagnostic routines
├── pyproject.toml              # Modern package metadata and build configuration
├── requirements.txt            # Locked runtime dependencies
└── config.yaml                 # Central application settings
```

---

## Getting Started

### Prerequisites
* Windows 11 (64-bit)
* Python 3.10, 3.11, or 3.12
* NVIDIA RTX GPU (6GB+ VRAM recommended for CUDA Whisper inference)

### Installation
1. Clone the repository and navigate to the project directory:
   ```powershell
   git clone https://github.com/your-org/ikkhi.git
   cd ikkhi
   ```

2. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the dependencies in editable mode:
   ```powershell
   pip install -e .
   ```

4. Configure your environment:
   ```powershell
   copy .env.example .env
   # Add your optional GEMINI_API_KEY for multimodal visual queries
   ```

5. Run the hardware and environment validation routine:
   ```powershell
   python scripts/validate_environment.py
   ```

---

## Running Ikkhi

### 1. Standalone GUI Companion (Default)
Launch the visual desktop companion (HUD Overlay + Dashboard + System Tray):
```powershell
# Via one-click launcher:
.\launch_ikkhi.bat

# Or directly via Python module:
python -m ikkhi
```

### 2. Standalone Single Binary Deployment
Ikkhi compiles into a self-contained, single-file Windows executable with zero runtime dependencies:
```powershell
.\dist\Ikkhi.exe
```

### 3. Interactive Diagnostic Console
Monitor live microphone audio levels and test wake-word detection:
```powershell
.\launch_tester.bat
```

---

## Quality Assurance & Testing

Run the full automated test suite (46 unit and integration tests):
```powershell
pytest tests/
```

---

## Credits, Acknowledgments & Open-Source Attributions

Ikkhi stands on the shoulders of the open-source community, foundational AI research, and premier interface design systems. We gratefully acknowledge and credit the following projects, models, libraries, and design paradigms:

### Core AI & Machine Learning Foundations
* **[faster-whisper](https://github.com/SYSTRAN/faster-whisper) & [OpenAI Whisper](https://github.com/openai/whisper):** Developed by SYSTRAN and OpenAI, powered by [CTranslate2](https://github.com/OpenNMT/CTranslate2). Provides Ikkhi's sub-200ms local, private speech-to-text inference on NVIDIA CUDA cores.
* **[openWakeWord](https://github.com/dscripka/openWakeWord):** Created by David Scripka. Powers Ikkhi's ultra-low-overhead (<1% CPU) continuous neural wake-word detection via ONNX Runtime.
* **[Piper TTS](https://github.com/rhasspy/piper):** Created by Michael Hansen (Rhasspy). Informs Ikkhi's fast, zero-token local voice synthesis.
* **[DeepSeek AI](https://github.com/deepseek-ai):** For foundational research and open weights across DeepSeek-V3, DeepSeek-R1 reasoning distillations, Multi-Head Latent Attention (MLA KV-cache compression), and Program-Aided Automation ("Code-as-Action") paradigms.
* **[Google AI Studio & Gemini](https://ai.google.dev):** Official `google-genai` SDK providing on-demand Tier 1 multimodal visual screen grounding and bounding box resolution.

### Windows Desktop & Automation Stack
* **[pywinauto](https://github.com/pywinauto/pywinauto):** Authored by Mark Hammond, Vasily Ryabov, and contributors. Powers Ikkhi's Tier 1/2 Windows UI Automation (UIA) accessibility tree inspection.
* **[PyAutoGUI](https://github.com/asweigart/pyautogui) & [pynput](https://github.com/moses-palmer/pynput):** Created by Al Sweigart and Moses Palmer. Provides hardware keyboard hooks and multi-monitor cursor kinematics.
* **[pywin32](https://github.com/mhammond/pywin32):** By Mark Hammond. Provides direct Win32 API access for DPI awareness, window stations, and audio device queries.
* **[sounddevice](https://github.com/spatialaudio/python-sounddevice):** By Matthias Geier. Powers 16kHz zero-copy microphone buffer streaming.

### Graphical User Interface & Frameworks
* **[PyQt6 & The Qt Project](https://www.riverbankcomputing.com/software/pyqt/):** By Riverbank Computing and The Qt Company. Drives Ikkhi's hardware-accelerated, double-buffered companion HUD overlay, reactive waveform visualizer, and dashboard.
* **[Pydantic](https://github.com/pydantic/pydantic):** By Samuel Colvin and contributors. Enforces type-safe system configuration, validation, and schema definitions.

### Architectural & Design System Inspirations
* **[Cloudflare](https://www.cloudflare.com/):** Inspired the high-density telemetry surfaces, hairline borders (`rgba(255,255,255,0.08)`), monospace metric readouts, and clean data tables in the Analytics Dashboard.
* **[Apple](https://www.apple.com/) (macOS & visionOS):** Inspired the translucent frosted glassmorphism, fluid spring physics, ambient drop shadows, and organic micro-animations in the Floating Companion HUD Overlay.
* **[Microsoft Fluent 2](https://fluent2.microsoft.design/):** Inspired the Windows 11 desktop harmony, Mica and Acrylic layered material elevations, and Segoe UI Variable typography.
* **[OpenClaw](https://github.com/openclaw) (formerly Clicky):** Provided early conceptual inspiration for hands-free voice companions in creative software.
* **[Linear](https://linear.app/) & [Vercel](https://vercel.com/):** Inspired the deep obsidian dark-mode palettes (`#07090e`), neon cyan/violet glowing states, and tactile keyboard shortcut keycaps (`<kbd>`).
* **[Talon Voice](https://talonvoice.com/) & [Microsoft UFO](https://github.com/microsoft/UFO):** Prior art in desktop accessibility grammars and dual-agent Windows UI automation.

---

## License
Distributed under the MIT License. See `LICENSE` for details.

