# Troubleshooting Guide

Dieser Guide hilft bei häufigen Problemen mit Netpulse auf Raspberry Pi.

## 🔧 Häufige Probleme

### Keine Daten im Webinterface

**Symptome:**
- Webinterface zeigt "Keine Daten" oder leere Tabellen
- Charts bleiben leer
- Health-Endpoint zeigt Fehler

**Ursachen & Lösungen:**

#### 1. Timer oder Service läuft nicht
```bash
# Status prüfen
sudo systemctl status netpulse.timer
sudo systemctl status netpulse.service

# Services aktivieren
sudo systemctl enable --now netpulse.timer
sudo systemctl enable --now netpulse-web

# Timer manuell starten
sudo systemctl start netpulse.timer
```

#### 2. Datenbank-Berechtigungsprobleme
```bash
# Berechtigungen prüfen
ls -la /var/lib/netpulse/

# Korrekte Berechtigungen setzen
sudo chown -R netpulse:netpulse /var/lib/netpulse/
sudo chmod 755 /var/lib/netpulse/
```

#### 3. librespeed-cli nicht gefunden
```bash
# Installation prüfen
which librespeed-cli
librespeed-cli --version

# Neu installieren falls nötig
curl -L https://github.com/librespeed/speedtest-cli/releases/latest/download/librespeed-cli-linux-arm64 -o /usr/local/bin/librespeed-cli
sudo chmod +x /usr/local/bin/librespeed-cli
```

#### 4. Manuelles Testen
```bash
# Als netpulse User testen
sudo -u netpulse netpulse-measure --type bandwidth --verbose

# Als aktueller User testen
netpulse-measure --type bandwidth --verbose
```

### Timer funktioniert nicht

**Symptome:**
- Keine automatischen Messungen
- `systemctl list-timers` zeigt keine anstehenden Jobs
- Nur manuelle Messungen funktionieren

**Lösungen:**

```bash
# Timer neu laden und starten
sudo systemctl daemon-reload
sudo systemctl restart netpulse.timer

# Konfiguration prüfen
cat /lib/systemd/system/netpulse.timer

# Logs prüfen
sudo journalctl -u netpulse.timer -f
sudo journalctl -u netpulse.service -f
```

### Webinterface nicht erreichbar

**Symptome:**
- Connection refused bei `http://<IP>:8080`
- Timeout beim Laden der Seite

**Lösungen:**

```bash
# Service-Status prüfen
sudo systemctl status netpulse-web

# Port prüfen
sudo netstat -tlnp | grep :8080

# Firewall prüfen
sudo ufw status

# Service neu starten
sudo systemctl restart netpulse-web

# Logs prüfen
sudo journalctl -u netpulse-web -f
```

### Performance-Probleme

**Symptome:**
- Lange Ladezeiten im Webinterface
- Timeouts bei Speedtests
- Hohe CPU-Auslastung

**Lösungen:**

```bash
# System-Ressourcen prüfen
htop
df -h
free -h

# Datenbankgröße prüfen
ls -lh /var/lib/netpulse/netpulse.db

# Alte Daten aufräumen (falls nötig)
sqlite3 /var/lib/netpulse/netpulse.db "DELETE FROM measurements WHERE timestamp < datetime('now', '-30 days');"
```

## 📋 Diagnose-Checkliste

### Grundlegende Checks
1. **Services laufen:**
   ```bash
   sudo systemctl status netpulse.timer netpulse.service netpulse-web
   ```

2. **Ports erreichbar:**
   ```bash
   curl -I http://localhost:8080
   ```

3. **Datenbank zugänglich:**
   ```bash
   sqlite3 /var/lib/netpulse/netpulse.db "SELECT COUNT(*) FROM measurements;"
   ```

4. **librespeed-cli funktioniert:**
   ```bash
   librespeed-cli --json --server 1
   ```

### Detaillierte Diagnose

#### 1. Timer-Debugging
```bash
# Nächste Ausführung prüfen
sudo systemctl list-timers | grep netpulse

# Timer-Konfiguration anzeigen
systemctl show netpulse.timer

# Manuelles Auslösen
sudo systemctl start netpulse.service
```

#### 2. Service-Debugging
```bash
# Letzte Ausführung prüfen
sudo journalctl -u netpulse.service --since "1 hour ago"

# Mit Debug-Level laufen
sudo systemctl edit netpulse.service
# Füge hinzu: Environment=NETPULSE_LOG_LEVEL=DEBUG
```

#### 3. Webinterface-Debugging
```bash
# API-Endpunkte testen
curl http://localhost:8080/api/health
curl http://localhost:8080/api/data

# Templates prüfen
ls -la /usr/lib/python3.11/dist-packages/netpulse/templates/
```

## 🆘 Hilfe bekommen

### Logs sammeln
```bash
# System-Logs
sudo journalctl -u netpulse.timer -u netpulse.service -u netpulse-web --since "1 hour ago" > netpulse-logs.txt

# Anwendung-Logs
tail -f /var/log/netpulse/netpulse.log

# System-Info
uname -a > system-info.txt
cat /etc/os-release >> system-info.txt
```

### Debug-Modus aktivieren
```bash
# Konfiguration anpassen
sudo nano /etc/netpulse/netpulse.conf

# Logging-Level erhöhen
logging.level = DEBUG

# Services neu starten
sudo systemctl restart netpulse-web
```

### Community Support
- **GitHub Issues**: [neues Issue erstellen](https://github.com/afinck/netpulse-py/issues)
- **Logs anhängen**: Immer relevante Logs mitteilen
- **System-Info**: Raspberry Pi Modell und OS-Version angeben
