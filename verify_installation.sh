#!/bin/bash

echo "=== Netpulse Installation Verification Script ==="
echo "Run this on your Raspberry Pi where the DEB is installed"
echo

echo "=== 1. Python Version ==="
python3 --version
echo

echo "=== 2. Package Installation Status ==="
dpkg -l | grep netpulse
echo

echo "=== 3. Entry Points ==="
which netpulse
which netpulse-measure
ls -la /usr/bin/netpulse*
echo

echo "=== 4. Python Package Locations ==="
echo "System-wide dist-packages:"
ls -la /usr/lib/python3/dist-packages/ | grep netpulse || echo "No netpulse in system-wide location"
echo

echo "Version-specific locations:"
for version in 3.10 3.11 3.12; do
    if [ -d "/usr/lib/python${version}/dist-packages" ]; then
        echo "Python ${version} dist-packages:"
        ls -la "/usr/lib/python${version}/dist-packages/" | grep netpulse || echo "  No netpulse found"
    fi
done
echo

echo "=== 5. Package Metadata Search ==="
echo "Looking for .dist-info files:"
find /usr/lib/python* -name "*netpulse*.dist-info" -type d 2>/dev/null
echo

echo "Looking for .egg-info files:"
find /usr/lib/python* -name "*netpulse*.egg-info" -type d 2>/dev/null
echo

echo "=== 6. Metadata Contents ==="
for info_dir in $(find /usr/lib/python* -name "*netpulse*info*" -type d 2>/dev/null); do
    echo "Found metadata in: $info_dir"
    echo "Contents:"
    ls -la "$info_dir"
    if [ -f "$info_dir/METADATA" ]; then
        echo "METADATA file:"
        head -10 "$info_dir/METADATA"
    fi
    if [ -f "$info_dir/entry_points.txt" ]; then
        echo "Entry points:"
        cat "$info_dir/entry_points.txt"
    fi
    echo "---"
done
echo

echo "=== 7. Python Package Discovery Test ==="
python3 -c "
import sys
print(f'Python version: {sys.version}')
try:
    import importlib.metadata
    print('importlib.metadata available')
    try:
        dist = importlib.metadata.distribution('netpulse')
        print(f'Found netpulse: {dist.version}')
        print(f'Metadata location: {dist._path}')
        print('Entry points:')
        for ep in dist.entry_points:
            print(f'  {ep.name}: {ep.value}')
    except importlib.metadata.PackageNotFoundError as e:
        print(f'PackageNotFoundError: {e}')
except ImportError:
    print('importlib.metadata not available')
"
echo

echo "=== 8. Manual Entry Point Test ==="
python3 -c "
import sys
try:
    from importlib.metadata import distribution, PackageNotFoundError
    try:
        dist = distribution('netpulse')
        print('SUCCESS: Found netpulse package metadata')
    except PackageNotFoundError:
        print('FAILED: PackageNotFoundError for netpulse')
        print('Trying manual discovery...')
        import importlib.util
        spec = importlib.util.find_spec('netpulse')
        if spec:
            print(f'Found netpulse module at: {spec.origin}')
        else:
            print('Could not find netpulse module')
except Exception as e:
    print(f'Error: {e}')
"
echo

echo "=== Verification Complete ==="
