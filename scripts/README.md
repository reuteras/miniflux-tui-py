# Scripts Directory

This directory contains utility scripts for project maintenance and automation.

## Scripts Overview

### `build_binary.py`

Builds standalone binary distributions of miniflux-tui using PyInstaller.

**Purpose:**

- Creates single-file executable for distribution
- Useful for users without Python installed

**Usage:**

```bash
uv run scripts/build_binary.py
```

## Best Practices

1. **Always test scripts in a fork first** before running on main repository
2. **Review script output** for errors or unexpected behavior
3. **Keep accounts secured** with 2FA and strong passwords
4. **Update scripts** when GitHub API or workflow changes occur
5. **Document changes** to scripts in commit messages

## Contributing

When adding new scripts:

1. Follow bash best practices:
    - Use `set -euo pipefail` for error handling
    - Add clear comments and documentation
    - Include usage examples
    - Add colored output for better UX
2. Make scripts executable: `chmod +x scripts/your_script.sh`
3. Update this README with script description and usage
4. Test thoroughly before committing

## Security

- Scripts use GitHub CLI authentication (no hardcoded tokens)
- Account switching uses `gh auth switch` (secure method)
- Scripts include timeout protection against infinite loops
- All API calls go through authenticated `gh` CLI

## Related Documentation

- [RELEASE.md](../RELEASE.md) - Release process documentation
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [AGENT.md](../AGENT.md) - Project architecture and workflows
