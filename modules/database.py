#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Datenbank fur Notes, Todos, Timer"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class JarvisDatabase:
    """SQLite Database Manager"""
    
    def __init__(self, db_path: str = "jarvis_data.db"):
        self.db_path = Path(db_path)
        self.init_db()
    
    def init_db(self):
        """Initialisiere Datenbank"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Notizen Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Todos Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY,
                    task TEXT,
                    completed INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Timer History
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS timers (
                    id INTEGER PRIMARY KEY,
                    duration INTEGER,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Chat History
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY,
                    user_message TEXT,
                    jarvis_response TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("[DB] Initialisiert")
        except Exception as e:
            logger.error(f"[DB] Init Fehler: {e}")
    
    def add_note(self, title: str, content: str):
        """Fuege Notiz hinzu"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO notes (title, content) VALUES (?, ?)', (title, content))
            conn.commit()
            conn.close()
            logger.info(f"[NOTE] Gespeichert: {title}")
            return True
        except Exception as e:
            logger.error(f"[NOTE] Fehler: {e}")
            return False
    
    def get_notes(self) -> List[Dict]:
        """Hole alle Notizen"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM notes ORDER BY created_at DESC')
            notes = cursor.fetchall()
            conn.close()
            return [{'id': n[0], 'title': n[1], 'content': n[2], 'date': n[3]} for n in notes]
        except Exception as e:
            logger.error(f"[NOTE] Get Fehler: {e}")
            return []
    
    def add_todo(self, task: str):
        """Fuege Todo hinzu"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO todos (task) VALUES (?)', (task,))
            conn.commit()
            conn.close()
            logger.info(f"[TODO] Hinzugefuegt: {task}")
            return True
        except Exception as e:
            logger.error(f"[TODO] Fehler: {e}")
            return False
    
    def get_todos(self) -> List[Dict]:
        """Hole unvollendete Todos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM todos WHERE completed=0')
            todos = cursor.fetchall()
            conn.close()
            return [{'id': t[0], 'task': t[1], 'date': t[3]} for t in todos]
        except Exception as e:
            logger.error(f"[TODO] Get Fehler: {e}")
            return []
    
    def complete_todo(self, todo_id: int):
        """Markiere Todo als erledigt"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE todos SET completed=1 WHERE id=?', (todo_id,))
            conn.commit()
            conn.close()
            logger.info(f"[TODO] Erledigt: {todo_id}")
            return True
        except Exception as e:
            logger.error(f"[TODO] Complete Fehler: {e}")
            return False
    
    def add_chat(self, user_msg: str, jarvis_response: str):
        """Speichere Chat"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO chat_history (user_message, jarvis_response) VALUES (?, ?)',
                          (user_msg, jarvis_response))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"[CHAT] Fehler: {e}")
    
    def get_chat_history(self, limit=50) -> List[Dict]:
        """Hole Chat-Historie"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM chat_history ORDER BY timestamp DESC LIMIT ?', (limit,))
            chats = cursor.fetchall()
            conn.close()
            return [{'user': c[1], 'jarvis': c[2], 'time': c[3]} for c in reversed(chats)]
        except Exception as e:
            logger.error(f"[CHAT] Get Fehler: {e}")
            return []
