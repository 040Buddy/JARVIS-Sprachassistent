#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Timer & Alarm Manager"""

import threading
import time
import logging
from typing import Optional, Callable
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TimerManager:
    """Verwaltet Timer und Alarme"""
    
    def __init__(self):
        self.timers = {}
        self.alarm_callback = None
    
    def set_timer(self, duration_seconds: int, name: str = "Timer", callback: Optional[Callable] = None):
        """Stelle Timer"""
        try:
            timer_id = f"timer_{int(time.time())*1000}"
            
            def timer_thread():
                time.sleep(duration_seconds)
                logger.info(f"[TIMER] FERTIG: {name}")
                
                if callback:
                    callback(name)
                elif self.alarm_callback:
                    self.alarm_callback(name)
            
            thread = threading.Thread(target=timer_thread, daemon=True)
            thread.start()
            
            self.timers[timer_id] = {
                'name': name,
                'duration': duration_seconds,
                'start': datetime.now(),
                'thread': thread
            }
            
            logger.info(f"[TIMER] Gestartet: {name} ({duration_seconds}s)")
            return timer_id
        
        except Exception as e:
            logger.error(f"[TIMER] Fehler: {e}")
            return None
    
    def get_timers(self):
        """Hole aktive Timer"""
        active = {}
        for tid, timer in self.timers.items():
            if timer['thread'].is_alive():
                elapsed = (datetime.now() - timer['start']).total_seconds()
                remaining = timer['duration'] - elapsed
                if remaining > 0:
                    active[tid] = {
                        'name': timer['name'],
                        'remaining': int(remaining),
                        'total': timer['duration']
                    }
        return active
    
    def cancel_timer(self, timer_id: str) -> bool:
        """Breche Timer ab"""
        if timer_id in self.timers:
            logger.info(f"[TIMER] Abgebrochen: {timer_id}")
            del self.timers[timer_id]
            return True
        return False
