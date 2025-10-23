#!/bin/bash
# Run the app with textual console for debugging
textual console &
CONSOLE_PID=$!
sleep 1
uv run miniflux-tui
kill $CONSOLE_PID 2>/dev/null
