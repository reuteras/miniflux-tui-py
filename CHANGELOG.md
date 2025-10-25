# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Pyright type checking integration
- MkDocs documentation site with GitHub Pages deployment
- GitHub Actions workflows for testing and publishing
- Comprehensive API reference documentation
- Test coverage reporting with codecov
- Dependabot configuration for automated dependency updates

### Changed
- Grouped mode now uses CSS-based hiding for better cursor position preservation

### Fixed
- Navigation in grouped mode now skips hidden entries when using j/k

## [0.1.1] - 2024-10-25

### Changed
- Removed notification messages for expand/collapse operations

### Fixed
- Cursor position preservation when expanding/collapsing feeds in grouped mode
- Navigation now works correctly through visible entries only in grouped mode

## [0.1.0] - 2024-10-20

### Added
- Initial release of miniflux-tui-py
- Terminal user interface for Miniflux RSS reader
- Keyboard-driven navigation with Vim-style bindings
- Multiple sort modes: date, feed, status
- Feed grouping with expand/collapse functionality
- Entry filtering: unread and starred views
- Mark entries as read/unread
- Star/unstar functionality
- Terminal-based configuration setup
- Support for self-signed SSL certificates
- Customizable colors for different entry states
- HTML to Markdown conversion for entry content
- Cross-platform configuration file support (Linux, macOS, Windows)
- Pre-commit hooks for code quality
- Performance optimization with incremental refresh

[Unreleased]: https://github.com/reuteras/miniflux-tui-py/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/reuteras/miniflux-tui-py/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/reuteras/miniflux-tui-py/releases/tag/v0.1.0
