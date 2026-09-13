#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baut JARVIS in eine eigenstaendige Windows EXE
Verwendung: python build_app.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

print("\n" + "="*60)
print("JARVIS v6.0 - EXE Builder")
print("="*60)

# CHECK PYINSTALLER
print("\n[1] Pruefe PyInstaller...")
try:
    import PyInstaller
    print("    OK - PyInstaller vorhanden")
except ImportError:
    print("    FEHLER - PyInstaller nicht gefunden")
    print("    Installiere: pip install pyinstaller")
    sys.exit(1)

# CLEAN
print("\n[2] Raeume alte Builds auf...")
for folder in ['build', 'dist', '__pycache__']:
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"    Geloescht: {folder}")

# BUILD COMMAND
print("\n[3] Baue EXE...")
build_cmd = [
    'pyinstaller',
    '--onefile',
    '--windowed',
    '--name=JARVIS',
    '--icon=jarvis_icon.ico',
    '--add-data=modules:modules',
    'main.py'
]

try:
    subprocess.run(build_cmd, check=True)
    print("    Erfolg! EXE erstellt")
except subprocess.CalledProcessError as e:
    print(f"    FEHLER: {e}")
    sys.exit(1)

# RESULT
print("\n[4] Fertig!")
print("\n  EXE-Datei: dist/JARVIS.exe")
print("  Starten: doppelklick auf JARVIS.exe")
print("\n" + "="*60 + "\n")
