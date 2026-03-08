#!/usr/bin/env python3
"""
Start script for Netpulse application
"""

import sys
import os

# Set up environment
sys.path.insert(0, '/app')

# Import and run the application
from netpulse.web import app
from netpulse.config import get_config

if __name__ == '__main__':
    # Get configuration
    config = get_config()
    
    # Get host and port from config
    host = config.get('web.host', '0.0.0.0')
    port = config.get('web.port', 8080)
    debug = config.get('web.debug', False)
    
    print(f"Starting Netpulse web server on {host}:{port}")
    
    # Run the Flask app
    app.run(host=host, port=port, debug=debug)
