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
- **Builds**: DEB packages for Ubuntu/Debian
- **Artifacts**: Uploads DEB packages for 30 days

## Development Workflow

1. **Feature branches**: Create `feature/your-feature` branches
2. **Testing**: All changes are tested automatically
3. **Building**: DEB packages are built automatically
4. **Manual release**: Download artifacts and upload to releases

## Future Enhancements

- Cross-compilation for ARM64
- Automatic release uploads
- Multi-architecture support
- Integration testing
