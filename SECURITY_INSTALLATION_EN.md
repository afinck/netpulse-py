# Security Installation Guide

## 🛡️ Netpulse Security Implementation

This document provides comprehensive security installation and configuration instructions for Netpulse, implementing OWASP Top 10 2021 security controls.

## 📋 Table of Contents

- [Security Overview](#security-overview)
- [Installation Security](#installation-security)
- [Configuration Security](#configuration-security)
- [Security Audit](#security-audit)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## 🔒 Security Overview

Netpulse implements enterprise-grade security controls based on OWASP Top 10 2021:

### Security Features
- **Content Security Policy (CSP)**: Prevents XSS and injection attacks
- **HTTP Security Headers**: HSTS, X-Frame-Options, X-Content-Type-Options
- **Rate Limiting**: API abuse protection with different limits per endpoint
- **Input Validation**: Strict type checking and sanitization
- **Secure File Permissions**: Database (600), Config (640), Logs (640)
- **Security Logging**: IP tracking and event monitoring
- **Secret Management**: Automatic secure secret key generation
- **Automated Auditing**: Comprehensive vulnerability scanning

### OWASP Top 10 2021 Coverage
| Risk | Control | Implementation |
|-------|----------|----------------|
| A01: Broken Access Control | Rate Limiting | ✅ Implemented |
| A02: Cryptographic Failures | Secret Management | ✅ Implemented |
| A03: Injection | Input Validation | ✅ Implemented |
| A04: Insecure Design | Secure Architecture | ✅ Implemented |
| A05: Security Misconfiguration | Automated Audits | ✅ Implemented |
| A06: Vulnerable Components | Dependency Scanning | ✅ Implemented |
| A07: Authentication Failures | Secure Sessions | ✅ Implemented |
| A08: Software/Data Integrity | Secure Logging | ✅ Implemented |
| A09: Logging/Monitoring | Security Events | ✅ Implemented |
| A10: Server-Side Forgery | CSRF Protection | ✅ Implemented |

## 🚀 Installation Security

### Automated Security Hardening

The DEB package includes automatic security hardening:

```bash
# Post-installation security setup runs automatically
sudo dpkg -i netpulse_v1.1.2_*.deb
```

**Automatic Security Actions:**
1. **Secret Key Generation**: Creates secure 256-bit secret key
2. **File Permissions**: Sets secure permissions on all files
3. **Directory Creation**: Creates secure directory structure
4. **Service Configuration**: Sets up secure systemd services
5. **Security Audit**: Runs initial security assessment

### Manual Security Setup

If installing from source:

```bash
# 1. Create secure directory structure
sudo mkdir -p /var/lib/netpulse /var/log/netpulse /etc/netpulse
sudo mkdir -p /usr/lib/netpulse/security

# 2. Set secure ownership
sudo chown -R netpulse:netpulse /var/lib/netpulse
sudo chown -R netpulse:netpulse /var/log/netpulse
sudo chown -R netpulse:netpulse /etc/netpulse

# 3. Set secure file permissions
sudo chmod 750 /var/lib/netpulse
sudo chmod 750 /var/log/netpulse
sudo chmod 750 /etc/netpulse
sudo chmod 640 /etc/netpulse/netpulse.conf

# 4. Generate secret key
python3 -c "
import secrets
print(f'NETPULSE_SECRET_KEY={secrets.token_hex(32)}')
" | sudo tee /etc/environment

# 5. Create database with secure permissions
sudo -u netpulse touch /var/lib/netpulse/netpulse.db
sudo chmod 600 /var/lib/netpulse/netpulse.db
```

## ⚙️ Configuration Security

### Environment Variables

Set secure environment variables:

```bash
# Secret key (required)
export NETPULSE_SECRET_KEY="your-256-bit-secret-key-here"

# Production mode (recommended)
export NETPULSE_TEST_MODE="false"

# Optional: Custom log level
export NETPULSE_LOG_LEVEL="INFO"
```

### Configuration File Security

Edit `/etc/netpulse/netpulse.conf`:

```ini
[web]
# Bind to localhost for security (change if remote access needed)
host = 127.0.0.1
port = 8080

# Use the generated secret key
secret_key = ${NETPULSE_SECRET_KEY}

[speedtest]
# Conservative interval for rate limiting
interval = 300
timeout = 60

[database]
# Secure database path
path = /var/lib/netpulse/netpulse.db

[logging]
# Secure logging configuration
file = /var/log/netpulse/netpulse.log
level = INFO
```

### Security Headers Configuration

Netpulse automatically configures security headers:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com 'unsafe-inline'; style-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Feature-Policy: geolocation 'none'; microphone 'none'; camera 'none'
```

## 🔍 Security Audit

### Running Security Audit

Netpulse includes an automated security audit tool:

```bash
# Run comprehensive security audit
python3 /usr/lib/python3/dist-packages/netpulse/security/security_check.py

# Check specific security areas
python3 /usr/lib/python3/dist-packages/netpulse/security/security_check.py --check permissions
python3 /usr/lib/python3/dist-packages/netpulse/security/security_check.py --check network
python3 /usr/lib/python3/dist-packages/netpulse/security/security_check.py --check dependencies
python3 /usr/lib/python3/dist-packages/netpulse/security/security_check.py --check services
```

### Audit Categories

#### 1. Secret Key Security
- ✅ Secret key exists
- ✅ Minimum length (32 characters)
- ✅ High entropy
- ✅ Not default value

#### 2. File Permissions
- ✅ Database: 600 (owner read/write only)
- ✅ Config: 640 (owner read/write, group read)
- ✅ Logs: 640 (owner read/write, group read)
- ✅ Directories: 750 (owner full, group/others read/execute)

#### 3. Network Security
- ✅ Service binding configuration
- ✅ Firewall recommendations
- ✅ SSL/TLS configuration
- ✅ Rate limiting status

#### 4. Dependency Security
- ✅ Known vulnerabilities scan
- ✅ Outdated packages check
- ✅ Security patches status

#### 5. Service Security
- ✅ Systemd service configuration
- ✅ Service user permissions
- ✅ Service isolation
- ✅ Resource limits

### Audit Results

The audit provides:
- **Overall Security Score**: 0-100 rating
- **Risk Assessment**: Critical/High/Medium/Low
- **Recommendations**: Actionable security improvements
- **Compliance Status**: OWASP alignment
- **Exit Codes**: 0 (OK), 1 (High), 2 (Critical)

## 🛡️ Security Best Practices

### Production Deployment

#### Network Security
```bash
# 1. Configure firewall
sudo ufw allow 8080/tcp
sudo ufw enable

# 2. Use reverse proxy (nginx example)
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # SSL configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
}
```

#### Monitoring and Logging
```bash
# 1. Monitor security logs
sudo tail -f /var/log/netpulse/netpulse.log | grep -i security

# 2. Monitor system logs
sudo journalctl -u netpulse-web -f

# 3. Set up log rotation
sudo tee /etc/logrotate.d/netpulse << EOF
/var/log/netpulse/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 640 netpulse netpulse
}
EOF
```

### Regular Security Tasks

#### Daily
```bash
# Run security audit
python3 /usr/lib/python3/dist-packages/netpulse/security/security_check.py

# Check for updates
sudo apt update && sudo apt list --upgradable

# Review security logs
sudo grep -i security /var/log/netpulse/netpulse.log
```

#### Weekly
```bash
# Dependency vulnerability scan
pip-audit

# File permission audit
find /var/lib/netpulse /etc/netpulse /var/log/netpulse -type f -exec ls -la {} \;

# Service status check
sudo systemctl status netpulse-web netpulse.timer
```

#### Monthly
```bash
# Comprehensive security review
python3 /usr/lib/python3/dist-packages/netpulse/security/security_check.py --full

# Update system packages
sudo apt update && sudo apt upgrade -y

# Review and rotate secrets
# Consider rotating secret key if compromised
```

## 🔧 Troubleshooting

### Common Security Issues

#### Secret Key Problems
```bash
# Error: No secret key configured
# Solution: Generate new secret key
python3 -c "import secrets; print(secrets.token_hex(32))" | sudo tee /etc/environment

# Reload service
sudo systemctl restart netpulse-web
```

#### Permission Issues
```bash
# Error: Permission denied
# Solution: Fix file permissions
sudo chown -R netpulse:netpulse /var/lib/netpulse
sudo chmod 600 /var/lib/netpulse/netpulse.db
sudo chmod 640 /etc/netpulse/netpulse.conf
```

#### Rate Limiting Issues
```bash
# Error: Rate limit exceeded
# Solution: Check rate limiting status
curl -I http://localhost:8080/api/test

# Adjust limits in configuration
sudo nano /etc/netpulse/netpulse.conf
```

### Security Log Analysis

```bash
# View security events
sudo grep -i security /var/log/netpulse/netpulse.log

# View blocked requests
sudo grep -i "blocked" /var/log/netpulse/netpulse.log

# View rate limiting events
sudo grep -i "rate" /var/log/netpulse/netpulse.log
```

## 📊 Security Metrics

### Monitoring Dashboard

Track these security metrics:

1. **Authentication Events**: Login attempts, failures
2. **Rate Limiting**: Blocked requests, limits hit
3. **Input Validation**: Rejected requests, sanitization
4. **Security Headers**: CSP violations, header issues
5. **System Access**: File access, permission changes

### Alert Thresholds

Set up alerts for:
- >10 failed authentication attempts/hour
- >100 rate limit blocks/hour
- Any security audit failures
- Unexpected file permission changes

## 🚨 Incident Response

### Security Incident Response

1. **Detection**: Monitor security logs and alerts
2. **Assessment**: Run security audit immediately
3. **Containment**: Isolate affected systems
4. **Eradication**: Patch vulnerabilities
5. **Recovery**: Restore secure configuration
6. **Lessons**: Document and improve procedures

### Emergency Procedures

```bash
# Immediate lockdown
sudo systemctl stop netpulse-web

# Backup data
sudo cp /var/lib/netpulse/netpulse.db /backup/

# Rotate secret key
python3 -c "import secrets; print(f'NETPULSE_SECRET_KEY={secrets.token_hex(32)}')" | sudo tee /etc/environment

# Restore service
sudo systemctl start netpulse-web
```

## 📞 Security Support

### Reporting Security Issues

For security vulnerabilities or concerns:

1. **Email**: axiomfield@gmail.com
2. **Encrypted Communication**: PGP Key available on request
3. **Private Disclosure**: We'll work with you on responsible disclosure

### Security Updates

- **Advisories**: Published on GitHub Security
- **Patches**: Released within 7 days for critical issues
- **Updates**: Available through package manager

---

## 📋 Security Checklist

### Pre-Deployment Checklist
- [ ] Secret key generated and configured
- [ ] File permissions set correctly
- [ ] Security audit passed
- [ ] Firewall configured
- [ ] SSL/TLS certificates installed
- [ ] Rate limiting tested
- [ ] Logging configured
- [ ] Monitoring set up

### Post-Deployment Checklist
- [ ] Security audit running
- [ ] Log monitoring active
- [ ] Alerts configured
- [ ] Backup procedures tested
- [ ] Incident response plan ready

---

**🛡️ Netpulse Security Implementation**

This document ensures Netpulse maintains enterprise-grade security standards while providing clear guidance for secure deployment and operation.

For questions or security concerns, contact: axiomfield@gmail.com

**Last Updated**: March 9, 2026
**Version**: 1.1.2
