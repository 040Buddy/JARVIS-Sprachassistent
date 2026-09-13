#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JARVIS Konfiguration"""

import os
from pathlib import Path

# PFADE
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# AUDIO
SAMPLE_RATE = 16000
AUDIO_DURATION = 15

# TTS
TTS_RATE = 150
TTS_VOLUME = 1.0
TTS_PITCH = 0.9

# SPRACHERKENNUNG
SR_LANGUAGE = "de-DE"
SR_ENERGY_THRESHOLD = 3500

# DATENBANK
DB_PATH = DATA_DIR / "jarvis.db"
CHAT_HISTORY_LIMIT = 100

# NOTIZEN
NOTES_DIR = Path.home() / "Desktop" / "JARVIS_Notes"

# UI
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 750
WINDOW_TITLE = "J.A.R.V.I.S v6.0"

# FARBEN
COLOR_PRIMARY = "#00D9FF"
COLOR_SECONDARY = "#00FF00"
COLOR_BACKGROUND = "#0a0e27"
COLOR_ERROR = "#FF0000"
