# Usage Guide

## Starting the Application

```bash
miniflux-tui
```

The application will load your feeds and display them in the entry list.

## Main Screen Layout

The main screen is divided into three sections:

1. **Header** - Shows the application title and current view
2. **Entry List** - The main content area showing your feeds and entries
3. **Footer** - Shows available keyboard shortcuts

## Navigation

### Basic Movement

| Key | Action |
|-----|--------|
| `j` | Move cursor down |
| `k` | Move cursor up |
| `↓` | Move cursor down |
| `↑` | Move cursor up |

### Opening and Reading Entries

| Key | Action |
|-----|--------|
| `Enter` | Open the selected entry for reading |
| `J` | Next entry (when reading) |
| `K` | Previous entry (when reading) |

## Managing Entries

### Mark as Read/Unread

| Key | Action |
|-----|--------|
| `m` | Toggle read/unread status of the current entry |

When you read an entry, it's automatically marked as read when you navigate away.

### Star/Unstar Entries

| Key | Action |
|-----|--------|
| `*` | Toggle star status of the current entry |

### Save Entries

| Key | Action |
|-----|--------|
| `e` | Save entry to a third-party service (configured in Miniflux) |

## Viewing Modes

### Sort Mode

Press `s` to cycle through sort modes:

- **Date** - Newest entries first (default)
- **Feed** - Alphabetically by feed name, then by date
- **Status** - Unread entries first, then by date

### Group by Feed

Press `g` to toggle grouping by feed. When enabled:

- Entries are grouped under their feed name
- Press `l` to expand a feed and see its entries
- Press `h` to collapse a feed
- Press `o` to toggle a feed's expansion state

### Filter Views

| Key | Action |
|-----|--------|
| `u` | Show only unread entries |
| `t` | Show only starred entries |

Press again to return to all entries in the current feed list.

## Feed Management

### Expand/Collapse Feeds (Grouped Mode)

When in grouped mode (`g` to toggle):

| Key | Action |
|-----|--------|
| `l` | Expand the highlighted feed |
| `h` | Collapse the highlighted feed |
| `o` | Toggle expansion of the highlighted feed |
| `→` | Expand the highlighted feed (alternative) |
| `←` | Collapse the highlighted feed (alternative) |

## Refreshing

| Key | Action |
|-----|--------|
| `r` | Refresh entries from your Miniflux server |
| `,` | Refresh entries (alternative) |

The refresh will:
1. Fetch the latest entries from your server
2. Preserve your view settings and position
3. Update the display with new/changed entries

## Getting Help

| Key | Action |
|-----|--------|
| `?` | Show keyboard shortcuts help |

## Quitting

| Key | Action |
|-----|--------|
| `q` | Quit the application |

## Entry Reader

When you open an entry with `Enter`:

- The entry's full content is displayed in a dedicated view
- Use `J` and `K` (uppercase) to navigate to the next/previous entry in your current list
- The order follows the current sort mode and grouping
- Press `Escape` or `q` to return to the entry list

### Entry Reader Actions

In the entry reader, you can also:

| Key | Action |
|-----|--------|
| `m` | Mark the entry as read/unread |
| `*` | Toggle star status |
| `e` | Save the entry |
| `o` | Open in your default browser |
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
