# Netpulse - Network Monitoring Tool

Ein leichtgewichtiges Netzwerk-Monitoring-Tool für Raspberry Pi, das Bandbreite und Latenz misst und in einem responsive Webinterface darstellt.

## License

Dieses Projekt ist unter der [MIT License](LICENSE) lizenziert.

## Features

- ✅ Automatische Messung von Bandbreite und Latenz (konfigurierbares Intervall)
- ✅ Responsive Webinterface mit Echtzeit-Charts und historischen Tabellen
- ✅ SQLite Datenbank für zuverlässige Datenspeicherung
- ✅ Systemd Timer für robuste automatische Messungen
- ✅ DEB-Paket für einfache Installation auf Raspberry Pi
- ✅ Unterstützung für librespeed-cli mit JSON-Array-Format
- ✅ Vollständige Fehlerbehandlung und Logging
- ✅ Manuelles Testen über Webinterface und Kommandozeile
- ✅ **Web-basierte Konfiguration** für Messintervall, Timeout und Wiederholungsversuche
- ✅ **Automatische SystemD-Timer-Aktualisierung** bei Konfigurationsänderungen

## Installation

### DEB-Paket (Empfohlen)
```bash
# DEB-Paket installieren
sudo dpkg -i netpulse_1.1.0_arm64.deb  # Raspberry Pi
sudo dpkg -i netpulse_1.1.0_amd64.deb  # x86_64 Systeme

# Abhängigkeiten installieren (falls nötig)
sudo apt-get install -f

# Services starten
sudo systemctl enable --now netpulse.timer
sudo systemctl enable --now netpulse-web
```

### Python 3.11+ Kompatibilität
Netpulse verwendet modernes Python-Packaging (`.dist-info` Format) und ist vollständig mit Python 3.11+ kompatibel.

### Cross-Compilation
Die DEB-Pakete werden automatisch für multiple Architekturen gebaut:
- **ARM64**: Für Raspberry Pi und andere ARM-Geräte
- **AMD64**: Für Standard x86_64 Systeme

Siehe `.github/workflows/build-deb-cross.yml` für Details.

## Verwendung

Nach der Installation ist das Webinterface unter `http://<RASPBERRY-PI-IP>:8080` erreichbar.

### Manuelles Testen
```bash
# Bandbreitentest
netpulse-measure --type bandwidth

# Latenztest  
netpulse-measure --type latency

# Mit detaillierter Ausgabe
netpulse-measure --type bandwidth --verbose
```

### Service-Status prüfen
```bash
# Webinterface-Status
sudo systemctl status netpulse-web

# Timer-Status
sudo systemctl status netpulse.timer

# Nächste Messung anzeigen
sudo systemctl list-timers | grep netpulse
```

## Konfiguration

Die Konfigurationsdatei befindet sich unter `/etc/netpulse/netpulse.conf`.

### Web-basierte Konfiguration (Empfohlen)
Die einfachste Methode zur Konfiguration ist über das Webinterface:
1. Webinterface unter `http://<RASPBERRY-PI-IP>:8080` öffnen
2. Menü "Einstellungen" auswählen
3. Gewünschte Werte anpassen und speichern
4. SystemD-Timer wird bei Bedarf automatisch aktualisiert

### Manuelle Konfiguration
**Wichtige Einstellungen:**
- `measurement.interval_minutes`: Messintervall (Standard: 15, Bereich: 1-1440)
- `measurement.timeout_seconds`: Timeout für Messungen (Standard: 30, Bereich: 5-300)
- `measurement.retry_count`: Wiederholungsversuche (Standard: 3, Bereich: 1-10)
- `database.path`: Datenbankpfad (Standard: `/var/lib/netpulse/netpulse.db`)
- `web.port`: Webinterface-Port (Standard: 8080)

**Beispiel-Konfiguration:**
```ini
# Measurement settings
measurement.interval_minutes=30
measurement.timeout_seconds=60
measurement.retry_count=5

# Web interface settings
web.host=0.0.0.0
web.port=8080
```

## Fehlerbehebung

### Keine Daten im Webinterface
```bash
# 1. Service-Status prüfen
sudo systemctl status netpulse.timer netpulse.service

# 2. Datenbank-Berechtigungen prüfen
sudo chown -R netpulse:netpulse /var/lib/netpulse/

# 3. Manuelles Testen
sudo -u netpulse netpulse-measure --type bandwidth --verbose
```

### PackageNotFoundError (Python 3.11+)
```bash
# 1. Installation prüfen
dpkg -l | grep netpulse

# 2. Package-Metadaten prüfen
./verify_installation.sh  # Verifikationsskript verwenden

# 3. Falls nötig, Paket neu installieren
sudo dpkg -r netpulse && sudo dpkg -i netpulse_1.1.0_*.deb
```

### Timer funktioniert nicht
```bash
# Timer neu starten
sudo systemctl restart netpulse.timer

# Service manuell auslösen
sudo systemctl start netpulse.service

# Logs prüfen
sudo journalctl -u netpulse.service -f
```

### Messungen funktionieren nicht
```bash
# Debug-Skript ausführen
./debug_measurements.sh

# Häufigste Probleme:
# - Datenbank-Berechtigungen: sudo chown -R netpulse:netpulse /var/lib/netpulse/
# - librespeed-cli fehlt: sudo apt-get install librespeed-cli
# - Netzwerk-Probleme: ping 8.8.8.8
```

## Entwicklung

```bash
# Entwicklungsumgebung einrichten
make install-dev

# Webserver starten
make dev

# Tests ausführen
make test

# Nur Unit Tests
make test-unit

# Integration Tests (benötigt Docker)
make test-integration

# Code-Qualität prüfen
make lint

# Code formatieren
make format
```

## Tests

Netpulse verwendet `pytest` für Tests mit Coverage-Reporting:

### Unit Tests
```bash
# Unit Tests mit Mocks
pytest tests/ -v -m "not integration"

# Mit Coverage
pytest tests/ --cov=netpulse --cov-report=html

# Nur Kern-Tests (empfohlen)
pytest tests/test_speedtest.py tests/test_database.py tests/test_config.py -v
```

### Integration Tests
```bash
# Mit Docker Compose
docker-compose -f docker-compose.test.yml --profile integration up --build

# Oder mit Make
make test-integration
```

### Docker Tests
```bash
# Alle Tests in Docker
make docker-test

# Manuelle Tests
docker-compose up --build
```

## Architektur

### Komponenten
- **`netpulse/speedtest.py`**: librespeed-cli Integration mit JSON-Array-Parsing
- **`netpulse/database.py`**: SQLite CRUD-Operationen und Statistiken
- **`netpulse/web.py`**: Flask Webinterface mit API-Endpunkten und Konfiguration
- **`netpulse/config.py`**: Konfigurationsmanagement mit Default-Werten und Speicherung

### Datenfluss
1. **Timer** löst `netpulse.service` im konfigurierten Intervall aus
2. **Speedtest** führt `librespeed-cli` aus und parst JSON-Array
3. **Datenbank** speichert Messwerte mit Timestamp
4. **Webinterface** zeigt Echtzeit- und historische Daten
5. **Konfiguration** kann über Webinterface oder Konfigurationsdatei angepasst werden

### Services
- **`netpulse.timer`**: Systemd Timer für automatische Messungen (konfigurierbar)
- **`netpulse.service`**: Oneshot Service für einzelne Messungen
- **`netpulse-web.service`**: Flask Webserver als Daemon

### API-Endpunkte
- `GET/POST /api/config`: Konfigurationsmanagement
- `GET /api/data`: Chart-Daten für verschiedene Zeiträume
- `GET /api/stats`: Statistische Auswertungen
- `POST /api/test`: Manuelles Auslösen von Messungen
- `GET /api/health`: Health-Check Endpunkt

## CI/CD

Die Anwendung hat eine vollständige CI/CD-Pipeline mit GitHub Actions:
- **Multi-Python-Version Tests**: 3.8, 3.9, 3.10, 3.11
- **Code-Qualität**: flake8, black, isort
- **Security**: bandit, safety
- **Integration Tests**: Docker-basiert
- **Cross-Compilation**: Automatische DEB-Pakete für ARM64 und AMD64
- **Coverage**: codecov Integration

### Cross-Compilation Workflow
Der `.github/workflows/build-deb-cross.yml` Workflow:
- **Docker Buildx**: Multi-architecture builds
- **Modern Python Packaging**: `.dist-info` Format für Python 3.11+
- **System-wide Installation**: Kompatibel mit allen Python-Versionen
- **Automated Releases**: DEB-Pakete für alle Architekturen

## Changelog

### v1.1.1 (2026-03-08)
- ✅ **Cross-Compilation**: GitHub Actions für ARM64 und AMD64 builds
- ✅ **Python 3.11+ Kompatibilität**: Modernes `.dist-info` packaging
- ✅ **System-wide Installation**: Universelle Python-Paketpfade
- ✅ **Debug-Tools**: Verifikations- und Debug-Skripte
- ✅ **Multi-Architecture Support**: Docker Buildx Integration
- ✅ **Package-Metadata-Fix**: `PackageNotFoundError` behoben

### v1.1.0 (2026-03-07)
- ✅ **Web-basierte Konfiguration** für Messintervall, Timeout und Wiederholungsversuche hinzugefügt
- ✅ **Automatische SystemD-Timer-Aktualisierung** bei Konfigurationsänderungen implementiert
- ✅ **API-Endpunkte** für Konfigurationsmanagement (`/api/config`) hinzugefügt
- ✅ **Einstellungsseite** im Webinterface mit Formular zur Konfiguration
- ✅ **Verbesserte UI** mit farblichen Statistikwerten für bessere Lesbarkeit
- ✅ **Erweiterte Tests** für neue Konfigurationsfunktionen
- ✅ **Dokumentation** aktualisiert und erweitert

### v1.0.0 (2026-03-06)
- ✅ JSON-Parsing für librespeed-cli Array-Format behoben
- ✅ Datenbank-Berechtigungsprobleme gelöst
- ✅ Timestamp-Parsing in History-Seite korrigiert
- ✅ Timer-Funktionalität vollständig implementiert
- ✅ Unittests aktualisiert und erweitert
- ✅ Fehlerbehandlung und Logging verbessert
- ✅ Dokumentation überarbeitet und erweitert
