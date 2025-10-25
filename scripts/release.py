#!/usr/bin/env python3
"""
miniflux-tui-py Release Script

Automates the release process:
1. Validates current state (tests, linting, types)
2. Updates version in pyproject.toml
3. Prompts to update CHANGELOG.md
4. Creates commit and git tag
5. Pushes to GitHub (triggers PyPI publish)
"""

import platform
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class Colors:
    """ANSI color codes"""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"


def print_header(text: str) -> None:
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{'━' * 70}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'━' * 70}{Colors.NC}\n")


def print_success(text: str) -> None:
    """Print a success message"""
    print(f"{Colors.GREEN}✓{Colors.NC} {text}")


def print_error(text: str) -> None:
    """Print an error message"""
    print(f"{Colors.RED}✗{Colors.NC} {text}")


def print_info(text: str) -> None:
    """Print an info message"""
    print(f"{Colors.YELLOW}[i]{Colors.NC} {text}")


def run_command(cmd: list[str], description: str = "", show_output: bool = False) -> bool:
    """Run a command and return success status"""
    try:
        subprocess.run(  # noqa: S603
            cmd,
            check=True,
            capture_output=not show_output,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        if description:
            print_error(f"{description} failed")
        if not show_output and hasattr(e, "stderr") and e.stderr:
            print(f"  {e.stderr}")
        return False


def get_current_version() -> str:
    """Get current version from pyproject.toml"""
    toml_path = Path("pyproject.toml")
    if not toml_path.exists():
        print_error("pyproject.toml not found")
        sys.exit(1)

    content = toml_path.read_text()
    match = re.search(r'version = "([0-9.]+)"', content)
    if not match:
        print_error("Could not find version in pyproject.toml")
        sys.exit(1)

    return match.group(1)


def validate_version(version: str) -> bool:
    """Validate semantic versioning format"""
    return bool(re.match(r"^\d+\.\d+\.\d+$", version))


def check_git_status() -> bool:
    """Check if git working directory is clean"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],  # noqa: S607
            check=True,
            capture_output=True,
            text=True,
        )
        return len(result.stdout.strip()) == 0
    except subprocess.CalledProcessError:
        return False


def update_version(new_version: str) -> bool:
    """Update version in pyproject.toml"""
    toml_path = Path("pyproject.toml")
    content = toml_path.read_text()
    current_version = get_current_version()

    new_content = re.sub(
        f'version = "{re.escape(current_version)}"',
        f'version = "{new_version}"',
        content,
    )

    if new_content == content:
        return False

    toml_path.write_text(new_content)
    return True


def edit_changelog(new_version: str) -> bool:
    """Open CHANGELOG for editing"""
    changelog_path = Path("CHANGELOG.md")
    if not changelog_path.exists():
        print_error("CHANGELOG.md not found")
        return False

    print_info("Opening CHANGELOG.md for editing...")
    print("Add a new section at the top for version", new_version)
    release_date = datetime.now(datetime.UTC).strftime("%Y-%m-%d")
    print(
        f"""
Example format:

## [{new_version}] - {release_date}

### Added
- Feature description

### Changed
- Improvement description

### Fixed
- Bug fix description
"""
    )

    # Open in default editor
    try:
        if platform.system() == "Windows":
            subprocess.run(["notepad", str(changelog_path)], check=True)  # noqa: S603, S607
        elif platform.system() == "Darwin":
            subprocess.run(  # noqa: S603
                ["open", "-a", "TextEdit", str(changelog_path)],  # noqa: S607
                check=True
            )
        else:
            # Try common Linux editors
            for editor in ["nano", "vim", "vi"]:
                try:
                    subprocess.run([editor, str(changelog_path)], check=True)  # noqa: S603
                    break
                except FileNotFoundError:
                    continue
    except Exception as e:
        print_error(f"Could not open editor: {e}")
        print_info("Please edit CHANGELOG.md manually and run this script again")
        return False

    # Verify changelog was updated
    content = changelog_path.read_text()
    if f"[{new_version}]" not in content:
        print_error("CHANGELOG.md was not updated")
        return False

    return True


def main() -> None:  # noqa: PLR0915
    """Main release process"""
    # Check if in git repo
    if not Path(".git").exists():
        print_error("Not in a git repository")
        sys.exit(1)

    print_header("miniflux-tui-py Release Script")

    # Get current version
    current_version = get_current_version()
    print_info(f"Current version: {current_version}")

    # Prompt for new version
    print(f"\n{Colors.YELLOW}Enter new version (e.g., 0.2.1):{Colors.NC}")
    new_version = input("New version: ").strip()

    if not validate_version(new_version):
        print_error("Invalid version format. Use semantic versioning (e.g., 0.2.1)")
        sys.exit(1)

    print_success(f"Version validated: {new_version}")

    # Check git status
    if not check_git_status():
        print_error("Working directory is not clean. Please commit or stash changes first.")
        sys.exit(1)

    print_header("Pre-Release Checks")

    # Run tests
    print_info("Running tests...")
    if not run_command(
        ["uv", "run", "pytest", "tests", "--cov=miniflux_tui", "-q"],
        "Tests",
    ):
        print_error("Tests failed. Fix issues before releasing.")
        sys.exit(1)
    print_success("All tests passed")

    # Run linting
    print_info("Running ruff linting...")
    if not run_command(
        ["uv", "run", "ruff", "check", "miniflux_tui", "tests"],
        "Linting",
    ):
        print_error("Linting failed. Run 'uv run ruff check miniflux_tui tests' to see issues.")
        sys.exit(1)
    print_success("Linting passed")

    # Run type checking
    print_info("Running type checking...")
    if not run_command(
        ["uv", "run", "pyright", "miniflux_tui", "tests"],
        "Type checking",
    ):
        print_error("Type checking failed. Run 'uv run pyright miniflux_tui tests' to see issues.")
        sys.exit(1)
    print_success("Type checking passed")

    print_header("Updating Files")

    # Update version in pyproject.toml
    print_info("Updating version in pyproject.toml...")
    if not update_version(new_version):
        print_error("Could not update version in pyproject.toml")
        sys.exit(1)
    print_success(f"Version updated: {current_version} → {new_version}")

    # Edit CHANGELOG
    print_header("Edit CHANGELOG")
    if not edit_changelog(new_version):
        # Revert version change if changelog edit failed
        update_version(current_version)
        sys.exit(1)
    print_success(f"CHANGELOG updated with version {new_version}")

    print_header("Creating Release")

    # Stage changes
    run_command(["git", "add", "pyproject.toml", "CHANGELOG.md"])
    print_success("Files staged for commit")

    # Create commit message
    commit_msg = f"chore: Release v{new_version}"
    full_msg = f"""{commit_msg}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"""

    # Commit
    run_command(["git", "commit", "-m", full_msg])
    print_success(f"Commit created: {commit_msg}")

    # Create git tag
    tag_msg = f"Release v{new_version}\n\nSee CHANGELOG.md for detailed changes."
    run_command(["git", "tag", "-a", f"v{new_version}", "-m", tag_msg])
    print_success(f"Git tag created: v{new_version}")

    # Push changes and tag
    print_info("Pushing changes and tag to origin...")
    run_command(["git", "push", "origin", "main"])
    run_command(["git", "push", "origin", f"v{new_version}"])
    print_success("Changes and tag pushed to GitHub")

    print_header("Release Complete! 🚀")
    print(f"{Colors.GREEN}{'━' * 70}{Colors.NC}")
    print(f"Version:      {Colors.GREEN}v{new_version}{Colors.NC}")
    print(f"Release Tag:  {Colors.GREEN}v{new_version}{Colors.NC}")
    print(
        f"GitHub:       {Colors.GREEN}https://github.com/reuteras/miniflux-tui-py/releases/tag/v{new_version}{Colors.NC}"
    )
    print(
        f"PyPI:         {Colors.GREEN}https://pypi.org/project/miniflux-tui-py/{new_version}/{Colors.NC}"
    )
    print(f"{Colors.GREEN}{'━' * 70}{Colors.NC}")

    print(f"\n{Colors.YELLOW}What happens next:{Colors.NC}")
    print("1. GitHub Actions will automatically:")
    print("   ✓ Run all tests")
    print("   ✓ Check linting and types")
    print("   ✓ Build distribution packages")
    print("   ✓ Publish to PyPI")
    print("   ✓ Create GitHub Release with artifacts")
    print("")
    print("2. Monitor the workflow at:")
    print("   https://github.com/reuteras/miniflux-tui-py/actions")
    print("")
    print("3. Check PyPI after publishing (usually within 1-2 minutes):")
    print("   https://pypi.org/project/miniflux-tui-py/")
    print("")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        print_error("Release cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
