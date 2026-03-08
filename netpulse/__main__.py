"""
Main entry point for Netpulse application
"""

import os
import sys

if __name__ == "__main__":
    # Import after setting up environment
    from netpulse.config import get_config
    from netpulse.web import app

    # Get configuration
    config = get_config()

    # Get host and port from config
    host = config.get("web.host", "0.0.0.0")
    port = config.get("web.port", 8080)
    debug = config.get("web.debug", False)

    print(f"Starting Netpulse web server on {host}:{port}")

    # Run the Flask app
    app.run(host=host, port=port, debug=debug)
