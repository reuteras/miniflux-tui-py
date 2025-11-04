# Usage Guide

## Starting the Application

```bash
miniflux-tui
```

The application will load your feeds and display them in the entry list.

If you installed via the container image, use:

The `latest` tag follows the default branch. Replace it with a release tag (for example `v0.4.0`) if you want to pin a specific version.

```bash
docker run --rm -it \
  -v ~/.config/miniflux-tui:/home/miniflux/.config/miniflux-tui \
  ghcr.io/reuteras/miniflux-tui:latest
```

## Main Screen Layout

The main screen is divided into three sections:

1. **Header** - Shows the application title and current view
2. **Entry List** - The main content area showing your feeds and entries
3. **Footer** - Shows available keyboard shortcuts

## Navigation

### Basic Movement

| Key | Action           |
|-----|------------------|
| `j` | Move cursor down |
| `k` | Move cursor up   |
| `↓` | Move cursor down |
| `↑` | Move cursor up   |

### Opening and Reading Entries

| Key     | Action                                                                         |
|---------|--------------------------------------------------------------------------------|
| `Enter` | Open the selected entry for reading (or first entry in feed if on feed header) |
| `J`     | Next entry (when reading)                                                      |
| `K`     | Previous entry (when reading)                                                  |

## Managing Entries

### Mark as Read/Unread

| Key | Action                                         |
|-----|------------------------------------------------|
| `m` | Toggle read/unread status of the current entry |

When you read an entry, it's automatically marked as read when you navigate away.

### Star/Unstar Entries

| Key | Action                                  |
|-----|-----------------------------------------|
| `*` | Toggle star status of the current entry |

### Save Entries

| Key | Action                                                       |
|-----|--------------------------------------------------------------|
| `e` | Save entry to a third-party service (configured in Miniflux) |

## Viewing Modes

### Sort Mode

Press `s` to cycle through sort modes:

- **Date** - Newest entries first (default)
- **Feed** - Alphabetically by feed name (A-Z), then by date within each feed (newest first)
- **Status** - Unread entries first, then by date (oldest first)

### Group by Feed

Press `g` to toggle grouping by feed. When enabled:

- Entries are grouped under their feed name
- Press `l` to expand a feed and see its entries
- Press `h` to collapse a feed
- Press `o` to toggle a feed's expansion state

### Filter Views

| Key | Action                    |
|-----|---------------------------|
| `u` | Show only unread entries  |
| `t` | Show only starred entries |

Press again to return to all entries in the current feed list.

## Feed Management

### Expand/Collapse Feeds (Grouped Mode)

When in grouped mode (`g` to toggle):

| Key       | Action                                       |
|-----------|----------------------------------------------|
| `l`       | Expand the highlighted feed                  |
| `h`       | Collapse the highlighted feed                |
| `o`       | Toggle expansion of the highlighted feed     |
| `→`       | Expand the highlighted feed (alternative)    |
| `←`       | Collapse the highlighted feed (alternative)  |
| `Shift+G` | Enable grouping by feed and expand all feeds |
| `Shift+Z` | Collapse all feeds                           |

## Category Management

### Accessing Category Management

Press `c` to open the category management screen where you can:

- View all categories
- Create new categories
- Edit category names
- Delete categories

### Category Management Actions

In the category management screen:

| Key       | Action                                           |
|-----------|--------------------------------------------------|
| `j` / `↓` | Move cursor down                                 |
| `k` / `↑` | Move cursor up                                   |
| `n`       | Create new category                              |
| `e`       | Edit the selected category name                  |
| `d`       | Delete the selected category (with confirmation) |
| `Esc`     | Return to entry list                             |

### Organizing Feeds with Categories

You can organize your feeds into categories via the Miniflux web interface or API. Then:

1. Press `c` to open category management
2. Create categories as needed by pressing `n`
3. Assign feeds to categories through Miniflux
4. Press `Shift+C` to group entries by category in the entry list

### Category Information

When deleting a category:
- Feeds in that category will be moved to the default "Uncategorized" category
- No feeds are deleted, only reassigned

## Feed Status and Error Indicators

### Feed Error Badges

When viewing entries in grouped mode, feed headers display status information:
- **⚠ ERRORS**: Feed has parsing errors (shown in yellow)
- **⊘ DISABLED**: Feed is disabled (shown in red)
- **(Category Name)**: Category assignment shown in parentheses

This allows you to quickly identify problematic feeds without opening the status screen.

### Status Screen

For detailed feed health information and error messages:

| Key | Action                                       |
|-----|----------------------------------------------|
| `i` | Show system status with detailed feed health |

The status screen displays:
- Total feed count and health summary
- Detailed list of all problematic feeds
- Error messages and last check timestamps

## Refreshing

| Key | Action                                    |
|-----|-------------------------------------------|
| `r` | Refresh entries from your Miniflux server |
| `,` | Refresh entries (alternative)             |

The refresh will:
1. Fetch the latest entries from your server
2. Preserve your view settings and position
3. Update the display with new/changed entries

## Getting Help

| Key | Action                       |
|-----|------------------------------|
| `?` | Show keyboard shortcuts help |

## Quitting

| Key | Action               |
|-----|----------------------|
| `q` | Quit the application |

## Entry Reader

When you open an entry with `Enter`:

- The entry's full content is displayed in a dedicated view
- Use `J` and `K` (uppercase) to navigate to the next/previous entry in your current list
- The order follows the current sort mode and grouping
- Press `Escape` or `q` to return to the entry list

### Entry Reader Actions

In the entry reader, you can also:

| Key | Action                             |
|-----|------------------------------------|
| `m` | Mark the entry as read/unread      |
| `*` | Toggle star status                 |
| `e` | Save the entry                     |
| `o` | Open in your default browser       |
| `f` | Fetch the original article content |

## Tips and Tricks

### Efficient Navigation

1. **Use grouped mode** - Press `g` to group by feed for easier organization
2. **Collapse inactive feeds** - Press `h` to hide feeds you don't want to read right now
3. **Sort by status** - Press `s` to quickly find unread entries

### Working with Many Entries

1. **Filter by status** - Use `u` for unread or `t` for starred entries
2. **Refresh strategically** - Use `r` to update entries without losing your position
3. **Star for later** - Use `*` to bookmark entries for review later

### Navigation Shortcuts

- Keep your hands on the keyboard - avoid using mouse when possible
- Use `j/k` for precise movement; arrow keys work but j/k is faster
- Use `J/K` in entry reader to quickly scan through articles

## Keyboard Shortcut Reference

Press `?` in the application to see all available shortcuts in a help screen.

## Common Workflows

### Reading Today's News

1. Start the application
2. Press `u` to see only unread entries
3. Use `j/k` to navigate, `Enter` to read
4. Use `m` to mark entries as read as you go
5. Use `*` to star important articles for later reading

### Organizing Feeds

1. Press `g` to enable grouping by feed
2. Press `h` on busy feeds you want to skip
3. Press `l` on feeds you want to catch up on
4. Navigate through visible entries with `j/k`

### Catching Up Quickly

1. Press `u` for unread only
2. Press `s` twice to sort by status (unread first)
3. Use `m` to mark entries as you review them
4. Press `s` to change sort order as needed
