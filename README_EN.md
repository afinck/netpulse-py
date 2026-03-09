# Netpulse - Network Monitoring Tool

<div align="center">

![Netpulse Logo](https://github.com/afinck/netpulse-py/raw/main/static/img/netpulse-logo.png)

**Professional Network Monitoring Tool with Enterprise-Grade Security**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Security](https://img.shields.io/badge/security-OWASP%20Top%2010-green.svg)](SECURITY_INSTALLATION.md)
[![Build Status](https://github.com/afinck/netpulse-py/workflows/Test/badge.svg)](https://github.com/afinck/netpulse-py/actions)

</div>

## 🌟 Features

### 🛡️ Security-First Design (OWASP Top 10 2021)
- **Security Headers**: CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- **Rate Limiting**: API endpoints with different limits (Test: 10/min, Config: 20/hour)
- **Input Validation**: Strict validation against injection attacks
- **Security Logging**: IP tracking and event monitoring
- **Secret Management**: Automatic secure secret key generation
- **File Permissions**: Secure permissions (Database: 600, Config: 640)
- **Security Audit Tool**: Automated vulnerability scanning

### 📱 Mobile-First Design
- **Responsive Layout**: Optimized for all screen sizes
- **Theme Persistence**: Dark/Light mode with localStorage persistence
- **Glassmorphism Footer**: Modern gradient design with blur effects
- **Statistics Icons**: Icons and abbreviations for mobile readability
- **Touch-Friendly**: Optimized for mobile interaction

### 📊 Network Monitoring
- **Real-time Charts**: Bandwidth and latency visualization with Chart.js
- **Historical Data**: SQLite database with rolling time periods
- **Automated Measurements**: SystemD timer for reliable testing
- **Multiple Test Servers**: Configurable LibreSpeed servers
- **Export Functionality**: CSV and JSON data export

### 🔧 Technical Excellence
- **Multi-Language Support**: English/German with Flask-Babel
- **Cross-Platform**: ARM64 and AMD64 support
- **Modern Tech Stack**: Flask 2.2+, Bootstrap 5.3, Chart.js 4.5
- **CI/CD Pipeline**: Automated testing and releases
- **Package Management**: DEB package with dependencies

## 🚀 Quick Start

### Installation

#### Option 1: Download DEB Package (Recommended)

```bash
# Download the latest release for your architecture
wget https://github.com/afinck/netpulse-py/releases/latest/download/netpulse_v1.1.2_arm64.deb  # ARM64 (Raspberry Pi)
# or
wget https://github.com/afinck/netpulse-py/releases/latest/download/netpulse_v1.1.2_amd64.deb  # AMD64 (Desktop/Server)

# Install the package
sudo dpkg -i netpulse_v1.1.2_*.deb
sudo apt-get install -f  # Install dependencies if needed

# Security hardening is automatic
sudo systemctl enable --now netpulse-web
sudo systemctl enable --now netpulse.timer
```

#### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/afinck/netpulse-py.git
cd netpulse-py

# Install dependencies
sudo apt-get install python3 python3-pip python3-flask python3-click python3-jinja2 python3-werkzeug
pip3 install -r requirements.txt

# Install the package
sudo python3 setup.py install

# Set up systemd services
sudo cp systemd/*.service /lib/systemd/system/
sudo cp systemd/*.timer /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now netpulse-web
sudo systemctl enable --now netpulse.timer
```

### Access

Open your browser and navigate to:
- **Local**: `http://localhost:8080`
- **Remote**: `http://your-raspberry-pi-ip:8080`

## 📊 Usage

### Dashboard
- **Real-time Charts**: View bandwidth and latency trends
- **Time Periods**: Switch between Day/Week/Month/Year views
- **Statistics**: See average speeds and measurement counts
- **Language Switch**: Toggle between English and German

### Configuration
- **Measurement Interval**: Set automatic testing frequency
- **Test Servers**: Choose specific LibreSpeed servers
- **Security Settings**: Configure rate limits and logging

### Data Management
- **History View**: Browse all historical measurements
- **Export Data**: Download as CSV or JSON
- **Security Audit**: Run automated security checks

## 🛡️ Security

Netpulse implements comprehensive security measures based on OWASP Top 10 2021:

### Security Features
- **Content Security Policy**: Prevents XSS and injection attacks
- **HTTP Security Headers**: HSTS, X-Frame-Options, etc.
- **Rate Limiting**: Protects against API abuse
- **Input Validation**: Strict type checking and sanitization
- **Secure File Permissions**: Database (600), Config (640), Logs (640)
- **Security Logging**: IP tracking and event monitoring
- **Automated Auditing**: Vulnerability scanning and reporting

### Security Audit
```bash
# Run comprehensive security audit
python3 /usr/lib/python3/dist-packages/netpulse/security/security_check.py

# Check specific areas
python3 /usr/lib/python3/dist-packages/netpulse/security/security_check.py --check permissions
python3 /usr/lib/python3/dist-packages/netpulse/security/security_check.py --check network
```

For detailed security information, see [SECURITY_INSTALLATION.md](SECURITY_INSTALLATION.md).

## 🔧 Configuration

### Environment Variables
```bash
export NETPULSE_SECRET_KEY="your-secret-key-here"
export NETPULSE_TEST_MODE="false"  # Set to "true" for development
```

### Configuration File
Edit `/etc/netpulse/netpulse.conf`:
```ini
[web]
host = 0.0.0.0
port = 8080
secret_key = your-secret-key-here

[speedtest]
interval = 300  # seconds
timeout = 60
servers = 1,2,3  # LibreSpeed server IDs

[database]
path = /var/lib/netpulse/netpulse.db

[logging]
file = /var/log/netpulse/netpulse.log
level = INFO
```

## 🌍 Internationalization

Netpulse supports multiple languages:

### Available Languages
- **English (en)**: Default language
- **German (de)**: Full German translation

### Language Switching
- **Browser Detection**: Automatically detects browser language preference
- **Manual Switch**: Language dropdown in navigation bar
- **Persistent**: Remembers user preference in localStorage
- **URL Parameter**: `?lang=en` or `?lang=de`

### Adding New Languages
```bash
# Extract translatable strings
cd netpulse/translations
pybabel extract -F babel.cfg -o messages.pot ..

# Create new language
pybabel init -i messages.pot -d fr/LC_MESSAGES -l fr  # French example

# Compile translations
pybabel compile -d fr/LC_MESSAGES -i fr/LC_MESSAGES/messages.po
```

## 📱 Mobile Support

Netpulse is optimized for mobile devices:

### Mobile Features
- **Responsive Design**: Adapts to all screen sizes
- **Touch Interface**: Optimized for touch interaction
- **Mobile Statistics**: Compact display with icons
- **Mobile Navigation**: Hamburger menu for small screens
- **Mobile Charts**: Responsive chart sizing

### Mobile Testing
Tested on:
- **iOS Safari**: iPhone 12+
- **Android Chrome**: Android 8+
- **Mobile Firefox**: All versions

## 🔧 Development

### Requirements
- Python 3.8+
- Flask 2.2+
- Bootstrap 5.3+
- Chart.js 4.5+
- LibreSpeed CLI

### Development Setup
```bash
# Clone repository
git clone https://github.com/afinck/netpulse-py.git
cd netpulse-py

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python3 -m netpulse
```

### Testing
```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=netpulse tests/

# Run specific test
pytest tests/test_web.py
```

### Building DEB Package
```bash
# Build for current architecture
./build.sh

# Cross-compile for ARM64
docker buildx build --platform linux/arm64 -t netpulse-builder .
docker run --rm -v $(pwd):/app netpulse-builder ./build.sh
```

## 📊 API Reference

### Endpoints

#### GET `/api/data`
Returns measurement data for charts.

**Parameters:**
- `period` (string): `day`, `week`, `month`, `year`

**Response:**
```json
{
  "labels": ["12:00", "12:15", ...],
  "download_speeds": [250.5, 280.2, ...],
  "upload_speeds": [100.3, 110.7, ...],
  "latencies": [15.2, 12.8, ...]
}
```

#### GET `/api/stats`
Returns summary statistics.

**Response:**
```json
{
  "total_measurements": 150,
  "avg_download": 275.4,
  "avg_upload": 105.2,
  "avg_latency": 14.7,
  "last_measurement": "2026-03-09 15:30:00"
}
```

#### POST `/api/test`
Triggers a new measurement.

**Rate Limiting:** 10 requests per minute

#### POST `/api/config`
Updates configuration.

**Rate Limiting:** 20 requests per hour

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to fork: `git push origin feature/amazing-feature`
5. Create Pull Request

### Code Style
- Follow PEP 8
- Use type hints
- Add tests for new features
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LibreSpeed**: For speed testing infrastructure
- **Flask**: Web framework
- **Bootstrap**: UI framework
- **Chart.js**: Data visualization
- **Bootstrap Icons**: Icon library

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/afinck/netpulse-py/issues)
- **Security**: Report security issues to axiomfield@gmail.com
- **Documentation**: [Wiki](https://github.com/afinck/netpulse-py/wiki)

---

<div align="center">

**🛡️ Enterprise-Grade Security | 📱 Mobile-First Design | 🌍 Multi-Language Support**

Made with ❤️ by [Andreas Finck](https://github.com/afinck)

</div>
