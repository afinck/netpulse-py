"""
Tests for web interface
"""

import pytest
import json
import os
from unittest.mock import patch, Mock

# Set test mode before importing app
os.environ['NETPULSE_TEST_MODE'] = 'true'
from netpulse.web import app


class TestWebInterface:
    """Test web interface endpoints"""
    
    def test_dashboard_page(self, flask_app, temp_db):
        """Test dashboard page loads"""
        response = flask_app.get('/')
        assert response.status_code == 200
        assert b'Netpulse' in response.data
        assert b'Dashboard' in response.data
    
    def test_history_page(self, flask_app, temp_db):
        """Test history page loads"""
        response = flask_app.get('/history')
        assert response.status_code == 200
        assert b'Verlauf' in response.data
        assert b'Messungen' in response.data
    
    def test_export_page(self, flask_app):
        """Test export page loads"""
        response = flask_app.get('/export')
        assert response.status_code == 200
        assert b'Export' in response.data
    
    def test_settings_page(self, flask_app):
        """Test settings page loads"""
        response = flask_app.get('/settings')
        assert response.status_code == 200
        assert b'Einstellungen' in response.data
        assert b'Messintervall' in response.data
    
    def test_api_config_get(self, flask_app):
        """Test API config GET endpoint"""
        response = flask_app.get('/api/config')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'measurement' in data
        assert 'interval_minutes' in data['measurement']
        assert 'timeout_seconds' in data['measurement']
        assert 'retry_count' in data['measurement']
    
    def test_api_config_post_valid(self, flask_app):
        """Test API config POST endpoint with valid data"""
        config_data = {
            'measurement': {
                'interval_minutes': 30,
                'timeout_seconds': 60,
                'retry_count': 5
            }
        }
        
        response = flask_app.post('/api/config',
                                 json=config_data,
                                 content_type='application/json')
        assert response.status_code == 200
        
        result = json.loads(response.data)
        assert result['success'] == True
    
    def test_api_config_post_invalid(self, flask_app):
        """Test API config POST endpoint with invalid data"""
        config_data = {
            'measurement': {
                'interval_minutes': 0,  # Invalid: less than 1
            }
        }
        
        response = flask_app.post('/api/config',
                                 json=config_data,
                                 content_type='application/json')
        assert response.status_code == 400
        
        result = json.loads(response.data)
        assert 'error' in result
    
    def test_api_data_endpoint(self, flask_app, temp_db):
        """Test API data endpoint"""
        response = flask_app.get('/api/data?period=day')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'labels' in data
        assert 'download_speeds' in data
        assert 'upload_speeds' in data
        assert 'latencies' in data
        assert len(data['labels']) > 0
    
    def test_api_stats_endpoint(self, flask_app, temp_db):
        """Test API stats endpoint"""
        response = flask_app.get('/api/stats?period=day')
        assert response.status_code == 200
        
        stats = json.loads(response.data)
        assert 'count' in stats
        assert 'download_speed' in stats
        assert 'upload_speed' in stats
        assert 'latency' in stats
        assert stats['count'] == 3  # From fixture
    
    def test_api_health_endpoint(self, flask_app, temp_db):
        """Test API health endpoint"""
        response = flask_app.get('/api/health')
        assert response.status_code == 200
        
        health = json.loads(response.data)
        assert health['status'] == 'healthy'
        assert health['database'] == 'connected'
        assert 'timestamp' in health
    
    def test_api_test_endpoint_bandwidth(self, flask_app, mock_subprocess, mock_librespeed_output):
        """Test API test endpoint for bandwidth"""
        mock_subprocess.return_value = Mock(returncode=0, stdout=json.dumps(mock_librespeed_output))
        
        response = flask_app.post('/api/test', 
                                 json={'type': 'bandwidth'},
                                 content_type='application/json')
        assert response.status_code == 200
        
        result = json.loads(response.data)
        assert result['success'] == True
    
    def test_api_test_endpoint_latency(self, flask_app, mock_subprocess, mock_ping_output):
        """Test API test endpoint for latency"""
        mock_subprocess.return_value = Mock(returncode=0, stdout=mock_ping_output)
        
        response = flask_app.post('/api/test', 
                                 json={'type': 'latency'},
                                 content_type='application/json')
        assert response.status_code == 200
        
        result = json.loads(response.data)
        assert result['success'] == True
    
    def test_api_test_endpoint_failure(self, flask_app, mock_subprocess):
        """Test API test endpoint failure"""
        mock_subprocess.return_value = Mock(returncode=1, stderr='Test failed')
        
        response = flask_app.post('/api/test', 
                                 json={'type': 'bandwidth'},
                                 content_type='application/json')
        assert response.status_code == 200
        
        result = json.loads(response.data)
        assert result['success'] == False
        assert 'error' in result
    
    def test_api_test_endpoint_no_json(self, flask_app):
        """Test API test endpoint without JSON"""
        response = flask_app.post('/api/test')
        assert response.status_code == 200
        
        result = json.loads(response.data)
        assert result['success'] == True  # Defaults to bandwidth
    
    def test_export_csv_endpoint(self, flask_app, temp_db):
        """Test CSV export endpoint"""
        response = flask_app.get('/export/csv')
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/csv; charset=utf-8'
        assert 'attachment' in response.headers['Content-Disposition']
        
        # Check CSV content
        csv_content = response.data.decode('utf-8')
        assert 'timestamp' in csv_content
        assert 'download_speed' in csv_content
        assert 'upload_speed' in csv_content
        assert 'latency' in csv_content
    
    def test_history_with_filters(self, flask_app, temp_db):
        """Test history page with filters"""
        response = flask_app.get('/history?period=day&test_type=bandwidth&limit=10')
        assert response.status_code == 200
        assert b'bandwidth' in response.data.lower()
    
    def test_dashboard_error_handling(self, flask_app):
        """Test dashboard error handling"""
        with patch('netpulse.web.db.get_latest_measurements', side_effect=Exception('Database error')):
            response = flask_app.get('/')
            assert response.status_code == 200  # Should still load, but with error message
    
    def test_api_data_error_handling(self, flask_app):
        """Test API data endpoint error handling"""
        with patch('netpulse.web.db.get_measurements_by_period', side_effect=Exception('Database error')):
            response = flask_app.get('/api/data?period=day')
            assert response.status_code == 500
    
    def test_api_health_error_handling(self, flask_app):
        """Test API health endpoint error handling"""
        with patch('netpulse.web.db.get_latest_measurements', side_effect=Exception('Database error')):
            response = flask_app.get('/api/health')
            assert response.status_code == 500
            
            health = json.loads(response.data)
            assert health['status'] == 'unhealthy'
            assert 'error' in health
    
    def test_static_files(self, flask_app):
        """Test static file serving"""
        response = flask_app.get('/static/css/style.css')
        assert response.status_code == 200
        assert 'text/css' in response.headers['Content-Type']
    
    def test_404_handling(self, flask_app):
        """Test 404 error handling"""
        response = flask_app.get('/nonexistent-page')
        assert response.status_code == 404
    
    def test_dashboard_with_no_data(self, flask_app, temp_db):
        """Test dashboard with no measurements"""
        # Clear all data
        temp_db.cleanup_old_data(0)
        
        response = flask_app.get('/')
        assert response.status_code == 200
        assert b'Keine Daten' in response.data
    
    def test_history_with_no_data(self, flask_app, temp_db):
        """Test history with no measurements"""
        # Clear all data
        temp_db.cleanup_old_data(0)
        
        response = flask_app.get('/history')
        assert response.status_code == 200
        assert b'Keine Messungen gefunden' in response.data
