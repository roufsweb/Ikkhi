# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Specification File for Ikkhi Desktop Assistant.
Compiles a fully self-contained, standalone Windows executable (Ikkhi.exe)
incorporating PortAudio, CTranslate2, CUDA libraries, and PyQt6 visual assets.
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

block_cipher = None
project_root = Path('.').resolve()

# Collect submodules and dynamic libraries
hidden_imports = [
    'sounddevice',
    'ctranslate2',
    'faster_whisper',
    'pynput',
    'pynput.keyboard',
    'pynput.mouse',
    'pynput.keyboard._win32',
    'pynput.mouse._win32',
    'pywinauto',
    'pywinauto.controls.uiawrapper',
    'pywinauto.application',
    'pyautogui',
    'pyautogui._pyautogui_win',
    'google.genai',
    'PIL',
    'PIL.Image',
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'win32com',
    'win32com.client',
    'pythoncom',
    'pydantic',
    'pydantic_settings',
    'yaml',
]

# Additional collect hooks for dynamic packages
hidden_imports += collect_submodules('ikkhi')
hidden_imports += collect_submodules('sounddevice')
hidden_imports += collect_submodules('faster_whisper')
hidden_imports += collect_submodules('edge_tts')
hidden_imports += collect_submodules('av')

# Collect data files
datas = [
    ('config.yaml', '.'),
]
datas += collect_data_files('faster_whisper')
datas += collect_data_files('sounddevice')

# Collect dynamic libraries / DLLs (e.g. portaudio, ctranslate2, av)
binaries = []
binaries += collect_dynamic_libs('sounddevice')
binaries += collect_dynamic_libs('ctranslate2')
binaries += collect_dynamic_libs('av')

a = Analysis(
    ['src/ikkhi/__main__.py'],
    pathex=['src', '.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'notebook', 'IPython'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Ikkhi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
