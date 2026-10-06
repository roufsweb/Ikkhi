@echo off
title Ikkhi Desktop Assistant
cd /d "%~dp0"
echo =======================================================
echo          LAUNCHING IKKHI DESKTOP ASSISTANT
echo =======================================================
echo  - Loading Translucent Companion HUD Overlay
echo  - Loading Token Analytics Dashboard
echo  - Initializing faster-whisper on NVIDIA CUDA
echo  - Activating Wake-Word ("Hey Ikkhi") & Push-to-Talk (Ctrl+Alt+Space)
echo =======================================================
.venv\Scripts\python.exe -m ikkhi
pause
