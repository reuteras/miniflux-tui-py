# Changelog

## [0.5.5] - 2025-11-04

### BUG FIXES

- Remove hash-based container tags and add release notes (#400)
- Disable Red Hat YAML telemetry prompts in Codespaces (#402)
- Improve Codespaces configuration for test discovery (#404)
- Add scraping helper (Shift+X) to entry reader screen (#408)
- Change scraping helper binding from shift+x to X (#409)
- Change scraping helper binding from shift+x to X (#409) (#411)
- improve content scraper UI layout (#421)
- add extra pause in test to wait for loading screen (#422)
- change shift+key bindings to uppercase keys (#424)
- resolve MegaLinter formatting warnings (#425)

### CI/CD

- ensure detached signatures uploaded (#417)
- restrict workflow token permissions (#416)
- add Python 3.14 to test matrix (#420)

### DOCUMENTATION

- Add comprehensive scraping helper feature documentation
- add last commit badge to README (#419)

### FEATURES

- Interactive scraping rule helper for content extraction (#405)
- Integrate scraping helper into entry list (closes #391) (#406)
- Add ASCII art loading screen on startup (#418)
- add __main__.py module and clarify running methods (#426)
- add automatic pagination for >100 entries and fix arrow key navigation (#427)

### TESTING

- Phase 2 - Comprehensive UI screen tests (#391) (#403)



#### Contributors

Thank you to everyone who contributed to this release!

**Humans:** 👤 Peter Reuterås

**AI & Automation:** 🤖 Claude (AI Assistant)

## [0.5.4] - 2025-11-03

### DOCUMENTATION

- Comprehensively document release process (#397)

### MAINTENANCE

- Release v0.5.3 (#396)



#### Contributors

Thank you to everyone who contributed to this release!

**Humans:** 👤 Peter Reuterås

**AI & Automation:** 🤖 Claude (AI Assistant)

## [0.5.3] - 2025-11-03

### BUG FIXES

- Address remaining 10 code scanning security alerts (#329)
- Resolve remaining code scanning security alerts to achieve zero alerts (#332)
- Add dependabot[bot] to auto-approve workflow to fix auto-merge (#348)
- Restrict auto-merge to verified dependabot[bot] account type (#349)
- Resolve cyclic import warnings with Protocol-based app interface (#353)
- Exclude CodeQL config from YAML v8r schema validation (#355)
- Exclude .yaml-lint.yml from YAML v8r schema validation (#357)
- Remove ellipsis statements from Protocol methods to resolve code scanning alerts (#359)
- Clean up Codespaces configuration (#361)
- Use raise NotImplementedError in Protocol methods (#363)
- Configure VS Code to run pytest via uv in Codespaces (#364)
- Exclude problematic YAML files from v8r schema validation (#368)
- Add pytest path to workspace settings for reliable test discovery (#369)
- Use unique coverage filenames to prevent overwriting during merge (#371)
- Set VALIDATE_ALL_CODEBASE to true in MegaLinter (#374)
- Add pull-requests write permission for coverage comments (#378)
- Update VS Code test plugin configuration for proper pytest discovery
- Set VALIDATE_ALL_CODEBASE to true in MegaLinter (#374)
- Add pull-requests write permission for coverage comments (#378)
- Enable editorconfig-checker in pre-commit hooks (#380)
- Add final newline to .vscode/settings.json
- Remove merge-multiple to preserve coverage data files (#381)
- Start groups collapsed when toggling group by category/feed (#383)
- Remove Python 3.14 from test matrix (#389)
- Rewrite history screen to extend EntryListScreen and sort by read time (#390)
- Copy .coverage file for python-coverage-comment-action (#393)
- Run coverage-report job only on PRs, not main pushes (#394)
- Require git-cliff and fix configuration (#395)

### FEATURES

- Auto-close Dependabot tracking issues when PRs are merged (#347)
- Add comprehensive GitHub labels configuration (#372)
- Enhance pre-commit checks to catch more errors before CI (#377)
- Enhance pre-commit checks to catch more errors before CI (#377)
- Replace custom changelog generator with git-cliff (#385)

### MAINTENANCE

- bump actions/setup-python from 5.1.0 to 6.0.0 (#338) 🤖
- bump actions/github-script from 7.0.1 to 8.0.0 (#339) 🤖
- bump actions/checkout from 4.2.2 to 5.0.0 (#344) 🤖
- bump chainguard-dev/actions (#342) 🤖
- Increase dependabot cooldown from 1 to 4 days (#351)
- Use "explicit" instead of true for VS Code code actions (#373)

### REFACTORING

- Rename MinifluxTUI class to MinifluxTuiApp for clarity (#336)
- Use uvx for tool execution instead of pip install + run (#346)

### TESTING

- Add key binding tests and coverage analysis (#392)



#### Contributors

Thank you to everyone who contributed to this release!

**Humans:** 👤 Peter Reuterås

**AI & Automation:** 🤖 Claude (AI Assistant), dependabot[bot] (Dependencies)

## [0.5.2] - 2025-11-02

### Added
-

### Changed
-

### Fixed
-


## [0.5.1] - 2025-11-02

### Features
- Add Dependabot PR to Issue tracker workflow ([#304](https://github.com/reuteras/miniflux-tui-py/pull/304))
- Configure Renovate to group all updates into single PR with labels ([#297](https://github.com/reuteras/miniflux-tui-py/pull/297))
- Add mutation testing for test quality verification ([#252](https://github.com/reuteras/miniflux-tui-py/pull/252))
- Enhance CodeQL and add pip-audit to dependency review ([#266](https://github.com/reuteras/miniflux-tui-py/pull/266))
- Add Renovate workflow for automated dependency updates
- Add coverage differential and parallel testing ([#258](https://github.com/reuteras/miniflux-tui-py/pull/258))
- Add performance benchmarking with pytest-benchmark ([#257](https://github.com/reuteras/miniflux-tui-py/pull/257))
- Add code complexity analysis to CI ([#251](https://github.com/reuteras/miniflux-tui-py/pull/251))
- Implement entry history view screen (Issue #56) ([#253](https://github.com/reuteras/miniflux-tui-py/pull/253))
- Add license compliance checking workflow ([#250](https://github.com/reuteras/miniflux-tui-py/pull/250))
- Implement user settings management screen (Issue #57) ([#249](https://github.com/reuteras/miniflux-tui-py/pull/249))
- Add Coveralls and GitHub Pages for coverage tracking ([#240](https://github.com/reuteras/miniflux-tui-py/pull/240))
- Replace Super-Linter with MegaLinter ([#242](https://github.com/reuteras/miniflux-tui-py/pull/242))
- Add Semgrep SAST security scanning ([#241](https://github.com/reuteras/miniflux-tui-py/pull/241))
- Add cosign signing and SLSA provenance to release workflow ([#230](https://github.com/reuteras/miniflux-tui-py/pull/230))

### Bug Fixes
- address outstanding code scanning alerts ([#314](https://github.com/reuteras/miniflux-tui-py/pull/314))
- guard entry browser launches against unsafe URLs ([#312](https://github.com/reuteras/miniflux-tui-py/pull/312))
- Enable Dependabot auto-merge for all dependency updates ([#306](https://github.com/reuteras/miniflux-tui-py/pull/306))
- Remove remaining invalid configuration options from Renovate and Dependabot ([#301](https://github.com/reuteras/miniflux-tui-py/pull/301))
- Remove invalid Renovate configuration options ([#299](https://github.com/reuteras/miniflux-tui-py/pull/299))
- Remove invalid configuration option blocking Renovate ([#291](https://github.com/reuteras/miniflux-tui-py/pull/291))
- Enable Renovate PR recreation for merged PRs (#268) ([#289](https://github.com/reuteras/miniflux-tui-py/pull/289))
- Fix Renovate PR creation with BOT_TOKEN and config fixes ([#287](https://github.com/reuteras/miniflux-tui-py/pull/287))
- Remove external Renovate config override and use immediate schedules (#268) ([#286](https://github.com/reuteras/miniflux-tui-py/pull/286))
- Enable all Renovate dependency updates without schedule delays ([#285](https://github.com/reuteras/miniflux-tui-py/pull/285))
- Resolve Renovate dependency issues and code quality problems ([#283](https://github.com/reuteras/miniflux-tui-py/pull/283))
- Resolve MegaLinter validation failures (#281) ([#282](https://github.com/reuteras/miniflux-tui-py/pull/282))
- Add markdown-link-check ignore patterns for dead links ([#280](https://github.com/reuteras/miniflux-tui-py/pull/280))
- Fix YAML and markdown linting violations across workflows and templates ([#279](https://github.com/reuteras/miniflux-tui-py/pull/279))
- Wrap bare URLs in angle brackets for markdown linting compliance ([#277](https://github.com/reuteras/miniflux-tui-py/pull/277))
- Add vulnerability alerts permission and configuration to Renovate ([#274](https://github.com/reuteras/miniflux-tui-py/pull/274))
- Update GitHub Actions workflows for compatibility ([#273](https://github.com/reuteras/miniflux-tui-py/pull/273))
- Add workflows permission to Renovate job ([#269](https://github.com/reuteras/miniflux-tui-py/pull/269))
- Add pytest-benchmark to dev dependencies ([#272](https://github.com/reuteras/miniflux-tui-py/pull/272))
- Resolve pyright type errors in entry_history.py ([#271](https://github.com/reuteras/miniflux-tui-py/pull/271))
- Add RENOVATE_REPOSITORIES env var to explicitly specify repo ([#267](https://github.com/reuteras/miniflux-tui-py/pull/267))
- Add RENOVATE_CONFIG_FILE environment variable to workflow
- Remove configurationFile parameter from Renovate workflow
- Correct datetime handling in entry_history.py (Issue #260) ([#261](https://github.com/reuteras/miniflux-tui-py/pull/261))
- Use generateSarif parameter for Semgrep output ([#259](https://github.com/reuteras/miniflux-tui-py/pull/259))
- Update Renovate config to extend shared preset and fix GitHub Actions hashing (#254) ([#255](https://github.com/reuteras/miniflux-tui-py/pull/255))
- Update Renovate config to extend shared preset and add missing managers ([#254](https://github.com/reuteras/miniflux-tui-py/pull/254))
- Add category header enter key support for consistent grouping behavior ([#244](https://github.com/reuteras/miniflux-tui-py/pull/244))
- Fix grouping by category expand/collapse and improve keybinding UX ([#233](https://github.com/reuteras/miniflux-tui-py/pull/233))
- Remove commit SHA tags from Docker container images ([#228](https://github.com/reuteras/miniflux-tui-py/pull/228))
- Prioritize version tags over commit SHA in Docker container builds ([#225](https://github.com/reuteras/miniflux-tui-py/pull/225))

### Documentation
- Update roadmap to reflect v0.5.0 release completion ([#248](https://github.com/reuteras/miniflux-tui-py/pull/248))
- Update roadmap to reflect v0.5.0 release completion

### CI/CD
- Add workflow to retroactively add bot reviews to closed PRs ([#231](https://github.com/reuteras/miniflux-tui-py/pull/231))

### Maintenance
- bump oxsecurity/megalinter from 8 to 9 ([#303](https://github.com/reuteras/miniflux-tui-py/pull/303))
- Pin GitHub Actions to commit hashes with version comments ([#309](https://github.com/reuteras/miniflux-tui-py/pull/309))
- bump coverallsapp/github-action from 2.3.0 to 2.3.6 ([#302](https://github.com/reuteras/miniflux-tui-py/pull/302))
- Update ghcr.io/astral-sh/uv:latest Docker digest to ba4857b ([#292](https://github.com/reuteras/miniflux-tui-py/pull/292))
- Update mcr.microsoft.com/devcontainers/python Docker tag to v3.14 ([#294](https://github.com/reuteras/miniflux-tui-py/pull/294))
- migrate config .renovaterc.json ([#296](https://github.com/reuteras/miniflux-tui-py/pull/296))
- Update docker/dockerfile Docker tag to v1.19 ([#293](https://github.com/reuteras/miniflux-tui-py/pull/293))
- Remove Codecov and archive workflow improvements ([#270](https://github.com/reuteras/miniflux-tui-py/pull/270))
- Improve Renovate configuration for better dependency management ([#246](https://github.com/reuteras/miniflux-tui-py/pull/246))


## [0.5.0] - 2025-11-01

### Features
- Implement v0.5.0 category support and feed management enhancements ([#217](https://github.com/reuteras/miniflux-tui-py/pull/217))
- Phase 2 - Comprehensive category management implementation ([#216](https://github.com/reuteras/miniflux-tui-py/pull/216))
- Phase 1 feed management with security hardening (#58) ([#215](https://github.com/reuteras/miniflux-tui-py/pull/215))
- Comprehensive developer experience improvements
- Add sponsorship support and improved badges

### Bug Fixes
- Enable malcontent to run on all PRs ([#222](https://github.com/reuteras/miniflux-tui-py/pull/222))
- Add explanatory comment to empty except clause ([#218](https://github.com/reuteras/miniflux-tui-py/pull/218))
- Remove path filters from linter.yml to ensure build check runs ([#219](https://github.com/reuteras/miniflux-tui-py/pull/219))
- Force refresh of OpenSSF Best Practices badge cache
- Create release as draft to allow asset uploads

### Documentation
- Improve scorecard workflow comments for clarity

### Maintenance
- Configure Renovate for dependency automation ([#214](https://github.com/reuteras/miniflux-tui-py/pull/214))
- Add auto-approve workflow for solo developer ([#212](https://github.com/reuteras/miniflux-tui-py/pull/212))


## [0.5.0] - 2025-10-31

### Features
- Add comprehensive category management support with CRUD operations
- Add category filtering to entry list for viewing entries by category
- Display category information in feed headers alongside error indicators
- Add feed error indicators to entry list headers (yellow ⚠ for parsing errors, red ⊘ for disabled feeds)
- Category-based grouping for organizing entries by category hierarchy
- Enhanced feed header display with category and error status badges

### Improvements
- Better visual feedback for feed health status in the main entry list
- Improved feed organization with category and error indicators visible at a glance
- Enhanced feed management workflow with category-aware operations

### Documentation
- Comprehensive category management documentation in usage guide
- Updated keyboard shortcut reference with category-specific commands
- Added section for feed status and error indicators
- Enhanced API documentation for category operations

## [0.4.22] - 2025-10-31

### Features
- Add GitHub issue templates for bugs and features

### Bug Fixes
- Wrap bare email URL in angle brackets for markdown linting
- use correct syft flags --source-name and --source-version

### Documentation
- Add SUPPORT.md community health file


## [0.4.21] - 2025-10-30

### Added
-

### Changed
-

### Fixed
-


## [0.4.20] - 2025-10-30

### Bug Fixes
- use syft flags supported by v1.36.0 ([#200](https://github.com/reuteras/miniflux-tui-py/pull/200))

### CI/CD
- disable credential persistence in malcontent workflow ([#199](https://github.com/reuteras/miniflux-tui-py/pull/199))
- add malcontent diff workflow ([#198](https://github.com/reuteras/miniflux-tui-py/pull/198))

### Maintenance
- bump syft to v1.46.1


## [0.4.19] - 2025-10-30


## [0.4.18] - 2025-10-29

### CI/CD
- improve sbom generation and release reruns ([#188](https://github.com/reuteras/miniflux-tui-py/pull/188))


## [0.4.17] - 2025-10-29

### CI/CD
- ensure release sbom step handles binary artifacts ([#185](https://github.com/reuteras/miniflux-tui-py/pull/185))

### Maintenance
- Release v0.4.16 ([#186](https://github.com/reuteras/miniflux-tui-py/pull/186))


## [0.4.16] - 2025-10-29

### CI/CD
- ensure release sbom step handles binary artifacts ([#185](https://github.com/reuteras/miniflux-tui-py/pull/185))


## [0.4.15] - 2025-10-29

### Bug Fixes
- detect branch protection in release ([#182](https://github.com/reuteras/miniflux-tui-py/pull/182))
- detect branch protection in release ([#180](https://github.com/reuteras/miniflux-tui-py/pull/180))
- detect branch protection in release

### Maintenance
- Release v0.4.14 ([#183](https://github.com/reuteras/miniflux-tui-py/pull/183))


## [0.4.14] - 2025-10-29

### Bug Fixes
- detect branch protection in release ([#182](https://github.com/reuteras/miniflux-tui-py/pull/182))
- detect branch protection in release ([#180](https://github.com/reuteras/miniflux-tui-py/pull/180))
- detect branch protection in release


## [0.4.13] - 2025-10-29

### Bug Fixes
- detect branch protection in release


## [0.4.12] - 2025-10-29

### Features
- load api token via password command ([#178](https://github.com/reuteras/miniflux-tui-py/pull/178))
- load api token via password command ([#177](https://github.com/reuteras/miniflux-tui-py/pull/177))
- publish standalone binaries

### Bug Fixes
- address code scanning alerts ([#179](https://github.com/reuteras/miniflux-tui-py/pull/179))
- handle tomllib type errors in config parsing
- satisfy lint and add healthcheck
- surface git push failures

### CI/CD
- fix gitleaks and zizmor regressions ([#175](https://github.com/reuteras/miniflux-tui-py/pull/175))
- expand security coverage ([#166](https://github.com/reuteras/miniflux-tui-py/pull/166))
- limit workflows to relevant paths ([#165](https://github.com/reuteras/miniflux-tui-py/pull/165))
- update cifuzz action pins
- quote fuzz extras install
- install clang for fuzzing workflow
- avoid installing fuzz extras in docs workflow
- add CIFuzz workflow and configuration fuzz target
- remove unsupported editorconfig options
- tighten publish workflow token permissions ([#143](https://github.com/reuteras/miniflux-tui-py/pull/143))
- run uv sync with locked lockfile

### Maintenance
- migrate config .renovaterc.json ([#176](https://github.com/reuteras/miniflux-tui-py/pull/176))
- bump actions/attest-build-provenance from 1.4.4 to 3.0.0 ([#168](https://github.com/reuteras/miniflux-tui-py/pull/168))
- fix CIFuzz workflow and docs indentation
- restore unreleased changelog section
- refresh container base image tooling
- align uv lockfile with project version
- Release v0.4.11
- sync uv metadata after release
- Release v0.4.9


## [Unreleased]

### Added
-

### Changed
-

### Fixed
-


## [0.4.11] - 2025-10-28

### Added
-

### Changed
-

### Fixed
-


## [0.4.9] - 2025-10-28

### Features
- publish standalone binaries
- publish signed container image

### CI/CD
- align container image publishing


## [0.4.8] - 2025-10-28

### Bug Fixes
- Add attestations:write permission for GitHub attestations


## [0.4.7] - 2025-10-28

### Fixed
- Correct release title template (remove invalid `$RELEASE_TITLE` variable) ([#131](https://github.com/reuteras/miniflux-tui-py/pull/131))
- Add GitHub attestations for cryptographic build provenance ([#131](https://github.com/reuteras/miniflux-tui-py/pull/131))
- Restore PyPI attestations (was accidentally removed) ([#131](https://github.com/reuteras/miniflux-tui-py/pull/131))

## [0.4.6] - 2025-10-28

### Changed
- Standardize macOS config path to `~/.config/miniflux-tui/config.toml` (same as Linux) ([#127](https://github.com/reuteras/miniflux-tui-py/pull/127))
  - Previous path: `~/Library/Application Support/miniflux-tui/config.toml`
  - Existing macOS users need to move their config file to the new location

### Security
- Fix CodeQL security alert by implementing principle of least privilege for GitHub Actions token permissions ([#129](https://github.com/reuteras/miniflux-tui-py/pull/129))
- Raise minimum supported versions for runtime and documentation dependencies (textual, miniflux, html2text, mkdocs suite) to address upstream advisories highlighted by Dependabot

## [0.4.5] - 2025-10-27

### Features
- Add feed status screen showing server info and problematic feeds ([#104](https://github.com/reuteras/miniflux-tui-py/pull/104))
- Implement feed-specific refresh for v0.5.0 (Issue #55) ([#93](https://github.com/reuteras/miniflux-tui-py/pull/93))

### Bug Fixes
- break cyclic import for CodeQL ([#106](https://github.com/reuteras/miniflux-tui-py/pull/106))
- Replace example.com with localhost in tests to prevent DNS lookups ([#94](https://github.com/reuteras/miniflux-tui-py/pull/94))
- Update Renovate SLSA constraint to only allow versions <=2.0.0 ([#88](https://github.com/reuteras/miniflux-tui-py/pull/88))

### Documentation
- Add comprehensive release process section to AGENT.md ([#100](https://github.com/reuteras/miniflux-tui-py/pull/100))

### CI/CD
- allow manual zizmor runs ([#105](https://github.com/reuteras/miniflux-tui-py/pull/105))
- harden workflows per zizmor findings ([#102](https://github.com/reuteras/miniflux-tui-py/pull/102))

### Maintenance
- repo housekeeping and headless smoke test ([#101](https://github.com/reuteras/miniflux-tui-py/pull/101))
- repo housekeeping and headless smoke test ([#97](https://github.com/reuteras/miniflux-tui-py/pull/97))
- align agent guide and entry list tests ([#96](https://github.com/reuteras/miniflux-tui-py/pull/96))
- Bump astral-sh/setup-uv from 7.1.1 to 7.1.2 ([#92](https://github.com/reuteras/miniflux-tui-py/pull/92))
- Bump github/codeql-action from 3.31.0 to 4.31.0 ([#90](https://github.com/reuteras/miniflux-tui-py/pull/90))
- Bump actions/checkout from 4.3.0 to 5.0.0 ([#89](https://github.com/reuteras/miniflux-tui-py/pull/89))
- Configure Renovate to exclude SLSA v2.1.0 ([#87](https://github.com/reuteras/miniflux-tui-py/pull/87))
- Update Renovate to exclude only SLSA v2.1.0
- Configure Renovate to exclude SLSA v2.1.0


## [0.4.4] - 2025-10-26

### Bug Fixes

- Downgrade SLSA action to v2.0.0 (v2.1.0 has incompatible directory structure)
- Improve system information widget update in help screen

## [0.4.3] - 2025-10-26

### Security & Infrastructure

- **SLSA Provenance**: Added automatic SLSA provenance generation for released
  artifacts (supply chain security)
- **Signed Releases**: All release artifacts now include cryptographic proof of
  provenance
- **Code Review**: Enforced code review on main branch (1 approval required)
- **Scorecard**: Improved OpenSSF Scorecard compliance

### Features

- **Application Version Display**: Shows app version from pyproject.toml in help
  screen
- **Server Information**: Displays Miniflux server version and API version in
  help
- **System Information**: Shows Python version, platform, and Textual framework
  version
- **User Display**: Shows current username from Miniflux server

### Improvements

- Branch protection rules enhanced with signed commit requirements
- GitHub Actions pinned to commit SHAs via Renovate Bot
- Pre-commit hooks configured for code quality
- Better error handling in async operations

### Dependency Updates

- Updated SLSA framework to v2.1.0 via Renovate

### Testing & Quality

- All 465 tests passing
- Code passes ruff linting and pyright type checking
- No security vulnerabilities detected

## [0.4.2] - 2025-10-26

### Security Documentation

- Added comprehensive security documentation (docs/security.md)
- OpenSSF Scorecard improvements and best practices
- CII Best Practices badge integration

## [0.4.0] - 2025-10-26

### Major Features

- **Search Functionality**: Full-text search across entry titles and content
  (Phase 2)
- **Enhanced Theme Support**: Comprehensive test coverage for color
  customization (Phase 3)
- **Improved Test Coverage**: Increased from 78% to 79% with 465 total tests
  (Phase 1)

### Features & Improvements

- Added `/` keybinding for search mode toggle
- Implemented `set_search_term()` method for programmatic search
- Search integrates with existing status filters (unread/starred)
- Added 10 search integration tests (Phase 2)
- Added 5 theme configuration tests (Phase 3)
- Added 24 entry_reader integration tests (Phase 1)

### Testing & Quality

- Phase 1: Improved test coverage to 80% for entry_reader.py
- Phase 2: Added comprehensive search functionality tests
- Phase 3: Added theme configuration integration tests
- Total tests: 465 (up from 426)
- Coverage: 79% (maintained from Phase 1)
- All quality checks passing (ruff, pyright, pytest)

### Bug Fixes & Refactoring

- Search filter properly integrates with existing filters
- Theme colors persist across config reloads
- All pre-commit hooks passing

### Documentation

- Documented search functionality
- Updated configuration examples with search and theme options
- All tests documented with clear descriptions

## [0.3.0] - 2025-10-26

### Major Achievements

- **Comprehensive Test Suite**: Reached 74% overall test coverage (403 tests)
- **Perfect Coverage**: 8 core modules at 100% coverage (api/client, config,
  utils, performance, etc.)
- **Production Ready**: All quality checks passing (ruff, pyright, pytest)

### Testing & Quality

- Achieved 100% coverage for ui/app.py (was 90%)
- Achieved 100% coverage for help.py (was 18%)
- Achieved 100% coverage for performance.py (was 59%)
- Improved overall coverage from ~55% to 74%
- Added comprehensive on_mount and load_entries lifecycle tests
- All 403 tests passing with 0 regressions

### Infrastructure

- Automated CI/CD with GitHub Actions
- Type checking with pyright (0 errors)
- Linting with ruff (all checks passing)
- Test coverage tracking with pytest-cov
- PyPI publishing with OIDC

### Documentation

- Complete MkDocs site with Material theme
- API reference documentation
- Installation and usage guides
- Contributing guidelines
- Security policies

## [0.2.9] - 2025-10-26

### Features

- Refactor long functions for improved readability
- Extract repeated code patterns from screens
- Apply consistent error handling to entry_list screen
- Apply retry logic to all API client methods

### Bug Fixes

- Add type hints to test assertions for mypy compliance

### Testing

- Add 22 comprehensive tests for entry_list helpers
- Add comprehensive tests for cursor position restoration

## [0.2.8] - 2025-10-25

### Bug Fixes

- Resolve linting errors and navigation persistence bug

## [0.2.7] - 2025-10-25

### Features

- Add expand/collapse all feeds in group mode
- Add expand/collapse all feeds in group mode
- Add Python 3.15 preview testing without blocking releases

### Bug Fixes

- Handle None value for list_view.index in type checking
- Wrap bare URLs in markdown links in RELEASE.md checklist
- Find entries by ID not object identity when restoring cursor
- Don't reset cursor index to 0 in _populate_list
- Properly restore cursor position to entry in grouped mode
- Resolve linting errors and navigation persistence bug
- Defer ListView focus and cursor restoration to prevent navigation hang in
  grouped mode
- Resolve markdown linting errors and prevent IndexError on entry list screen
- Restore ListView focus when returning from entry reader
- Restore ListView focus when returning from entry reader
- Resolve all remaining markdown linter errors
- Fix markdown linter errors

## [0.2.6] - 2025-10-25

### Fixed

- Linter errors in Markdown files.

## [0.2.5] - 2025-10-25

### Bug Fixes

- Download artifacts in release job for GitHub Release creation

## [0.2.4] - 2025-10-25

### Fixed

- Relase scripts

## [0.2.3] - 2025-10-25

### Features

- Update release script defaults per user preferences

### Bug Fixes

- Remove bash release script and fix test indentation

## [0.2.2] - 2025-10-25

### Features

- Add changelog automation from conventional commits

### Bug Fixes

- Use timezone.utc instead of datetime.UTC for Python 3.11 compatibility

### Documentation

- Add release troubleshooting guide and update README

All notable changes to miniflux-tui-py will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2025-10-25

Small fix for .gitignore

## [0.2.0] - 2025-10-25

### Added

- **Comprehensive Test Coverage Expansion (Phases 1-4)**
  - **Phase 1:** Added 22 tests for `api/client.py`
    - Async API client initialization and configuration
    - Feed management operations (fetch, create, update, delete)
    - Entry operations (listing, retrieval, status changes)
    - Error handling and edge cases
  - **Phase 2:** Added 32 tests for `main.py` and expanded `config.py` to 100%
    - CLI argument parsing (--init, --check-config, --version, --help)
    - Configuration initialization and validation
    - Application startup and error handling
    - Platform-specific configuration paths (Linux, macOS, Windows)
    - Comprehensive configuration options (colors, sorting, grouping)
  - **Phase 3:** Added 40 tests for UI screens
    - Entry reader screen with HTML to Markdown conversion
    - Scrolling actions and navigation
    - Entry management (mark read/unread, star, save)
    - Help screen with keyboard bindings
    - Screen composition and binding verification
  - **Phase 4:** Added 50 tests for entry list screen
    - `EntryListItem` and `FeedHeaderItem` widget classes
    - Sorting modes (by date, feed, status)
    - Filtering (unread only, starred only)
    - Grouping by feed with fold/unfold operations
  - Cursor navigation and visibility control
  - Incremental updates and position persistence

### Changed

- **Coverage Metrics:** Overall test coverage increased from 22% to 56%

  - `api/client.py`: 0% → 100%
  - `config.py`: 43% → 100%
  - `main.py`: 0% → 98%
  - `api/models.py`: 0% → 100%
  - `constants.py`: 0% → 100%
  - `utils.py`: 0% → 100%
  - `ui/screens/entry_list.py`: 22% → 43%
  - `ui/screens/entry_reader.py`: 26% → 34%

- **CI Configuration:** Updated GitHub Actions workflow

  - Coverage threshold increased from 35% → 40% → 50% → 55%
  - Added permission constraints
  - Improved test reporting

- **Code Quality:** Strict adherence to linting and type checking

  - All code passes `ruff` linting
  - All code passes `pyright` type checking
  - Pre-commit hooks enforced

### Fixed

- Entry ordering when using grouping mode (now uses `sorted_entries`
  consistently)
- Cursor navigation in grouped mode (properly skips hidden entries)
- Position persistence when returning from entry reader
- Incremental update performance for single entry changes

### Testing

- Total test count: 215 tests across all modules
- Test frameworks: pytest with asyncio support
- Coverage reporting: XML format for CI/CD integration
- Multi-version testing: Python 3.11, 3.12, 3.13

## [0.1.1] - 2025-10-01

### Added

- Initial project structure with Python TUI framework (Textual)
- Async Miniflux API client wrapper
- Entry list screen with sorting and grouping
- Entry reader screen with HTML to Markdown conversion
- Help screen with keyboard shortcuts
- Configuration management with platform-specific paths
- Basic testing setup

### Features

- **Entry Management**

  - View feed entries in a terminal UI
  - Mark entries as read/unread
  - Toggle starred status
  - Save entries to third-party services

- **Sorting & Filtering**

  - Sort by date (newest first)
  - Sort by feed (alphabetically)
  - Sort by status (unread first)
  - Filter by unread or starred

- **Navigation**

  - Vim-style key bindings (j/k for navigation)
  - Arrow key support
  - Feed grouping with collapse/expand
  - Position persistence

- **Configuration**

  - TOML-based configuration
  - Customizable colors (unread/read)
  - Theme preferences
  - Server and API key setup
