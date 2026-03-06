"""
Tests for speedtest module
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from netpulse.speedtest import SpeedtestRunner


class TestSpeedtestRunner:
    """Test speedtest operations"""
    
    def test_check_librespeed_available(self, mock_subprocess):
        """Test librespeed-cli availability check"""
        mock_subprocess.return_value = Mock(returncode=0)
        
        runner = SpeedtestRunner()
        assert runner.check_librespeed() == True
        
        mock_subprocess.assert_called_once_with(['librespeed-cli', '--version'], 
                                              capture_output=True, text=True, timeout=5)
    
    def test_check_librespeed_not_available(self, mock_subprocess):
        """Test librespeed-cli not available"""
        mock_subprocess.side_effect = FileNotFoundError()
        
        runner = SpeedtestRunner()
        assert runner.check_librespeed() == False
    
    def test_parse_result_success(self, mock_librespeed_output):
        """Test successful parsing of librespeed-cli output"""
        runner = SpeedtestRunner()
        result = runner._parse_result(json.dumps(mock_librespeed_output))
        
        assert result is not None
        assert result['download_speed'] == 48.0  # Direct Mbps value
        assert result['upload_speed'] == 10.0     # Direct Mbps value
        assert result['latency'] == 15.5
        assert result['jitter'] == 2.1
        assert result['server_name'] == 'Test Server (Germany)'
        assert result['test_type'] == 'bandwidth'
    
    def test_parse_result_invalid_json(self):
        """Test parsing invalid JSON"""
        runner = SpeedtestRunner()
        result = runner._parse_result('invalid json')
        
        assert result is None
    
    def test_parse_result_missing_fields(self):
        """Test parsing JSON with missing fields"""
        runner = SpeedtestRunner()
        incomplete_data = [{'download': 100.0}]  # New format: array with direct Mbps
        result = runner._parse_result(json.dumps(incomplete_data))
        
        assert result is not None
        assert result['download_speed'] > 0
        assert result['upload_speed'] == 0
        assert result['latency'] == 0
    
    def test_parse_ping_result(self, mock_ping_output):
        """Test parsing ping output"""
        runner = SpeedtestRunner()
        result = runner._parse_ping_result(mock_ping_output)
        
        assert result is not None
        assert result['latency'] == 14.9
        assert result['server_name'] == '8.8.8.8 (Google DNS)'
        assert result['test_type'] == 'latency'
    
    def test_parse_ping_result_invalid(self):
        """Test parsing invalid ping output"""
        runner = SpeedtestRunner()
        result = runner._parse_ping_result('invalid ping output')
        
        assert result is None
