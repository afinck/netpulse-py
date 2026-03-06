# Netpulse - Network Monitoring Tool

Ein leichtgewichtiges Netzwerk-Monitoring-Tool für Raspberry Pi, das Bandbreite und Latenz misst und in einem responsive Webinterface darstellt.

## License

Dieses Projekt ist unter der [MIT License](LICENSE) lizenziert.

## Features

- ✅ Automatische Messung von Bandbreite und Latenz (alle 15 Minuten)
- ✅ Responsive Webinterface mit Echtzeit-Charts und historischen Tabellen
- ✅ SQLite Datenbank für zuverlässige Datenspeicherung
- ✅ Systemd Timer für robuste automatische Messungen
- ✅ DEB-Paket für einfache Installation auf Raspberry Pi
- ✅ Unterstützung für librespeed-cli mit JSON-Array-Format
- ✅ Vollständige Fehlerbehandlung und Logging
- ✅ Manuelles Testen über Webinterface und Kommandozeile

## Installation

```bash
# DEB-Paket installieren
sudo dpkg -i netpulse_1.0.0_arm64.deb

# Abhängigkeiten installieren (falls nötig)
sudo apt-get install -f

# Services starten
sudo systemctl enable --now netpulse.timer
sudo systemctl enable --now netpulse-web
```

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

**Wichtige Einstellungen:**
- `measurement.interval_minutes`: Messintervall (Standard: 15)
- `database.path`: Datenbankpfad (Standard: `/var/lib/netpulse/netpulse.db`)
- `web.port`: Webinterface-Port (Standard: 8080)

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

### Timer funktioniert nicht
```bash
# Timer neu starten
sudo systemctl restart netpulse.timer

# Service manuell auslösen
sudo systemctl start netpulse.service

# Logs prüfen
sudo journalctl -u netpulse.service -f
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
- **`netpulse/web.py`**: Flask Webinterface mit API-Endpunkten
- **`netpulse/config.py`**: Konfigurationsmanagement mit Default-Werten

### Datenfluss
1. **Timer** löst `netpulse.service` alle 15 Minuten aus
2. **Speedtest** führt `librespeed-cli` aus und parst JSON-Array
3. **Datenbank** speichert Messwerte mit Timestamp
4. **Webinterface** zeigt Echtzeit- und historische Daten

### Services
- **`netpulse.timer`**: Systemd Timer für automatische Messungen
- **`netpulse.service`**: Oneshot Service für einzelne Messungen
- **`netpulse-web.service`**: Flask Webserver als Daemon

## CI/CD

Die Anwendung hat eine vollständige CI/CD-Pipeline mit GitHub Actions:
- **Multi-Python-Version Tests**: 3.8, 3.9, 3.10, 3.11
- **Code-Qualität**: flake8, black, isort
- **Security**: bandit, safety
- **Integration Tests**: Docker-basiert
- **Automatische Builds**: DEB-Pakete und Docker Images
- **Coverage**: codecov Integration

## Changelog

### v1.0.0 (2026-03-06)
- ✅ JSON-Parsing für librespeed-cli Array-Format behoben
- ✅ Datenbank-Berechtigungsprobleme gelöst
- ✅ Timestamp-Parsing in History-Seite korrigiert
- ✅ Timer-Funktionalität vollständig implementiert
- ✅ Unittests aktualisiert und erweitert
- ✅ Fehlerbehandlung und Logging verbessert
- ✅ Dokumentation überarbeitet und erweitert
