@echo off
title Ikkhi Wake-Word Diagnostic Console
cd /d "%~dp0"
echo =======================================================
echo     LAUNCHING IKKHI LIVE WAKE-WORD TESTING CONSOLE
echo =======================================================
echo  - Displays real-time microphone detection
echo  - Logs every time you speak "Hey Ikkhi" or press Ctrl+Alt+Space
echo =======================================================
.venv\Scripts\python.exe scripts\test_live_wakeword.py
pause
