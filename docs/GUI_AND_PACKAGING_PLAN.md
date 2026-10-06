# Master Implementation Plan: Standalone GUI Application & Single-Executable Deployment

## 1. Executive Summary & Architectural Vision

This master blueprint specifies the complete architectural paradigm, engineering workflow, and packaging toolchain required to transform **Ikkhi** into an opulent, production-grade desktop GUI companion application. The entire software ecosystem will culminate in a self-contained, single-file Windows binary (`Ikkhi.exe`), possessing zero external runtime prerequisites and obviating the requirement for an ambient Python interpreter or package manager on client workstations.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 IKKHI DESKTOP GUI STACK                                │
├───────────────────────────────────────────┬────────────────────────────────────────────┤
│                                           │                                            │
│        ┌──────────────────────────────────┼──────────────────────────────────┐         │
│        ▼                                  ▼                                  ▼         │
│ [ Floating HUD Overlay ]         [ System Tray Applet ]       [ Settings & Analytics ] │
│ • Translucent frosted glass      • Discreet notification icon • Real-time token meter  │
│ • Reactive RMS audio waveform    • Status & profile inspector • Hardware & hotkey cfg  │
│ • Non-stealing stay-on-top       • Graceful lifecycle control • Adaptive UIA viewer    │
└───────────────────────────────────────────┴────────────────────────────────────────────┘
                                            │
                                            ▼
                    ┌────────────────────────────────────────────────┐
                    │     PyInstaller Single-File Executable Engine  │
                    │        (Standalone Windows Binary: Ikkhi.exe)  │
                    │   • Bundled PortAudio, CTranslate2 & CUDA DLLs │
                    │   • Virtualised resource loader (sys._MEIPASS) │
                    │   • Persistent local storage under %APPDATA%   │
                    └────────────────────────────────────────────────┘
```

---

## 2. Core Graphical Components & Subsystems

### 2.1 Design Language & Stylistic Tokens ([`src/ikkhi/ui/theme.py`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/ui/theme.py))
* **Palette:** Deep Obsidian (`#0b0f17`), Translucent Slate (`rgba(22, 27, 34, 0.88)`), Electric Cyan (`#00e5ff`), Royal Violet (`#7209b7`), Emerald Accent (`#10b981`), and Crimson Mute (`#f43f5e`).
* **Typography:** Modern variable sans-serif hierarchy prioritizing `Segoe UI Variable`, `Segoe UI`, and fallback system UI fonts with curated kerning and weights.
* **Component Styling:** Glassmorphic borders (`border: 1px solid rgba(255, 255, 255, 0.12)`), pill geometry, and vibrant linear gradient accents.

### 2.2 Floating Companion HUD Overlay ([`src/ikkhi/ui/overlay.py`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/ui/overlay.py))
* **Window Characteristics:** `Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool`. Crucially, the `Tool` window attribute eliminates Alt+Tab pollution and circumvents focus-stealing issues over resource-intensive creative suites such as DaVinci Resolve or VS Code.
* **Dynamic Waveform Visualizer:** Real-time multi-bar RMS visualizer reacting continuously to incoming microphone amplitude variations while Push-to-Talk is engaged.
* **State Transition Machine:**
  * `IDLE`: Compact translucent pill displaying the Bengali monogram "ইক্ষি" with a subtle ambient glow.
  * `LISTENING`: Cyan/violet halo with pulsing waveform bars during audio acquisition.
  * `PROCESSING`: Indigo indeterminate pulse during local CUDA transcription and intent classification.
  * `SPEAKING` / `ACTING`: Emerald indicator presenting a transcription excerpt and synthesized speech confirmation.

### 2.3 System Tray Applet ([`src/ikkhi/ui/tray.py`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/ui/tray.py))
* **Shell Integration:** Integrates into the Windows Shell notification area using procedural multi-resolution icon rendering.
* **Context Capabilities:** One-click toggling of HUD visibility, instant launch of the Analytics Dashboard, hotkey mute switch, profile cache flush, and graceful termination.

### 2.4 Control Panel & Token Analytics Dashboard ([`src/ikkhi/ui/dashboard.py`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/ui/dashboard.py))
* **Analytics Tab:** Visual metrics quantifying 0-token local fast-path execution volume versus cloud Gemini fallback queries, detailing cumulative tokens and fiscal expenditure conserved.
* **Adaptive Profiles Tab:** Interactive inspection tree detailing per-application controls and coordinates cached under `storage/profiles/`.
* **Hardware & Configuration Tab:** In-app modification of audio trigger bindings (`ctrl+alt+space`), Whisper model dimensions, Gemini credentials, and proxy parameters.

### 2.5 Thread-Safe GUI Controller & Signals ([`src/ikkhi/ui/controller.py`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/ui/controller.py))
* Decouples the Qt GUI event loop from asynchronous audio streaming, global keyboard hooks, and background inference.
* Utilizes dedicated `QThread` workers communicating via queued `pyqtSignal` events, guaranteeing 60 FPS UI responsiveness without freezing.

---

## 3. PyInstaller Packaging Strategy for Standalone Binary (`Ikkhi.exe`)

### 3.1 Path Resolution & Frozen Runtime Normalization
When packaged via PyInstaller's `--onefile` architecture, static program resources are unpacked dynamically into `sys._MEIPASS`, whereas application data must be persistently written to the local filesystem.
```python
def get_resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parent.parent.parent / relative_path

def get_writable_storage_path(subpath: str = "") -> Path:
    base = Path(os.environ.get("APPDATA", ".")) / "Ikkhi" if getattr(sys, "frozen", False) else Path("storage")
    base.mkdir(parents=True, exist_ok=True)
    return base / subpath
```

### 3.2 Compilation Specification (`Ikkhi.spec`) & Automated Build Pipeline (`scripts/build_executable.py`)
* Consolidates all required dynamic link libraries (PortAudio, CTranslate2, CUDA libraries).
* Includes hidden imports for `pynput`, `sounddevice`, `pywinauto`, `ctranslate2`, `faster_whisper`, `google.genai`, `PyQt6`.
* Generates `dist/Ikkhi.exe` with zero external dependencies.

---

## 4. Phase Schedule & Task Breakdown

| Task ID | Component Name | Deliverable | Status |
| :--- | :--- | :--- | :--- |
| `GUI-01` | Design System & Visual Tokens | `src/ikkhi/ui/theme.py` | 🟢 Completed |
| `GUI-02` | Floating Companion HUD Overlay | `src/ikkhi/ui/overlay.py` | 🟡 In Progress |
| `GUI-03` | Windows System Tray Applet | `src/ikkhi/ui/tray.py` | ⚪ Queued |
| `GUI-04` | Settings & Analytics Dashboard | `src/ikkhi/ui/dashboard.py` | ⚪ Queued |
| `GUI-05` | Asynchronous Orchestrator Controller | `src/ikkhi/ui/controller.py` | ⚪ Queued |
| `GUI-06` | Universal GUI Entrypoint Integration | `src/ikkhi/ui/app.py` & `__main__.py` | ⚪ Queued |
| `EXE-01` | Frozen Path Resolution Engine | `src/ikkhi/core/paths.py` | ⚪ Queued |
| `EXE-02` | PyInstaller Spec & Binary Bundler | `Ikkhi.spec` & `scripts/build_executable.py` | ⚪ Queued |
| `EXE-03` | Verification & Automated Test Suite | `tests/unit/test_ui.py` | ⚪ Queued |
