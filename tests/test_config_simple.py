"""
Simple configuration tests that don't require database access
"""

import pytest
import tempfile
import os
from netpulse.config import Config


class TestConfigSimple:
    """Test configuration without database dependencies"""
    
    def test_default_config_values(self):
        """Test that default configuration values are set"""
        config = Config()
        
        # Test some default values exist
        assert config.get('measurement.interval_minutes') is not None
        assert config.get('web.port') is not None
        assert config.get('database.path') is not None
    
    def test_get_nonexistent_key_with_default(self):
        """Test getting non-existent key with default value"""
        config = Config()
        
        result = config.get('non.existent.key', 'default_value')
        assert result == 'default_value'
    
    def test_set_and_get_value(self):
        """Test setting and getting configuration values"""
        config = Config()
        
        # Set a value
        config.set('test.key', 'test_value')
        
        # Get the value
        result = config.get('test.key')
        assert result == 'test_value'
    
    def test_nested_key_operations(self):
        """Test nested key operations"""
        config = Config()
        
        # Set nested value
        config.set('level1.level2.value', 'nested_value')
        
        # Get nested value
        result = config.get('level1.level2.value')
        assert result == 'nested_value'
    
    def test_load_simple_config_file(self):
        """Test loading a simple configuration file"""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write("""# Simple test config
measurement.interval_minutes=25
web.port=9090
""")
            config_file = f.name
        
        try:
            config = Config(config_file)
            
            assert config.get('measurement.interval_minutes') == 25
            assert config.get('web.port') == 9090
            
        finally:
            os.unlink(config_file)
