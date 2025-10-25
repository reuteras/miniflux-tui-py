# UI Screens Reference

The TUI application is built using [Textual](https://textual.textualize.io/) and organized into different screens for different views.

## EntryListScreen

The main screen showing the list of entries.

::: miniflux_tui.ui.screens.entry_list.EntryListScreen
    options:
      docstring_style: google

### Key Features

- **Entry display**: Shows entries with status icons and formatting
- **Sorting**: Multiple sort modes (date, feed, status)
- **Grouping**: Optional grouping by feed with expand/collapse
- **Filtering**: Filter to unread or starred entries only
- **Navigation**: Vim-style cursor movement (j/k)

### Actions

| Method | Binding | Description |
|--------|---------|-------------|
| `action_cursor_down` | `j` | Move cursor down |
| `action_cursor_up` | `k` | Move cursor up |
| `action_select_entry` | `Enter` | Open entry in reader |
| `action_toggle_read` | `m` | Toggle read/unread |
| `action_toggle_star` | `*` | Toggle star status |
| `action_cycle_sort` | `s` | Cycle sort modes |
| `action_toggle_group` | `g` | Toggle grouping |
| `action_expand_feed` | `l` | Expand feed |
| `action_collapse_feed` | `h` | Collapse feed |
| `action_refresh` | `r` | Refresh entries |

## EntryReaderScreen

The detailed view for reading a single entry.

::: miniflux_tui.ui.screens.entry_reader.EntryReaderScreen
    options:
      docstring_style: google

### Key Features

- **Full entry display**: Shows title, content, metadata
- **Navigation**: Move between entries in the current list (J/K)
- **Content**: HTML is converted to readable Markdown
- **Actions**: Mark read/unread, star, save, open in browser

### Actions

| Method | Binding | Description |
|--------|---------|-------------|
| `action_next_entry` | `J` | Move to next entry |
| `action_prev_entry` | `K` | Move to previous entry |
| `action_toggle_read` | `m` | Toggle read/unread |
| `action_toggle_star` | `*` | Toggle star |
| `action_save_entry` | `e` | Save entry |
| `action_open_in_browser` | `o` | Open URL in browser |

## HelpScreen

Shows keyboard shortcuts and help information.

::: miniflux_tui.ui.screens.help.HelpScreen
    options:
      docstring_style: google

## MinifluxTUI (Main App)

The main application container.

::: miniflux_tui.ui.app.MinifluxTUI
    options:
      docstring_style: google

### Methods

- **push_entry_reader**: Opens an entry in the detailed reader view
- **load_entries**: Fetches entries from the API

## Navigation Flow

```
MinifluxTUI (App)
├─ EntryListScreen (main view)
│  ├─ navigate with j/k
│  ├─ press Enter → EntryReaderScreen
│  ├─ press ? → HelpScreen
│  └─ press q → exit
├─ EntryReaderScreen (detail view)
│  ├─ navigate with J/K
│  └─ press Escape → back to EntryListScreen
└─ HelpScreen (help view)
  └─ press any key → back to previous screen
```

## Widget Classes

### EntryListItem

Custom ListItem for displaying an entry in the list.

### FeedHeaderItem

Custom ListItem for displaying a feed group header.

Both use CSS-based hiding for collapsed feeds (via the "collapsed" class).

## Styling

The application uses Textual's CSS system. Main styles are defined in:
- `miniflux_tui/ui/app.py` - Application-wide styles
- Screen CSS in individual screen files

Color customization is available through configuration (theme colors).
