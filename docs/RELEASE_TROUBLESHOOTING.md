# Release Troubleshooting Guide

This guide explains how to handle and recover from failures during the release process.

## Quick Reference

| Issue           | Command                                      | Docs                                        |
|-----------------|----------------------------------------------|---------------------------------------------|
| Tests failing   | `uv run pytest tests --cov=miniflux_tui -vv` | [Test Failures](#test-failures)             |
| Linting errors  | `uv run ruff check miniflux_tui tests`       | [Linting Failures](#linting-failures)       |
| Type errors     | `uv run pyright miniflux_tui tests`          | [Type Check Failures](#type-check-failures) |
| Need to restart | Go back to `main` branch                     | [Restarting Release](#restarting-release)   |

---

## Test Failures

### Problem

During release, you see:

```text
✗ Tests failed. Fix issues before releasing.
```

### Solution

1. **Run tests with verbose output:**
  ```bash
  uv run pytest tests --cov=miniflux_tui -vv
  ```

2. **Analyze the failure:**
- Look for test names with `FAILED` status
- Read the assertion errors carefully
- Check the test file to understand what's being tested

3. **Fix the issue:**
- Edit the relevant source code or test file
- Common issues:
  - Logic bugs in features
  - Missing type hints
  - Incorrect mocks/fixtures
  - Test isolation problems

4. **Verify the fix:**
  ```bash
  # Run just the failed test
  uv run pytest tests/test_file.py::test_name -v

  # Or run all tests
  uv run pytest tests --cov=miniflux_tui
  ```

5. **Commit your fix:**
  ```bash
  git add miniflux_tui/ tests/
  git commit -m "fix: Fix test failure

  [Brief description of what was fixed]"
  ```

6. **Retry the release:**
  ```bash
  uv run python scripts/release.py
  ```

### Common Test Failures

**AsyncIO/Coroutine Issues:**
- Ensure async tests have `@pytest.mark.asyncio` decorator
- Check that fixtures are properly awaited
- Verify mock objects are set up correctly for async code

**Mock/Fixture Issues:**
- Make sure fixtures are properly defined
- Check fixture scope (function, class, module, session)
- Verify mocks return expected values

**Import Errors:**
- Check that all imports are at the top of test files
- Verify module paths are correct
- Look for circular import issues

**Coverage Issues:**
- If coverage is below threshold, add more tests
- Focus on uncovered lines in the failing module
- See [Agent guide: Testing & quality](https://github.com/reuteras/miniflux-tui-py/blob/main/AGENT.md#testing--quality) for additional tips

---

## Linting Failures

### Linting Problem

During release, you see:

```text
✗ Linting failed. Run 'uv run ruff check miniflux_tui tests' to see issues.
```

### Fixing Linting Issues

1. **See all linting errors:**
  ```bash
  uv run ruff check miniflux_tui tests
  ```

2. **Auto-fix common issues:**
  ```bash
  # Many issues can be auto-fixed
  uv run ruff check miniflux_tui tests --fix
  ```

3. **Fix remaining issues manually:**
- Import ordering: Put stdlib imports first, then third-party, then local
- Naming: Use snake_case for variables/functions, PascalCase for classes
- Unused imports: Remove lines that aren't used
- Docstring format: Ensure proper docstring formatting
- Line length: Keep lines under 140 characters

4. **Verify the fixes:**
  ```bash
  uv run ruff check miniflux_tui tests
  ```

5. **Commit your fixes:**
  ```bash
  git add miniflux_tui/ tests/
  git commit -m "chore: Fix linting issues"
  ```

6. **Retry the release:**
  ```bash
  uv run python scripts/release.py
  ```

### Common Linting Issues

**E501 - Line too long:**
```python
# Bad
def function_with_very_long_name_that_exceeds_the_line_length_limit(param1, param2, param3):
  pass

# Good
def function_with_very_long_name(param1, param2, param3):
  pass
```

**F401 - Unused import:**
```python
# Bad
import os
import sys  # Not used

# Good
import os
```

**I001 - Import sorting:**
```python
# Bad
from mymodule import something
import os
from thirdparty import other

# Good
import os
from thirdparty import other
from mymodule import something
```

**S603/S607 - Security with subprocess:**
```python
# Common in release.py - use # noqa: S603, S607
subprocess.run(["git", "push", "origin", "main"])  # noqa: S603, S607
```

---

## Type Check Failures

### Type Check Problem

During release, you see:

```text
✗ Type checking failed. Run 'uv run pyright miniflux_tui tests' to see issues.
```

### Fixing Type Issues

1. **See all type errors:**
  ```bash
  uv run pyright miniflux_tui tests
  ```

2. **Understand the error:**
- Read the error message carefully
- Look for the file path and line number
- Understand what type was expected vs. what was provided

3. **Fix type issues:**
  ```python
  # Bad - missing type hint
  def function(arg):
    return arg.upper()

  # Good
  def function(arg: str) -> str:
    return arg.upper()
  ```

4. **Add type annotations:**
- Function parameters: `def func(x: int) -> str:`
- Class attributes: `name: str = ""`
- List/Dict types: `items: list[str]` or `data: dict[str, int]`

5. **Use TYPE_CHECKING for circular imports:**
  ```python
  from typing import TYPE_CHECKING

  if TYPE_CHECKING:
    from mymodule import MyClass  # Only imported for type checking
  ```

6. **Suppress intentional issues:**
  ```python
  # If you know better than pyright, use noqa comment
  something = cast(str, maybe_none_value)  # type: ignore
  ```

7. **Verify the fixes:**
  ```bash
  uv run pyright miniflux_tui tests
  ```

8. **Commit your fixes:**
  ```bash
  git add miniflux_tui/ tests/
  git commit -m "fix: Add type hints and fix type errors"
  ```

9. **Retry the release:**
  ```bash
  uv run python scripts/release.py
  ```

### Common Type Issues

**Missing type annotations:**
```python
# Bad
def process(data):
  return data[0]

# Good
from typing import Any
def process(data: list[Any]) -> Any:
  return data[0]
```

**Optional/None handling:**
```python
# Bad
def get_name(person):
  return person.name

# Good
from typing import Optional
def get_name(person: dict) -> Optional[str]:
  return person.get("name")
```

**Generic types:**
```python
# Bad
def get_first(items):
  return items[0]

# Good
from typing import TypeVar
T = TypeVar('T')
def get_first(items: list[T]) -> T:
  return items[0]
```

---

## Restarting Release

If something goes wrong or you need to cancel the release process:

### Cancel Release (Before Commit)

If the script exits before running `git commit`, you can just fix the issue and restart:

```bash
# Fix whatever failed
# Then retry
uv run python scripts/release.py
```

### Revert Release (After Commit)

If the script committed but you need to undo everything:

```bash
# Check recent commits
git log --oneline -5

# Undo the last commit (assuming v0.2.1 was the release commit)
git reset --soft HEAD~1

# Undo the version change in pyproject.toml
git checkout HEAD -- pyproject.toml

# Undo changes to CHANGELOG.md if needed
git checkout HEAD -- CHANGELOG.md

# Now you're back to before the release
git status

# Fix the issue, then retry
uv run python scripts/release.py
```

### Revert Push (After Push to GitHub)

If you accidentally pushed a bad release tag:

```bash
# Remove local tag
git tag -d v0.2.1

# Remove remote tag
git push origin --delete v0.2.1

# Remove the commit from main
git reset --hard HEAD~1

# Force push (dangerous - only if main is protected)
# Usually you'll need to use the GitHub web interface to update the branch

# Or revert the commit instead (safer)
git revert HEAD
git push origin main
```

---

## Prevention Tips

### Before Running Release

1. **Create a feature branch:**
  ```bash
  git checkout -b release/v0.2.1
  ```

2. **Test locally first:**
  ```bash
  uv run pytest tests
  uv run ruff check .
  uv run pyright .
  ```

3. **Verify CHANGELOG.md:**
- Make sure it's well-formatted
- Add entry for new version if needed
- Check for typos

4. **Ensure clean working directory:**
  ```bash
  git status
  ```

### During Release

1. **Review suggested version:**
- Release script suggests next patch version
- Press Enter to accept, or type custom version

2. **Review auto-generated changelog:**
- Script can auto-generate from commits
- Review the entries for accuracy
- Can edit manually if needed

3. **Double-check before confirming:**
- Version number is correct
- CHANGELOG.md looks good
- All checks passed

### After Release

1. **Monitor GitHub Actions:**
- Go to <https://github.com/reuteras/miniflux-tui-py/actions>
- Watch the build job
- Verify publish job succeeds

2. **Check PyPI:**
- <https://pypi.org/project/miniflux-tui-py/>
- Verify new version appears (may take 1-2 minutes)
- Check that all files are uploaded

3. **Verify installation:**
  ```bash
  pip install --upgrade miniflux-tui-py
  miniflux-tui --version
  ```

---

## Getting Help

- **Release documentation**: See [RELEASE.md](https://github.com/reuteras/miniflux-tui-py/blob/main/RELEASE.md)
- **Contributing guide**: See [CONTRIBUTING.md](./contributing.md)
- **Project README**: See [README.md](https://github.com/reuteras/miniflux-tui-py/blob/main/README.md)
- **GitHub Issues**: <https://github.com/reuteras/miniflux-tui-py/issues>

If you encounter an issue not covered here, please open a GitHub issue with:
- The exact command you ran
- The full error output
- Steps to reproduce
- Your Python version and OS
