#!/bin/bash

echo "=== Netpulse Measurement Debug Script ==="
echo "Run this on your Raspberry Pi where measurements aren't working"
echo

echo "=== 1. Service Status ==="
systemctl status netpulse.service --no-pager
echo
systemctl status netpulse-web.service --no-pager
echo
systemctl status netpulse.timer --no-pager
echo

echo "=== 2. Timer Information ==="
systemctl list-timers netpulse.timer --no-pager
echo
echo "Next run time:"
systemctl show netpulse.timer -p NextElapseUSecRealtime
echo

echo "=== 3. Manual Measurement Test ==="
echo "Running netpulse-measure manually..."
sudo -u netpulse netpulse-measure --verbose 2>&1 || echo "Manual measurement failed"
echo

echo "=== 4. librespeed-cli Check ==="
echo "Checking if librespeed-cli is available:"
which librespeed-cli
echo
echo "Testing librespeed-cli directly:"
librespeed-cli --version 2>/dev/null || echo "librespeed-cli not working"
echo

echo "=== 5. Database Check ==="
echo "Checking database location and permissions:"
find /var -name "*netpulse*.db" 2>/dev/null
echo
echo "Database file details:"
for db in $(find /var -name "*netpulse*.db" 2>/dev/null); do
    echo "Database: $db"
    ls -la "$db"
    echo "Recent entries:"
    sqlite3 "$db" "SELECT COUNT(*) as total_measurements FROM measurements;" 2>/dev/null || echo "Cannot read database"
    sqlite3 "$db" "SELECT datetime(timestamp, 'localtime') as time, download, upload, ping FROM measurements ORDER BY timestamp DESC LIMIT 3;" 2>/dev/null || echo "Cannot query recent measurements"
    echo
done

echo "=== 6. Logs Analysis ==="
echo "Recent netpulse logs:"
journalctl -u netpulse.service --since "1 hour ago" --no-pager -n 10
echo
echo "Recent netpulse-measure logs:"
journalctl -u netpulse.service --since "1 hour ago" -g "netpulse-measure" --no-pager -n 5
echo

echo "=== 7. Network Connectivity ==="
echo "Testing basic connectivity:"
ping -c 3 8.8.8.8 2>/dev/null || echo "Basic connectivity failed"
echo
echo "Testing DNS resolution:"
nslookup google.com 2>/dev/null || echo "DNS resolution failed"
echo

echo "=== 8. Configuration Check ==="
echo "Checking netpulse configuration:"
find /etc -name "*netpulse*" 2>/dev/null
echo
for config in $(find /etc -name "*netpulse*" 2>/dev/null); do
    echo "Config file: $config"
    cat "$config" 2>/dev/null || echo "Cannot read config"
    echo
done

echo "=== 9. User and Permissions ==="
echo "Netpulse user info:"
id netpulse 2>/dev/null || echo "netpulse user not found"
echo
echo "Checking if netpulse user can run measurement:"
sudo -u netpulse whoami 2>/dev/null || echo "Cannot switch to netpulse user"
echo

echo "=== Debug Complete ==="
