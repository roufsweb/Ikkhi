"""
Standalone Binary Compilation & Verification Automation Script.
Compiles Ikkhi into a zero-dependency, single-file Windows executable (dist/Ikkhi.exe).
"""

import os
import sys
import time
import shutil
import subprocess
from pathlib import Path


def main() -> None:
    print("=" * 70)
    print("       IKKHI STANDALONE EXECUTABLE COMPILATION PIPELINE")
    print("=" * 70)

    project_root = Path(__file__).resolve().parent.parent
    spec_file = project_root / "Ikkhi.spec"
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    target_exe = dist_dir / "Ikkhi.exe"

    if not spec_file.is_file():
        print(f"[Error] PyInstaller specification not found at: {spec_file}")
        sys.exit(1)

    print(f"  • Host OS:             Windows ({os.name})")
    print(f"  • Python Interpreter:  {sys.executable}")
    print(f"  • Target Binary:       {target_exe}")
    print(f"  • Specification:       {spec_file.name}")
    print("=" * 70)

    # Step 1: Clean stale build artifacts
    print("\n[Step 1/3] Purging obsolete build cache...")
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)
    if target_exe.exists():
        try:
            target_exe.unlink()
        except Exception as exc:
            print(f"  [Warning] Could not remove existing binary (in use?): {exc}")

    # Step 2: Invoke PyInstaller compilation
    print("\n[Step 2/3] Invoking PyInstaller bundler (this may require 1-3 minutes)...")
    start_time = time.time()
    
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file)
    ]

    process = subprocess.Popen(
        cmd,
        cwd=str(project_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    for line in iter(process.stdout.readline, ""):
        line_clean = line.strip()
        if line_clean:
            # Output key progress indicators
            if any(k in line_clean for k in ("INFO:", "WARNING:", "ERROR:", "Building", "completed")):
                print(f"    {line_clean}", flush=True)

    process.wait()
    duration = time.time() - start_time

    if process.returncode != 0:
        print(f"\n[Error] PyInstaller compilation failed with exit code: {process.returncode}")
        sys.exit(process.returncode)

    # Step 3: Verify binary generation & integrity
    print("\n[Step 3/3] Validating compiled binary payload...")
    if not target_exe.is_file():
        print(f"[Error] Expected executable not found at: {target_exe}")
        sys.exit(1)

    size_bytes = target_exe.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    print(f"\n[Success] Standalone executable compiled successfully!")
    print(f"  • Output Path:    {target_exe}")
    print(f"  • Binary Size:    {size_mb:.2f} MB")
    print(f"  • Build Elapsed:  {duration:.1f} seconds")
    print("\nThe executable is fully self-contained. It requires no Python installation,")
    print("no external packages, and can be distributed directly to client machines.\n")


if __name__ == "__main__":
    main()
