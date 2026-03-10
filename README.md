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
- ✅ **Mobile-optimiertes Interface** mit verbesserten Layout und Footer
- ✅ **Rolling Zeitperioden** (letzten 7/30/365 Tage statt Kalenderwochen)
- ✅ **Theme-Persistenz** - gewähltes Theme bleibt über Seiten-Reloads hinweg erhalten
- ✅ **Comprehensive Security Features**:
  - 🔒 OWASP-konforme Security Headers (CSP, HSTS, X-Frame-Options)
  - 🛡️ Rate Limiting für API-Endpunkte zum Schutz vor Missbrauch
  - 🔍 Strikte Input Validation gegen Injection-Angriffe
  - 📝 Security Logging mit IP-Tracking und Event-Monitoring
  - 🔐 Automatische Secret-Key-Generierung bei Installation
  - 🔒 Sichere File Permissions (Database: 600, Config: 640)
- ✅ **Complete Internationalization (i18n)**:
  - 🌍 Multi-Language Support für Englisch und Deutsch
  - 🎨 Professional Language Switcher mit Flaggen
  - 🔄 URL Parameter Support (`?lang=en`/`?lang=de`)
  - 🌐 Automatische Browser-Spracherkennung
  - 🇺🇸 Englisch als Default-Sprache
  - 🔗 Language-Preserving Navigation
  - 📝 Vollständige Übersetzung aller Templates (Dashboard, History, Settings, Export)
  - 📦 Gettext-basierte Übersetzungs-Infrastruktur

## Installation

```bash
# DEB-Paket installieren
sudo dpkg -i netpulse_1.1.2_arm64.deb

# Abhängigkeiten installieren (falls nötig)
sudo apt-get install -f

# Services starten
sudo systemctl enable --now netpulse.timer
sudo systemctl enable --now netpulse-web
```

> 📋 **Hinweis**: Die Installation konfiguriert automatisch Security-Features:
> - Generiert einen sicheren Secret Key
> - Setzt sichere File Permissions
> - Aktiviert Security Headers und Rate Limiting
> - Führt einen automatischen Security Audit durch

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

## 🛡️ Security

Netpulse implementiert umfassende Security-Maßnahmen nach OWASP Top 10 2021 Standards:

### Automatische Security-Features
- **🔒 Security Headers**: CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- **🛡️ Rate Limiting**: API-Endpunkte sind gegen Missbrauch geschützt
- **🔍 Input Validation**: Strikte Validierung gegen Injection-Angriffe
- **📝 Security Logging**: IP-Tracking und Event-Monitoring
- **🔐 Secret Management**: Automatische Generierung sicherer Secret Keys
- **🔒 File Permissions**: Sichere Berechtigungen für Datenbank und Konfiguration

### Security Audit
```bash
# Automatischer Security Check
python3 /usr/lib/python3/dist-packages/netpulse/security/security_check.py

# Manuelle Überprüfung
curl -I http://localhost:8080/  # Security Headers prüfen
```

### Security Best Practices
- **🔍 Regelmäßige Audits**: Wöchentliche Security-Scans empfehlen
- **📦 Dependency Updates**: Monatliche Sicherheits-Updates
- **🔐 HTTPS**: Reverse Proxy mit SSL/TLS in Produktion
- **🔥 Firewall**: Netzwerkzugriff beschränken

### Security-Konfiguration
Die Installation konfiguriert automatisch:
- Sicheren Secret Key in `/etc/environment`
- File Permissions (Database: 600, Config: 640)
- Security Headers und Rate Limiting
- Post-Installation Security Audit

> 📋 **Details**: Siehe `SECURITY_INSTALLATION.md` für umfassende Security-Anleitung

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
- **Automatische Builds**: DEB-Pakete und Docker Images
- **Coverage**: codecov Integration

## Changelog

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
