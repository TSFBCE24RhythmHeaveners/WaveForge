# 🎵 WaveForge Audio Recorder - Alpha 0.1

## 🎉 First Alpha Release

Dies ist die erste Alpha-Version von WaveForge, einem professionellen Audio-Recorder mit Live-Upload-Funktionalität und umfassender Netzwerk-Resilienz.

---

## ✨ Hauptfeatures

### 🎤 Audio Recording
- **Professionelle Audioaufnahme** mit WebM/Opus-Codec
- **Live-Upload während der Aufnahme** für optimale Performance
- **Chunk-basiertes Upload-System** für Zuverlässigkeit
- **Echtzeit-Visualisierung** der Aufnahme

### 🌐 Netzwerk-Resilienz (NEU in 0.1)
- ✅ **Automatische Upload-Wiederaufnahme** nach Netzwerkunterbrechungen
- ✅ **Intelligente Offline-Erkennung** mit Service Worker
- ✅ **Korrekte Fortschrittsanzeige** (z.B. 16/16 statt 26/27)
- ✅ **Visuelle Status-Indikatoren** (grün für erfolgreich, nicht rot)

### 🛡️ CrashGuard System
- **Automatische Crash-Erkennung** bei Browser-Abstürzen
- **Chunk-basierte Recovery** aus IndexedDB
- **Nahtlose Wiederherstellung** unterbrochener Aufnahmen

### 🔄 Hybrid Upload System
- **Online-Modus**: Direkter Upload während der Aufnahme
- **Offline-Modus**: Lokale Speicherung mit späterem Upload
- **Service Worker Background Sync** für zuverlässige Uploads

---

## 🐛 Behobene Fehler

### Upload-System
- **Fixed**: Upload-Wiederaufnahme nach Netzwerkunterbrechung funktioniert jetzt zuverlässig
- **Fixed**: Assembly-Signal wird nicht mehr als Chunk gezählt (Off-by-One-Fehler behoben)
- **Fixed**: Status-Badge zeigt nach erfolgreicher Wiederherstellung grün statt rot
- **Fixed**: Service Worker erkennt Verbindungswiederherstellung korrekt

### UI/UX
- **Fixed**: Toast-Benachrichtigungen sind jetzt in E2E-Tests sichtbar (z-index erhöht)
- **Fixed**: Playback-Assertion prüft jetzt auf korrektes Icon ('❚❚')
- **Fixed**: Upload-Status wird konsistent über alle UI-Komponenten hinweg angezeigt

---

## 🔧 Technische Verbesserungen

### Service Worker
- Verbesserte Offline-Erkennung mit `checkServerConnection()`
- Connection-Check bei `TRIGGER_UPLOAD` und `PROCESS_UPLOADS`
- Robustere Fehlerbehandlung und Retry-Logik

### Frontend
- Optimiertes `UploadCoordinator` Status-Management
- Korrekte Chunk-Zählung mit Assembly-Signal-Filter
- Status-Reset von 'failed' zu 'uploading' bei erfolgreichen Uploads

### Testing
- E2E-Tests für Online-Recording mit Metadaten
- E2E-Tests für Offline-Recording und Playback
- E2E-Tests für Netzwerkunterbrechung und Recovery
- Verbesserte Test-Stabilität und Zuverlässigkeit

---

## 📝 Dokumentation

Neue Dokumentation in `.agent/` Verzeichnis:
- `NETWORK_INTERRUPTION_FIX.md` - Upload-Wiederaufnahme nach Netzwerkunterbrechung
- `CHUNK_COUNT_FIX.md` - Korrekte Chunk-Zählung
- `RED_BADGE_FIX.md` - Status-Badge-Farbe nach Recovery

---

## ♿ Accessibility

- **BITV 2.0 Konformität** (Barrierefreie Informationstechnik-Verordnung)
- **ARIA-Labels** für alle interaktiven Elemente
- **Keyboard-Navigation** vollständig unterstützt
- **Screen-Reader-Optimierung**

---

## 📦 Installation

```bash
# Repository klonen
git clone https://github.com/bmaier/waveforge.git
cd waveforge

# Starten (automatische Dependency-Installation)
./start.sh
```

Die Anwendung ist dann verfügbar unter: **http://localhost:8000**

---

## 🧪 Testing

```bash
# E2E-Tests ausführen
./.venv/bin/python -m pytest tests/e2e/ -v

# Integration-Tests
./.venv/bin/python -m pytest tests/integration/ -v

# Unit-Tests
./.venv/bin/python -m pytest tests/unit/ -v
```

---

## 📋 Systemanforderungen

- **Python**: 3.11+
- **Node.js**: 18+ (für Frontend-Development)
- **Browser**: Chrome/Edge 90+, Firefox 88+, Safari 14+
- **Service Worker Support** erforderlich

---

## 📄 Lizenz

Dual-Lizenz:
- **Apache 2.0**: Für Open-Source und nicht-kommerzielle Nutzung
- **Business Source License 1.1**: Für kommerzielle Modifikationen

---

## 🙏 Danksagungen

Entwickelt mit ❤️ von Nina

**Technologie-Stack:**
- FastAPI (Backend)
- Vanilla JavaScript (Frontend)
- Service Workers (Background Sync)
- IndexedDB (Lokale Speicherung)
- WebAudio API (Aufnahme)
- Playwright (E2E-Tests)

---

## 🔜 Roadmap

- [ ] Multi-Track-Recording
- [ ] Audio-Effekte (EQ, Kompressor)
- [ ] Export in verschiedene Formate (MP3, WAV)
- [ ] Cloud-Storage-Integration
- [ ] Collaborative Recording

---

**Vollständige Dokumentation**: [docs/](https://github.com/bmaier/waveforge/tree/main/docs)  
**Issues & Feedback**: [GitHub Issues](https://github.com/bmaier/waveforge/issues)  
**Lizenz**: [LICENSE.md](https://github.com/bmaier/waveforge/blob/main/LICENSE.md)

---

© 2025 Licensed under Apache 2.0 / Business Source License 1.1
