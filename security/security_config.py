"""
Security configuration and utilities for Netpulse
"""

import os
import secrets
import hashlib
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security configuration management"""
    
    def __init__(self):
        self.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': self._get_csp(),
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        
        self.rate_limits = {
            'default': '200 per day, 50 per hour',
            'api_test': '10 per minute',
            'api_stats': '100 per hour',
            'api_config': '20 per hour',
            'api_health': '1000 per hour'
        }
    
    def _get_csp(self) -> str:
        """Get Content Security Policy"""
        return (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "object-src 'none'; "
            "media-src 'self'; "
            "frame-src 'none'"
        )
    
    def generate_secure_secret_key(self) -> str:
        """Generate a cryptographically secure secret key"""
        return secrets.token_hex(32)
    
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        try:
            salt, password_hash = hashed.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
        except ValueError:
            return False
    
    def validate_input(self, data: Dict, rules: Dict) -> List[str]:
        """Validate input data against rules"""
        errors = []
        
        for field, rule in rules.items():
            if field not in data:
                if rule.get('required', False):
                    errors.append(f"Field '{field}' is required")
                continue
            
            value = data[field]
            
            # Type validation
            if 'type' in rule:
                expected_type = rule['type']
                if not isinstance(value, expected_type):
                    errors.append(f"Field '{field}' must be of type {expected_type.__name__}")
                    continue
            
            # Range validation for numbers
            if isinstance(value, (int, float)):
                if 'min' in rule and value < rule['min']:
                    errors.append(f"Field '{field}' must be at least {rule['min']}")
                if 'max' in rule and value > rule['max']:
                    errors.append(f"Field '{field}' must be at most {rule['max']}")
            
            # Length validation for strings
            if isinstance(value, str):
                if 'min_length' in rule and len(value) < rule['min_length']:
                    errors.append(f"Field '{field}' must be at least {rule['min_length']} characters")
                if 'max_length' in rule and len(value) > rule['max_length']:
                    errors.append(f"Field '{field}' must be at most {rule['max_length']} characters")
                
                # Enum validation
                if 'enum' in rule and value not in rule['enum']:
                    errors.append(f"Field '{field}' must be one of: {', '.join(rule['enum'])}")
        
        return errors
    
    def sanitize_log_message(self, message: str) -> str:
        """Sanitize log messages to remove sensitive information"""
        # Remove potential passwords, tokens, etc.
        import re
        
        # Remove patterns that look like passwords or secrets
        message = re.sub(r'(?i)password["\']?\s*[:=]\s*["\']?[^"\']+', 'password=***', message)
        message = re.sub(r'(?i)secret["\']?\s*[:=]\s*["\']?[^"\']+', 'secret=***', message)
        message = re.sub(r'(?i)token["\']?\s*[:=]\s*["\']?[^"\']+', 'token=***', message)
        message = re.sub(r'(?i)key["\']?\s*[:=]\s*["\']?[^"\']+', 'key=***', message)
        
        # Remove email addresses
        message = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'email@***', message)
        
        # Remove IP addresses (optional, comment out if you need IP logging)
        # message = re.sub(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', 'x.x.x.x', message)
        
        return message


def get_security_config() -> SecurityConfig:
    """Get the security configuration instance"""
    return SecurityConfig()


def validate_api_key(api_key: str) -> bool:
    """Validate API key (placeholder for future implementation)"""
    # This is a placeholder for future API key validation
    # Currently returns True as no authentication is implemented
    return True


def log_security_event(event_type: str, details: str, source_ip: str = None):
    """Log security events with proper sanitization"""
    sec_config = get_security_config()
    
    log_message = f"SECURITY: {event_type}"
    if source_ip:
        log_message += f" from {source_ip}"
    if details:
        log_message += f" - {sec_config.sanitize_log_message(details)}"
    
    if event_type in ['CRITICAL', 'HIGH']:
        logger.error(log_message)
    elif event_type in ['MEDIUM']:
        logger.warning(log_message)
    else:
        logger.info(log_message)
