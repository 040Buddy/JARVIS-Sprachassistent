#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
J.A.R.V.I.S - Just A Rather Very Intelligent System
Spracherkennung mit verbesserter Architektur & KI-Integration
Version 5.0 - Überarbeitete & optimierte Version
"""

import sys
import os
import json
import webbrowser
import subprocess
import datetime
import time
import platform
import threading
import logging
from typing import Optional, Dict, List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import traceback

# ============= LOGGING SETUP =============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============= DEPENDENCIES =============
try:
    import speech_recognition as sr
except ImportError:
    logger.error("❌ SpeechRecognition nicht installiert")
    sys.exit(1)

try:
    import pyttsx3
except ImportError:
    logger.error("❌ pyttsx3 nicht installiert")
    sys.exit(1)

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QTextEdit, QPushButton, QSystemTrayIcon, QMenu, QMessageBox,
        QScrollArea, QProgressBar
    )
    from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QTimer, QSize
    from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPainter, QPen, QBrush
except ImportError:
    logger.error("❌ PyQt5 nicht installiert")
    sys.exit(1)

try:
    import psutil
except ImportError:
    logger.warning("⚠️  psutil nicht installiert - System-Info deaktiviert")
    psutil = None

try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
except ImportError:
    logger.warning("⚠️  sounddevice/numpy nicht installiert")
    sd = None
    np = None


class CommandType(Enum):
    """Befehlstypen für bessere Kategorisierung"""
    GREETING = "greeting"
    APP_CONTROL = "app_control"
    SEARCH = "search"
    TIME_DATE = "time_date"
    SYSTEM_INFO = "system_info"
    MEMORY = "memory"
    UNKNOWN = "unknown"


@dataclass
class Command:
    """Kommando-Datenklasse"""
    text: str
    type: CommandType
    confidence: float
    timestamp: datetime.datetime


class MaleVoiceEngine:
    """Männliche realistische Sprachausgabe mit Error-Handling"""
    
    def __init__(self):
        self.engine = None
        self.initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialisiere TTS Engine mit Fehlerbehandlung"""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 130)
            self.engine.setProperty('volume', 0.95)
            
            voices = self.engine.getProperty('voices')
            male_voice = self._find_male_voice(voices)
            
            if male_voice:
                self.engine.setProperty('voice', male_voice)
                logger.info(f"✓ Männliche Stimme geladen: {male_voice}")
            
            try:
                self.engine.setProperty('pitch', 0.85)
            except Exception as e:
                logger.warning(f"Pitch-Anpassung nicht möglich: {e}")
            
            self.initialized = True
            logger.info("✓ TTS-Engine erfolgreich initialisiert")
        
        except Exception as e:
            logger.error(f"❌ TTS-Fehler: {e}")
            self.initialized = False
    
    def _find_male_voice(self, voices: List) -> Optional[str]:
        """Finde männliche deutsche Stimme"""
        for voice in voices:
            voice_name = voice.name.lower()
            if any(m in voice_name for m in ['male', 'mann', 'david', 'mark', 'viktor']):
                if any(de in str(voice.languages).lower() for de in ['de', 'german']):
                    return voice.id
        
        # Fallback: Erste männliche Stimme
        for voice in voices:
            if 'male' in voice.name.lower():
                return voice.id
        
        return None
    
    def speak(self, text: str, wait: bool = True):
        """Spricht Text in männlicher Stimme"""
        if not self.initialized or not text or text.strip() == "":
            return
        
        try:
            self.engine.say(text)
            if wait:
                self.engine.runAndWait()
            logger.debug(f"Spreche: {text[:50]}...")
        except Exception as e:
            logger.error(f"Fehler bei Sprachausgabe: {e}")
    
    def speak_async(self, text: str):
        """Spricht asynchron in separatem Thread"""
        thread = threading.Thread(target=self.speak, args=(text, True), daemon=True)
        thread.start()


class SpeechRecognitionThread(QThread):
    """Verbesserte Spracherkennung mit robustem Error-Handling"""
    
    recognized = pyqtSignal(str)
    listening = pyqtSignal(bool)
    error = pyqtSignal(str)
    status = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.running = True
        self.is_listening = False
        self.sample_rate = 16000
        self.duration = 20
        self.configureRecognizer()
    
    def configureRecognizer(self):
        """Konfiguriere Recognizer optimal"""
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.phrase_threshold = 0.1
        logger.info("✓ Recognizer konfiguriert")
    
    def record_audio_with_sounddevice(self) -> Optional[np.ndarray]:
        """Nimmt Audio mit sounddevice auf"""
        if not sd or not np:
            logger.warning("sounddevice nicht verfügbar, nutze Fallback")
            return None
        
        try:
            self.status.emit(f"🎤 Höre zu... (max {self.duration}s)")
            audio_data = sd.rec(int(self.sample_rate * self.duration),
                               samplerate=self.sample_rate,
                               channels=1, dtype='float32')
            sd.wait()
            return audio_data
        except Exception as e:
            self.error.emit(f"Audio-Fehler: {str(e)}")
            logger.error(f"Audio-Fehler: {e}")
            return None
    
    def run(self):
        """Läuft in separatem Thread"""
        logger.info("🎤 Spracherkennung aktiv...")
        
        while self.running:
            try:
                self.is_listening = True
                self.listening.emit(True)
                self.status.emit("🎤 Warte auf Sprache...")
                
                # Audio aufnehmen
                audio_data = self.record_audio_with_sounddevice()
                
                if audio_data is None:
                    self.is_listening = False
                    self.listening.emit(False)
                    time.sleep(1)
                    continue
                
                # Konvertiere zu AudioData
                try:
                    audio_frames = (audio_data * 32767).astype('int16')
                    audio_obj = sr.AudioData(audio_frames.tobytes(),
                                            self.sample_rate, 2)
                    
                    self.is_listening = False
                    self.listening.emit(False)
                    self.status.emit("🔍 Erkenne Sprache...")
                    
                    # Google Speech Recognition
                    text = self.recognizer.recognize_google(audio_obj, language="de-DE")
                    logger.info(f"✓ Erkannt: {text}")
                    self.recognized.emit(text)
                
                except sr.UnknownValueError:
                    self.error.emit("❌ Konnte Sprache nicht verstehen")
                except sr.RequestError as e:
                    self.error.emit(f"❌ Google API Fehler: {str(e)}")
                except Exception as e:
                    self.error.emit(f"❌ Fehler: {str(e)}")
                    logger.error(f"Fehler: {e}")
            
            except Exception as e:
                self.is_listening = False
                self.listening.emit(False)
                logger.error(f"Thread-Fehler: {e}")
            
            time.sleep(0.5)
    
    def stop(self):
        """Stoppt Spracherkennung sauber"""
        self.running = False
        logger.info("🛑 Spracherkennung gestoppt")


class CommandProcessor:
    """Erweiterte Verarbeitung mit KI-Integration"""
    
    def __init__(self):
        self.memory_file = "jarvis_memory.json"
        self.load_memory()
        logger.info("✓ CommandProcessor initialisiert")
    
    def load_memory(self):
        """Lädt Gedächtnis aus Datei"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memory = json.load(f)
                logger.info("✓ Gedächtnis geladen")
            except Exception as e:
                logger.error(f"Fehler beim Laden: {e}")
                self.memory = self._default_memory()
        else:
            self.memory = self._default_memory()
    
    def _default_memory(self) -> dict:
        """Standard-Gedächtnis"""
        return {
            "user_name": "Sir",
            "conversations": [],
            "learned_commands": {},
            "preferences": {"language": "de", "voice_speed": 130},
            "command_history": [],
            "statistics": {"total_commands": 0, "success_rate": 0}
        }
    
    def save_memory(self):
        """Speichert Gedächtnis"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Fehler beim Speichern: {e}")
    
    def classify_command(self, text: str) -> Command:
        """Klassifiziere Befehl"""
        text_lower = text.lower().strip()
        
        # Grüße
        if any(w in text_lower for w in ["hallo", "hi", "guten", "morgen", "tag", "abend"]):
            return Command(text, CommandType.GREETING, 0.95, datetime.datetime.now())
        
        # Merken
        if "merke" in text_lower or "erinnere" in text_lower:
            return Command(text, CommandType.MEMORY, 0.9, datetime.datetime.now())
        
        # Anwendungen
        if "öffne" in text_lower or "starte" in text_lower:
            return Command(text, CommandType.APP_CONTROL, 0.85, datetime.datetime.now())
        
        # Suche
        if "suche" in text_lower or "google" in text_lower:
            return Command(text, CommandType.SEARCH, 0.85, datetime.datetime.now())
        
        # Zeit/Datum
        if any(w in text_lower for w in ["uhr", "zeit", "datum", "wann"]):
            return Command(text, CommandType.TIME_DATE, 0.9, datetime.datetime.now())
        
        # System
        if any(w in text_lower for w in ["speicher", "system", "cpu", "ram", "status"]):
            return Command(text, CommandType.SYSTEM_INFO, 0.85, datetime.datetime.now())
        
        return Command(text, CommandType.UNKNOWN, 0.3, datetime.datetime.now())
    
    def process(self, text: str) -> str:
        """Verarbeitet Befehl und gibt Antwort zurück"""
        if not text or text.strip() == "":
            return ""
        
        command = self.classify_command(text)
        self.memory["command_history"].append({
            "text": text,
            "type": command.type.value,
            "timestamp": command.timestamp.isoformat()
        })
        
        # Dispatch basierend auf Typ
        if command.type == CommandType.GREETING:
            return self._greeting()
        elif command.type == CommandType.MEMORY:
            return self._learn(text)
        elif command.type == CommandType.APP_CONTROL:
            return self._open_app(text)
        elif command.type == CommandType.SEARCH:
            return self._search(text)
        elif command.type == CommandType.TIME_DATE:
            return self._tell_time()
        elif command.type == CommandType.SYSTEM_INFO:
            return self._system_info()
        else:
            return self._smart_response(text)
    
    def _greeting(self) -> str:
        """JARVIS-ähnliche Grüße"""
        hour = datetime.datetime.now().hour
        user = self.memory['user_name']
        
        if hour < 12:
            return f"Guten Morgen, {user}. Ich hoffe, Sie haben gut geschlafen."
        elif hour < 18:
            return f"Guten Nachmittag, {user}. Wie kann ich dir heute behilflich sein?"
        else:
            return f"Guten Abend, {user}. Was kann ich für dich tun?"
    
    def _learn(self, text: str) -> str:
        """Lerne neue Befehle"""
        try:
            if ":" not in text:
                return "Bitte verwende: Merke dir [Befehl] Doppelpunkt [Aktion]"
            
            parts = text.split(":")
            trigger = parts[1].strip().lower() if len(parts) > 1 else ""
            action = parts[2].strip() if len(parts) > 2 else ""
            
            if trigger and action:
                self.memory["learned_commands"][trigger] = action
                self.save_memory()
                return f"Verstanden. Ich merke mir: '{trigger}'"
            
            return "Format nicht erkannt"
        except Exception as e:
            logger.error(f"Fehler beim Lernen: {e}")
            return "Fehler beim Speichern"
    
    def _open_app(self, text: str) -> str:
        """Öffnet Anwendungen"""
        apps = {
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
            "terminal": "cmd" if platform.system() == "Windows" else "xterm"
        }
        
        for app_name, cmd in apps.items():
            if app_name in text.lower():
                try:
                    if platform.system() == "Windows" and app_name == "explorer":
                        os.startfile(os.path.expanduser("~"))
                    else:
                        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    logger.info(f"✓ Öffne {app_name}")
                    return f"Öffne {app_name} jetzt."
                except Exception as e:
                    logger.error(f"Fehler beim Öffnen von {app_name}: {e}")
                    return f"Konnte {app_name} nicht öffnen."
        
        return "Diese Anwendung erkenne ich nicht. Versuche: Chrome, Firefox, Discord, etc."
    
    def _search(self, text: str) -> str:
        """Web-Suche"""
        query = text.replace("suche", "").replace("google", "").strip()
        if query:
            url = f"https://www.google.com/search?q={query}"
            try:
                webbrowser.open(url)
                logger.info(f"✓ Suche: {query}")
                return f"Suche nach: {query}"
            except Exception as e:
                logger.error(f"Browser-Fehler: {e}")
                return "Konnte Browser nicht öffnen."
        return "Was möchtest du suchen?"
    
    def _tell_time(self) -> str:
        """Sagt Zeit an"""
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M")
        days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        day_name = days[now.weekday()]
        date_str = now.strftime("%d. %B %Y")
        return f"Es ist {time_str} Uhr, {day_name}, den {date_str}."
    
    def _system_info(self) -> str:
        """System-Informationen"""
        if not psutil:
            return "System-Info nicht verfügbar."
        
        try:
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return (f"System-Status: CPU {cpu:.1f}% | "
                   f"RAM {memory.percent:.1f}% ({memory.available / (1024**3):.1f}GB verfügbar) | "
                   f"Festplatte {disk.percent:.1f}%")
        except Exception as e:
            logger.error(f"System-Info Fehler: {e}")
            return "Konnte System-Infos nicht abrufen."
    
    def _smart_response(self, text: str) -> str:
        """Intelligente Fallback-Antwort"""
        responses = [
            f"Interessante Frage. Kannst du mir mehr Details geben?",
            f"Das kann ich noch nicht. Versuche: Öffne Chrome, Suche nach etwas oder frag mich die Zeit.",
            f"Habe dich nicht ganz verstanden. Wiederhole bitte.",
        ]
        return responses[hash(text) % len(responses)]


class JarvisUI(QMainWindow):
    """JARVIS UI - Iron Man inspiriertes Interface"""
    
    def __init__(self):
        super().__init__()
        self.processor = CommandProcessor()
        self.tts = MaleVoiceEngine()
        
        # Spracherkennung Thread
        self.speech_thread = SpeechRecognitionThread()
        self.speech_thread.recognized.connect(self.on_speech_recognized)
        self.speech_thread.listening.connect(self.on_listening_changed)
        self.speech_thread.error.connect(self.on_speech_error)
        self.speech_thread.status.connect(self.on_status_changed)
        
        self.init_ui()
        self.speech_thread.start()
        logger.info("✓ UI initialisiert")
    
    def init_ui(self):
        """Erstelle JARVIS-ähnliches Interface"""
        self.setWindowTitle("J.A.R.V.I.S v5.0 - Intelligent System")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(self._get_stylesheet())
        
        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # ===== HEADER =====
        header = QLabel("J.A.R.V.I.S")
        header_font = QFont("Arial", 50, QFont.Bold)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #00D9FF; text-shadow: 0 0 20px #00D9FF;")
        layout.addWidget(header)
        
        subtitle = QLabel("Just A Rather Very Intelligent System v5.0")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #00FF00; letter-spacing: 2px;")
        layout.addWidget(subtitle)
        
        # ===== STATUS =====
        self.status_label = QLabel("🟢 BEREIT")
        self.status_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #00FF00; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # ===== CHAT DISPLAY =====
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setFont(QFont("Courier", 10))
        self.chat.setStyleSheet("""
            QTextEdit {
                background-color: #0a0e27;
                color: #00D9FF;
                border: 3px solid #00D9FF;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        layout.addWidget(self.chat)
        
        self.chat.append("🤖 JARVIS: System online. Bereit zum Dienst.\n")
        
        # ===== INPUT SECTION =====
        input_label = QLabel("Sprich jetzt oder tippe hier:")
        input_label.setStyleSheet("color: #00D9FF; font-weight: bold; font-size: 12px;")
        layout.addWidget(input_label)
        
        self.input_box = QTextEdit()
        self.input_box.setMaximumHeight(80)
        self.input_box.setFont(QFont("Courier", 11))
        self.input_box.setStyleSheet("""
            QTextEdit {
                background-color: #0a0e27;
                color: #00FF00;
                border: 2px solid #00FF00;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        self.input_box.setPlaceholderText("Spreche ins Mikrofon oder tippe hier...")
        layout.addWidget(self.input_box)
        
        # ===== BUTTONS =====
        btn_layout = QHBoxLayout()
        
        send_btn = QPushButton("➤ SENDEN")
        send_btn.setMinimumHeight(45)
        send_btn.setFont(QFont("Arial", 11, QFont.Bold))
        send_btn.clicked.connect(self.send_text_command)
        btn_layout.addWidget(send_btn)
        
        clear_btn = QPushButton("🗑️  LÖSCHEN")
        clear_btn.setMinimumHeight(45)
        clear_btn.setFont(QFont("Arial", 11, QFont.Bold))
        clear_btn.clicked.connect(self.clear_chat)
        btn_layout.addWidget(clear_btn)
        
        stats_btn = QPushButton("📊 STATS")
        stats_btn.setMinimumHeight(45)
        stats_btn.setFont(QFont("Arial", 11, QFont.Bold))
        stats_btn.clicked.connect(self.show_stats)
        btn_layout.addWidget(stats_btn)
        
        layout.addLayout(btn_layout)
        
        # ===== INFO =====
        self.info_label = QLabel("✓ System bereit | Spracherkennung aktiv")
        self.info_label.setStyleSheet("color: #00D9FF; font-size: 9pt;")
        layout.addWidget(self.info_label)
        
        self.input_box.keyPressEvent = self.key_press_handler
        self.setup_tray()
    
    def setup_tray(self):
        """Taskleisten-Icon"""
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.create_icon())
        
        menu = QMenu()
        menu.addAction("Fenster", self.show_window)
        menu.addAction("Status", self.show_stats)
        menu.addSeparator()
        menu.addAction("Beenden", self.close_app)
        
        self.tray.setContextMenu(menu)
        self.tray.show()
    
    def create_icon(self) -> QIcon:
        """Erstelle JARVIS Icon"""
        pixmap = QPixmap(128, 128)
        pixmap.fill(QColor(10, 14, 39))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Ringe
        painter.setPen(QPen(QColor(0, 217, 255), 4))
        painter.drawEllipse(10, 10, 108, 108)
        
        painter.setPen(QPen(QColor(0, 217, 255), 2))
        painter.drawEllipse(25, 25, 78, 78)
        
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        painter.drawEllipse(40, 40, 48, 48)
        
        painter.setBrush(QBrush(QColor(0, 217, 255)))
        painter.drawEllipse(60, 60, 8, 8)
        
        painter.end()
        return QIcon(pixmap)
    
    def on_speech_recognized(self, text: str):
        """Sprache erkannt"""
        self.display_message("👤 Du", text)
        response = self.processor.process(text)
        if response:
            self.display_message("🤖 JARVIS", response)
            self.tts.speak_async(response)
        self.processor.save_memory()
    
    def on_listening_changed(self, listening: bool):
        """Höre-Status geändert"""
        if listening:
            self.status_label.setText("🔴 HÖRE ZU...")
            self.status_label.setStyleSheet("color: #FF0000; font-weight: bold;")
        else:
            self.status_label.setText("🟢 BEREIT")
            self.status_label.setStyleSheet("color: #00FF00; font-weight: bold;")
    
    def on_speech_error(self, error: str):
        """Fehler bei Spracherkennung"""
        self.display_message("⚠️  FEHLER", error)
        logger.warning(f"Fehler: {error}")
    
    def on_status_changed(self, status: str):
        """Status geändert"""
        self.info_label.setText(status)
    
    def send_text_command(self):
        """Verarbeite Text-Eingabe"""
        text = self.input_box.toPlainText().strip()
        if text:
            self.display_message("👤 Du", text)
            response = self.processor.process(text)
            if response:
                self.display_message("🤖 JARVIS", response)
                self.tts.speak_async(response)
            self.input_box.clear()
            self.processor.save_memory()
    
    def display_message(self, sender: str, message: str):
        """Zeige Nachricht"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat.append(f"[{timestamp}] {sender}: {message}")
    
    def key_press_handler(self, event):
        """Tastatur Handler - Ctrl+Enter zum Senden"""
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            self.send_text_command()
        else:
            QTextEdit.keyPressEvent(self.input_box, event)
    
    def clear_chat(self):
        """Löscht Chat"""
        self.chat.clear()
        self.display_message("🤖 JARVIS", "Chat gelöscht.")
    
    def show_stats(self):
        """Zeige Statistiken"""
        stats = self.processor.memory.get("statistics", {})
        cmd_count = len(self.processor.memory.get("command_history", []))
        msg = f"📊 STATISTIKEN\n\nBefehle verarbeitet: {cmd_count}\nGelernter Befehle: {len(self.processor.memory['learned_commands'])}"
        QMessageBox.information(self, "JARVIS Statistiken", msg)
    
    def show_window(self):
        """Fenster zeigen"""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def closeEvent(self, event):
        """Minimiere zu Tray"""
        if self.tray.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()
    
    def close_app(self):
        """Beende App sauber"""
        logger.info("🛑 JARVIS wird beendet...")
        self.speech_thread.stop()
        self.processor.save_memory()
        QApplication.quit()
    
    def _get_stylesheet(self) -> str:
        """JARVIS-ähnliches Stylesheet"""
        return """
        QMainWindow {
            background-color: #0a0e27;
        }
        QLabel {
            color: #00D9FF;
        }
        QTextEdit {
            background-color: #0a0e27;
            color: #00D9FF;
            border: 2px solid #00D9FF;
            border-radius: 5px;
        }
        QPushButton {
            background-color: #00D9FF;
            color: #0a0e27;
            border: none;
            border-radius: 5px;
            padding: 10px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #00FF00;
        }
        QPushButton:pressed {
            background-color: #00AA00;
        }
        """


def main():
    """Starte JARVIS"""
    print("\n" + "="*70)
    print("█ J.A.R.V.I.S v5.0 - Überarbeitete & Optimierte Version")
    print("█ Just A Rather Very Intelligent System")
    print("█ Features: Spracherkennung | Männliche Stimme | KI-Integration")
    print("="*70)
    logger.info("✓ Initialisiere JARVIS v5.0...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("JARVIS")
    
    window = JarvisUI()
    window.show()
    
    print("="*70)
    print("✅ JARVIS v5.0 ONLINE - Bereit zum Dienst")
    print("="*70 + "\n")
    logger.info("✅ JARVIS erfolgreich gestartet")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
