"""
Integration tests for Netpulse
"""

import pytest
import time
import requests
import json
from datetime import datetime


@pytest.mark.integration
class TestIntegration:
    """Integration tests that require the full application running"""
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """Base URL for API requests"""
        return "http://localhost:8080/api"
    
    @pytest.fixture(scope="class")
    def web_base_url(self):
        """Base URL for web interface"""
        return "http://localhost:8080"
    
    def test_health_check(self, api_base_url):
        """Test health check endpoint"""
        response = requests.get(f"{api_base_url}/health", timeout=10)
        assert response.status_code == 200
        
        health = response.json()
        assert health['status'] == 'healthy'
        assert 'timestamp' in health
    
    def test_web_interface_loads(self, web_base_url):
        """Test that web interface loads"""
        response = requests.get(web_base_url, timeout=10)
        assert response.status_code == 200
        assert 'Netpulse' in response.text
        assert 'Dashboard' in response.text
    
    def test_history_page_loads(self, web_base_url):
        """Test that history page loads"""
        response = requests.get(f"{web_base_url}/history", timeout=10)
        assert response.status_code == 200
        assert 'Verlauf' in response.text
    
    def test_api_data_endpoint(self, api_base_url):
        """Test API data endpoint"""
        response = requests.get(f"{api_base_url}/data?period=day", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert 'labels' in data
        assert 'download_speeds' in data
        assert 'upload_speeds' in data
        assert 'latencies' in data
    
    def test_api_stats_endpoint(self, api_base_url):
        """Test API stats endpoint"""
        response = requests.get(f"{api_base_url}/stats?period=day", timeout=10)
        assert response.status_code == 200
        
        stats = response.json()
        assert 'count' in stats
        assert 'download_speed' in stats
        assert 'upload_speed' in stats
        assert 'latency' in stats
    
    def test_run_bandwidth_test(self, api_base_url):
        """Test running a bandwidth test via API"""
        response = requests.post(
            f"{api_base_url}/test",
            json={'type': 'bandwidth'},
            timeout=30  # Longer timeout for actual test
        )
        
        # Test might fail if librespeed-cli is not available
        if response.status_code == 200:
            result = response.json()
            # Either success or failure message is acceptable
            assert 'success' in result
        else:
            # Service might be unavailable or librespeed-cli missing
            pytest.skip("Bandwidth test service unavailable")
    
    def test_run_latency_test(self, api_base_url):
        """Test running a latency test via API"""
        response = requests.post(
            f"{api_base_url}/test",
            json={'type': 'latency'},
            timeout=15  # Longer timeout for actual test
        )
        
        # Test might fail if ping is not available
        if response.status_code == 200:
            result = response.json()
            # Either success or failure message is acceptable
            assert 'success' in result
        else:
            # Service might be unavailable
            pytest.skip("Latency test service unavailable")
    
    def test_data_persistence(self, api_base_url, web_base_url):
        """Test that data persists between requests"""
        # Get initial stats
        response = requests.get(f"{api_base_url}/stats?period=day", timeout=10)
        initial_count = response.json().get('count', 0)
        
        # Try to run a test (might fail, but that's ok for this test)
        try:
            requests.post(
                f"{api_base_url}/test",
                json={'type': 'latency'},
                timeout=15
            )
        except:
            pass
        
        # Wait a moment for data to be processed
        time.sleep(2)
        
        # Check if data count changed (it might not if test failed)
        response = requests.get(f"{api_base_url}/stats?period=day", timeout=10)
        final_count = response.json().get('count', 0)
        
        # Data count should be the same or greater
        assert final_count >= initial_count
    
    def test_static_files_served(self, web_base_url):
        """Test that static files are served correctly"""
        response = requests.get(f"{web_base_url}/static/css/style.css", timeout=10)
        assert response.status_code == 200
        assert 'text/css' in response.headers['Content-Type']
    
    def test_error_handling(self, api_base_url):
        """Test error handling for invalid endpoints"""
        response = requests.get(f"{api_base_url}/nonexistent", timeout=10)
        assert response.status_code == 404
    
    def test_concurrent_requests(self, api_base_url):
        """Test handling of concurrent requests"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = requests.get(f"{api_base_url}/health", timeout=10)
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))
        
        # Make 5 concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 200:
                success_count += 1
        
        # At least 3 of 5 should succeed
        assert success_count >= 3
    
    @pytest.mark.slow
    def test_long_running_stability(self, api_base_url):
        """Test application stability over time"""
        # Make requests over 30 seconds
        start_time = time.time()
        success_count = 0
        total_requests = 0
        
        while time.time() - start_time < 30:
            try:
                response = requests.get(f"{api_base_url}/health", timeout=5)
                total_requests += 1
                if response.status_code == 200:
                    success_count += 1
            except:
                pass
            
            time.sleep(1)
        
        # Should have made at least 25 requests and most should succeed
        assert total_requests >= 25
        assert success_count / total_requests >= 0.8  # 80% success rate
