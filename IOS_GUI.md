# iOS GUI Support for Miniflux-TUI-Py

This document describes the iOS GUI version of miniflux-tui-py, built with BeeWare Toga framework.

## Overview

The iOS GUI version provides a **native graphical interface** for iOS devices, while reusing the core API client and data models from the TUI version. This proof-of-concept demonstrates that the architecture is flexible enough to support multiple UI paradigms.

### What's Different?

| Component | TUI Version | GUI Version |
|-----------|-------------|-------------|
| UI Framework | Textual (terminal) | Toga (native widgets) |
| Platform Support | Terminal/SSH | iOS, Android, macOS, Windows, Linux |
| Entry Point | `miniflux-tui` | `miniflux-gui` |
| API Client | ✅ Shared | ✅ Shared |
| Data Models | ✅ Shared | ✅ Shared |
| Configuration | ✅ Shared | ✅ Shared |

## Features

The iOS GUI version includes:

- ✅ **Entry List**: Browse unread entries with feed name and publish date
- ✅ **Entry Detail**: Read full article content with metadata
- ✅ **Mark Read/Unread**: Toggle entry read status
- ✅ **Star/Unstar**: Bookmark favorite articles
- ✅ **Open in Browser**: Open original article URL
- ✅ **Pull to Refresh**: Reload entries from server
- ✅ **Native iOS UI**: Uses native UIKit widgets

### Coming Soon

- [ ] Category browsing
- [ ] Feed management
- [ ] Search functionality
- [ ] Offline reading
- [ ] Push notifications
- [ ] iOS Widgets

## Architecture

```
miniflux_tui/
├── api/
│   ├── client.py          ← Shared async API wrapper
│   └── models.py          ← Shared data models (Entry, Feed, Category)
├── config.py              ← Shared configuration loading
├── ui/                    ← TUI screens (Textual)
│   └── screens/
└── gui/                   ← GUI screens (Toga) **NEW**
    └── app.py             ← Main Toga application
```

### Code Reuse

**100% reused (no changes needed)**:
- `api/client.py` - Async Miniflux API wrapper
- `api/models.py` - Entry, Feed, Category dataclasses
- `config.py` - Configuration loading (TOML)

**New code (Toga-specific)**:
- `gui/app.py` - Main Toga application
- Entry list screen (native)
- Entry detail screen (native)

## Installation & Setup

### Prerequisites

1. **macOS with Xcode** (required for iOS development)
   ```bash
   xcode-select --install
   ```

2. **Python 3.11+**
   ```bash
   python --version  # Should be 3.11 or higher
   ```

3. **BeeWare Briefcase**
   ```bash
   # Install GUI dependencies
   uv pip install -e ".[gui]"
   # Or with pip:
   pip install -e ".[gui]"
   ```

### Configuration

The GUI version uses the **same configuration** as the TUI version:

```bash
# Create config (if not already done)
miniflux-tui --init

# Config location (same for both versions):
# - macOS: ~/.config/miniflux-tui/config.toml
# - Linux: ~/.config/miniflux-tui/config.toml
# - Windows: %APPDATA%\miniflux-tui\config.toml
```

## Development & Testing

### Run GUI on Desktop (macOS/Linux/Windows)

```bash
# Run in development mode
briefcase dev

# Or run directly with Python
python -m miniflux_tui.gui.app
```

### Build for iOS

#### Step 1: Create iOS Project

```bash
# Create Xcode project
briefcase create iOS

# This generates:
# iOS/Xcode/Miniflux Reader/
```

#### Step 2: Build iOS App

```bash
# Build the iOS app
briefcase build iOS
```

#### Step 3: Run in iOS Simulator

```bash
# Launch in iOS Simulator
briefcase run iOS

# Or specify a specific simulator
briefcase run iOS -d "iPhone 15 Pro"
```

#### Step 4: Package for Distribution

```bash
# Package for App Store or TestFlight
briefcase package iOS --adhoc  # For testing (AdHoc distribution)
briefcase package iOS          # For App Store submission
```

### Available Briefcase Commands

```bash
# Create app scaffold for a platform
briefcase create iOS
briefcase create android
briefcase create macOS

# Build the app
briefcase build iOS

# Run in simulator/emulator
briefcase run iOS
briefcase run android

# Open in Xcode (for debugging)
briefcase open iOS

# Update app code without rebuilding
briefcase update iOS

# Package for distribution
briefcase package iOS
```

## Testing on Real iOS Device

### Requirements

1. **Apple Developer Account** (free or paid)
2. **iOS device** with USB cable
3. **Xcode** installed on macOS

### Steps

1. **Connect your iOS device** via USB

2. **Open Xcode project**:
   ```bash
   briefcase open iOS
   ```

3. **Configure code signing** in Xcode:
   - Select your development team
   - Choose your device as the target

4. **Build and run**:
   ```bash
   briefcase run iOS -d "Your Device Name"
   ```

## Deployment to App Store

### Prerequisites

- **Apple Developer Program** membership ($99/year)
- **App Store Connect** account
- **Valid certificates and provisioning profiles**

### Steps

1. **Prepare app metadata**:
   - App name, description, screenshots
   - Privacy policy URL
   - App category and keywords

2. **Build release version**:
   ```bash
   briefcase package iOS
   ```

3. **Upload to App Store Connect**:
   ```bash
   # Briefcase will guide you through the upload process
   briefcase publish iOS
   ```

4. **Submit for review** via App Store Connect web interface

## Troubleshooting

### Common Issues

#### "briefcase: command not found"

```bash
# Install GUI dependencies
uv pip install -e ".[gui]"
```

#### "No module named 'toga'"

```bash
# Install toga separately
pip install toga>=0.5.0
```

#### "Configuration Error" on app launch

```bash
# Ensure config exists
miniflux-tui --init

# Verify config location
cat ~/.config/miniflux-tui/config.toml
```

#### iOS build fails with certificate errors

1. Open Xcode: `briefcase open iOS`
2. Go to **Signing & Capabilities** tab
3. Select your **Team** and **Signing Certificate**
4. Rebuild: `briefcase build iOS`

#### App crashes on iOS simulator

```bash
# Check logs
briefcase run iOS --log

# Or view Xcode console
briefcase open iOS
# Then run from Xcode to see detailed logs
```

### Dependency Issues

If you encounter dependency issues on iOS:

1. **Check wheel availability**:
   ```bash
   # All dependencies must be available as wheels (not source tarballs)
   # iOS does not support compiling packages from source
   ```

2. **Common problematic packages**:
   - Packages with C extensions may need iOS-specific wheels
   - Check PyPI for iOS wheel availability

3. **Alternative packages**:
   - If a package doesn't have iOS wheels, find an alternative
   - Or build the wheel yourself using `cibuildwheel`

## Development Workflow

### Making Changes

1. **Edit Python code** in `miniflux_tui/gui/`

2. **Update app** (fast, doesn't rebuild):
   ```bash
   briefcase update iOS
   briefcase run iOS
   ```

3. **Full rebuild** (slower, use when dependencies change):
   ```bash
   briefcase build iOS
   briefcase run iOS
   ```

### Testing Changes

```bash
# Quick test on desktop
briefcase dev

# Test on iOS simulator
briefcase run iOS

# Test on real device
briefcase run iOS -d "Your iPhone"
```

## Performance Considerations

### App Size

- **TUI version**: ~10-20 MB (Python + dependencies)
- **GUI version**: ~30-50 MB (Python + Toga + native frameworks)

### Startup Time

- **TUI version**: Instant (<1 second)
- **GUI version**: 2-5 seconds (loading Python runtime)

### Memory Usage

- **TUI version**: ~20-40 MB
- **GUI version**: ~50-100 MB (native UI frameworks)

## Differences from TUI Version

### Feature Parity

| Feature | TUI | GUI |
|---------|-----|-----|
| Browse unread entries | ✅ | ✅ |
| Browse starred entries | ⏱️ | ⏱️ |
| Entry detail view | ✅ | ✅ |
| Mark read/unread | ✅ | ✅ |
| Star/unstar | ✅ | ✅ |
| Open in browser | ✅ | ✅ |
| Refresh entries | ✅ | ✅ |
| Keyboard shortcuts | ✅ | ❌ |
| Touch gestures | ❌ | ✅ |
| Sort/filter | ✅ | ⏱️ |
| Group by feed | ✅ | ⏱️ |
| Search | ⏱️ | ⏱️ |
| Category management | ⏱️ | ⏱️ |
| Feed management | ⏱️ | ⏱️ |

✅ = Available | ⏱️ = Coming soon | ❌ = Not applicable

### UI Paradigm Differences

**TUI (Textual)**:
- Keyboard-driven navigation (j/k/vim keys)
- List-based interface
- Optimized for terminal/SSH
- Works over slow connections

**GUI (Toga)**:
- Touch-driven navigation (swipe/tap)
- Native iOS widgets
- Optimized for mobile devices
- Requires stable internet

## Future Enhancements

### Short Term (v0.7.0)

- [ ] Add starred entries view
- [ ] Implement sort/filter UI
- [ ] Add search functionality
- [ ] Improve content rendering (better HTML→Markdown)
- [ ] Add images/media support

### Medium Term (v0.8.0)

- [ ] Category browsing
- [ ] Feed management UI
- [ ] Settings screen (sync interval, theme, etc.)
- [ ] Offline reading support
- [ ] Background sync

### Long Term (v1.0.0+)

- [ ] iOS Widgets (Today view)
- [ ] Push notifications (new entries)
- [ ] Handoff support (macOS ↔ iOS)
- [ ] iCloud sync
- [ ] Share extension (save to Miniflux)

## Contributing

Contributions to the iOS GUI version are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas Needing Help

1. **UI/UX Design**: Improve interface layouts and interactions
2. **Performance**: Optimize entry loading and rendering
3. **Features**: Implement missing features (search, categories, etc.)
4. **Testing**: Test on various iOS versions and devices
5. **Documentation**: Improve this guide with screenshots and examples

## References

- [BeeWare Project](https://beeware.org/) - Official BeeWare website
- [Toga Documentation](https://toga.readthedocs.io/) - Toga API reference
- [Briefcase Documentation](https://briefcase.readthedocs.io/) - Briefcase packaging guide
- [iOS Deployment Guide](https://briefcase.readthedocs.io/en/latest/how-to/contribute-docs.html) - Official iOS deployment docs
- [Miniflux API](https://miniflux.app/docs/api.html) - Miniflux API documentation

## License

Same as the main project: **MIT License**

See [LICENSE](LICENSE) for details.

---

**Questions or issues?** Open an issue at <https://github.com/reuteras/miniflux-tui-py/issues>
