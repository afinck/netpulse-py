# Netpulse Security Installation Guide

## Overview

Netpulse includes comprehensive security features that are automatically enabled after installation. This guide explains what security measures are implemented and how they work on different systems.

## 🔧 Automated Security Features (Code-Level)

These security features are automatically active after installation on any system:

### 1. Security Headers & CSP
- **Content Security Policy (CSP)**: Prevents XSS attacks
- **HTTP Strict Transport Security (HSTS)**: Enforces HTTPS
- **X-Frame-Options**: Prevents clickjacking
- **X-Content-Type-Options**: Prevents MIME-type sniffing
- **Feature Policy**: Restricts access to camera, microphone, geolocation

### 2. Rate Limiting
- **API Endpoints**: Protected against abuse
- **Different limits per endpoint**:
  - Test API: 10 requests per minute
  - Stats API: 100 requests per hour
  - Config API: 20 requests per hour
  - Health API: 1000 requests per hour

### 3. Input Validation
- **Strict parameter validation** for all API endpoints
- **Type checking** and range validation
- **Enum validation** for allowed values
- **Sanitized error messages** (no sensitive data exposure)

### 4. Security Logging
- **Enhanced logging** with IP addresses
- **Security event tracking**
- **Sanitized log messages** (passwords/secrets removed)

### 5. Security Audit Tool
- **Automated security scanning**
- **Vulnerability detection**
- **Configuration validation**
- **Permission checking**

## ⚙️ System-Level Security (Automated)

These security measures are automatically configured during package installation:

### 1. Secret Key Generation
- **Automatic generation** of cryptographically secure secret key
- **Stored in** `/etc/environment` for persistence
- **Unique per system** for maximum security

### 2. File Permissions
- **Database**: `600` (owner read/write only)
- **Configuration**: `640` (owner + group read)
- **Log files**: `640` (owner + group read)
- **Directories**: `750` (owner + group access)

### 3. Post-Installation Security Audit
- **Automatic security scan** after installation
- **Vulnerability report** with recommendations
- **Permission validation** and fixes

## 🚀 Installation Security Process

### Automatic Security Setup
When you install Netpulse with `dpkg -i netpulse_*.deb`, the following happens automatically:

1. **Package installation** with security dependencies
2. **Secret key generation** and configuration
3. **File permission hardening**
4. **Security audit execution**
5. **Service restart** with security features enabled

### Manual Security Setup (if needed)
If automatic setup fails, you can manually configure security:

```bash
# 1. Set secure secret key
export NETPULSE_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "NETPULSE_SECRET_KEY=$NETPULSE_SECRET_KEY" | sudo tee -a /etc/environment

# 2. Set file permissions
sudo chmod 600 /var/lib/netpulse/netpulse.db
sudo chmod 640 /etc/netpulse/netpulse.conf /var/log/netpulse/netpulse.log
sudo chmod 750 /var/lib/netpulse/ /var/log/netpulse/

# 3. Install security dependencies
sudo pip3 install Flask-Talisman Flask-Limiter psutil pip-audit --break-system-packages

# 4. Run security audit
python3 /usr/lib/python3/dist-packages/netpulse/security/security_check.py
```

## 🔍 Security Verification

### Check Security Headers
```bash
curl -I http://localhost:8080/
```
Look for security headers like:
- `Content-Security-Policy`
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`

### Test Input Validation
```bash
# Test invalid input (should be rejected)
curl -s -X POST -H "Content-Type: application/json" \
     -d '{"measurement": {"interval_minutes": 2000}}' \
     http://localhost:8080/api/config

# Test rate limiting (should be limited after repeated requests)
for i in {1..15}; do
    curl -s -X POST http://localhost:8080/api/test
done
```

### Run Security Audit
```bash
python3 /usr/lib/python3/dist-packages/netpulse/security/security_check.py
```

## 🛡️ Security Best Practices

### Production Deployment
1. **Use HTTPS** with reverse proxy (nginx/apache)
2. **Firewall configuration** to restrict access
3. **Regular updates** of system packages
4. **Monitor security logs** for suspicious activity
5. **Regular security audits** with the provided tool

### Network Security
1. **Bind to specific interfaces** instead of 0.0.0.0
2. **Use VPN or SSH tunnel** for remote access
3. **Implement fail2ban** for brute force protection
4. **Network segmentation** if possible

### Ongoing Security
1. **Weekly security audits** with the provided tool
2. **Monthly dependency updates** with pip-audit
3. **Log monitoring** for security events
4. **Backup security** (encrypted backups)

## 📋 Security Checklist

### Before Production Use
- [ ] Secret key is set and secure
- [ ] File permissions are correct
- [ ] Security headers are active
- [ ] Rate limiting is working
- [ ] Input validation is active
- [ ] Security audit passes
- [ ] HTTPS is configured
- [ ] Firewall is configured
- [ ] Log monitoring is set up
- [ ] Backup strategy is in place

### After Installation
- [ ] Run security audit: `python3 /path/to/security_check.py`
- [ ] Verify security headers: `curl -I http://localhost:8080/`
- [ ] Test input validation with invalid data
- [ ] Check file permissions: `ls -la /var/lib/netpulse/ /etc/netpulse/`
- [ ] Verify secret key: `echo $NETPULSE_SECRET_KEY`

## 🚨 Security Response

### If Security Issues Are Found
1. **Immediate action**: Block access if critical
2. **Audit logs**: Check for exploitation
3. **Update system**: Apply security patches
4. **Change secrets**: Regenerate secret key if compromised
5. **Monitor**: Watch for suspicious activity
6. **Report**: Document incident and response

### Security Incident Response
1. **Isolate**: Disconnect from network if needed
2. **Assess**: Run security audit and check logs
3. **Contain**: Change passwords and secrets
4. **Eradicate**: Remove malware/vulnerabilities
5. **Recover**: Restore from clean backup
6. **Learn**: Update security measures

---

**Note**: This security implementation follows OWASP Top 10 2021 guidelines and industry best practices. Regular security audits and updates are recommended for optimal protection.
