"""
Pytest configuration and fixtures for Netpulse tests
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from netpulse.config import Config


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    from netpulse.database import Database
    
    # Create a temporary directory for database
    with tempfile.TemporaryDirectory() as temp_dir:
        test_db_path = os.path.join(temp_dir, 'test.db')
        
        # Create a fresh database instance with test path
        # Use the test_config to avoid config conflicts
        test_config = Config()
        test_config._config = {
            'database': {
                'path': test_db_path,
                'backup_enabled': False,
                'backup_interval_days': 7,
            }
        }
        
        with patch('netpulse.database.get_config', return_value=test_config):
            db = Database(test_db_path)
            db.ensure_database()
            
            # Add some test data
            from datetime import datetime
            test_measurements = [
                {
                    'timestamp': datetime.now().strftime('%Y-%m-%d 10:00:00'),
                    'download_speed': 50.5,
                    'upload_speed': 10.2,
                    'latency': 15.3,
                    'jitter': 2.1,
                    'packet_loss': 0.0,
                    'server_name': 'Test Server 1',
                    'test_type': 'bandwidth'
                },
                {
                    'timestamp': datetime.now().strftime('%Y-%m-%d 10:15:00'),
                    'download_speed': 48.2,
                    'upload_speed': 9.8,
                    'latency': 16.1,
                    'jitter': 2.3,
                    'packet_loss': 0.1,
                    'server_name': 'Test Server 2',
                    'test_type': 'bandwidth'
                },
                {
                    'timestamp': datetime.now().strftime('%Y-%m-%d 10:30:00'),
                    'download_speed': 0.0,
                    'upload_speed': 0.0,
                    'latency': 14.8,
                    'jitter': 1.9,
                    'packet_loss': 0.0,
                    'server_name': '8.8.8.8 (Google DNS)',
                    'test_type': 'latency'
                }
            ]
            
            for measurement in test_measurements:
                db.add_measurement(measurement)
            
            yield db


@pytest.fixture
def test_config():
    """Create a test configuration"""
    config = Config()
    config._config = {
        'database': {
            'path': ':memory:',  # In-memory database for testing
            'backup_enabled': True,
            'backup_interval_days': 7,
        },
        'measurement': {
            'interval_minutes': 15,
            'timeout_seconds': 30,
            'retry_count': 3,
            'servers': [],
        },
        'web': {
            'host': '127.0.0.1',
            'port': 8080,
            'debug': True,
            'secret_key': 'test-secret-key',
        },
        'logging': {
            'level': 'DEBUG',
            'file': '/tmp/test_netpulse.log',
            'max_size_mb': 1,
            'backup_count': 1,
        }
    }
    # Override config file location for tests
    config.config_file = '/tmp/test_netpulse.conf'
    return config


@pytest.fixture
def mock_librespeed_output():
    """Mock librespeed-cli JSON output - matches actual librespeed-cli format"""
    return [
        {
            'download': 48.0,  # Direct Mbps value
            'upload': 10.0,   # Direct Mbps value
            'ping': 15.5,     # Direct ms value
            'jitter': 2.1,    # Direct ms value
            'server': {
                'name': 'Test Server',
                'country': 'Germany'
            }
        }
    ]


@pytest.fixture
def mock_ping_output():
    """Mock ping command output"""
    return """PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=116 time=14.123 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=116 time=15.456 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=116 time=14.789 ms
64 bytes from 8.8.8.8: icmp_seq=4 ttl=116 time=15.234 ms

--- 8.8.8.8 ping statistics ---
4 packets transmitted, 4 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 14.123/14.900/15.456/0.567 ms"""


@pytest.fixture
def flask_app(test_config, temp_db):
    """Create Flask app for testing"""
    import os
    os.environ['NETPULSE_TEST_MODE'] = 'true'
    
    from netpulse.web import app
    
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Override both database and config for testing
    with patch('netpulse.web.get_database', return_value=temp_db):
        with patch('netpulse.web.get_config', return_value=test_config):
            with patch('netpulse.speedtest.get_config', return_value=test_config):
                with patch('netpulse.database.get_config', return_value=test_config):
                    with app.test_client() as client:
                        with app.app_context():
                            yield client


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls"""
    with patch('subprocess.run') as mock_run:
        yield mock_run
