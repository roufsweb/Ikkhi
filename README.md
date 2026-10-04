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

Execute the assistant in CLI testing mode:
```powershell
# Test deterministic local fast-path (0 tokens):
python -m ikkhi cut clip

# Test visual query routing:
python -m ikkhi where is the export button
```

---

## Quality Assurance & Testing

Run unit tests via `pytest`:
```powershell
pytest tests/unit
```

---

## License
Distributed under the MIT License. See `LICENSE` for details.
