#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
J.A.R.V.I.S v6.0 - Komplette Professional App
Alle Features: Notizen, Timer, Apps, Browser, Todos
"""

import sys
import os
import logging
import platform
from pathlib import Path

# UNICODE FIX WINDOWS (besser)
if platform.system() == "Windows":
    try:
        import io
        if sys.stdout and hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        if sys.stderr and hasattr(sys.stderr, 'buffer'):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass  # Fallback wenn nicht möglich

# LOGGING
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('jarvis.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# IMPORTS
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QSystemTrayIcon, QMenu, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPainter, QPen, QBrush

from modules.voice import VoiceEngine
from modules.database import JarvisDatabase
from modules.notes import NoteManager
from modules.timer import TimerManager
from modules.commands import CommandProcessor


class SpeechThread(QThread):
    """Spracherkennung in separatem Thread"""
    recognized = pyqtSignal(str)
    listening = pyqtSignal(bool)
    error = pyqtSignal(str)
    
    def __init__(self, voice_engine):
        super().__init__()
        self.voice = voice_engine
        self.running = True
    
    def run(self):
        logger.info("[SPEECH] Thread aktiv")
        while self.running:
            try:
                self.listening.emit(True)
                text = self.voice.listen(timeout=15)
                self.listening.emit(False)
                
                if text:
                    self.recognized.emit(text)
            except Exception as e:
                self.error.emit(f"Fehler: {str(e)}")
                logger.error(f"[SPEECH] {e}")
    
    def stop(self):
        self.running = False


class JarvisApp(QMainWindow):
    """Hauptanwendung"""
    
    def __init__(self):
        super().__init__()
        
        # INITIALIZE MODULES
        self.voice = VoiceEngine()
        self.db = JarvisDatabase()
        self.notes = NoteManager()
        self.timers = TimerManager()
        self.processor = CommandProcessor(self.db, self.notes, self.timers, self.voice)
        
        # SPEECH THREAD
        self.speech_thread = SpeechThread(self.voice)
        self.speech_thread.recognized.connect(self.on_speech_recognized)
        self.speech_thread.listening.connect(self.on_listening_changed)
        self.speech_thread.error.connect(self.on_speech_error)
        
        self.init_ui()
        self.speech_thread.start()
        
        logger.info("[APP] Gestartet")
    
    def init_ui(self):
        """UI Setup"""
        self.setWindowTitle("J.A.R.V.I.S v6.0")
        self.setGeometry(100, 100, 1100, 750)
        self.setStyleSheet(self._get_stylesheet())
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # HEADER
        header = QLabel("J.A.R.V.I.S v6.0")
        header.setFont(QFont("Arial", 40, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #00D9FF;")
        main_layout.addWidget(header)
        
        subtitle = QLabel("Just A Rather Very Intelligent System")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #00FF00;")
        main_layout.addWidget(subtitle)
        
        # STATUS
        self.status_label = QLabel("BEREIT")
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #00FF00;")
        main_layout.addWidget(self.status_label)
        
        # CHAT DISPLAY
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
        main_layout.addWidget(self.chat)
        self.chat.append("JARVIS: Guten Tag! Ich bin bereit.\n")
        self.chat.append("Befehle: Oeffne Chrome, Schreibe Notiz, Timer fuer 5 Minuten, etc.\n")
        
        # INPUT
        self.input_box = QTextEdit()
        self.input_box.setMaximumHeight(70)
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
        main_layout.addWidget(self.input_box)
        
        # BUTTONS
        btn_layout = QHBoxLayout()
        
        send_btn = QPushButton("SENDEN (Ctrl+Enter)")
        send_btn.setMinimumHeight(45)
        send_btn.clicked.connect(self.send_command)
        btn_layout.addWidget(send_btn)
        
        speech_btn = QPushButton("SPRECHEN")
        speech_btn.setMinimumHeight(45)
        speech_btn.clicked.connect(self.listen_speech)
        btn_layout.addWidget(speech_btn)
        
        clear_btn = QPushButton("LOESCHEN")
        clear_btn.setMinimumHeight(45)
        clear_btn.clicked.connect(self.clear_chat)
        btn_layout.addWidget(clear_btn)
        
        main_layout.addLayout(btn_layout)
        
        # INFO
        self.info_label = QLabel("Spracherkennung aktiv")
        self.info_label.setStyleSheet("color: #00D9FF; font-size: 9pt;")
        main_layout.addWidget(self.info_label)
        
        # KEYBOARD
        self.input_box.keyPressEvent = self.key_press_handler
        
        # TRAY
        self.setup_tray()
    
    def setup_tray(self):
        """System Tray"""
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.create_icon())
        
        menu = QMenu()
        menu.addAction("Fenster", self.show_window)
        menu.addSeparator()
        menu.addAction("Beenden", self.close_app)
        
        self.tray.setContextMenu(menu)
        self.tray.show()
    
    def create_icon(self):
        """App Icon"""
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
    
    def send_command(self):\n        \"\"\"Text-Befehl senden\"\"\"\n        text = self.input_box.toPlainText().strip()\n        if text:\n            self.process_command(text)\n            self.input_box.clear()\n    \n    def listen_speech(self):\n        \"\"\"Sprechen hoeren\"\"\"\n        self.status_label.setText(\"HOERE ZU...\")\n        self.status_label.setStyleSheet(\"color: #FF0000;\")\n        self.voice.listen()  # Blockiert\n        self.status_label.setText(\"BEREIT\")\n        self.status_label.setStyleSheet(\"color: #00FF00;\")\n    \n    def on_speech_recognized(self, text: str):\n        \"\"\"Sprache erkannt\"\"\"\n        self.process_command(text)\n    \n    def on_listening_changed(self, listening: bool):\n        \"\"\"Hoer-Status geaendert\"\"\"\n        if listening:\n            self.status_label.setText(\"HOERE ZU...\")\n            self.status_label.setStyleSheet(\"color: #FF0000;\")\n        else:\n            self.status_label.setText(\"BEREIT\")\n            self.status_label.setStyleSheet(\"color: #00FF00;\")\n    \n    def on_speech_error(self, error: str):\n        \"\"\"Fehler\"\"\"\n        self.display_message(\"FEHLER\", error)\n    \n    def process_command(self, text: str):\n        \"\"\"Verarbeite Befehl\"\"\"\n        self.display_message(\"Du\", text)\n        response, should_speak = self.processor.process(text)\n        \n        if response:\n            self.display_message(\"JARVIS\", response)\n            self.db.add_chat(text, response)\n            \n            if should_speak:\n                self.voice.speak(response, async_mode=True)\n    \n    def display_message(self, sender: str, message: str):\n        \"\"\"Zeige Nachricht\"\"\"\n        self.chat.append(f\"{sender}: {message}\")\n    \n    def key_press_handler(self, event):\n        \"\"\"Keyboard\"\"\"\n        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:\n            self.send_command()\n        else:\n            QTextEdit.keyPressEvent(self.input_box, event)\n    \n    def clear_chat(self):\n        \"\"\"Loesche Chat\"\"\"\n        self.chat.clear()\n        self.display_message(\"JARVIS\", \"Chat geloescht.\")\n    \n    def show_window(self):\n        \"\"\"Zeige Fenster\"\"\"\n        self.show()\n        self.raise_()\n        self.activateWindow()\n    \n    def closeEvent(self, event):\n        \"\"\"Minimiere zu Tray\"\"\"\n        if self.tray.isVisible():\n            self.hide()\n            event.ignore()\n        else:\n            event.accept()\n    \n    def close_app(self):\n        \"\"\"Beende\"\"\"\n        logger.info(\"[APP] Beende JARVIS\")\n        self.speech_thread.stop()\n        QApplication.quit()\n    \n    def _get_stylesheet(self):\n        \"\"\"Stylesheet\"\"\"\n        return \"\"\"\n        QMainWindow { background-color: #0a0e27; }\n        QLabel { color: #00D9FF; }\n        QTextEdit { background-color: #0a0e27; color: #00D9FF; border: 2px solid #00D9FF; border-radius: 5px; }\n        QPushButton { background-color: #00D9FF; color: #0a0e27; border: none; border-radius: 5px; padding: 10px; font-weight: bold; }\n        QPushButton:hover { background-color: #00FF00; }\n        QPushButton:pressed { background-color: #00AA00; }\n        \"\"\"\n\n\ndef main():\n    print(\"\\n\" + \"=\"*60)\n    print(\"J.A.R.V.I.S v6.0 - KOMPLETTE APP\")\n    print(\"=\"*60)\n    logger.info(\"[STARTUP] JARVIS v6.0\")\n    \n    app = QApplication(sys.argv)\n    app.setApplicationName(\"JARVIS\")\n    \n    window = JarvisApp()\n    window.show()\n    \n    print(\"=\"*60)\n    print(\"JARVIS ONLINE\")\n    print(\"=\"*60 + \"\\n\")\n    \n    sys.exit(app.exec_())\n\n\nif __name__ == \"__main__\":\n    main()\n