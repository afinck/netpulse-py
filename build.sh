#!/bin/bash

# Build script for Netpulse DEB package

set -e

echo "Building Netpulse DEB package..."

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "Error: setup.py not found. Please run this script from the project root."
    exit 1
fi

# Get version from setup.py
VERSION=$(grep "version=" setup.py | cut -d'"' -f2)

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.deb debian/*.debhelper.log debian/*.substvars debian/tmp/

# Install build dependencies
echo "Installing build dependencies..."
sudo apt-get update
sudo apt-get install -y debhelper dh-python python3 python3-setuptools

# Set permissions for debian scripts
chmod +x debian/postinst debian/prerm debian/rules

# Build the package
echo "Building DEB package for version $VERSION..."
dpkg-buildpackage -us -uc -b

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
