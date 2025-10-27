# miniflux-tui-py Roadmap

This document outlines the planned features and improvements for the miniflux-tui-py project. Features are organized by category and priority.

## Legend

- 🚀 **High Priority** - Core features that significantly improve functionality
- ⭐ **Medium Priority** - Nice-to-have features that enhance UX
- 💡 **Low Priority** - Future improvements or nice-to-have additions
- ✅ **Completed** - Features already implemented
- 🔄 **In Progress** - Currently being worked on
- 📋 **Planned** - Scheduled for next release

## Version 0.5.0 - Feed Management & Categories

### Category Support (🚀 High Priority)
- [ ] Support categories in feed list display
- [ ] Filter entries by category
- [ ] Move/copy feeds between categories
- [ ] Create/edit/delete categories
- [ ] Category-based grouping option
- **Issue**: [#TBD](https://github.com/reuteras/miniflux-tui-py/issues)
- **Status**: 📋 Planned

### Feed Operations (🚀 High Priority)
- [x] Implement `refresh_all_feeds()` with 'R' keybinding
- [x] Change refresh behavior:
  - 'r' or ',' → `refresh_feed()` for current feed
  - 'R' → `refresh_all_feeds()` for all feeds
- [x] Display feed sync status/progress (via notifications)
- [ ] Show feed error indicators (bad certs, bot protection, etc.)
- **Issue**: [#55](https://github.com/reuteras/miniflux-tui-py/issues/55)
- **Status**: 🔄 In Progress (refresh functionality completed)

### Feed Management (⭐ Medium Priority)
- [ ] Create/discover new feeds
- [ ] OPML import (consider for later)
- [ ] Edit feed settings:
  - Update fetch rules
  - Toggle full content fetching
  - Configure scraping rules
- [ ] Display feed metadata (last update, item count, etc.)
- **Issue**: [#TBD](https://github.com/reuteras/miniflux-tui-py/issues)
- **Status**: 📋 Planned

### Feed Status Screen (⭐ Medium Priority)
- [ ] New "Status" screen showing problematic feeds
- [ ] Display feeds with errors:
  - SSL certificate issues
  - Bot protection blocking
  - Connection timeouts
  - Other HTTP errors
- [ ] Configuration option for status indicator in toolbar
- [ ] Links to feed settings on web UI
- [ ] Show server version and URL
- **Issue**: [#TBD](https://github.com/reuteras/miniflux-tui-py/issues)
- **Status**: 📋 Planned

## Version 0.6.0 - History & User Settings

### Entry History (⭐ Medium Priority)
- [ ] View history of last read entries
- [ ] Search through reading history
- [ ] Filter history by date range
- [ ] Filter history by feed
- [ ] Restore entries from history
- **Issue**: [#TBD](https://github.com/reuteras/miniflux-tui-py/issues)
- **Status**: 📋 Planned

### User Settings Management (⭐ Medium Priority)
- [ ] View current user settings
- [ ] View/edit global feed settings
- [ ] Configuration screen in TUI:
  - Display current settings
  - Allow inline edits
  - Link to web UI for advanced settings
- [ ] Display enabled integrations
  - Service name and status
  - Link to web UI for configuration
- [ ] Settings persistence
- **Issue**: [#TBD](https://github.com/reuteras/miniflux-tui-py/issues)
- **Status**: 📋 Planned

### Application Info (💡 Low Priority)
- [ ] Display app version from pyproject.toml in help screen
- [ ] Show server version in status screen
- [ ] Display API version info
- [ ] Show connectivity status
- **Issue**: [#TBD](https://github.com/reuteras/miniflux-tui-py/issues)
- **Status**: 📋 Planned

## Version 0.7.0 - Advanced Features

### Search & Discovery (📋 Planned)
- [ ] Full-text search across all entries
- [ ] Search filters by date, category, feed
- [ ] Save search queries
- [ ] Search history

### Performance & Optimization (💡 Low Priority)
- [ ] Database caching for faster startup
- [ ] Incremental feed sync
- [ ] Background refresh with notifications
- [ ] Memory optimization for large feed lists

### UI/UX Improvements (💡 Low Priority)
- [ ] Dark/light theme toggle
- [ ] Customizable keybindings
- [ ] Sidebar for category/feed navigation
- [ ] Bookmark/clipboard integration
- [ ] Export entries to various formats

## Completed Features ✅

- ✅ Basic entry list with sorting (date, feed, status)
- ✅ Entry detail view with HTML to Markdown conversion
- ✅ Mark as read/unread
- ✅ Mark as starred/unstarred
- ✅ Save entries to third-party services
- ✅ Keyboard-driven navigation
- ✅ Feed grouping
- ✅ Unread/starred filtering
- ✅ Search functionality (v0.4.0)
- ✅ Theme configuration (v0.4.0)

## Technical Considerations

### API Requirements
Features will leverage the [Miniflux Python client](https://github.com/miniflux/python-client):
- `get_categories()` - Category list
- `create_category()` - New categories
- `update_category()` - Edit categories
- `delete_category()` - Remove categories
- `refresh_all_feeds()` - Refresh all feeds
- `refresh_feed()` - Refresh single feed
- `create_feed()` - Add new feed
- `discover_feed()` - Auto-discover feeds
- `update_feed()` - Modify feed settings
- `get_feed_history()` - Last read entries
- `get_user()` - User settings
- `get_server_info()` - Server version

### Data Model Updates
- Add `Category` model
- Extend `Feed` model with status/error info
- Add `History` model for read entries
- Add `UserSettings` model
- Add `Integration` model

### UI Components Needed
- Category selector/list
- Feed status indicator
- Settings view
- History browser
- Status dashboard

## Release Schedule

- **v0.4.0** ✅ Released - Search & Theme support
- **v0.5.0** 📋 Planned (Q4 2025) - Categories & Feed Management
- **v0.6.0** 📋 Planned (Q1 2026) - History & User Settings
- **v0.7.0** 📋 Planned (Q2 2026) - Advanced Features

## Contributing

To work on features from this roadmap:

1. Check if an Issue exists for the feature
2. Create one if needed with the roadmap label
3. Create a feature branch: `git checkout -b feat/feature-name`
4. Submit a PR with reference to the issue
5. Updates will be tracked on the GitHub Project board

## Feedback & Ideas

Have ideas for new features? Please:
1. Check existing issues to avoid duplicates
2. Create a new issue with the `enhancement` label
3. Describe the use case and expected behavior
4. Add to this roadmap if appropriate

---

**Last Updated**: October 26, 2025
**Current Version**: v0.4.0
**Next Milestone**: v0.5.0 (Categories & Feed Management)
