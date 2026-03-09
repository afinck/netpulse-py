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
- **Release option**: Can create releases manually

### Release Workflow (`release.yml`)
- **Trigger**: Release publication on GitHub
- **Automatic**: Builds and uploads DEB packages to releases
- **Cross-compilation**: AMD64 and ARM64 packages
- **Version tagging**: Uses release tag for package naming
- **Zero-touch**: Complete automation

## Release Process

### Automatic Release (Recommended)
1. **Create tag**: `git tag v1.1.2`
2. **Push tag**: `git push origin v1.1.2`
3. **Create release**: GitHub UI creates release from tag
4. **Automatic build**: Release workflow builds both architectures
5. **Assets uploaded**: DEB packages attached to release
6. **Download ready**: Users can download from release page

### Manual Release
1. **Run build workflow**: Manual trigger with "Create release" option
2. **Automatic release**: Workflow creates release and uploads artifacts
3. **Download available**: DEB packages in release assets

## Cross-Compilation Support

The build workflows support cross-compilation using Docker Buildx:

- **AMD64**: Standard x86_64 systems (desktops, servers)
- **ARM64**: ARM systems (Raspberry Pi 4, ARM servers)
- **Base Images**: Ubuntu 22.04 for both architectures
- **Output**: Two DEB packages per build

## Development Workflow

1. **Feature branches**: Create `feature/your-feature` branches
2. **Testing**: All changes are tested automatically on Python 3.8-3.13
3. **Building**: DEB packages are built for both architectures
4. **Releasing**: Automatic or manual release with asset uploads

## Artifacts

### Build Artifacts
After each build, two artifacts are available:
- `netpulse-deb-amd64`: Contains the AMD64 DEB package
- `netpulse-deb-arm64`: Contains the ARM64 DEB package

### Release Assets
After each release, DEB packages are available:
- `netpulse_VERSION_amd64.deb`: AMD64 package for desktops/servers
- `netpulse_VERSION_arm64.deb`: ARM64 package for Raspberry Pi

## Future Enhancements

- Multi-distribution support (Debian, Ubuntu variants)
- Integration testing across architectures
- Automated security scanning
- Docker image releases
