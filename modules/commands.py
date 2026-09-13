#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Befehl-Verarbeitung"""

import logging
import subprocess
import webbrowser
import platform
import shutil
from pathlib import Path
from datetime import datetime
from typing import Tuple

logger = logging.getLogger(__name__)


class CommandProcessor:
    """Verarbeitet Benutzer-Befehle"""
    
    def __init__(self, db_manager, note_manager, timer_manager, voice_engine):
        self.db = db_manager
        self.notes = note_manager
        self.timers = timer_manager
        self.voice = voice_engine
        self.memory = {
            'user_name': 'Meister',
            'last_query': None
        }
    
    def process(self, text: str) -> Tuple[str, bool]:
        """Verarbeite Befehl, return (response, should_speak)"""
        if not text:
            return "", False
        
        text_lower = text.lower().strip()
        
        # GRÜSSE
        if any(w in text_lower for w in ["hallo", "hi", "guten morgen", "guten tag"]):
            hour = datetime.now().hour
            if hour < 12:
                response = f"Guten Morgen, {self.memory['user_name']}!"
            elif hour < 18:
                response = f"Guten Nachmittag, {self.memory['user_name']}!"
            else:
                response = f"Guten Abend, {self.memory['user_name']}!"
            return response, True
        
        # NOTIZEN
        if "schreibe" in text_lower and "notiz" in text_lower:
            content = text.replace("schreibe eine notiz", "").replace("schreibe notiz", "").strip()
            if content:
                self.notes.create_note("Notiz", content)
                response = f"Notiz gespeichert: {content}"
                return response, True
            return "Kein Inhalt fur Notiz angegeben", True
        
        # TODO
        if "aufgabe" in text_lower or "todo" in text_lower:
            task = text.replace("aufgabe", "").replace("erstelle aufgabe", "").replace("todo", "").strip()
            if task:
                self.db.add_todo(task)
                response = f"Aufgabe hinzugefuegt: {task}"
                return response, True
        
        # TIMER
        if "timer" in text_lower or "wecker" in text_lower:
            return self._handle_timer(text), True
        
        # ÖFFNE APP
        if "oeffne" in text_lower or "starte" in text_lower:
            return self._handle_app(text), True
        
        # SUCHE
        if "suche" in text_lower or "google" in text_lower:
            return self._handle_search(text), True
        
        # ZEIT
        if "uhr" in text_lower or "zeit" in text_lower or "datum" in text_lower:
            now = datetime.now()
            response = f"Es ist {now.strftime('%H:%M')} Uhr, {now.strftime('%A, %d. %B %Y')}"
            return response, True
        
        # WETTER
        if "wetter" in text_lower:
            return "Wetter-Feature kommt bald", True
        
        # TODOS ANZEIGEN
        if "meine aufgaben" in text_lower or "todos zeigen" in text_lower:
            todos = self.db.get_todos()
            if todos:
                response = "Deine Aufgaben: " + ", ".join([t['task'] for t in todos])
            else:
                response = "Keine offenen Aufgaben"
            return response, True
        
        # DEFAULT
        response = "Das kann ich noch nicht, aber ich lerne..."
        return response, True
    
    def _handle_timer(self, text: str) -> str:
        """Verarbeite Timer-Befehl"""
        try:
            # Versuche Zeit zu extrahieren (z.B. "5 Minuten")
            words = text.lower().split()
            duration = None
            
            for i, word in enumerate(words):
                if word.isdigit():
                    num = int(word)
                    if i + 1 < len(words):
                        unit = words[i + 1]
                        if "minute" in unit:
                            duration = num * 60
                        elif "sekunde" in unit:
                            duration = num
                        elif "stunde" in unit:
                            duration = num * 3600
                    break
            
            if duration:
                self.timers.set_timer(duration, f"Timer {duration}s")
                return f"Timer fuer {duration} Sekunden gestartet"
            else:
                return "Konnte Zeit nicht erkennen. Versuche: Timer fuer 5 Minuten"
        except Exception as e:
            logger.error(f"[TIMER] Fehler: {e}")
            return f"Timer-Fehler: {e}"
    
    def _handle_app(self, text: str) -> str:
        """Oeffne Anwendungen"""
        apps = {
            "chrome": ["chrome.exe", "google chrome"],
            "firefox": ["firefox.exe"],
            "edge": ["msedge.exe"],
            "notepad": ["notepad.exe"],
            "explorer": ["explorer.exe"],
            "vscode": ["code.exe"],
            "discord": ["discord.exe"],
            "uhr": ["C:\\Windows\\System32\\timedate.cpl"],
            "rechner": ["calc.exe"],
            "calculator": ["calc.exe"],
        }
        
        text_lower = text.lower()
        for app_name, commands in apps.items():
            if app_name in text_lower:
                for cmd in commands:
                    try:
                        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        logger.info(f"[APP] Oeffne {app_name}")
                        return f"Oeffne {app_name}..."
                    except:
                        continue
                return f"Konnte {app_name} nicht oeffnen"
        
        return "App nicht erkannt. Versuche: Chrome, Firefox, Discord, Uhr, Rechner"
    
    def _handle_search(self, text: str) -> str:
        """Google-Suche"""
        query = text.replace("suche", "").replace("google", "").strip()
        if query:
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            logger.info(f"[SEARCH] {query}")
            return f"Suche nach: {query}"
        return "Keine Suchanfrage angegeben"
