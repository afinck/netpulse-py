"""
Tests for database module
"""

import pytest
import sqlite3
from datetime import datetime, timedelta
from netpulse.database import Database


class TestDatabase:
    """Test database operations"""
    
    def test_ensure_database(self, temp_db):
        """Test database creation"""
        assert temp_db.db_path.endswith('.db')
        
        # Check if tables exist
        with sqlite3.connect(temp_db.db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='measurements'"
            )
            tables = cursor.fetchall()
            assert len(tables) == 1
            assert tables[0][0] == 'measurements'
    
    def test_add_measurement(self, temp_db):
        """Test adding a measurement"""
        measurement = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'download_speed': 100.5,
            'upload_speed': 50.2,
            'latency': 20.1,
            'jitter': 3.2,
            'packet_loss': 0.1,
            'server_name': 'Test Server',
            'test_type': 'bandwidth'
        }
        
        measurement_id = temp_db.add_measurement(measurement)
        assert measurement_id > 0
        
        # Verify measurement was added
        measurements = temp_db.get_measurements(limit=1)
        assert len(measurements) == 1
        assert measurements[0]['download_speed'] == 100.5
    
    def test_get_measurements(self, temp_db):
        """Test retrieving measurements"""
        measurements = temp_db.get_measurements()
        assert len(measurements) == 3  # From fixture
        
        # Test with limit
        limited = temp_db.get_measurements(limit=2)
        assert len(limited) == 2
    
    def test_get_measurements_by_period(self, temp_db):
        """Test getting measurements by time period"""
        # Test day period
        day_measurements = temp_db.get_measurements_by_period('day')
        assert len(day_measurements) == 3
        
        # Test week period
        week_measurements = temp_db.get_measurements_by_period('week')
        assert len(week_measurements) == 3
    
    def test_get_statistics(self, temp_db):
        """Test statistics calculation"""
        stats = temp_db.get_statistics('day')
        
        assert 'count' in stats
        assert 'download_speed' in stats
        assert 'upload_speed' in stats
        assert 'latency' in stats
        
        assert stats['count'] == 3
        assert stats['download_speed']['min'] > 0
        assert stats['download_speed']['max'] > 0
        assert stats['download_speed']['avg'] > 0
    
    def test_cleanup_old_data(self, temp_db):
        """Test cleanup of old data"""
        # Add old measurement
        old_timestamp = (datetime.now() - timedelta(days=40)).strftime('%Y-%m-%d %H:%M:%S')
        old_measurement = {
            'timestamp': old_timestamp,
            'download_speed': 10.0,
            'upload_speed': 5.0,
            'latency': 30.0,
            'test_type': 'bandwidth'
        }
        temp_db.add_measurement(old_measurement)
        
        # Should have 4 measurements now
        all_measurements = temp_db.get_measurements()
        assert len(all_measurements) == 4
        
        # Cleanup data older than 30 days
        deleted_count = temp_db.cleanup_old_data(30)
        assert deleted_count == 1
        
        # Should have 3 measurements now
        remaining = temp_db.get_measurements()
        assert len(remaining) == 3
    
    def test_export_to_csv(self, temp_db):
        """Test CSV export"""
        import csv
        import os
        
        filename = '/tmp/test_export.csv'
        temp_db.export_to_csv(filename)
        
        assert os.path.exists(filename)
        
        # Check CSV content
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 3
            
            # Check headers
            expected_headers = ['timestamp', 'download_speed', 'upload_speed', 
                              'latency', 'jitter', 'packet_loss', 'server_name', 'test_type']
            assert reader.fieldnames == expected_headers
        
        # Cleanup
        os.unlink(filename)
    
    def test_get_latest_measurements(self, temp_db):
        """Test getting latest measurements"""
        latest = temp_db.get_latest_measurements(2)
        assert len(latest) == 2
        
        # Should be ordered by timestamp (newest first)
        assert latest[0]['timestamp'] >= latest[1]['timestamp']
    
    def test_get_measurements_with_filters(self, temp_db):
        """Test getting measurements with filters"""
        # Filter by test type
        bandwidth_tests = temp_db.get_measurements(test_type='bandwidth')
        assert len(bandwidth_tests) == 2
        
        latency_tests = temp_db.get_measurements(test_type='latency')
        assert len(latency_tests) == 1
        
        # Filter by date range (use current year)
        from datetime import datetime
        current_year = datetime.now().year
        start_date = f'{current_year}-01-01 10:00:00'
        end_date = f'{current_year}-12-31 23:59:59'
        filtered = temp_db.get_measurements(start_date=start_date, end_date=end_date)
        assert len(filtered) >= 2  # Should find our test data
