#!/usr/bin/env python3
"""
Generate changelog entries from conventional commits.

This module parses git commits between tags and generates formatted
changelog entries based on conventional commit types.
"""

import re
import subprocess
from datetime import datetime, timezone
from typing import NamedTuple


class Commit(NamedTuple):
    """Represents a parsed commit."""

    commit_type: str  # feat, fix, docs, etc.
    message: str  # Commit message without type prefix
    sha: str  # Commit SHA
    pr_number: str | None  # PR number if mentioned


class CommitGroup(NamedTuple):
    """Group of commits by type."""

    group_name: str
    display_name: str
    commits: list[Commit]


# Mapping of commit types to display names
COMMIT_TYPE_MAP = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "docs": "Documentation",
    "style": "Code Style",
    "refactor": "Refactoring",
    "perf": "Performance",
    "test": "Testing",
    "ci": "CI/CD",
    "chore": "Maintenance",
}


def get_git_log(from_tag: str | None = None, to_tag: str = "HEAD") -> str:
    """Get git log between tags in pretty format."""
    log_range = f"{from_tag}..{to_tag}" if from_tag else to_tag

    try:
        result = subprocess.run(
            ["git", "log", log_range, "--pretty=format:%H|%s"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return ""


def parse_commit(line: str) -> Commit | None:
    """Parse a single commit line from git log."""
    if not line.strip():
        return None

    parts = line.split("|", 1)
    if len(parts) != 2:
        return None

    sha = parts[0][:7]
    subject = parts[1]

    # Parse conventional commit format: type(scope): message
    match = re.match(r"^(\w+)(?:\(.+\))?:\s*(.+?)(?:\s*\(#(\d+)\))?$", subject)
    if not match:
        return None

    commit_type = match.group(1).lower()
    message = match.group(2)
    pr_number = match.group(3)

    return Commit(
        commit_type=commit_type,
        message=message,
        sha=sha,
        pr_number=pr_number,
    )


def group_commits(commits: list[Commit]) -> list[CommitGroup]:
    """Group commits by type."""
    groups_dict: dict[str, list[Commit]] = {}

    for commit in commits:
        if commit.commit_type not in COMMIT_TYPE_MAP:
            continue

        if commit.commit_type not in groups_dict:
            groups_dict[commit.commit_type] = []

        groups_dict[commit.commit_type].append(commit)

    # Return in a consistent order
    return [
        CommitGroup(
            group_name=commit_type,
            display_name=COMMIT_TYPE_MAP[commit_type],
            commits=groups_dict[commit_type],
        )
        for commit_type in ["feat", "fix", "docs", "style", "refactor", "perf", "test", "ci", "chore"]
        if commit_type in groups_dict
    ]


def format_changelog_entry(version: str, from_tag: str | None = None) -> str:
    """Generate a changelog entry for a new version."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")  # noqa: UP017

    # Get commits since last tag
    log_output = get_git_log(from_tag=from_tag, to_tag="HEAD")
    lines = log_output.strip().split("\n")

    # Parse commits
    commits = [parse_commit(line) for line in lines]
    commits = [c for c in commits if c is not None]

    if not commits:
        # No commits found, return a basic template
        return f"""## [{version}] - {timestamp}

### Added
-

### Changed
-

### Fixed
-
"""

    # Group commits by type
    groups = group_commits(commits)

    # Format changelog
    lines_out = [f"## [{version}] - {timestamp}", ""]

    for group in groups:
        lines_out.append(f"### {group.display_name}")
        for commit in group.commits:
            if commit.pr_number:
                line = f"- {commit.message} ([#{commit.pr_number}](https://github.com/reuteras/miniflux-tui-py/pull/{commit.pr_number}))"
            else:
                line = f"- {commit.message}"
            lines_out.append(line)
        lines_out.append("")

    return "\n".join(lines_out)


def get_previous_tag() -> str | None:
    """Get the most recent git tag."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def main() -> None:
    """Demo: show changelog generation for next version."""
    previous_tag = get_previous_tag()
    next_version = "0.3.0"  # Example

    print("=" * 70)
    print(f"Changelog for version {next_version}")
    print("=" * 70)
    print()
    print(format_changelog_entry(next_version, from_tag=previous_tag))


if __name__ == "__main__":
    main()
