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

# UNICODE FIX WINDOWS
if platform.system() == "Windows":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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
    
    def send_command(self):
        """Text-Befehl senden"""
        text = self.input_box.toPlainText().strip()
        if text:
            self.process_command(text)
            self.input_box.clear()
    
    def listen_speech(self):
        """Sprechen hoeren"""
        self.status_label.setText("HOERE ZU...")
        self.status_label.setStyleSheet("color: #FF0000;")
        self.voice.listen()  # Blockiert
        self.status_label.setText("BEREIT")
        self.status_label.setStyleSheet("color: #00FF00;")
    
    def on_speech_recognized(self, text: str):
        """Sprache erkannt"""
        self.process_command(text)
    
    def on_listening_changed(self, listening: bool):
        """Hoer-Status geaendert"""
        if listening:
            self.status_label.setText("HOERE ZU...")
            self.status_label.setStyleSheet("color: #FF0000;")
        else:
            self.status_label.setText("BEREIT")
            self.status_label.setStyleSheet("color: #00FF00;")
    
    def on_speech_error(self, error: str):
        """Fehler"""
        self.display_message("FEHLER", error)
    
    def process_command(self, text: str):
        """Verarbeite Befehl"""
        self.display_message("Du", text)
        response, should_speak = self.processor.process(text)
        
        if response:
            self.display_message("JARVIS", response)
            self.db.add_chat(text, response)
            
            if should_speak:
                self.voice.speak(response, async_mode=True)
    
    def display_message(self, sender: str, message: str):
        """Zeige Nachricht"""
        self.chat.append(f"{sender}: {message}")
    
    def key_press_handler(self, event):
        """Keyboard"""
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            self.send_command()
        else:
            QTextEdit.keyPressEvent(self.input_box, event)
    
    def clear_chat(self):
        """Loesche Chat"""
        self.chat.clear()
        self.display_message("JARVIS", "Chat geloescht.")
    
    def show_window(self):
        """Zeige Fenster"""
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
        """Beende"""
        logger.info("[APP] Beende JARVIS")
        self.speech_thread.stop()
        QApplication.quit()
    
    def _get_stylesheet(self):
        """Stylesheet"""
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
    print("J.A.R.V.I.S v6.0 - KOMPLETTE APP")
    print("="*60)
    logger.info("[STARTUP] JARVIS v6.0")
    
    app = QApplication(sys.argv)
    app.setApplicationName("JARVIS")
    
    window = JarvisApp()
    window.show()
    
    print("="*60)
    print("JARVIS ONLINE")
    print("="*60 + "\n")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
