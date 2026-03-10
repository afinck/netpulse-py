"""
Web interface for Netpulse
"""

import logging
# Configure logging
import os
from datetime import datetime

from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   send_file, session)
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_babel import Babel, gettext as _
from flask_session import Session

from .config import get_config
from .database import get_database
from .speedtest import SpeedtestRunner
from . import __version__
from .i18n import babel, get_locale

if os.getenv("NETPULSE_TEST_MODE"):
    # Use simple logging for tests
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
else:
    # Configure logging
    config = get_config()
    log_file = config.get("logging.file", "/var/log/netpulse/netpulse.log")
    
    # Create log directory if it doesn't exist
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    except (PermissionError, OSError):
        # Fallback to /tmp if we can't create the log directory
        import tempfile
        temp_dir = tempfile.gettempdir()
        log_file = os.path.join(temp_dir, "netpulse.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
    )

    logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Initialize i18n
app.config['BABEL_TRANSLATION_DIRECTORIES'] = '/usr/lib/python3/dist-packages/netpulse/translations'
babel.init_app(app)

# Initialize config
config = get_config()
app.secret_key = config.get("web.secret_key", "change-me-in-production")

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = '/tmp/netpulse_sessions'

# Initialize session
sess = Session(app)

# Security headers and CSP
if not os.getenv("NETPULSE_TEST_MODE"):
    # Enable security headers in production
    csp = {
        'default-src': '\'self\'',
        'script-src': [
            '\'self\'',
            'https://cdn.jsdelivr.net',
            'https://cdnjs.cloudflare.com',
            '\'unsafe-inline\''
        ],
        'style-src': [
            '\'self\'',
            'https://cdn.jsdelivr.net',
            'https://cdnjs.cloudflare.com',
            '\'unsafe-inline\''
        ],
        'img-src': [
            '\'self\'',
            'data:'
        ],
        'connect-src': [
            '\'self\'',
            'https://cdn.jsdelivr.net',
            'https://cdnjs.cloudflare.com'
        ],
        'font-src': [
            '\'self\'',
            'https://cdn.jsdelivr.net'
        ],
        'object-src': '\'none\'',
        'media-src': '\'self\'',
        'frame-src': '\'none\''
    }
    
    Talisman(app, 
             force_https=os.getenv("FORCE_HTTPS", "false").lower() == "true",
             strict_transport_security=True,
             content_security_policy=csp,
             referrer_policy='strict-origin-when-cross-origin',
             feature_policy={
                 'geolocation': '\'none\'',
                 'camera': '\'none\'',
                 'microphone': '\'none\''
             })

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "500 per hour"]  # Increased from 200/50
)

# Ensure necessary directories exist (only in production)
if not os.getenv("NETPULSE_TEST_MODE"):
    try:
        config.ensure_directories()
    except (PermissionError, OSError):
        # Skip directory creation in environments where we don't have permissions
        pass


@app.context_processor
def inject_locale():
    """Inject locale functions into templates"""
    return dict(get_locale=get_locale)


@app.route("/test")
def test():
    """Test route for debugging"""
    from flask_babel import gettext as _
    return {
        'locale': get_locale(),
        'session_language': session.get('language'),
        'url_lang': request.args.get('lang'),
        'accept_languages': str(request.accept_languages),
        'test_translation': _('Network Dashboard'),
        'test_german': _('Period Selection')
    }


@app.route("/")
@limiter.limit("5000 per hour")  # Massive increase for auto-refresh
def dashboard():
    """Main dashboard page"""
    try:
        db = get_database()

        # Get latest measurements
        latest_measurements = db.get_latest_measurements(1)
        latest = latest_measurements[0] if latest_measurements else None

        # Convert timestamp string to datetime object if latest exists
        if latest and "timestamp" in latest:
            try:
                latest["timestamp"] = datetime.strptime(latest["timestamp"], "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError) as e:
                logger.error(f"Error parsing timestamp: {e}")
                latest = None

        # Get today's statistics
        today_stats = db.get_statistics("day")

        # Get current period statistics (default to day)
        period = request.args.get("period", "day")
        stats = db.get_statistics(period)

        return render_template(
            "dashboard.html",
            latest=latest,
            today_stats=today_stats,
            stats=stats,
            period=period,
            version=__version__,
        )

    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        flash(f"Fehler beim Laden des Dashboards: {e}", "error")
        return render_template(
            "dashboard.html", latest=None, today_stats={}, stats={}, period="day", version=__version__
        )


@app.route("/history")
@limiter.limit("2000 per hour")  # Massive increase for auto-refresh
def history():
    """History page with all measurements"""
    try:
        db = get_database()

        # Get filter parameters
        period = request.args.get("period", "")
        test_type = request.args.get("test_type", "")
        limit = int(request.args.get("limit", 50))

        # Get measurements
        if period:
            measurements = db.get_measurements_by_period(period)
        else:
            measurements = db.get_measurements(test_type=test_type, limit=limit)

        # Filter by test type if specified
        if test_type and period:
            measurements = [m for m in measurements if m["test_type"] == test_type]

        # Limit results
        measurements = measurements[:limit]

        # Convert timestamp strings to datetime objects
        for measurement in measurements:
            if "timestamp" in measurement and isinstance(measurement["timestamp"], str):
                try:
                    measurement["timestamp"] = datetime.strptime(
                        measurement["timestamp"], "%Y-%m-%d %H:%M:%S"
                    )
                except (ValueError, TypeError) as e:
                    logger.error(f"Error parsing timestamp: {e}")
                    # Keep as string if parsing fails

        return render_template(
            "history.html",
            measurements=measurements,
            period=period,
            test_type=test_type,
            limit=limit,
            version=__version__,
        )

    except Exception as e:
        logger.error(f"Error loading history: {e}")
        flash(f"Fehler beim Laden des Verlaufs: {e}", "error")
        return render_template(
            "history.html", measurements=[], period="", test_type="", limit=50, version=__version__
        )


@app.route("/export")
@limiter.limit("1000 per hour")  # Massive increase for auto-refresh
def export():
    """Export page"""
    return render_template("export.html", version=__version__)


@app.route("/settings")
@limiter.limit("1000 per hour")  # Massive increase for auto-refresh
def settings():
    """Settings page"""
    return render_template("settings.html", version=__version__)


@app.route("/export/csv")
def export_csv():
    """Export measurements as CSV"""
    temp_filename = None
    try:
        db = get_database()

        # Get filter parameters
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_filename = f"{temp_dir}/netpulse_export_{timestamp}.csv"

        # Export data
        db.export_to_csv(temp_filename, start_date, end_date)

        # Send file and cleanup
        def remove_file(response):
            try:
                import os
                if temp_filename and os.path.exists(temp_filename):
                    os.unlink(temp_filename)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_filename}: {e}")
            return response

        response = send_file(
            temp_filename,
            as_attachment=True,
            download_name=f"netpulse_export_{timestamp}.csv",
        )
        response.call_on_close(lambda: remove_file(response))
        return response

    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        # Cleanup on error
        if temp_filename:
            try:
                import os
                if os.path.exists(temp_filename):
                    os.unlink(temp_filename)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file on error: {cleanup_error}")
        flash(f"Fehler beim Exportieren: {e}", "error")
        return redirect("/export")


@app.route("/api/data")
def api_data():
    """API endpoint for chart data"""
    try:
        db = get_database()

        period = request.args.get("period", "day")
        measurements = db.get_measurements_by_period(period)

        # Prepare data for charts
        labels = []
        download_speeds = []
        upload_speeds = []
        latencies = []

        for measurement in measurements:
            # Format timestamp for display
            timestamp = datetime.strptime(measurement["timestamp"], "%Y-%m-%d %H:%M:%S")

            if period == "day":
                labels.append(timestamp.strftime("%H:%M"))
            elif period == "week":
                labels.append(timestamp.strftime("%a %H:%M"))
            elif period == "month":
                labels.append(timestamp.strftime("%d.%m"))
            elif period == "year":
                labels.append(timestamp.strftime("%d.%m"))

            download_speeds.append(measurement["download_speed"] or 0)
            upload_speeds.append(measurement.get("upload_speed", 0) or 0)
            latencies.append(measurement["latency"] or 0)

        return jsonify(
            {
                "labels": labels,
                "download_speeds": download_speeds,
                "upload_speeds": upload_speeds,
                "latencies": latencies,
            }
        )

    except Exception as e:
        logger.error(f"Error getting API data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/test", methods=["POST"])
@limiter.limit("10 per minute")
def api_test():
    """API endpoint to run a test"""
    try:
        # Validate content type
        if not request.is_json:
            logger.warning(f"Invalid content type for test API from {get_remote_address()}")
            return jsonify({"error": "JSON content type required"}), 400

        test_type = request.json.get("type", "bandwidth")
        
        # Input validation
        if not isinstance(test_type, str) or test_type not in ["bandwidth", "latency"]:
            logger.warning(f"Invalid test type '{test_type}' from {get_remote_address()}")
            return jsonify({"error": "Invalid test type. Must be 'bandwidth' or 'latency'"}), 400

        logger.info(f"Running {test_type} test from {get_remote_address()}")
        runner = SpeedtestRunner()
        success = runner.run_measurement(test_type)

        if success:
            return jsonify(
                {"success": True, "message": "Test erfolgreich durchgeführt"}
            )
        else:
            return jsonify({"success": False, "error": "Test fehlgeschlagen"})

    except Exception as e:
        logger.error(f"Error running test from {get_remote_address()}: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@app.route("/api/stats")
@limiter.limit("100 per hour")
def api_stats():
    """API endpoint for statistics"""
    try:
        # Input validation for period parameter
        period = request.args.get("period", "day")
        valid_periods = ["day", "week", "month", "year"]
        
        if period not in valid_periods:
            logger.warning(f"Invalid period '{period}' requested from {get_remote_address()}")
            return jsonify({"error": f"Invalid period. Must be one of: {', '.join(valid_periods)}"}), 400
        
        db = get_database()
        stats = db.get_statistics(period)
        return jsonify(stats)

    except Exception as e:
        logger.error(f"Error getting stats from {get_remote_address()}: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/health")
def api_health():
    """Health check endpoint"""
    try:
        # Get database for this request
        db = get_database()

        # Check database connection
        latest = db.get_latest_measurements(1)

        return jsonify(
            {
                "status": "healthy",
                "database": "connected",
                "latest_measurement": len(latest) > 0,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@app.route("/api/config", methods=["GET"])
def api_config_get():
    """API endpoint to get current configuration"""
    try:
        config = get_config()

        # Return only the configuration settings that should be editable via web interface
        return jsonify(
            {
                "measurement": {
                    "interval_minutes": config.get("measurement.interval_minutes", 15),
                    "timeout_seconds": config.get("measurement.timeout_seconds", 30),
                    "retry_count": config.get("measurement.retry_count", 3),
                }
            }
        )

    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/config", methods=["POST"])
@limiter.limit("20 per hour")
def api_config_set():
    """API endpoint to update configuration"""
    try:
        # Validate content type
        if not request.is_json:
            logger.warning(f"Invalid content type for config API from {get_remote_address()}")
            return jsonify({"error": "JSON data required"}), 400

        data = request.get_json()
        if not isinstance(data, dict):
            logger.warning(f"Invalid JSON format from {get_remote_address()}")
            return jsonify({"error": "Invalid JSON format - object required"}), 400
        
        config = get_config()
        old_interval = config.get("measurement.interval_minutes", 15)
        new_interval = old_interval

        # Update measurement interval if provided
        if "measurement" in data:
            measurement_config = data["measurement"]
            if not isinstance(measurement_config, dict):
                logger.warning(f"Invalid measurement config from {get_remote_address()}")
                return jsonify({"error": "measurement section must be an object"}), 400
                
            if "interval_minutes" in measurement_config:
                new_interval = measurement_config["interval_minutes"]
                if (
                    not isinstance(new_interval, int)
                    or new_interval < 1
                    or new_interval > 1440
                ):
                    logger.warning(f"Invalid interval {new_interval} from {get_remote_address()}")
                    return (
                        jsonify(
                            {
                                "error": "interval_minutes must be an integer between 1 and 1440"
                            }
                        ),
                        400,
                    )
                config.set("measurement.interval_minutes", new_interval)
                logger.info(f"Interval changed from {old_interval} to {new_interval} by {get_remote_address()}")

            if "timeout_seconds" in measurement_config:
                timeout = measurement_config["timeout_seconds"]
                if not isinstance(timeout, int) or timeout < 5 or timeout > 300:
                    logger.warning(f"Invalid timeout {timeout} from {get_remote_address()}")
                    return (
                        jsonify(
                            {
                                "error": "timeout_seconds must be an integer between 5 and 300"
                            }
                        ),
                        400,
                    )
                config.set("measurement.timeout_seconds", timeout)
                logger.info(f"Timeout changed to {timeout} by {get_remote_address()}")

            if "retry_count" in measurement_config:
                retry = measurement_config["retry_count"]
                if not isinstance(retry, int) or retry < 1 or retry > 10:
                    logger.warning(f"Invalid retry count {retry} from {get_remote_address()}")
                    return (
                        jsonify({"error": "retry_count must be an integer between 1 and 10"}),
                        400,
                    )
                config.set("measurement.retry_count", retry)
                logger.info(f"Retry count changed to {retry} by {get_remote_address()}")

        # Save configuration
        if config.save():
            logger.info("Configuration updated successfully")

            # If interval changed, try to update systemd timer
            if old_interval != new_interval:
                try:
                    update_systemd_timer(new_interval)
                    return jsonify(
                        {
                            "success": True,
                            "message": (
                                f"Konfiguration erfolgreich gespeichert. "
                                f"Timer auf {new_interval} Minuten aktualisiert."
                            ),
                        }
                    )
                except Exception as timer_error:
                    logger.warning(f"Failed to update systemd timer: {timer_error}")
                    return jsonify(
                        {
                            "success": True,
                            "message": (
                                "Konfiguration gespeichert. "
                                "Timer-Update fehlgeschlagen - manueller Neustart erforderlich: "
                                "sudo systemctl restart netpulse.timer"
                            ),
                        }
                    )
            else:
                return jsonify(
                    {
                        "success": True,
                        "message": "Konfiguration erfolgreich gespeichert",
                    }
                )
        else:
            logger.error("Failed to save configuration")
            return jsonify({"error": "Failed to save configuration"}), 500

    except Exception as e:
        logger.error(f"Error updating config from {get_remote_address()}: {e}")
        return jsonify({"error": "Internal server error"}), 500


def update_systemd_timer(interval_minutes):
    """Update systemd timer configuration using helper script"""
    import subprocess

    logger.info(f"Updating systemd timer to {interval_minutes} minutes")

    try:
        # Use helper script with sudo
        result = subprocess.run(
            ["sudo", "/usr/lib/netpulse/netpulse-timer-helper.sh", str(interval_minutes)],
            check=True,
            capture_output=True,
            text=True,
            shell=False
        )
        
        logger.info(f"Timer update successful: {result.stdout}")
        logger.info(f"SystemD timer updated to run every {interval_minutes} minutes")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to update systemd timer: {e}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Failed to update systemd timer: {e}")
        return False


def main():
    """Main entry point for the web server"""
    host = config.get("web.host", "0.0.0.0")
    port = config.get("web.port", 8080)
    debug = config.get("web.debug", False)

    logger.info(f"Starting Netpulse web server on {host}:{port}")

    try:
        app.run(host=host, port=port, debug=debug, load_dotenv=False)
    except KeyboardInterrupt:
        logger.info("Web server stopped by user")
    except Exception as e:
        logger.error(f"Web server error: {e}")
        raise


if __name__ == "__main__":
    main()
