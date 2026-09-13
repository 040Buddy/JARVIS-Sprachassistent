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

# BUILD COMMAND - FIX: Use python -m pyinstaller
print("\n[3] Baue EXE...")

build_cmd = [
    sys.executable,  # Nutze den gleichen Python Interpreter
    '-m',
    'PyInstaller',
    '--onefile',
    '--windowed',
    '--name=JARVIS',
    '--add-data=modules:modules',
    'main.py'
]

try:
    result = subprocess.run(build_cmd, check=True, capture_output=True, text=True)
    print("    Erfolg! EXE erstellt")
    if result.stdout:
        print(result.stdout)
except subprocess.CalledProcessError as e:
    print(f"    FEHLER: {e}")
    if e.stderr:
        print(f"    Details: {e.stderr}")
    sys.exit(1)
except FileNotFoundError as e:
    print(f"    FEHLER: {e}")
    print("    PyInstaller nicht im PATH gefunden")
    sys.exit(1)

# RESULT
print("\n[4] Fertig!")
exe_path = Path("dist") / "JARVIS.exe"
if exe_path.exists():
    print(f"\n  ✅ EXE-Datei erstellt: {exe_path}")
    print(f"  📦 Größe: {exe_path.stat().st_size / (1024*1024):.1f} MB")
    print(f"\n  ▶️  Starten: doppelklick auf dist/JARVIS.exe")
else:
    print(f"\n  ⚠️  EXE nicht gefunden: {exe_path}")
    print("     Pruefe den Output oben auf Fehler")

print("\n" + "="*60 + "\n")
