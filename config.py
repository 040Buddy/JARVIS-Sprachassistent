#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Konfigurationsdatei für JARVIS
"""

import os
from pathlib import Path

# ============= PATHS =============
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

# Erstelle Verzeichnisse falls nicht vorhanden
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# ============= LOGGING =============
LOG_FILE = LOG_DIR / "jarvis.log"
LOG_LEVEL = "INFO"

# ============= AUDIO =============
SAMPLE_RATE = 16000
AUDIO_DURATION = 20  # Sekunden
AUDIO_CHUNK_SIZE = 1024

# ============= TTS (Text-to-Speech) =============
TTS_RATE = 130  # Sprechgeschwindigkeit
TTS_VOLUME = 0.95  # 0-1
TTS_PITCH = 0.85  # Tonhöhe

# ============= RECOGNITION =============
RECOGNITION_LANGUAGE = "de-DE"  # Deutsch
RECOGNITION_TIMEOUT = 10
ENERGY_THRESHOLD = 4000

# ============= GUI =============
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "J.A.R.V.I.S v5.0 - Intelligent System"

# Farben (Hex)
COLOR_PRIMARY = "#00D9FF"  # Cyan
COLOR_SECONDARY = "#00FF00"  # Grün
COLOR_BACKGROUND = "#0a0e27"  # Dunkelblau
COLOR_ACCENT = "#FF0000"  # Rot

# ============= MEMORY =============
MEMORY_FILE = DATA_DIR / "jarvis_memory.json"
MAX_HISTORY = 1000  # Max. Befehle speichern

# ============= API KEYS =============
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ============= COMMANDS =============
BUILT_IN_COMMANDS = {
    "öffne": "app_control",
    "starte": "app_control",
    "suche": "search",
    "google": "search",
    "uhr": "time_date",
    "zeit": "time_date",
    "datum": "time_date",
    "speicher": "system_info",
    "cpu": "system_info",
    "ram": "system_info",
    "merke": "memory",
    "erinnere": "memory",
}

APPS = {
    "chrome": "chrome",
    "firefox": "firefox",
    "edge": "msedge",
    "notepad": "notepad",
    "explorer": "explorer",
    "vscode": "code",
    "discord": "discord",
    "spotify": "spotify",
    "vlc": "vlc",
    "steam": "steam",
}
