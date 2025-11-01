#!/usr/bin/env python3
"""
Diagnostic tool to understand why entries show as "Uncategorized".
Run this to see exactly what the Miniflux API is returning.
"""

import asyncio

from miniflux_tui.api.client import MinifluxClient
from miniflux_tui.config import load_config


async def diagnose():  # noqa: PLR0912, PLR0915
    """Run diagnostic checks on category data."""

    print("=" * 80)
    print("MINIFLUX TUI - CATEGORY DIAGNOSTIC TOOL")
    print("=" * 80)

    # Load config
    try:
        config = load_config()
        if not config:
            print("\n✗ No config found - run 'uv run miniflux-tui --init' first")
            return
        print("\n✓ Config loaded")
        print(f"  Server URL: {config.server_url}")
        print(f"  API Key: {'*' * 20}...")
    except Exception as e:
        print(f"\n✗ Failed to load config: {e}")
        return

    # Create client
    client = MinifluxClient(
        base_url=config.server_url,
        api_key=config.api_key,
        allow_invalid_certs=config.allow_invalid_certs,
    )

    # Test 1: Get categories
    print("\n" + "-" * 80)
    print("TEST 1: Fetching categories...")
    print("-" * 80)
    try:
        categories = await client.get_categories()
        print(f"✓ Fetched {len(categories)} categories")
        for cat in categories:
            print(f"  - ID {cat.id}: {cat.title}")
        if not categories:
            print("  ⚠ WARNING: No categories found!")
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Test 2: Get feeds
    print("\n" + "-" * 80)
    print("TEST 2: Fetching all feeds...")
    print("-" * 80)
    try:
        feeds = await client.get_feeds()
        print(f"✓ Fetched {len(feeds)} feeds")

        # Check if any have category_id
        feeds_with_category = sum(1 for f in feeds if f.category_id is not None)
        feeds_without_category = sum(1 for f in feeds if f.category_id is None)

        print("\n  Category assignment status:")
        print(f"    - With category_id: {feeds_with_category}")
        print(f"    - Without category_id: {feeds_without_category}")

        if feeds_without_category > 0:
            print(f"\n  ⚠ WARNING: {feeds_without_category} feeds don't have category_id!")
            print("  These will appear as 'Uncategorized'")

        print("\n  First 5 feeds:")
        for feed in feeds[:5]:
            cat_str = f"category_id={feed.category_id}" if feed.category_id else "NO CATEGORY_ID"
            print(f"    - ID {feed.id}: {feed.title} ({cat_str})")

        if len(feeds) > 5:
            print(f"    ... and {len(feeds) - 5} more feeds")

    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Test 3: Get entries (unread)
    print("\n" + "-" * 80)
    print("TEST 3: Fetching unread entries...")
    print("-" * 80)
    try:
        entries = await client.get_unread_entries(limit=5)
        print(f"✓ Fetched {len(entries)} unread entries")

        if entries:
            print("\n  First 3 entries and their feed category info:")
            for i, entry in enumerate(entries[:3], 1):
                feed_cat = entry.feed.category_id
                cat_str = f"category_id={feed_cat}" if feed_cat else "NO CATEGORY_ID"
                print(f"    Entry {i}:")
                print(f"      - feed_id: {entry.feed_id}")
                print(f"      - feed.title: {entry.feed.title}")
                print(f"      - feed.category_id: {cat_str}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Test 4: Detailed feed check
    print("\n" + "-" * 80)
    print("TEST 4: Checking if individual feed fetch has more info...")
    print("-" * 80)
    if feeds and feeds_without_category > 0:
        print("Fetching details for first feed without category_id...")
        feed_without_cat = next((f for f in feeds if f.category_id is None), None)
        if feed_without_cat:
            try:
                detailed = await client.get_feed(feed_without_cat.id)
                print(f"✓ Fetched detailed info for feed {detailed.id}: {detailed.title}")
                print(f"  category_id in detailed response: {detailed.category_id}")
                if detailed.category_id:
                    print("  ✓ Individual fetch HAS category_id - fallback method will work!")
                else:
                    print("  ✗ Individual fetch also missing category_id - fallback won't help")
            except Exception as e:
                print(f"✗ Error fetching detailed feed: {e}")
    elif feeds_with_category == len(feeds):
        print("✓ All feeds have category_id - no issues expected")

    # Summary
    print("\n" + "=" * 80)
    print("DIAGNOSIS SUMMARY")
    print("=" * 80)

    if feeds_with_category == len(feeds):
        print("\n✓ STATUS: Category data is complete")
        print("  All feeds have category_id, enrichment should work")
        print("  If you still see 'Uncategorized', the issue is elsewhere")
    elif feeds_without_category > 0:
        print("\n⚠ STATUS: Incomplete category data")
        print(f"  {feeds_without_category}/{len(feeds)} feeds missing category_id")
        print("  App will attempt fallback (fetching individual feeds)")
        print("  If fallback succeeds, categories should appear")
    else:
        print("\n✗ STATUS: No feeds found - check your Miniflux server")

    if len(categories) == 0:
        print("\n✓ NOTE: No categories defined on server")
        print("  Create categories in Miniflux web UI and assign feeds to them")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(diagnose())
