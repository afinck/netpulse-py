# Changelog

Alle wichtigen Änderungen des Netpulse Projekts werden hier dokumentiert.

## [1.0.0] - 2026-03-06

### 🐛 Bug Fixes
- **JSON-Parsing**: Behobenes Problem mit librespeed-cli Array-Format
  - librespeed-cli gibt JSON-Array zurück, aber Code erwartete einzelnes Objekt
  - Feldnamen waren verschachtelt (`download.bandwidth`) statt direkt (`download`)
- **Datenbank-Berechtigungen**: "readonly database" Fehler behoben
  - netpulse User hatte keine Schreibrechte auf `/var/lib/netpulse/`
  - Korrekte User/Group-Berechtigungen implementiert
- **Timestamp-Parsing**: History-Seite Fehler `'str object' has no attribute 'strftime'`
  - Timestamp-Strings werden jetzt vor der Anzeige zu datetime-Objekten konvertiert

### ✨ Features
- **Timer-Funktionalität**: Vollständig implementiert und getestet
  - Automatische Messungen alle 15 Minuten
  - Robuste Fehlerbehandlung und Logging
- **Manuelle Tests**: Über Webinterface und Kommandozeile möglich
- **Service-Management**: Verbesserte systemd Integration

### 🧪 Testing
- **Unittests**: Aktualisiert für neues librespeed-cli Format
  - Mock-Daten an echtes JSON-Array-Format angepasst
  - Alle 27 Kern-Tests bestehen erfolgreich
- **Integration**: Webinterface und Timer-Komponenten getestet

### 📚 Documentation
- **README.md**: Komplett überarbeitet und erweitert
  - Detaillierte Installationsanleitung
  - Fehlerbehebungs-Sektion
  - Architektur-Beschreibung
  - Service-Management Befehle
- **CHANGELOG.md**: Neue Datei für Änderungshistorie

### 🔧 Technical Improvements
- **Fehlerbehandlung**: Verbesserte Exception-Handling im Speedtest
- **Logging**: Detailliertere Logging-Meldungen für Debugging
- **Code-Qualität**: Refactoring und Optimierung der Parsing-Logik

---

## [0.9.0] - 2026-02-XX

### ✨ Initial Release
- Grundlegende Netzwerk-Monitoring-Funktionalität
- Flask Webinterface mit Charts
- SQLite Datenbank-Integration
- Systemd Timer und Services
- DEB-Paket-Build-Prozess
