#!/bin/bash
# Manual ARM64 DEB package build

set -e

echo "=== Building ARM64 DEB Package (Manual Method) ==="

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

# Copy package to temp directory
cp "$AMD64_PACKAGE" "$TEMP_DIR/"

cd "$TEMP_DIR"

# Create directory structure
mkdir -p arm64_package/DEBIAN

# Extract control file
ar x "$AMD64_PACKAGE"
tar xf control.tar.*

# Move control file to our structure
mv DEBIAN/control arm64_package/DEBIAN/

# Extract data
tar xf data.tar.*
mv * arm64_package/ 2>/dev/null || true

# Update architecture in control file
sed -i 's/Architecture: amd64/Architecture: arm64/' arm64_package/DEBIAN/control
echo "Updated architecture:"
grep "Architecture:" arm64_package/DEBIAN/control

# Clean up temporary files
rm -f control.tar.* data.tar.* debian-binary

# Repackage
cd arm64_package
dpkg-deb -b . "../$ARM64_PACKAGE"

# Clean up
cd /home/andreas/Repos/netpulse-py
rm -rf "$TEMP_DIR"

# Verify package
echo "=== ARM64 Package Created ==="
echo "Package: $ARM64_PACKAGE"
echo "Size: $(stat -c%s "$ARM64_PACKAGE") bytes"

if command -v dpkg-deb >/dev/null 2>&1; then
    echo "Architecture: $(dpkg-deb -I "$ARM64_PACKAGE" | grep Architecture | cut -d' ' -f2')"
fi

echo ""
echo "ARM64 package built successfully!"
echo "Install with: sudo dpkg -i $ARM64_PACKAGE"
