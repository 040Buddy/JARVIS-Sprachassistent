#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Spracherkennung & Text-to-Speech"""

import threading
import logging
from typing import Optional, Callable
import pyttsx3
import speech_recognition as sr

logger = logging.getLogger(__name__)


class VoiceEngine:
    """Sprachausgabe & Erkennung"""
    
    def __init__(self):
        self.tts_engine = None
        self.recognizer = sr.Recognizer()
        self._init_tts()
        self._init_recognizer()
        self._speaking = False
    
    def _init_tts(self):
        """Initialisiere Text-to-Speech"""
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 1.0)
            
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'male' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            self.tts_engine.setProperty('pitch', 0.9)
            logger.info("[TTS] Initialisiert")
        except Exception as e:
            logger.error(f"[TTS] Fehler: {e}")
    
    def _init_recognizer(self):
        """Initialisiere Spracherkennung"""
        self.recognizer.energy_threshold = 3500
        self.recognizer.dynamic_energy_threshold = True
        logger.info("[SR] Initialisiert")
    
    def speak(self, text: str, async_mode=True):
        """Spricht Text"""
        if not text or not self.tts_engine:
            return
        
        if async_mode:
            thread = threading.Thread(target=self._speak_sync, args=(text,), daemon=True)
            thread.start()
        else:
            self._speak_sync(text)
    
    def _speak_sync(self, text: str):
        """Spricht synchron"""
        try:
            if self._speaking:
                return
            self._speaking = True
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            self._speaking = False
        except Exception as e:
            logger.error(f"[SPEAK] Fehler: {e}")
            self._speaking = False
    
    def listen(self, timeout=15) -> Optional[str]:
        """Hoert zu und erkennt Sprache"""
        try:
            import sounddevice as sd
            import numpy as np
            
            audio_data = sd.rec(int(16000 * timeout), samplerate=16000, channels=1, dtype='float32')
            sd.wait()
            
            audio_frames = (audio_data * 32767).astype('int16')
            audio_obj = sr.AudioData(audio_frames.tobytes(), 16000, 2)
            
            text = self.recognizer.recognize_google(audio_obj, language="de-DE")
            logger.info(f"[SPEECH] {text}")
            return text
        
        except sr.UnknownValueError:
            logger.warning("[SR] Nicht verstanden")
            return None
        except sr.RequestError as e:
            logger.error(f"[SR] API Fehler: {e}")
            return None
        except Exception as e:
            logger.error(f"[LISTEN] Fehler: {e}")
            return None
