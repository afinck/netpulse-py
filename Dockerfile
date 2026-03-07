FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    librespeed-cli \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the application
RUN pip install -e .

# Create netpulse user
RUN useradd --system --home /var/lib/netpulse --shell /usr/sbin/nologin netpulse

# Create necessary directories
RUN mkdir -p /var/lib/netpulse /var/log/netpulse /etc/netpulse && \
    chown -R netpulse:netpulse /var/lib/netpulse /var/log/netpulse

# Copy configuration
COPY config/default.conf /etc/netpulse/netpulse.conf

# Copy start script
COPY start_app.py /app/start_app.py
RUN chmod +x /app/start_app.py

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Run as netpulse user
USER netpulse

# Default command
CMD ["python", "-m", "netpulse.web"]
