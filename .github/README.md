# Netpulse CI/CD

This directory contains the GitHub Actions workflows for Netpulse.

## Workflows

### Test Workflow (`test.yml`)
- **Trigger**: Push to main/feature branches, pull requests
- **Python versions**: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- **Tests**: Unit tests and web API tests
- **Coverage**: Uploads to Codecov

### Build Workflow (`build.yml`)
- **Trigger**: Push to main/feature branches, manual dispatch
- **Architectures**: AMD64 and ARM64 (cross-compilation)
- **Builds**: DEB packages for Ubuntu/Debian
- **Docker**: Uses Docker Buildx for cross-compilation
- **Artifacts**: Separate artifacts per architecture (30-day retention)

## Cross-Compilation Support

The build workflow supports cross-compilation using Docker Buildx:

- **AMD64**: Standard x86_64 systems (desktops, servers)
- **ARM64**: ARM systems (Raspberry Pi 4, ARM servers)
- **Base Images**: Ubuntu 22.04 for both architectures
- **Output**: Two DEB packages per build

## Development Workflow

1. **Feature branches**: Create `feature/your-feature` branches
2. **Testing**: All changes are tested automatically on Python 3.8-3.13
3. **Building**: DEB packages are built for both architectures
4. **Manual release**: Download artifacts and upload to releases

## Artifacts

After each build, two artifacts are available:
- `netpulse-deb-amd64`: Contains the AMD64 DEB package
- `netpulse-deb-arm64`: Contains the ARM64 DEB package

## Future Enhancements

- Automatic release uploads
- Multi-distribution support (Debian, Ubuntu variants)
- Integration testing across architectures
- Automated security scanning
