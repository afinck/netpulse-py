# Changelog

Alle wichtigen Änderungen des Netpulse Projekts werden hier dokumentiert.

## [1.1.1] - 2026-03-08

### ✨ Features
- **Cross-Compilation**: GitHub Actions für automatische Multi-Architecture builds
  - ARM64 builds für Raspberry Pi und andere ARM-Geräte
  - AMD64 builds für Standard x86_64 Systeme
  - Docker Buildx Integration für cross-platform builds
- **Python 3.11+ Kompatibilität**: Modernes Python-Packaging mit `.dist-info` Format
  - Behebung von `PackageNotFoundError` auf Python 3.11+
  - System-wide Installation in `/usr/lib/python3/dist-packages/`
  - Kompatibel mit allen Python-Versionen (3.8+)
- **Debug-Tools**: Zwei neue Verifikationsskripte
  - `verify_installation.sh`: Prüft Paketinstallation und Metadaten
  - `debug_measurements.sh`: Diagnostiziert Messungsprobleme

### 🔧 Technical Improvements
- **Modern Packaging**: Wheel-basierte builds mit `.dist-info` Metadaten
- **System-wide Installation**: Universelle Python-Paketpfade
- **Debian Rules Enhancement**: Automatische Metadaten-Extraktion aus Wheels
- **Build Script Improvements**: Robuste Fehlerbehandlung und Debug-Ausgaben
- **Docker Integration**: Multi-architecture Docker Buildx workflow

### 🐛 Bug Fixes
- **PackageNotFoundError**: Behoben durch system-weite Metadaten-Installation
- **Python Version Mismatch**: Paket funktioniert auf allen Python-Versionen
- **Cross-compilation Issues**: DEB-Pakete für alle Architekturen funktionieren

### 📚 Documentation
- **README.md**: Aktualisiert mit Cross-Compilation und Python 3.11+ Infos
- **Troubleshooting**: Erweiterte Fehlerbehebungs-Sektion mit Debug-Skripten
- **CI/CD**: Dokumentation des neuen Cross-Compilation Workflows

---

## [1.1.0] - 2026-03-07

### ✨ Features
- **Web-basierte Konfiguration**: Vollständige Konfiguration über Webinterface
  - Messintervall anpassbar (1-1440 Minuten)
  - Timeout für Messungen konfigurierbar (5-300 Sekunden)
  - Wiederholungsversuche einstellbar (1-10)
  - Formular mit Validierung und Fehlerbehandlung
- **Automatische SystemD-Timer-Aktualisierung**: Timer wird bei Intervalländerung automatisch neu konfiguriert
  - Unterstützung für verschiedene Intervalle (Minuten, Stunden, täglich)
  - Automatische systemd daemon-reload und Timer-Restart
  - Fallback auf manuelle Anleitung bei Berechtigungsproblemen
- **API-Endpunkte für Konfiguration**: RESTful API für Konfigurationsmanagement
  - `GET /api/config`: Abruf aktueller Konfiguration
  - `POST /api/config`: Aktualisierung mit Validierung
  - JSON-Format mit Fehlerbehandlung

### 🎨 UI/UX Improvements
- **Einstellungsseite**: Neue Seite im Webinterface mit Konfigurationsformular
  - Responsive Bootstrap-Design
  - Klare Beschriftungen und Hilfetexte
  - Echtzeit-Validierung und Benutzer-Feedback
- **Verbesserte Statistik-Anzeige**: Farbliche Werte für bessere Lesbarkeit
  - Download-Werte in Blau (`text-primary`)
  - Upload-Werte in Grün (`text-success`)
  - Latenz-Werte in Orange (`text-warning`)
  - Besser sichtbar auf gestreiftem Tabellenhintergrund

### 🧪 Testing
- **Erweiterte Tests**: Neue Tests für Konfigurationsfunktionalität
  - `test_settings_page`: Lade-Test für Einstellungsseite
  - `test_api_config_get`: API GET-Endpunkt Test
  - `test_api_config_post_valid`: API POST mit gültigen Daten
  - `test_api_config_post_invalid`: API POST mit ungültigen Daten
- **Config-Tests**: Alle 11 Konfigurations-Tests bestehen erfolgreich
- **Web-Tests**: Alle neuen Web-Interface-Tests bestehen

### 📚 Documentation
- **README.md**: Vollständig aktualisiert mit neuen Features
  - Web-basierte Konfigurationsanleitung
  - Erweiterte Konfigurationsparameter mit Bereichen
  - Neue API-Endpunkte dokumentiert
  - Aktualisierte Architektur-Beschreibung
- **Version**: Auf v1.1.0 erhöht in setup.py

### 🔧 Technical Improvements
- **Config-Klasse**: Neue `save()` Methode für persistente Konfiguration
  - Automatische Verzeichniserstellung
  - Strukturierte Ausgabe mit Kommentaren
  - Type-Konvertierung für booleans
- **Web-Interface**: Erweiterte Flask-Routen und Templates
  - Neue `/settings` Route
  - Konfigurations-API mit Validierung
  - SystemD-Integration für Timer-Updates
- **Error Handling**: Verbesserte Fehlerbehandlung und Logging

---

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
