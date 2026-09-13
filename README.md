# J.A.R.V.I.S v6.0 - Komplette Professional App

**Just A Rather Very Intelligent System** - Dein persoenlicher KI-Sprachassistent fuer Windows

## 🎯 Features

### 🎤 Spracherkennung
- Deutsche Spracherkennung mit Google API
- Realistische maennliche Stimme (Text-to-Speech)
- Asynchrone Verarbeitung (keine Verzoegerung)

### 📝 Notizen
- Schreibe schnell Notizen
- Automatisch auf Desktop gespeichert
- "Schreibe eine Notiz: Einkaufen Milch, Brot, Kaese"

### ⏱️ Timer & Alarme
- Timer stellen: "Timer fuer 5 Minuten"
- Automatische Benachrichtigung
- Mehrere Timer gleichzeitig

### 🚀 Apps oeffnen
- Chrome, Firefox, Edge, Discord, Spotify
- Uhr, Rechner, Notepad, Explorer
- "Oeffne Chrome" → Chrome startet sofort

### 🔍 Browser-Befehle
- Google-Suche: "Suche nach Python"
- Direkt im Standard-Browser

### ✅ Todo/Aufgaben
- Aufgaben-Verwaltung: "Erstelle Aufgabe Projekt fertig"
- Offline gespeichert
- In Datenbank

### 💾 Chat-Historie
- Alle Gespraeche gespeichert
- Zeitstempel
- Durchsuchbar

### ⚙️ Erweiterte Einstellungen
- Benutzername aendern
- Sprachwechsel (bald)
- Auto-Start Option (bald)

## 📥 Installation

### Option 1: Fertige EXE (Schnell)
```bash
1. Lade JARVIS.exe herunter
2. Doppelklick -> Starten
3. Keine Installation noetig!
```

### Option 2: Aus Source (Entwickler)
```bash
# 1. Klone Repository
git clone https://github.com/040Buddy/JARVIS-Sprachassistent.git
cd JARVIS-Sprachassistent

# 2. Installiere Dependencies
pip install -r requirements.txt

# 3. Starte
python main.py
```

### Option 3: Baue eigene EXE
```bash
# Installiere PyInstaller
pip install pyinstaller

# Baue EXE
python build_app.py

# Starten
dist/JARVIS.exe
```

## 🎮 Befehle

### Grueße
```
"Hallo" → JARVIS antwortet nach Tageszeit
"Guten Morgen"
"Guten Tag"
```

### Notizen
```
"Schreibe eine Notiz: Meine Einkaufsliste"
→ Speichert als: Desktop/JARVIS_Notes/Notiz_*.txt

"Schreibe Notiz: Projektideen: Spiele, Apps, Websites"
```

### Aufgaben
```
"Erstelle Aufgabe: Projekt bis Freitag fertig"
"Erstelle Aufgabe: Meeting mit Team"
"Meine Aufgaben" → Zeigt alle ToDos
```

### Timer
```
"Timer fuer 5 Minuten"
"Timer 30 Sekunden"
"Wecker fuer 1 Stunde"
→ Benachrichtigung wenn fertig
```

### Apps oeffnen
```
"Oeffne Chrome" → Google Chrome startet
"Starte Discord"
"Oeffne VS Code"
"Oeffne Uhr"
"Oeffne Rechner"
"Starte Firefox"
```

### Suche
```
"Suche nach Python Tutorial"
"Google: Machine Learning"
→ Oeffnet Google mit Suchergebnis
```

### Zeit & Datum
```
"Wie spaet ist es?" → "Es ist 15:30 Uhr, Freitag..."
"Datum" → Heutiges Datum
```

## 📊 Datenbank

Alle Daten werden lokal gespeichert:
- `jarvis.db` - SQLite Datenbank
  - Notizen
  - Aufgaben/Todos
  - Chat-Historie
  - Timer-History

## 🔧 Konfiguration

Editiere `config.py`:

```python
# Sprachgeschwindigkeit (80-400)
TTS_RATE = 150

# Lautstärke (0.0-1.0)
TTS_VOLUME = 1.0

# Sprache
SR_LANGUAGE = "de-DE"  # Deutsch

# Notizen-Verzeichnis
NOTES_DIR = Path.home() / "Desktop" / "JARVIS_Notes"
```

## 📋 Systemanforderungen

- **OS**: Windows 7+
- **RAM**: 2GB minimum (4GB empfohlen)
- **Internet**: Fuer Spracherkennung & Suche
- **Mikrofon**: Fuer Spracherkennung
- **Lautsprecher**: Fuer Sprachausgabe

## 🐛 Troubleshooting

### Spracherkennung funktioniert nicht
1. Pruefe Mikrofon in Windows
2. Stelle sicher, dass Internet verbunden ist
3. Restart JARVIS

### Stimme wird nicht abgespielt
1. Pruefe Lautsprecher
2. Erhoehe Lautstärke in Windows

### Apps oeffnen nicht
1. App muss im PATH sein oder auf Desktop
2. Nutze kompletten Pfad in config.py

## 📈 Geplante Features

- [ ] Offline Speech Recognition
- [ ] OpenAI GPT Integration
- [ ] Smarthome Control (Philips Hue, etc.)
- [ ] Kalender-Integration (Google Cal)
- [ ] Emai-Zugriff
- [ ] Wetter-Daten (live)
- [ ] Mobile App (Android/iOS)
- [ ] Cloud-Sync
- [ ] Plugin-System
- [ ] Web-Interface

## 📄 Lizenz

MIT License - Frei verwendbar

## 👨‍💻 Autor

Erstellt von 040Buddy

## 🤝 Support

Probleme? Issues posten auf GitHub oder frag JARVIS direkt!

---

**Version**: 6.0  
**Status**: Release  
**Letzte Aenderung**: 2024
