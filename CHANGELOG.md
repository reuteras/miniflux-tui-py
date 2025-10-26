# Changelog

## [0.4.3] - 2025-10-26

### Security & Infrastructure
- **SLSA Provenance**: Added automatic SLSA provenance generation for released artifacts (supply chain security)
- **Signed Releases**: All release artifacts now include cryptographic proof of provenance
- **Code Review**: Enforced code review on main branch (1 approval required)
- **Scorecard**: Improved OpenSSF Scorecard compliance

### Features
- **Application Version Display**: Shows app version from pyproject.toml in help screen
- **Server Information**: Displays Miniflux server version and API version in help
- **System Information**: Shows Python version, platform, and Textual framework version
- **User Display**: Shows current username from Miniflux server

### Improvements
- Branch protection rules enhanced with signed commit requirements
- GitHub Actions pinned to commit SHAs via Renovate Bot
- Pre-commit hooks configured for code quality
- Better error handling in async operations

### Dependency Updates
- Updated SLSA framework to v2.1.0 via Renovate

### Testing & Quality
- All 465 tests passing
- Code passes ruff linting and pyright type checking
- No security vulnerabilities detected

## [0.4.2] - 2025-10-26

### Security Documentation
- Added comprehensive security documentation (docs/security.md)
- OpenSSF Scorecard improvements and best practices
- CII Best Practices badge integration

## [0.4.0] - 2025-10-26

### Major Features
- **Search Functionality**: Full-text search across entry titles and content (Phase 2)
- **Enhanced Theme Support**: Comprehensive test coverage for color customization (Phase 3)
- **Improved Test Coverage**: Increased from 78% to 79% with 465 total tests (Phase 1)

### Features & Improvements
- Added `/` keybinding for search mode toggle
- Implemented `set_search_term()` method for programmatic search
- Search integrates with existing status filters (unread/starred)
- Added 10 search integration tests (Phase 2)
- Added 5 theme configuration tests (Phase 3)
- Added 24 entry_reader integration tests (Phase 1)

### Testing & Quality
- Phase 1: Improved test coverage to 80% for entry_reader.py
- Phase 2: Added comprehensive search functionality tests
- Phase 3: Added theme configuration integration tests
- Total tests: 465 (up from 426)
- Coverage: 79% (maintained from Phase 1)
- All quality checks passing (ruff, pyright, pytest)

### Bug Fixes & Refactoring
- Search filter properly integrates with existing filters
- Theme colors persist across config reloads
- All pre-commit hooks passing

### Documentation
- Documented search functionality
- Updated configuration examples with search and theme options
- All tests documented with clear descriptions

## [0.3.0] - 2025-10-26

### Major Achievements
- **Comprehensive Test Suite**: Reached 74% overall test coverage (403 tests)
- **Perfect Coverage**: 8 core modules at 100% coverage (api/client, config, utils, performance, etc.)
- **Production Ready**: All quality checks passing (ruff, pyright, pytest)

### Testing & Quality
- Achieved 100% coverage for ui/app.py (was 90%)
- Achieved 100% coverage for help.py (was 18%)
- Achieved 100% coverage for performance.py (was 59%)
- Improved overall coverage from ~55% to 74%
- Added comprehensive on_mount and load_entries lifecycle tests
- All 403 tests passing with 0 regressions

### Infrastructure
- Automated CI/CD with GitHub Actions
- Type checking with pyright (0 errors)
- Linting with ruff (all checks passing)
- Test coverage tracking with pytest-cov
- PyPI publishing with OIDC

### Documentation
- Complete MkDocs site with Material theme
- API reference documentation
- Installation and usage guides
- Contributing guidelines
- Security policies

## [0.2.9] - 2025-10-26

### Features
- Refactor long functions for improved readability
- Extract repeated code patterns from screens
- Apply consistent error handling to entry_list screen
- Apply retry logic to all API client methods

### Bug Fixes
- Add type hints to test assertions for mypy compliance

### Testing
- Add 22 comprehensive tests for entry_list helpers
- Add comprehensive tests for cursor position restoration


## [0.2.8] - 2025-10-25

### Bug Fixes
- Resolve linting errors and navigation persistence bug


## [0.2.7] - 2025-10-25

### Features
- Add expand/collapse all feeds in group mode
- Add expand/collapse all feeds in group mode
- Add Python 3.15 preview testing without blocking releases

### Bug Fixes
- Handle None value for list_view.index in type checking
- Wrap bare URLs in markdown links in RELEASE.md checklist
- Find entries by ID not object identity when restoring cursor
- Don't reset cursor index to 0 in _populate_list
- Properly restore cursor position to entry in grouped mode
- Resolve linting errors and navigation persistence bug
- Defer ListView focus and cursor restoration to prevent navigation hang in grouped mode
- Resolve markdown linting errors and prevent IndexError on entry list screen
- Restore ListView focus when returning from entry reader
- Restore ListView focus when returning from entry reader
- Resolve all remaining markdown linter errors
- Fix markdown linter errors


## [0.2.6] - 2025-10-25

### Fixed
- Linter errors in Markdown files.


## [0.2.5] - 2025-10-25

### Bug Fixes
- Download artifacts in release job for GitHub Release creation


## [0.2.4] - 2025-10-25

### Fixed
- Relase scripts


## [0.2.3] - 2025-10-25

### Features
- Update release script defaults per user preferences

### Bug Fixes
- Remove bash release script and fix test indentation


## [0.2.2] - 2025-10-25

### Features
- Add changelog automation from conventional commits

### Bug Fixes
- Use timezone.utc instead of datetime.UTC for Python 3.11 compatibility

### Documentation
- Add release troubleshooting guide and update README


All notable changes to miniflux-tui-py will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2025-10-25

Small fix for .gitignore

## [0.2.0] - 2025-10-25

### Added

**Comprehensive Test Coverage Expansion (Phases 1-4)**

- **Phase 1:** Added 22 tests for `api/client.py`
  - Async API client initialization and configuration
  - Feed management operations (fetch, create, update, delete)
  - Entry operations (listing, retrieval, status changes)
  - Error handling and edge cases

- **Phase 2:** Added 32 tests for `main.py` and expanded `config.py` to 100%
  - CLI argument parsing (--init, --check-config, --version, --help)
  - Configuration initialization and validation
  - Application startup and error handling
  - Platform-specific configuration paths (Linux, macOS, Windows)
  - Comprehensive configuration options (colors, sorting, grouping)

- **Phase 3:** Added 40 tests for UI screens
  - Entry reader screen with HTML to Markdown conversion
  - Scrolling actions and navigation
  - Entry management (mark read/unread, star, save)
  - Help screen with keyboard bindings
  - Screen composition and binding verification

- **Phase 4:** Added 50 tests for entry list screen
  - `EntryListItem` and `FeedHeaderItem` widget classes
  - Sorting modes (by date, feed, status)
  - Filtering (unread only, starred only)
  - Grouping by feed with fold/unfold operations
  - Cursor navigation and visibility control
  - Incremental updates and position persistence

### Changed

- **Coverage Metrics:** Overall test coverage increased from 22% to 56%
  - `api/client.py`: 0% → 100%
  - `config.py`: 43% → 100%
  - `main.py`: 0% → 98%
  - `api/models.py`: 0% → 100%
  - `constants.py`: 0% → 100%
  - `utils.py`: 0% → 100%
  - `ui/screens/entry_list.py`: 22% → 43%
  - `ui/screens/entry_reader.py`: 26% → 34%

- **CI Configuration:** Updated GitHub Actions workflow
  - Coverage threshold increased from 35% → 40% → 50% → 55%
  - Added permission constraints
  - Improved test reporting

- **Code Quality:** Strict adherence to linting and type checking
  - All code passes `ruff` linting
  - All code passes `pyright` type checking
  - Pre-commit hooks enforced

### Fixed

- Entry ordering when using grouping mode (now uses `sorted_entries` consistently)
- Cursor navigation in grouped mode (properly skips hidden entries)
- Position persistence when returning from entry reader
- Incremental update performance for single entry changes

### Testing

- Total test count: 215 tests across all modules
- Test frameworks: pytest with asyncio support
- Coverage reporting: XML format for CI/CD integration
- Multi-version testing: Python 3.11, 3.12, 3.13

## [0.1.1] - 2025-10-01

### Added

- Initial project structure with Python TUI framework (Textual)
- Async Miniflux API client wrapper
- Entry list screen with sorting and grouping
- Entry reader screen with HTML to Markdown conversion
- Help screen with keyboard shortcuts
- Configuration management with platform-specific paths
- Basic testing setup

### Features

- **Entry Management**
  - View feed entries in a terminal UI
  - Mark entries as read/unread
  - Toggle starred status
  - Save entries to third-party services

- **Sorting & Filtering**
  - Sort by date (newest first)
  - Sort by feed (alphabetically)
  - Sort by status (unread first)
  - Filter by unread or starred

- **Navigation**
  - Vim-style key bindings (j/k for navigation)
  - Arrow key support
  - Feed grouping with collapse/expand
  - Position persistence

- **Configuration**
  - TOML-based configuration
  - Customizable colors (unread/read)
  - Theme preferences
  - Server and API key setup
