#!/bin/bash

# Build script for Netpulse DEB package

set -e

echo "Building Netpulse DEB package..."

# Check if we're in the right directory
echo "=== Directory debug ==="
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la | head -10
echo "Looking for setup.py:"
find . -name "setup.py" -exec ls -la {} \;
echo "Testing setup.py file existence:"
if [ -f "setup.py" ]; then
    echo "setup.py exists and is readable"
else
    echo "setup.py does not exist or is not readable"
fi
echo "=== End directory debug ==="

if [ ! -f "setup.py" ]; then
    echo "Error: setup.py not found. Please run this script from the project root."
    exit 1
fi

# Get version from setup.py
VERSION=$(grep "version=" setup.py | cut -d'"' -f2)

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ *.deb debian/*.debhelper.log debian/*.substvars debian/tmp/ || true

# Install build dependencies
echo "Installing build dependencies..."
if command -v sudo >/dev/null 2>&1; then
    # Running with sudo (outside Docker)
    sudo apt-get update
    sudo apt-get install -y debhelper dh-python python3-setuptools
else
    # Running without sudo (inside Docker)
    apt-get update
    apt-get install -y debhelper dh-python python3-setuptools
fi

# Set permissions for debian scripts
chmod +x debian/postinst debian/prerm debian/rules

# Build the package
echo "Building DEB package for version ${VERSION}..."
# Force wheel format to get .dist-info instead of .egg-info
python3 setup.py bdist_wheel 2>/dev/null || echo "Wheel build failed, continuing with egg format"
dpkg-buildpackage -us -uc -b

# Debug: Show what was created
echo "Files created:"
ls -la ../netpulse_${VERSION}_*

# Check if package was built
if [ -f "../netpulse_${VERSION}_arm64.deb" ] || [ -f "../netpulse_${VERSION}_amd64.deb" ]; then
    echo "Package built successfully!"
    
    # Move package to current directory
    mv ../netpulse_${VERSION}_*.deb ./
    
    # Show package info
    echo "Package information:"
    dpkg -I netpulse_${VERSION}_*.deb
    
    echo ""
    echo "To install the package:"
    echo "  sudo dpkg -i netpulse_${VERSION}_*.deb"
    echo "  sudo apt-get install -f  # Install dependencies if needed"
    
else
    echo "Error: Package build failed!"
    exit 1
fi
