#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Notiz Manager"""

import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class NoteManager:
    """Verwaltet Notizen"""
    
    def __init__(self, notes_dir: str = None):
        if notes_dir is None:
            self.notes_dir = Path.home() / "Desktop" / "JARVIS_Notes"
        else:
            self.notes_dir = Path(notes_dir)
        
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[NOTES] Verzeichnis: {self.notes_dir}")
    
    def create_note(self, title: str, content: str) -> bool:
        """Erstelle Notiz auf Desktop"""
        try:
            filename = f"{title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = self.notes_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Notiz: {title}\n")
                f.write(f"Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
                f.write("="*50 + "\n\n")
                f.write(content)
            
            logger.info(f"[NOTE] Erstellt: {filepath}")
            return True
        except Exception as e:
            logger.error(f"[NOTE] Fehler: {e}")
            return False
    
    def get_all_notes(self):
        """Hole alle Notizen"""
        try:
            notes = list(self.notes_dir.glob("*.txt"))
            return sorted(notes, key=lambda x: x.stat().st_mtime, reverse=True)
        except Exception as e:
            logger.error(f"[NOTES] Get Fehler: {e}")
            return []
