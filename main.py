#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
J.A.R.V.I.S - Just A Rather Very Intelligent System v5.1
Schneller, besser, mit Windows-Unicode Fix
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
import shutil
from typing import Optional, Dict, List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# UNICODE FIX FÜR WINDOWS
if platform.system() == "Windows":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# LOGGING SETUP (UTF-8)
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('jarvis.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# DEPENDENCIES
try:
    import speech_recognition as sr
except ImportError:
    logger.error("SpeechRecognition nicht installiert")
    sys.exit(1)

try:
    import pyttsx3
except ImportError:
    logger.error("pyttsx3 nicht installiert")
    sys.exit(1)

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QTextEdit, QPushButton, QSystemTrayIcon, QMenu
    )
    from PyQt5.QtCore import Qt, pyqtSignal, QThread
    from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPainter, QPen, QBrush
except ImportError:
    logger.error("PyQt5 nicht installiert")
    sys.exit(1)

try:
    import psutil
except ImportError:
    psutil = None

try:
    import sounddevice as sd
    import numpy as np
except ImportError:
    sd = None
    np = None


class CommandType(Enum):
    GREETING = "greeting"
    APP_CONTROL = "app_control"
    SEARCH = "search"
    TIME_DATE = "time_date"
    SYSTEM_INFO = "system_info"
    MEMORY = "memory"
    UNKNOWN = "unknown"


@dataclass
class Command:
    text: str
    type: CommandType
    confidence: float
    timestamp: datetime.datetime


class MaleVoiceEngine:
    """Schnelle männliche Stimme"""
    
    def __init__(self):
        self.engine = None
        self.initialized = False
        self._speaking = False
        self._initialize()
    
    def _initialize(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 1.0)
            
            voices = self.engine.getProperty('voices')
            male_voice = self._find_male_voice(voices)
            
            if male_voice:
                self.engine.setProperty('voice', male_voice)
                logger.info("[OK] Maennliche Stimme geladen")
            
            try:
                self.engine.setProperty('pitch', 0.9)
            except:
                pass
            
            self.initialized = True
            logger.info("[OK] TTS bereit")
        except Exception as e:
            logger.error(f"[ERROR] TTS: {e}")
            self.initialized = False
    
    def _find_male_voice(self, voices):
        for voice in voices:
            voice_name = voice.name.lower()
            if any(m in voice_name for m in ['male', 'mann', 'david', 'mark']):
                if any(de in str(voice.languages).lower() for de in ['de', 'german']):
                    return voice.id
        
        for voice in voices:
            if 'male' in voice.name.lower():
                return voice.id
        
        return None
    
    def speak(self, text: str, async_mode=True):
        if not self.initialized or not text or text.strip() == "":
            return
        
        if async_mode:
            thread = threading.Thread(target=self._speak_sync, args=(text,), daemon=True)
            thread.start()
        else:
            self._speak_sync(text)
    
    def _speak_sync(self, text: str):
        try:
            if self._speaking:
                return
            
            self._speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
            self._speaking = False
            logger.info(f"[SPEAK] {text[:40]}")
        except Exception as e:
            logger.error(f"[ERROR] Speak: {e}")
            self._speaking = False


class SpeechRecognitionThread(QThread):
    """Schnelle Spracherkennung"""
    
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
        self.duration = 15
        self.configureRecognizer()
    
    def configureRecognizer(self):
        self.recognizer.energy_threshold = 3500
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.phrase_threshold = 0.1
        logger.info("[OK] Speech recognition ready")
    
    def record_audio_with_sounddevice(self):
        if not sd or not np:
            return None
        
        try:
            self.status.emit(f"Hoere zu ({self.duration}s max)...")
            audio_data = sd.rec(int(self.sample_rate * self.duration),
                               samplerate=self.sample_rate,
                               channels=1, dtype='float32')
            sd.wait()
            return audio_data
        except Exception as e:
            self.error.emit(f"Audio error: {str(e)}")
            logger.error(f"Audio: {e}")
            return None
    
    def run(self):
        logger.info("[MICROPHONE] Aktiv...")
        
        while self.running:
            try:
                self.is_listening = True
                self.listening.emit(True)
                self.status.emit("Hoere zu...")
                
                audio_data = self.record_audio_with_sounddevice()
                
                if audio_data is None:
                    self.is_listening = False
                    self.listening.emit(False)
                    time.sleep(0.5)
                    continue
                
                try:
                    audio_frames = (audio_data * 32767).astype('int16')
                    audio_obj = sr.AudioData(audio_frames.tobytes(),
                                            self.sample_rate, 2)
                    
                    self.is_listening = False
                    self.listening.emit(False)
                    self.status.emit("Erkenne...")
                    
                    text = self.recognizer.recognize_google(audio_obj, language="de-DE")
                    logger.info(f"[SPEECH] {text}")
                    self.recognized.emit(text)
                
                except sr.UnknownValueError:
                    self.error.emit("Nicht verstanden")
                except sr.RequestError:
                    self.error.emit("Google API Fehler")
                except Exception as e:
                    self.error.emit(f"Fehler: {str(e)}")
                    logger.error(f"Error: {e}")
            
            except Exception as e:
                self.is_listening = False
                self.listening.emit(False)
                logger.error(f"Thread error: {e}")
            
            time.sleep(0.5)
    
    def stop(self):
        self.running = False
        logger.info("[STOP] Beendet")


class CommandProcessor:
    """Kommando-Verarbeiter"""
    
    def __init__(self):
        self.memory_file = "jarvis_memory.json"
        self.load_memory()
        logger.info("[OK] Processor ready")
    
    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memory = json.load(f)
                logger.info("[OK] Memory geladen")
            except Exception as e:
                logger.error(f"Memory error: {e}")
                self.memory = self._default_memory()
        else:
            self.memory = self._default_memory()
    
    def _default_memory(self):
        return {
            "user_name": "Sir",
            "conversations": [],
            "learned_commands": {},
            "preferences": {"language": "de", "voice_speed": 150}
        }
    
    def save_memory(self):
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Save error: {e}")
    
    def classify_command(self, text: str) -> Command:
        text_lower = text.lower().strip()
        
        if any(w in text_lower for w in ["hallo", "hi", "guten", "morgen", "tag", "abend", "wie geht"]):
            return Command(text, CommandType.GREETING, 0.95, datetime.datetime.now())
        
        if "merke" in text_lower or "erinnere" in text_lower:
            return Command(text, CommandType.MEMORY, 0.9, datetime.datetime.now())
        
        if "oeffne" in text_lower or "oeffne" in text_lower or "starte" in text_lower:
            return Command(text, CommandType.APP_CONTROL, 0.85, datetime.datetime.now())
        
        if "suche" in text_lower or "google" in text_lower:
            return Command(text, CommandType.SEARCH, 0.85, datetime.datetime.now())
        
        if any(w in text_lower for w in ["uhr", "zeit", "datum", "wann"]):
            return Command(text, CommandType.TIME_DATE, 0.9, datetime.datetime.now())
        
        if any(w in text_lower for w in ["speicher", "system", "cpu", "ram", "status"]):
            return Command(text, CommandType.SYSTEM_INFO, 0.85, datetime.datetime.now())
        
        return Command(text, CommandType.UNKNOWN, 0.3, datetime.datetime.now())
    
    def process(self, text: str) -> str:
        if not text or text.strip() == "":
            return ""
        
        command = self.classify_command(text)
        
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
    
    def _greeting(self):
        hour = datetime.datetime.now().hour
        user = self.memory['user_name']
        
        if hour < 12:
            return f"Guten Morgen, {user}."
        elif hour < 18:
            return f"Guten Nachmittag, {user}."
        else:
            return f"Guten Abend, {user}."
    
    def _learn(self, text: str):
        try:
            if ":" not in text:
                return "Merke dir: Befehl : Aktion"
            
            parts = text.split(":")
            trigger = parts[1].strip().lower() if len(parts) > 1 else ""
            action = parts[2].strip() if len(parts) > 2 else ""
            
            if trigger and action:
                self.memory["learned_commands"][trigger] = action
                self.save_memory()
                return f"Merke mir: {trigger}"
            
            return "Format falsch"
        except Exception as e:
            logger.error(f"Learn error: {e}")
            return "Fehler"
    
    def _open_app(self, text: str):
        text_lower = text.lower()
        
        apps = {
            "chrome": ["chrome.exe", "google chrome"],
            "firefox": ["firefox.exe"],
            "edge": ["msedge.exe"],
            "notepad": ["notepad.exe"],
            "explorer": ["explorer.exe"],
            "vscode": ["code.exe"],
            "uhr": ["C:\\Windows\\System32\\timedate.cpl"],
            "rechner": ["calc.exe"],
            "calculator": ["calc.exe"],
            "discord": ["discord.exe"],
            "spotify": ["spotify.exe"],
        }
        
        for app_name, cmds in apps.items():
            if app_name in text_lower:
                for cmd in cmds:
                    try:
                        if platform.system() == "Windows":
                            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            logger.info(f"[APP] Oeffne {app_name}")
                            return f"Oeffne {app_name}."
                        else:
                            subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            logger.info(f"[APP] Open {app_name}")
                            return f"Opening {app_name}."
                    except:
                        continue
                
                logger.warning(f"[APP] {app_name} nicht gefunden")
                return f"Kann {app_name} nicht oeffnen."
        
        return "App nicht erkannt. Chrome, Uhr, Rechner, etc."
    
    def _search(self, text: str):
        query = text.replace("suche", "").replace("google", "").strip()
        if query:
            url = f"https://www.google.com/search?q={query}"
            try:
                webbrowser.open(url)
                logger.info(f"[SEARCH] {query}")
                return f"Suche nach {query}."
            except Exception as e:
                logger.error(f"Browser error: {e}")
                return "Browser-Fehler."
        return "Was moechtest du suchen?"
    
    def _tell_time(self):
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M")
        days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        day_name = days[now.weekday()]
        return f"Es ist {time_str} Uhr, {day_name}."
    
    def _system_info(self):
        if not psutil:
            return "System-Info nicht verfuegbar."
        
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            memory = psutil.virtual_memory()
            return f"CPU {cpu:.0f}% - RAM {memory.percent:.0f}%"
        except Exception as e:
            logger.error(f"System info error: {e}")
            return "Fehler auslesen."
    
    def _smart_response(self, text: str):
        responses = [
            "Das kann ich noch nicht. Versuche eine andere Frage.",
            "Interessant. Wiederhole bitte.",
            "Habe dich nicht verstanden.",
        ]
        return responses[hash(text) % len(responses)]


class JarvisUI(QMainWindow):
    """JARVIS UI"""
    
    def __init__(self):
        super().__init__()
        self.processor = CommandProcessor()
        self.tts = MaleVoiceEngine()
        
        self.speech_thread = SpeechRecognitionThread()
        self.speech_thread.recognized.connect(self.on_speech_recognized)
        self.speech_thread.listening.connect(self.on_listening_changed)
        self.speech_thread.error.connect(self.on_speech_error)
        self.speech_thread.status.connect(self.on_status_changed)
        
        self.init_ui()
        self.speech_thread.start()
        logger.info("[OK] UI ready")
    
    def init_ui(self):
        self.setWindowTitle("J.A.R.V.I.S v5.1")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet(self._get_stylesheet())
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header = QLabel("J.A.R.V.I.S")
        header_font = QFont("Arial", 45, QFont.Bold)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #00D9FF;")
        layout.addWidget(header)
        
        self.status_label = QLabel("BEREIT")
        self.status_label.setFont(QFont("Arial", 13, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #00FF00;")
        layout.addWidget(self.status_label)
        
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setFont(QFont("Courier", 10))
        self.chat.setStyleSheet("""
            QTextEdit {
                background-color: #0a0e27;
                color: #00D9FF;
                border: 2px solid #00D9FF;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.chat)
        self.chat.append("JARVIS: System online.")
        
        self.input_box = QTextEdit()
        self.input_box.setMaximumHeight(60)
        self.input_box.setFont(QFont("Courier", 10))
        self.input_box.setStyleSheet("""
            QTextEdit {
                background-color: #0a0e27;
                color: #00FF00;
                border: 2px solid #00FF00;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.input_box)
        
        btn_layout = QHBoxLayout()
        
        send_btn = QPushButton("SENDEN")
        send_btn.setMinimumHeight(40)
        send_btn.clicked.connect(self.send_text_command)
        btn_layout.addWidget(send_btn)
        
        clear_btn = QPushButton("LOESCHEN")
        clear_btn.setMinimumHeight(40)
        clear_btn.clicked.connect(self.clear_chat)
        btn_layout.addWidget(clear_btn)
        
        layout.addLayout(btn_layout)
        
        self.info_label = QLabel("Spracherkennung aktiv")
        self.info_label.setStyleSheet("color: #00D9FF; font-size: 9pt;")
        layout.addWidget(self.info_label)
        
        self.input_box.keyPressEvent = self.key_press_handler
        self.setup_tray()
    
    def setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.create_icon())
        
        menu = QMenu()
        menu.addAction("Fenster", self.show_window)
        menu.addSeparator()
        menu.addAction("Beenden", self.close_app)
        
        self.tray.setContextMenu(menu)
        self.tray.show()
    
    def create_icon(self):
        pixmap = QPixmap(100, 100)
        pixmap.fill(QColor(10, 14, 39))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(0, 217, 255), 3))
        painter.drawEllipse(5, 5, 90, 90)
        painter.setBrush(QBrush(QColor(0, 217, 255)))
        painter.drawEllipse(45, 45, 10, 10)
        painter.end()
        
        return QIcon(pixmap)
    
    def on_speech_recognized(self, text: str):
        self.display_message("Du", text)
        response = self.processor.process(text)
        if response:
            self.display_message("JARVIS", response)
            self.tts.speak(response, async_mode=True)
        self.processor.save_memory()
    
    def on_listening_changed(self, listening: bool):
        if listening:
            self.status_label.setText("HOERE ZU...")
            self.status_label.setStyleSheet("color: #FF0000;")
        else:
            self.status_label.setText("BEREIT")
            self.status_label.setStyleSheet("color: #00FF00;")
    
    def on_speech_error(self, error: str):
        self.display_message("FEHLER", error)
        logger.warning(f"Error: {error}")
    
    def on_status_changed(self, status: str):
        self.info_label.setText(status)
    
    def send_text_command(self):
        text = self.input_box.toPlainText().strip()
        if text:
            self.display_message("Du", text)
            response = self.processor.process(text)
            if response:
                self.display_message("JARVIS", response)
                self.tts.speak(response, async_mode=True)
            self.input_box.clear()
            self.processor.save_memory()
    
    def display_message(self, sender: str, message: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat.append(f"[{timestamp}] {sender}: {message}")
    
    def key_press_handler(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            self.send_text_command()
        else:
            QTextEdit.keyPressEvent(self.input_box, event)
    
    def clear_chat(self):
        self.chat.clear()
        self.display_message("JARVIS", "Chat geloescht.")
    
    def show_window(self):
        self.show()
        self.raise_()
        self.activateWindow()
    
    def closeEvent(self, event):
        if self.tray.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()
    
    def close_app(self):
        logger.info("[SHUTDOWN] JARVIS beendet")
        self.speech_thread.stop()
        self.processor.save_memory()
        QApplication.quit()
    
    def _get_stylesheet(self):
        return """
        QMainWindow { background-color: #0a0e27; }
        QLabel { color: #00D9FF; }
        QTextEdit { background-color: #0a0e27; color: #00D9FF; border: 2px solid #00D9FF; border-radius: 5px; }
        QPushButton { background-color: #00D9FF; color: #0a0e27; border: none; border-radius: 5px; padding: 10px; font-weight: bold; }
        QPushButton:hover { background-color: #00FF00; }
        QPushButton:pressed { background-color: #00AA00; }
        """


def main():
    print("\n" + "="*60)
    print("J.A.R.V.I.S v5.1 - Starte...")
    print("="*60)
    logger.info("[START] JARVIS v5.1")
    
    app = QApplication(sys.argv)
    app.setApplicationName("JARVIS")
    
    window = JarvisUI()
    window.show()
    
    print("="*60)
    print("JARVIS ONLINE - Bereit!")
    print("="*60 + "\n")
    logger.info("[READY] Online")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
