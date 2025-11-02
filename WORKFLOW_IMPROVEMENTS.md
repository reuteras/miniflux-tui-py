# GitHub Actions Workflow Improvements

## Current State Assessment ✅

Your GitHub Actions setup is **already excellent** with comprehensive security practices:

- **18 workflow files** covering testing, security, quality, and deployment
- **8 active security scanners**: CodeQL, OSV-Scanner, Bandit, Gitleaks, Trivy, Malcontent, Zizmor, Scorecard
- **Pinned actions** with SHA-256 hashes for supply chain security
- **Step Security Harden Runner** on all critical workflows
- **SBOM generation** with Syft and signing with Cosign
- **735 test functions** across 20 test files
- **55% code coverage** with Codecov integration

## Quick Wins (High Priority)

### 1. Replace Codecov with Free Alternatives

**Problem:** Codecov has rate limits on free tier
**Solution:** Use Coveralls + Self-hosted GitHub Pages + PR Comments

#### Option A: Coveralls (Recommended - No Rate Limits)

```yaml
# Replace Codecov upload in test.yml with:
      - name: Upload coverage to Coveralls
        uses: coverallsapp/github-action@v2
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          path-to-lcov: ./coverage.xml
          format: cobertura
          flag-name: ${{ matrix.os }}-py${{ matrix.python-version }}
          parallel: true

# Add finish job after the test job:
  coverage-finish:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Coveralls Finished
        uses: coverallsapp/github-action@v2
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          parallel-finished: true
```

#### Option B: Self-Hosted + GitHub Pages (100% Free)

```yaml
# Add to test.yml after coverage generation
      - name: Upload coverage artifact
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.os }}-py${{ matrix.python-version }}
          path: coverage.xml

      - name: Coverage comment on PR
        if: github.event_name == 'pull_request'
        uses: py-cov-action/python-coverage-comment-action@v3
        with:
          GITHUB_TOKEN: ${{ github.token }}

# Add new job to deploy to GitHub Pages
  coverage-report:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v5
        with:
          persist-credentials: false

      - name: Download coverage artifacts
        uses: actions/download-artifact@v4
        with:
          pattern: coverage-*
          merge-multiple: true

      - name: Install uv
        uses: astral-sh/setup-uv@v7

      - name: Generate HTML report
        run: |
          uv pip install coverage
          uv run coverage combine
          uv run coverage html

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./htmlcov
          destination_dir: coverage
```

**Benefits:**
- ✅ No rate limits
- ✅ No external service dependencies
- ✅ Full control over reports
- ✅ Beautiful HTML reports at `https://yourname.github.io/repo/coverage/`

### 2. Add Semgrep SAST

Create `.github/workflows/semgrep.yml` for pattern-based security analysis that complements CodeQL:

```yaml
---
name: Semgrep Security Scan

on:
  push:
    branches: [main]
    paths: ['miniflux_tui/**']
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'

permissions:
  contents: read

jobs:
  semgrep:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - name: Harden the runner
        uses: step-security/harden-runner@f4a75cfd619ee5ce8d5b864b0d183aff3c69b55a
        with:
          egress-policy: audit

      - uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8
        with:
          persist-credentials: false

      - name: Run Semgrep
        uses: semgrep/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/python
            p/owasp-top-ten
            p/command-injection
          generateSarif: true

      - name: Upload SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: semgrep.sarif
```

### 3. Add Mutation Testing for Test Quality

Verify that your tests actually catch bugs by adding mutation testing on PRs:

```yaml
# Add to .github/workflows/test.yml as new job
  mutation-testing:
    name: Mutation Testing
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    continue-on-error: true
    steps:
      - name: Harden the runner
        uses: step-security/harden-runner@f4a75cfd619ee5ce8d5b864b0d183aff3c69b55a
        with:
          egress-policy: audit

      - uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8
        with:
          persist-credentials: false

      - name: Install uv
        uses: astral-sh/setup-uv@85856786d1ce8acfbcc2f13a5f3fbd6b938f9f41
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}

      - name: Install dependencies
        run: |
          uv sync --locked
          uv pip install mutmut

      - name: Run mutation tests
        run: |
          uv run mutmut run --paths-to-mutate miniflux_tui --tests-dir tests || true
          uv run mutmut results
          uv run mutmut html

      - name: Upload mutation report
        uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4
        with:
          name: mutation-report
          path: html/
```

## Medium Priority Enhancements

### 4. Replace Super-Linter with MegaLinter

**Problem:** Super-Linter is slower and less configurable
**Solution:** MegaLinter - better performance and actively maintained

```yaml
# Replace Super-Linter in linter.yml with:
  megalinter:
    name: MegaLinter
    runs-on: ubuntu-latest
    steps:
      - name: Harden the runner
        uses: step-security/harden-runner@f4a75cfd619ee5ce8d5b864b0d183aff3c69b55a
        with:
          egress-policy: audit

      - uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8
        with:
          fetch-depth: 0
          persist-credentials: false

      - name: MegaLinter
        uses: oxsecurity/megalinter/flavors/python@v8
        env:
          VALIDATE_ALL_CODEBASE: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          FILTER_REGEX_EXCLUDE: '(CHANGELOG\.md|CLAUDE\.md)'
```

**Benefits:**
- ✅ Faster execution
- ✅ Better caching
- ✅ More linters included
- ✅ Active development

### 5. Code Complexity Analysis

Add to `.github/workflows/linter.yml`:

```yaml
  complexity:
    name: Code Complexity Analysis
    runs-on: ubuntu-latest
    steps:
      - name: Harden the runner
        uses: step-security/harden-runner@f4a75cfd619ee5ce8d5b864b0d183aff3c69b55a
        with:
          egress-policy: audit

      - uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8
        with:
          persist-credentials: false

      - name: Install uv
        uses: astral-sh/setup-uv@85856786d1ce8acfbcc2f13a5f3fbd6b938f9f41

      - name: Install tools
        run: |
          uv sync --locked
          uv pip install radon xenon

      - name: Check cyclomatic complexity
        run: |
          uv run radon cc miniflux_tui -a -nb
          uv run xenon --max-absolute B --max-modules B --max-average A miniflux_tui

      - name: Check maintainability index
        run: uv run radon mi miniflux_tui -nb
```

### 6. License Compliance Checking

Create `.github/workflows/license-check.yml`:

```yaml
---
name: License Compliance

on:
  pull_request:
    paths: ['pyproject.toml', 'uv.lock']
  schedule:
    - cron: '0 0 * * 1'

permissions:
  contents: read

jobs:
  license:
    runs-on: ubuntu-latest
    steps:
      - name: Harden the runner
        uses: step-security/harden-runner@f4a75cfd619ee5ce8d5b864b0d183aff3c69b55a
        with:
          egress-policy: audit

      - uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8
        with:
          persist-credentials: false

      - name: Install uv
        uses: astral-sh/setup-uv@85856786d1ce8acfbcc2f13a5f3fbd6b938f9f41

      - name: Check licenses
        run: |
          uv pip install pip-licenses
          uv run pip-licenses --format=markdown --output-file=licenses.md
          uv run pip-licenses --fail-on="GPL;AGPL;LGPL"

      - name: Upload license report
        uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4
        with:
          name: licenses
          path: licenses.md
```

### 7. Performance Benchmarking

Create `.github/workflows/performance.yml`:

```yaml
---
name: Performance Testing

on:
  pull_request:
    branches: [main]
    paths: ['miniflux_tui/**']

permissions:
  contents: write

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - name: Harden the runner
        uses: step-security/harden-runner@f4a75cfd619ee5ce8d5b864b0d183aff3c69b55a
        with:
          egress-policy: audit

      - uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8
        with:
          persist-credentials: false

      - name: Install uv
        uses: astral-sh/setup-uv@85856786d1ce8acfbcc2f13a5f3fbd6b938f9f41

      - name: Install dependencies
        run: |
          uv sync --locked
          uv pip install pytest-benchmark

      - name: Run benchmarks
        run: uv run pytest tests --benchmark-only --benchmark-json=benchmark.json || true

      - name: Store benchmark result
        uses: benchmark-action/github-action-benchmark@v1
        with:
          tool: 'pytest'
          output-file-path: benchmark.json
          github-token: ${{ secrets.GITHUB_TOKEN }}
          auto-push: false
          comment-on-alert: true
          fail-on-alert: false
```

## Existing Workflow Enhancements

### Improve test.yml

```yaml
# Replace single-threaded pytest with parallel execution
- name: Run tests with coverage
  run: |
    uv pip install pytest-xdist
    uv run pytest tests --cov=miniflux_tui --cov-report=xml \
      --cov-report=term-missing --cov-report=html \
      -n auto --dist=loadscope

# Add coverage differential on PRs
- name: Coverage diff
  if: github.event_name == 'pull_request'
  run: |
    uv pip install diff-cover
    uv run diff-cover coverage.xml --compare-branch=origin/main --fail-under=70
```

### Enhance codeql.yml

```yaml
# Use more comprehensive query suites
- name: Initialize CodeQL
  uses: github/codeql-action/init@0f47cf5ea395a08f5ca3b81a506c66a63ecb648a
  with:
    languages: ${{ matrix.language }}
    queries: security-extended,security-and-quality
    packs: codeql/python-queries:experimental
```

### Enhance dependency-review.yml

```yaml
# Add pip-audit for Python-specific vulnerability scanning
- name: Dependency Review with pip-audit
  run: |
    uv pip install pip-audit
    uv run pip-audit --desc --format json --output audit.json

- name: Upload audit results
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4
  with:
    name: pip-audit
    path: audit.json
```

## Metrics to Track

### New Recommended Metrics

| Metric | Current | Target | Priority |
|--------|---------|--------|----------|
| Code Coverage | 55% | 70%+ | High |
| Mutation Score | - | 70%+ | High |
| Cyclomatic Complexity | - | Max 10 | Medium |
| Test Execution Time | - | <5 min | Medium |
| Type Coverage | - | 90%+ | Low |
| Flaky Test Rate | - | <1% | Low |

## Free & Open Source Tool Stack

### Coverage Reporting (Codecov Alternatives)
| Tool | Free Tier | Rate Limits | Recommendation |
|------|-----------|-------------|----------------|
| **Coveralls** | Unlimited for OSS | None | ⭐ **Recommended** |
| **Codacy** | Unlimited for OSS | None | Good alternative |
| **GitHub Pages** | Unlimited | None | Best for full control |
| **py-cov-action** | Free | None | Perfect for PR comments |

### Linting & Code Quality
| Tool | Current | Alternative | Benefit |
|------|---------|-------------|---------|
| Super-Linter | ✅ | **MegaLinter** | Faster, more features |
| Ruff | ✅ Keep | - | Already best option |
| Pyright | ✅ Keep | - | Already best option |

### Security Scanning (All Free for OSS)
| Category | Tools | Status |
|----------|-------|--------|
| **SAST** | CodeQL ✅, **Semgrep** (add), Bandit ✅ | Excellent |
| **Secrets** | Gitleaks ✅ | Perfect |
| **Dependencies** | OSV-Scanner ✅, **Snyk** (optional) | Very good |
| **Containers** | Trivy ✅, Grype (alternative) | Keep Trivy |
| **Supply Chain** | Scorecard ✅, SBOM ✅, Cosign ✅ | Excellent |
| **Workflows** | Zizmor ✅, Malcontent ✅ | Outstanding |

### Additional Free Tools to Consider
- **Snyk Open Source**: Free tier for open source (comprehensive vuln DB)
- **Socket Security**: Free for OSS (supply chain security)
- **Fossa**: Free for OSS (license compliance)

## Implementation Roadmap

### Week 1 - Coverage Migration (No Breaking Changes)
1. ✅ Add Coveralls alongside Codecov
2. ✅ Add GitHub Pages coverage HTML
3. ✅ Add PR coverage comments
4. ✅ Test parallel execution

### Week 2 - Verify & Switch
5. ✅ Verify Coveralls working correctly
6. ✅ Remove Codecov dependency
7. ✅ Update README badges

### Week 3-4 - Enhanced Security
8. ✅ Add Semgrep workflow
9. ✅ Replace Super-Linter with MegaLinter
10. ✅ Add mutation testing
11. ✅ Enhance CodeQL queries

### Month 2 - Quality Improvements
12. ✅ Add complexity analysis
13. ✅ Add performance benchmarks
14. ✅ Add license compliance
15. ✅ Implement coverage differential

## Cost & Resource Considerations

- **All recommendations use free tools** for open source projects
- **GitHub-hosted runners** are sufficient (no need for self-hosted)
- **Watch execution time**: Mutation testing can be slow, limit to PRs only
- **Artifact storage**: Clean up old artifacts regularly

## Notes

- Your current setup already exceeds most open source projects
- Focus on **test quality** over quantity (mutation testing helps here)
- **Incremental improvements** are better than overwhelming changes
- Keep **security scanners diverse** (you already do this well)

## Questions or Issues?

If implementing any of these improvements, consider:
1. Test on a feature branch first
2. Monitor workflow execution times
3. Adjust thresholds based on your project needs
4. Document any project-specific configurations
