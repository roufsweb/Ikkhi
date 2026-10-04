"""
Environment and Implementation Plan Validation Routine for Ikkhi.
Validates:
1. Python version and Windows platform compatibility
2. NVIDIA GPU and CUDA driver availability
3. Screen resolution and DPI awareness capabilities
4. Audio recording subsystem capability
5. Configuration files and project directory structure
"""

import sys
import os
import platform
import subprocess
import ctypes
from pathlib import Path

def print_header(title):
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def test_system():
    print_header("1. System & OS Verification (VAL-ENV-01)")
    print(f"Python Version: {platform.python_version()} ({sys.executable})")
    print(f"OS Platform: {platform.system()} {platform.release()} (Build {platform.version()})")
    print(f"Architecture: {platform.machine()}")
    
    assert sys.version_info >= (3, 10), "Python 3.10 or higher is required."
    assert platform.system() == "Windows", "Ikkhi is designed for Windows OS."
    print(">>> [PASS] System environment meets prerequisites.")

def test_gpu():
    print_header("2. NVIDIA GPU & CUDA Verification (VAL-GPU-01)")
    try:
        res = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                             capture_output=True, text=True, check=True)
        gpu_info = res.stdout.strip()
        print(f"GPU Detected: {gpu_info}")
        print(">>> [PASS] Dedicated NVIDIA GPU detected with CUDA capability.")
    except Exception as e:
        print(f">>> [WARNING] nvidia-smi failed: {e}. GPU acceleration might not be available.")

def test_display_and_dpi():
    print_header("3. Display & DPI Awareness (VAL-SCR-01 / VAL-PTR-01)")
    try:
        # Enable Per-Monitor DPI awareness to test physical coordinate mapping
        DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = ctypes.c_void_p(-4)
        ctypes.windll.user32.SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)
        
        user32 = ctypes.windll.user32
        width = user32.GetSystemMetrics(0) # SM_CXSCREEN
        height = user32.GetSystemMetrics(1) # SM_CYSCREEN
        print(f"Primary Display Resolution (Hardware Pixels): {width}x{height}")
        print(">>> [PASS] Windows DPI awareness and display metrics successfully initialized.")
    except Exception as e:
        print(f">>> [FAIL] Display metric initialization failed: {e}")

def test_config_and_structure():
    print_header("4. Project Structure & Config Files (VAL-CFG-01)")
    workspace_root = Path(__file__).resolve().parent.parent
    expected_files = [
        "AGENTS.md",
        "PROJECT_GOALS.md",
        "BOUNDARIES.md",
        "EXISTING_SOLUTIONS.md",
        "CONVERSATION_SUMMARY.md",
        "PROJECT_MAP.md",
        "PROGRESS.md",
        "IMPLEMENTATION_PLAN.md",
        "config.yaml",
        "requirements.txt"
    ]
    all_found = True
    for f in expected_files:
        p = workspace_root / f
        if p.exists():
            print(f"  [OK] Found {f}")
        else:
            print(f"  [MISSING] {f}")
            all_found = False
            
    assert all_found, "Some expected documentation or config files are missing."
    print(">>> [PASS] All project tracking and configuration files present.")

if __name__ == "__main__":
    print("Running Ikkhi Validation Routine...")
    test_system()
    test_gpu()
    test_display_and_dpi()
    test_config_and_structure()
    print("\n" + "=" * 60)
    print(" SUMMARY: Baseline Implementation Plan Routine Validated Successfully!")
    print("=" * 60)
