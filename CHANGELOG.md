# Changelog

All notable changes to miniflux-tui-py will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
