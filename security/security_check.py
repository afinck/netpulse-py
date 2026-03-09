#!/usr/bin/env python3
"""
Security audit and checking script for Netpulse
"""

import os
import sys
import subprocess
import sqlite3
import logging
from pathlib import Path
from typing import Dict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from netpulse.config import get_config
from security.security_config import get_security_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SecurityAuditor:
    """Security auditor for Netpulse"""
    
    def __init__(self):
        self.config = get_config()
        self.sec_config = get_security_config()
        self.issues = []
        self.warnings = []
        self.recommendations = []
    
    def run_full_audit(self) -> Dict:
        """Run complete security audit"""
        logger.info("Starting security audit...")
        
        results = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'info': []
        }
        
        # Check 1: Secret key security
        self._check_secret_key(results)
        
        # Check 2: Database security
        self._check_database_security(results)
        
        # Check 3: File permissions
        self._check_file_permissions(results)
        
        # Check 4: Network exposure
        self._check_network_exposure(results)
        
        # Check 5: Logging security
        self._check_logging_security(results)
        
        # Check 6: Dependencies
        self._check_dependencies(results)
        
        # Check 7: System services
        self._check_system_services(results)
        
        # Check 8: Configuration security
        self._check_configuration_security(results)
        
        logger.info(f"Security audit completed. Found {len(results['critical'])} critical, "
                   f"{len(results['high'])} high, {len(results['medium'])} medium issues.")
        
        return results
    
    def _check_secret_key(self, results: Dict):
        """Check secret key security"""
        secret_key = self.config.get("web.secret_key", "")
        
        if not secret_key or secret_key == "change-me-in-production":
            results['critical'].append({
                'issue': 'Weak or missing secret key',
                'description': 'Secret key is not set or uses default value',
                'recommendation': 'Set a strong, unique secret key via NETPULSE_SECRET_KEY environment variable'
            })
        elif len(secret_key) < 32:
            results['high'].append({
                'issue': 'Short secret key',
                'description': f'Secret key is only {len(secret_key)} characters',
                'recommendation': 'Use a longer secret key (at least 32 characters)'
            })
        else:
            results['info'].append({
                'issue': 'Secret key check',
                'description': 'Secret key appears to be properly configured'
            })
    
    def _check_database_security(self, results: Dict):
        """Check database security"""
        db_path = self.config.get("database.path", "")
        
        if not db_path:
            results['high'].append({
                'issue': 'Database path not configured',
                'description': 'Database path is not set in configuration'
            })
            return
        
        if not os.path.exists(db_path):
            results['medium'].append({
                'issue': 'Database file not found',
                'description': f'Database file {db_path} does not exist'
            })
            return
        
        # Check file permissions
        stat_info = os.stat(db_path)
        mode = oct(stat_info.st_mode)[-3:]
        
        if mode != '600':
            results['high'].append({
                'issue': 'Insecure database file permissions',
                'description': f'Database file has permissions {mode} (should be 600)',
                'recommendation': 'Run: chmod 600 ' + db_path
            })
        
        # Check ownership
        try:
            import pwd
            file_owner = pwd.getpwuid(stat_info.st_uid).pw_name
            if file_owner != 'netpulse':
                results['medium'].append({
                    'issue': 'Database file ownership',
                    'description': f'Database file owned by {file_owner} (should be netpulse)',
                    'recommendation': 'Run: chown netpulse:netpulse ' + db_path
                })
        except ImportError:
            results['low'].append({
                'issue': 'Cannot check file ownership',
                'description': 'pwd module not available'
            })
    
    def _check_file_permissions(self, results: Dict):
        """Check critical file permissions"""
        critical_files = [
            '/etc/netpulse/netpulse.conf',
            '/var/log/netpulse/',
            '/var/lib/netpulse/'
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                stat_info = os.stat(file_path)
                mode = oct(stat_info.st_mode)[-3:]
                
                if os.path.isfile(file_path) and mode not in ['600', '640', '644']:
                    results['medium'].append({
                        'issue': f'Insecure file permissions: {file_path}',
                        'description': f'File has permissions {mode}',
                        'recommendation': 'Consider restricting file permissions'
                    })
                elif os.path.isdir(file_path) and mode not in ['700', '750', '755']:
                    results['medium'].append({
                        'issue': f'Insecure directory permissions: {file_path}',
                        'description': f'Directory has permissions {mode}',
                        'recommendation': 'Consider restricting directory permissions'
                    })
    
    def _check_network_exposure(self, results: Dict):
        """Check network exposure"""
        host = self.config.get("web.host", "")
        port = self.config.get("web.port", 8080)
        
        if host == "0.0.0.0":
            results['medium'].append({
                'issue': 'Application bound to all interfaces',
                'description': f'Web server listening on 0.0.0.0:{port}',
                'recommendation': 'Consider binding to specific IP addresses if not needed'
            })
        
        # Check if running on privileged port
        if port < 1024:
            results['high'].append({
                'issue': 'Running on privileged port',
                'description': f'Web server running on port {port} (below 1024)',
                'recommendation': 'Consider using a non-privileged port (>1024) with reverse proxy'
            })
    
    def _check_logging_security(self, results: Dict):
        """Check logging security"""
        log_file = self.config.get("logging.file", "")
        log_level = self.config.get("logging.level", "INFO")
        
        if not log_file:
            results['medium'].append({
                'issue': 'Log file not configured',
                'description': 'No log file path specified in configuration'
            })
        elif os.path.exists(log_file):
            stat_info = os.stat(log_file)
            mode = oct(stat_info.st_mode)[-3:]
            
            if mode not in ['600', '640', '644']:
                results['medium'].append({
                    'issue': 'Insecure log file permissions',
                    'description': f'Log file has permissions {mode}',
                    'recommendation': 'Run: chmod 640 ' + log_file
                })
        
        if log_level == "DEBUG":
            results['medium'].append({
                'issue': 'Debug logging enabled',
                'description': 'Debug logging may expose sensitive information',
                'recommendation': 'Use INFO or WARNING level in production'
            })
    
    def _check_dependencies(self, results: Dict):
        """Check for vulnerable dependencies"""
        try:
            # Check if we can run pip-audit or safety
            result = subprocess.run(['pip-audit', '--format', 'json'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                results['info'].append({
                    'issue': 'Dependency check',
                    'description': 'No known vulnerabilities found in dependencies'
                })
            else:
                results['high'].append({
                    'issue': 'Dependency vulnerabilities detected',
                    'description': 'Run: pip-audit for details',
                    'recommendation': 'Update vulnerable dependencies'
                })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            results['medium'].append({
                'issue': 'Dependency scanning tool not available',
                'description': 'pip-audit not installed',
                'recommendation': 'Install pip-audit: pip install pip-audit'
            })
    
    def _check_system_services(self, results: Dict):
        """Check system service security"""
        services = ['netpulse.service', 'netpulse.timer', 'netpulse-web.service']
        
        for service in services:
            try:
                result = subprocess.run(['systemctl', 'status', service], 
                                      capture_output=True, text=True, timeout=10)
                
                if 'active (running)' in result.stdout:
                    results['info'].append({
                        'issue': f'Service status: {service}',
                        'description': 'Service is running'
                    })
                elif 'inactive (dead)' in result.stdout:
                    results['medium'].append({
                        'issue': f'Service not running: {service}',
                        'description': 'Service is not active'
                    })
                else:
                    results['low'].append({
                        'issue': f'Service status unknown: {service}',
                        'description': 'Could not determine service status'
                    })
            except (subprocess.TimeoutExpired, FileNotFoundError):
                results['low'].append({
                    'issue': f'Cannot check service: {service}',
                    'description': 'systemctl not available or timeout'
                })
    
    def _check_configuration_security(self, results: Dict):
        """Check configuration security"""
        # Check measurement configuration
        interval = self.config.get("measurement.interval_minutes", 15)
        timeout = self.config.get("measurement.timeout_seconds", 30)
        
        if interval < 5:
            results['medium'].append({
                'issue': 'Very frequent measurements',
                'description': f'Measurement interval is {interval} minutes',
                'recommendation': 'Consider longer intervals to reduce system load'
            })
        
        if timeout > 300:
            results['medium'].append({
                'issue': 'Very long timeout',
                'description': f'Measurement timeout is {timeout} seconds',
                'recommendation': 'Consider shorter timeouts to prevent hanging'
            })
        
        # Check debug mode
        debug = self.config.get("web.debug", False)
        if debug:
            results['high'].append({
                'issue': 'Debug mode enabled',
                'description': 'Flask debug mode is enabled in production',
                'recommendation': 'Disable debug mode in production'
            })
    
    def print_results(self, results: Dict):
        """Print audit results"""
        severity_colors = {
            'critical': '\033[91m',  # Red
            'high': '\033[93m',     # Yellow
            'medium': '\033[94m',   # Blue
            'low': '\033[92m',      # Green
            'info': '\033[97m'      # White
        }
        
        reset_color = '\033[0m'
        
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            issues = results[severity]
            if not issues:
                continue
            
            color = severity_colors.get(severity, '')
            print(f"\n{color}{severity.upper()} ISSUES ({len(issues)}):{reset_color}")
            print("=" * 50)
            
            for i, issue in enumerate(issues, 1):
                print(f"\n{i}. {issue.get('issue', 'Unknown issue')}")
                print(f"   Description: {issue.get('description', 'No description')}")
                if issue.get('recommendation'):
                    print(f"   Recommendation: {issue['recommendation']}")
        
        print(f"\n{'='*50}")
        print("Security audit completed.")
        
        if results['critical'] or results['high']:
            print("\033[91mCRITICAL or HIGH severity issues found! Address immediately.\033[0m")
        elif results['medium']:
            print("\033[94mMEDIUM severity issues found. Address soon.\033[0m")
        else:
            print("\033[92mNo major security issues found.\033[0m")


def main():
    """Main security audit function"""
    auditor = SecurityAuditor()
    results = auditor.run_full_audit()
    auditor.print_results(results)
    
    # Exit with appropriate code
    if results['critical'] or results['high']:
        sys.exit(2)
    elif results['medium']:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
