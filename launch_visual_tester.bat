@echo off
title Ikkhi Visual Navigation & Guidance Tester
cd /d "%~dp0"
echo =======================================================
echo     LAUNCHING IKKHI VISUAL GUIDANCE TESTER
echo =======================================================
echo  - Tests active foreground window detection
echo  - Validates WebP compression (<80KB, <260 tokens)
echo  - Tests Local UIA Accessibility Tree fast-path (<25ms, 0 tokens)
echo  - Pulses neon reticle beacon and glides cursor
echo =======================================================
.venv\Scripts\python.exe scripts\test_visual_navigation.py %*
pause
