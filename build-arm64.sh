#!/bin/bash
# Build ARM64 DEB package by repackaging AMD64 package

set -e

echo "=== Building ARM64 DEB Package ==="

# Check if AMD64 package exists
AMD64_PACKAGE="netpulse_1.1.1_amd64.deb"
if [ ! -f "$AMD64_PACKAGE" ]; then
    echo "Error: AMD64 package not found: $AMD64_PACKAGE"
    echo "Please run ./build.sh first to create the AMD64 package"
    exit 1
fi

echo "Found AMD64 package: $AMD64_PACKAGE"

# Create temporary directory for repackaging
TEMP_DIR=$(mktemp -d)
ARM64_PACKAGE="netpulse_1.1.1_arm64.deb"

echo "Using temporary directory: $TEMP_DIR"

# Extract AMD64 package
echo "Extracting AMD64 package..."
mkdir -p "$TEMP_DIR/extracted"
cd "$TEMP_DIR/extracted"

# Extract using ar and tar
ar x "/home/andreas/Repos/netpulse-py/$AMD64_PACKAGE"
tar xf control.tar.*
tar xf data.tar.*
cd ..
rm -f control.tar.* data.tar.* debian-binary

# Update architecture in control file
echo "Updating architecture to arm64..."
if [ -f "./DEBIAN/control" ]; then
    sed -i 's/Architecture: amd64/Architecture: arm64/' "./DEBIAN/control"
    echo "Updated control file:"
    grep "Architecture:" "./DEBIAN/control"
else
    echo "Error: Could not find control file in extracted package"
    echo "Contents of current directory:"
    ls -la
    exit 1
fi

# Repackage as ARM64
echo "Repackaging as ARM64..."
dpkg-deb -b "$TEMP_DIR/extracted" "$ARM64_PACKAGE"

# Clean up
rm -rf "$TEMP_DIR"

# Verify package
echo "=== ARM64 Package Created ==="
echo "Package: $ARM64_PACKAGE"
echo "Size: $(stat -c%s "$ARM64_PACKAGE") bytes"
echo "Architecture: $(dpkg-deb -I "$ARM64_PACKAGE" | grep Architecture | cut -d' ' -f2)"

# Show package info
echo ""
echo "Package information:"
dpkg-deb -I "$ARM64_PACKAGE"

echo ""
echo "ARM64 package built successfully!"
echo "Install with: sudo dpkg -i $ARM64_PACKAGE"
