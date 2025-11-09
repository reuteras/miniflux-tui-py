# Merge Conflict Resolution Guide

This branch has intentional conflicts with `main` in `miniflux_tui/ui/screens/settings_management.py`.

## Why Conflicts Exist

**Main branch** added TUI configuration display while keeping all server settings (user info, display preferences, reading preferences, integrations).

**This branch** completely rewrote the settings screen to show ONLY TUI application settings per design requirements.

## Conflict Locations

### 1. Key Bindings (lines 26-32)

**Main has:**
```python
Binding("r", "refresh", "Refresh"),
Binding("o", "open_web_settings", "Web Settings"),
Binding("e", "edit_settings", "Edit"),
Binding("i", "toggle_info_messages", "Toggle Info Messages"),
```

**This branch has:**
```python
Binding("i", "toggle_info_messages", "Toggle Info Messages"),
```

**Resolution:** Accept this branch (TUI-only, no server operations)

### 2. Widget Composition (lines 65-82)

**Main has:**
- User Information
- Display Preferences
- Reading Preferences
- TUI Configuration
- Integrations Status

**This branch has:**
- Application Configuration (TUI settings)
- Configuration File (location and server URL)

**Resolution:** Accept this branch (TUI-only widgets)

### 3. Update Methods (lines 92-100)

**Main calls:**
```python
self._update_user_info()
self._update_display_preferences()
self._update_reading_preferences()
self._update_tui_config()
self._update_integrations()
```

**This branch calls:**
```python
self._update_tui_config()
self._update_config_file_info()
```

**Resolution:** Accept this branch (TUI-only updates)

## How to Resolve

When GitHub shows the conflict:

1. Click "Resolve conflicts" button
2. For each conflict section, choose "Accept incoming changes" (this branch)
3. Or manually edit to keep only the TUI-only implementation
4. Mark as resolved

## Why This Version is Correct

✅ **Design Requirement:** "Settings screen should only be for settings in the tui app. Not server settings"

✅ **Testing:** All 960 tests pass with this implementation

✅ **Performance:** No API calls on mount (faster screen load)

✅ **Simplicity:** Removed ~200 lines of server settings code

✅ **User Experience:** Clear separation between TUI settings (shown here) and server settings (Miniflux web UI)

## What Was Removed

- All server-side user information (username, timezone, language, theme)
- Display preferences (entries per page, etc.)
- Reading preferences (sort order, mark_read_on_view, etc.)
- Integrations status display
- API calls to get_user_info() and get_integrations_status()
- Key bindings: 'r' (refresh), 'o' (open web), 'e' (edit server settings)
- Settings edit dialog functionality

## What Was Kept

- TUI Configuration display (colors, defaults, notifications)
- Info messages toggle ('i' key)
- Configuration file location and server URL
- Instructions to edit config.toml for settings
- Direction to Miniflux web UI for server settings

## Final Note

This is an **intentional architectural change** to simplify the TUI settings screen and provide clearer boundaries between client-side (TUI) and server-side (Miniflux web UI) configuration.
