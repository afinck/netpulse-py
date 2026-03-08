#!/bin/bash
# Simple ARM64 DEB package build

set -e

echo "=== Building ARM64 DEB Package (Simple Method) ==="

# Check if AMD64 package exists
AMD64_PACKAGE="netpulse_1.1.1_amd64.deb"
if [ ! -f "$AMD64_PACKAGE" ]; then
    echo "Error: AMD64 package not found: $AMD64_PACKAGE"
    echo "Please run ./build.sh first to create the AMD64 package"
    exit 1
fi

echo "Found AMD64 package: $AMD64_PACKAGE"

# Create ARM64 package by copying and modifying
ARM64_PACKAGE="netpulse_1.1.1_arm64.deb"
TEMP_DIR=$(mktemp -d)

echo "Using temporary directory: $TEMP_DIR"

# Copy package and extract
cp "$AMD64_PACKAGE" "$TEMP_DIR/"
cd "$TEMP_DIR"

# Extract the package
mkdir extracted
cd extracted
ar x "../$AMD64_PACKAGE"

# Extract control and data
tar xf control.tar.*
tar xf data.tar.*

# Update architecture
sed -i 's/Architecture: amd64/Architecture: arm64/' DEBIAN/control
echo "Updated architecture:"
grep "Architecture:" DEBIAN/control

# Clean up temporary files
rm -f control.tar.* data.tar.* debian-binary

# Go back to temp directory
cd ..

# Repackage
dpkg-deb -b extracted "$ARM64_PACKAGE"

# Clean up
cd /home/andreas/Repos/netpulse-py
rm -rf "$TEMP_DIR"

# Verify package
echo "=== ARM64 Package Created ==="
echo "Package: $ARM64_PACKAGE"
echo "Size: $(stat -c%s "$ARM64_PACKAGE") bytes"
echo "Architecture: $(dpkg-deb -I "$ARM64_PACKAGE" | grep Architecture | cut -d' ' -f2)"

echo ""
echo "ARM64 package built successfully!"
echo "Install with: sudo dpkg -i $ARM64_PACKAGE"
