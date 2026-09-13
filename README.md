# J.A.R.V.I.S - Sprachassistent v5.0

**Just A Rather Very Intelligent System** - Ein moderner Sprachassistent mit PyQt5 GUI, realistischer männlicher Stimme und KI-Integration.

## 🚀 Features

- **Spracherkennung** - Deutsche Spracherkennung mit Google Speech-to-Text
- **Männliche Stimme** - Realistische männliche Sprachausgabe (JARVIS-Stil)
- **PyQt5 GUI** - Iron Man inspiertes Interface mit Echtzeit-Feedback
- **Befehlssystem** - Umfassendes Befehlssystem für Apps, Suche, Zeit, System-Info
- **Gedächtnis-System** - Lernt neue Befehle und speichert Präferenzen
- **Error-Handling** - Robuste Fehlerbehandlung und Logging
- **System-Monitoring** - CPU, RAM und Festplatte Überwachung
- **Multi-Threading** - Asynchrone Spracherkennung

## 📋 Anforderungen

- Python 3.8+
- Windows/macOS/Linux
- Mikrofon für Spracherkennung

## 🔧 Installation

### 1. Repository klonen
```bash
git clone https://github.com/040Buddy/JARVIS-Sprachassistent.git
cd JARVIS-Sprachassistent
```

### 2. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 3. JARVIS starten
```bash
python main.py
```

## 💬 Befehle

### Grüße
```
"Hallo JARVIS"
"Guten Morgen"
```

### Anwendungen öffnen
```
"Öffne Chrome"
"Starte Discord"
"Öffne Visual Studio Code"
```

### Web-Suche
```
"Suche nach Python"
"Google: Wie mache ich Pizza"
```

### Zeit & Datum
```
"Wie spät ist es?"
"Sag mir das Datum"
```

### System-Information
```
"Wie ist die CPU Auslastung?"
"Speicher Status"
```

### Neue Befehle lernen
```
"Merke dir: hallo : Hallo Meister!"
"Erinnere mich: test : Das ist ein Test"
```

## 📁 Projektstruktur

```
JARVIS-Sprachassistent/
├── main.py              # Hauptanwendung
├── requirements.txt     # Abhängigkeiten
├── README.md           # Dokumentation
├── jarvis_memory.json  # Gedächtnis-Datei (wird erstellt)
└── jarvis.log          # Log-Datei (wird erstellt)
```

## 🎯 Komponenten

### MaleVoiceEngine
- Text-to-Speech mit männlicher Stimme
- Automatische Stimme-Erkennung
- Asynchrone Sprachausgabe

### SpeechRecognitionThread
- Läuft in separatem Thread
- Google Speech Recognition (deutsch)
- Robustes Error-Handling
- Live-Status Updates

### CommandProcessor
- Intelligente Befehl-Klassifikation
- Befehl-Historie
- Gedächtnis-System
- Modulares Design

### JarvisUI
- PyQt5 basiert
- Dark Mode mit Cyan/Green Styling
- Echtzeit Chat-Display
- Taskbar Integration

## 🔐 Sicherheit

- Logging aller Befehle und Fehler
- Lokal gespeicherte Gedächtnis-Datei (JSON)
- Keine Cloud-Abhängigkeit außer Google Speech API
- Thread-safe Operations

## 🐛 Troubleshooting

### Spracherkennung funktioniert nicht
- Überprüfe Mikrofon-Einstellungen
- Stelle sicher, dass sounddevice installiert ist
- Prüfe Internet-Verbindung (Google API benötigt online)

### Stimme wird nicht abgespielt
- Überprüfe Lautsprecher-Einstellungen
- Stelle sicher, dass pyttsx3 korrekt installiert ist

### PyQt5 Fehler
```bash
pip install --upgrade PyQt5
```

## 📝 Logs

Alle Aktionen werden in `jarvis.log` geloggt:
```bash
tail -f jarvis.log
```

## 🎨 Customization

### Stimme anpassen
Editiere in `main.py` (MaleVoiceEngine):
```python
self.engine.setProperty('rate', 130)  # Sprechgeschwindigkeit
self.engine.setProperty('volume', 0.95)  # Lautstärke
self.engine.setProperty('pitch', 0.85)  # Tonhöhe
```

### Benutzer-Name
Editiere `jarvis_memory.json`:
```json
{
  "user_name": "Dein Name",
  ...
}
```

## 🤝 Beiträge

Pull Requests sind willkommen! Für größere Änderungen bitte zuerst ein Issue öffnen.

## 📄 Lizenz

MIT License - siehe LICENSE Datei

## 🙏 Credits

- Google Speech Recognition API
- pyttsx3 Text-to-Speech
- PyQt5 GUI Framework
- sounddevice Audio Library

## ⭐ Features für die Zukunft

- [ ] OpenAI GPT Integration für intelligentere Antworten
- [ ] Offline-Spracherkennung
- [ ] Mehrsprachige Unterstützung
- [ ] Custom Voice-Profile
- [ ] Website-Scraping für Live-Daten
- [ ] Todo/Reminder System
- [ ] Musik-Integration
- [ ] Smart Home Integration

---

**Autor:** 040Buddy  
**Version:** 5.0  
**Letzte Aktualisierung:** 2024
