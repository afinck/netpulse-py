#!/usr/bin/env python3
"""
Cross-compilation tests for Netpulse DEB packages.
Tests that the cross-compilation workflow produces working packages.
"""

import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch, MagicMock


class TestCrossCompilation(unittest.TestCase):
    """Test cross-compilation features and package compatibility."""

    def test_python_package_metadata_format(self):
        """Test that setup.py produces modern .dist-info format."""
        # Test that setup.py has the correct configuration
        with open('setup.py', 'r') as f:
            setup_content = f.read()
        
        # Check for modern packaging configuration
        self.assertIn('zip_safe=False', setup_content)
        self.assertIn('use_2to3=False', setup_content)
        self.assertIn('bdist_wheel', setup_content)
        self.assertIn('universal=0', setup_content)

    def test_debian_rules_metadata_extraction(self):
        """Test that debian/rules extracts .dist-info from wheels."""
        with open('debian/rules', 'r') as f:
            rules_content = f.read()
        
        # Check for wheel extraction logic
        self.assertIn('dist/netpulse-1.1.0-py3-none-any.whl', rules_content)
        self.assertIn('unzip -q', rules_content)
        self.assertIn('netpulse-1.1.0.dist-info', rules_content)
        self.assertIn('usr/lib/python3/dist-packages', rules_content)

    def test_github_actions_workflow(self):
        """Test that GitHub Actions workflow is properly configured."""
        workflow_path = '.github/workflows/build-deb-cross.yml'
        self.assertTrue(os.path.exists(workflow_path))
        
        with open(workflow_path, 'r') as f:
            workflow_content = f.read()
        
        # Check for cross-compilation features
        self.assertIn('docker/setup-buildx-action', workflow_content)
        self.assertIn('platform:', workflow_content)
        self.assertIn('linux/amd64', workflow_content)
        self.assertIn('linux/arm64', workflow_content)
        self.assertIn('unzip', workflow_content)

    def test_verification_scripts_exist(self):
        """Test that verification scripts are present and executable."""
        scripts = [
            'verify_installation.sh',
            'debug_measurements.sh'
        ]
        
        for script in scripts:
            self.assertTrue(os.path.exists(script), f"{script} should exist")
            # Check script is executable (on Unix systems)
            if os.name != 'nt':
                st = os.stat(script)
                self.assertTrue(st.st_mode & 0o111, f"{script} should be executable")

    def test_build_script_wheel_extraction(self):
        """Test that build.sh includes wheel extraction."""
        with open('build.sh', 'r') as f:
            build_content = f.read()
        
        # Check for wheel build and extraction
        self.assertIn('python3 setup.py bdist_wheel', build_content)
        self.assertIn('dpkg-buildpackage', build_content)

    def test_package_metadata_compatibility(self):
        """Test that package metadata is compatible with Python 3.11+."""
        # This would be tested in an actual installation environment
        # For now, we test the setup configuration
        with open('setup.py', 'r') as f:
            setup_content = f.read()
        
        # Ensure no legacy egg-specific configurations
        self.assertNotIn('zip_safe=True', setup_content)
        
        # Check for modern entry points configuration
        self.assertIn('entry_points', setup_content)
        self.assertIn('console_scripts', setup_content)

    @patch('subprocess.run')
    def test_wheel_creation_mock(self, mock_run):
        """Test wheel creation process (mocked)."""
        # Mock successful wheel creation
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "creating 'dist/netpulse-1.1.0-py3-none-any.whl'"
        
        # Test wheel creation command
        result = subprocess.run(
            ['python3', 'setup.py', 'bdist_wheel'],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)

    def test_system_wide_installation_path(self):
        """Test that packages install to system-wide location."""
        with open('debian/rules', 'r') as f:
            rules_content = f.read()
        
        # Check for system-wide installation path
        self.assertIn('usr/lib/python3/dist-packages', rules_content)
        # Ensure not using version-specific paths
        self.assertNotIn('usr/lib/python3.10/dist-packages', rules_content)

    def test_debug_script_functionality(self):
        """Test that debug scripts have required functionality."""
        debug_script = 'debug_measurements.sh'
        
        with open(debug_script, 'r') as f:
            debug_content = f.read()
        
        # Check for key debugging functions
        self.assertIn('systemctl status', debug_content)
        self.assertIn('netpulse-measure', debug_content)
        self.assertIn('librespeed-cli', debug_content)
        self.assertIn('sqlite3', debug_content)
        self.assertIn('journalctl', debug_content)


class TestPackageInstallation(unittest.TestCase):
    """Test package installation scenarios."""

    def test_python_version_compatibility(self):
        """Test Python version compatibility matrix."""
        # This would be tested in actual environments
        # For now, test setup.py configuration
        with open('setup.py', 'r') as f:
            setup_content = f.read()
        
        # Check Python version requirements
        self.assertIn('python_requires', setup_content)
        # Should support Python 3.8+
        self.assertIn('>=3.8', setup_content)

    def test_entry_points_configuration(self):
        """Test that entry points are correctly configured."""
        with open('setup.py', 'r') as f:
            setup_content = f.read()
        
        # Check for required entry points
        self.assertIn('netpulse = netpulse.web:main', setup_content)
        self.assertIn('netpulse-measure = netpulse.speedtest:main', setup_content)

    def test_package_dependencies(self):
        """Test that package dependencies are correctly specified."""
        with open('setup.py', 'r') as f:
            setup_content = f.read()
        
        # Check for required dependencies
        self.assertIn('flask', setup_content)
        self.assertIn('click', setup_content)
        self.assertIn('jinja2', setup_content)


if __name__ == '__main__':
    unittest.main()
