#!/usr/bin/env python3
"""
Debug script to test systemd timer update functionality
"""

import sys
import os
sys.path.insert(0, '/usr/lib/python3/dist-packages')

from netpulse.web import update_systemd_timer
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_timer_update():
    """Test the timer update function"""
    print("=== Testing systemd timer update ===")
    
    # Test different intervals
    test_intervals = [15, 30, 60, 120, 1440]
    
    for interval in test_intervals:
        print(f"\n--- Testing {interval} minutes ---")
        try:
            result = update_systemd_timer(interval)
            print(f"Result: {result}")
            
            # Read the current timer file to verify
            with open('/lib/systemd/system/netpulse.timer', 'r') as f:
                content = f.read()
                print("Current timer content:")
                for line in content.split('\n'):
                    if 'OnCalendar=' in line:
                        print(f"  {line}")
                        
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

def check_current_timer():
    """Check current timer status"""
    print("\n=== Current timer status ===")
    import subprocess
    
    try:
        # Check timer status
        result = subprocess.run(['systemctl', 'status', 'netpulse.timer'], 
                              capture_output=True, text=True)
        print("Timer status:")
        print(result.stdout)
        
        # Check when timer will run next
        result = subprocess.run(['systemctl', 'list-timers', 'netpulse.timer'], 
                              capture_output=True, text=True)
        print("\nNext run time:")
        print(result.stdout)
        
    except Exception as e:
        print(f"Error checking timer: {e}")

def check_config():
    """Check current configuration"""
    print("\n=== Current configuration ===")
    try:
        from netpulse.config import get_config
        config = get_config()
        interval = config.get("measurement.interval_minutes", 15)
        print(f"Configured interval: {interval} minutes")
    except Exception as e:
        print(f"Error reading config: {e}")

if __name__ == "__main__":
    check_config()
    check_current_timer()
    
    # Ask user which interval to test
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
            print(f"\n=== Testing {interval} minutes ===")
            result = update_systemd_timer(interval)
            print(f"Result: {result}")
            check_current_timer()
        except ValueError:
            print("Please provide a valid integer interval")
    else:
        print("Usage: python3 debug_timer.py <interval_minutes>")
        print("Example: python3 debug_timer.py 60")
