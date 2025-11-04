# Free and Open Source Tool Alternatives - REFERENCE

> **Note**: This project has already implemented all the tools mentioned in this guide.
> This document is kept as a reference for other projects or future considerations.

## Current State (November 2025)

✅ **Coveralls** - Implemented and active
✅ **GitHub Pages Coverage** - Implemented
✅ **Semgrep** - Implemented
✅ **MegaLinter** - Replaced Super-Linter
✅ **Mutation Testing** - Implemented with mutmut
✅ **License Compliance** - Implemented with pip-licenses
✅ **Performance Benchmarking** - Implemented with pytest-benchmark

---

## Coverage: Coveralls + GitHub Pages (IMPLEMENTED ✅)

### Why Replace?
- Codecov has rate limits on free tier
- Occasional service outages
- External dependency

### Recommended: Coveralls + GitHub Pages + PR Comments

This combination gives you everything Codecov provides, with no limits:

#### Step 1: Add Coveralls

```yaml
# In test.yml, replace Codecov with:
      - name: Upload coverage to Coveralls
        uses: coverallsapp/github-action@v2
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          path-to-lcov: ./coverage.xml
          format: cobertura
          flag-name: ${{ matrix.os }}-py${{ matrix.python-version }}
          parallel: true

# Add a finish job after the test job:
  coverage-finish:
    needs: test
    runs-on: ubuntu-latest
    if: always()
    steps:
      - name: Coveralls Finished
        uses: coverallsapp/github-action@v2
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          parallel-finished: true
```

#### Step 2: Add GitHub Pages HTML Reports

```yaml
# Add new job in test.yml:
  coverage-report:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    permissions:
      contents: write
    steps:
      - name: Harden the runner
        uses: step-security/harden-runner@f4a75cfd619ee5ce8d5b864b0d183aff3c69b55a
        with:
          egress-policy: audit

      - uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8
        with:
          persist-credentials: false

      - name: Download coverage artifacts
        uses: actions/download-artifact@v4
        with:
          pattern: coverage-*
          merge-multiple: true

      - name: Install uv
        uses: astral-sh/setup-uv@v7

      - name: Generate HTML coverage report
        run: |
          uv pip install coverage
          uv run coverage combine
          uv run coverage html --directory=htmlcov

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./htmlcov
          destination_dir: coverage
          enable_jekyll: false
```

#### Step 3: Add PR Comments

```yaml
# Add to test job in test.yml after coverage generation:
      - name: Coverage comment on PR
        if: github.event_name == 'pull_request'
        uses: py-cov-action/python-coverage-comment-action@v3
        with:
          GITHUB_TOKEN: ${{ github.token }}
          MINIMUM_GREEN: 80
          MINIMUM_ORANGE: 60
```

#### Step 4: Enable GitHub Pages

1. Go to repository Settings → Pages
2. Source: Deploy from a branch
3. Branch: `gh-pages` / `root`
4. Save

Your coverage reports will be at: `https://[username].github.io/[repo]/coverage/`

#### Step 5: Update README Badge

```markdown
<!-- Replace Codecov badge with: -->
[![Coverage Status](https://coveralls.io/repos/github/[username]/[repo]/badge.svg?branch=main)](https://coveralls.io/github/[username]/[repo]?branch=main)

<!-- Or link to GitHub Pages: -->
[![Coverage Report](https://img.shields.io/badge/coverage-report-blue)](https://[username].github.io/[repo]/coverage/)
```

### Alternative: 100% Self-Hosted (No External Service)

If you want zero external dependencies:

```yaml
  coverage:
    runs-on: ubuntu-latest
    needs: test
    if: always()
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v5
        with:
          persist-credentials: false

      - name: Download all coverage artifacts
        uses: actions/download-artifact@v4
        with:
          pattern: coverage-*
          merge-multiple: true

      - name: Install coverage tools
        run: |
          pip install coverage coverage-badge

      - name: Combine coverage
        run: |
          coverage combine
          coverage xml
          coverage html
          coverage report

      - name: Generate badge
        if: github.ref == 'refs/heads/main'
        run: coverage-badge -o coverage.svg -f

      - name: PR Comment
        if: github.event_name == 'pull_request'
        uses: py-cov-action/python-coverage-comment-action@v3
        with:
          GITHUB_TOKEN: ${{ github.token }}

      - name: Deploy reports
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./htmlcov
          destination_dir: coverage

      - name: Commit badge
        if: github.ref == 'refs/heads/main'
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          file_pattern: coverage.svg
          commit_message: "Update coverage badge [skip ci]"
```

## Linting: Replace Super-Linter with MegaLinter

### Why Replace?
- Super-Linter is slower
- Less actively maintained
- Limited configuration options

### MegaLinter Implementation

```yaml
# Replace Super-Linter job in linter.yml with:
  megalinter:
    name: MegaLinter
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
      pull-requests: write
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
        id: ml
        uses: oxsecurity/megalinter/flavors/python@v8
        env:
          VALIDATE_ALL_CODEBASE: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          FILTER_REGEX_EXCLUDE: '(CHANGELOG\.md|CLAUDE\.md)'
          # Optional: Disable specific linters
          DISABLE_LINTERS: SPELL_CSPELL,MARKDOWN_MARKDOWNLINT
          # Python-specific configs
          PYTHON_RUFF_CONFIG_FILE: pyproject.toml
          PYTHON_MYPY_CONFIG_FILE: pyproject.toml

      - name: Upload MegaLinter artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: MegaLinter reports
          path: |
            megalinter-reports
            mega-linter.log
```

### Benefits
- ✅ 50+ linters in one
- ✅ Faster with better caching
- ✅ Auto-fix capabilities
- ✅ Better PR comments
- ✅ Detailed HTML reports

## Container Scanning: Trivy vs Grype

Both are excellent and free. Grype is slightly faster:

### Add Grype (Alternative to Trivy)

```yaml
# In container-image.yml, replace or add alongside Trivy:
      - name: Scan with Grype
        uses: anchore/scan-action@v4
        id: scan
        with:
          image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}@${{ steps.build.outputs.digest }}
          fail-build: true
          severity-cutoff: high
          output-format: sarif
          only-fixed: true

      - name: Upload Grype SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: ${{ steps.scan.outputs.sarif }}
          category: grype
```

**Recommendation:** Keep Trivy - it's already excellent. Only switch if you need different features.

## Security: Add Free SAST Tools

### Semgrep (Highly Recommended)

Free tier is generous for open source:

```yaml
# .github/workflows/semgrep.yml
---
name: Semgrep Security Scan

on:
  push:
    branches: [main]
    paths: ['miniflux_tui/**', 'tests/**']
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
            p/secrets
          generateSarif: true

      - name: Upload SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: semgrep.sarif
          category: semgrep
```

### Snyk (Optional - Free for OSS)

```yaml
# .github/workflows/snyk.yml
---
name: Snyk Security Scan

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 0 * * 0'

permissions:
  contents: read

jobs:
  snyk:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - uses: actions/checkout@v5
        with:
          persist-credentials: false

      - name: Run Snyk
        uses: snyk/actions/python@master
        continue-on-error: true
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --sarif-file-output=snyk.sarif --all-projects

      - name: Upload SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: snyk.sarif
          category: snyk
```

## Complete Free Stack Summary

### Essential (Already Have)
- ✅ **CodeQL** - SAST (GitHub native)
- ✅ **OSV-Scanner** - Vulnerability DB
- ✅ **Gitleaks** - Secret scanning
- ✅ **Bandit** - Python security
- ✅ **Trivy** - Container scanning
- ✅ **Scorecard** - Supply chain
- ✅ **Zizmor** - Workflow security

### Recommended Additions
- ⭐ **Semgrep** - Pattern-based SAST
- ⭐ **Coveralls** - Coverage tracking
- ⭐ **MegaLinter** - Multi-language linting
- ⭐ **GitHub Pages** - Self-hosted reports

### Optional Enhancements
- **Snyk** - Additional vulnerability scanning
- **Grype** - Alternative container scanner
- **Socket Security** - Supply chain analysis
- **Fossa** - License compliance

## Migration Checklist

### Phase 1: Coverage (Week 1)
- [ ] Set up Coveralls account (free)
- [ ] Add Coveralls workflow steps
- [ ] Enable GitHub Pages
- [ ] Add PR comment action
- [ ] Test on a PR
- [ ] Verify coverage reports work
- [ ] Update README badges

### Phase 2: Remove Codecov (Week 2)
- [ ] Confirm Coveralls working for 1 week
- [ ] Remove Codecov token
- [ ] Remove Codecov workflow steps
- [ ] Update documentation

### Phase 3: Enhanced Linting (Week 3)
- [ ] Add MegaLinter configuration
- [ ] Test MegaLinter on PR
- [ ] Compare results with Super-Linter
- [ ] Switch to MegaLinter
- [ ] Remove Super-Linter

### Phase 4: Security (Week 4)
- [ ] Add Semgrep workflow
- [ ] Test Semgrep findings
- [ ] Add Snyk (optional)
- [ ] Review all security findings

## Cost Comparison

| Tool             | Free Tier     | Limits                | Best For       |
|------------------|---------------|-----------------------|----------------|
| **Coveralls**    | Unlimited     | None                  | OSS projects   |
| **Codecov**      | Limited       | Rate limits           | May hit limits |
| **MegaLinter**   | Unlimited     | None                  | All projects   |
| **Super-Linter** | Unlimited     | Slower                | Basic needs    |
| **Semgrep**      | Generous      | Some features paid    | Security focus |
| **Snyk**         | OSS unlimited | Private repos limited | Vuln scanning  |
| **GitHub Pages** | Unlimited     | None                  | Full control   |

## FAQ

**Q: Will I lose coverage history switching from Codecov?**
A: Coveralls will start fresh, but GitHub Pages will maintain historical reports as commits.

**Q: Is Coveralls really unlimited?**
A: Yes, for public/open source repositories. No rate limits, no usage caps.

**Q: What about private repos?**
A: For private repos, use the self-hosted GitHub Pages approach - completely free.

**Q: Can I use multiple coverage services?**
A: Yes! You can upload to both Coveralls and self-host. No conflicts.

**Q: How long does migration take?**
A: Coverage migration: 1-2 hours. Full stack migration: 1-2 weeks testing everything.

## Support

- Coveralls: <https://coveralls.io>
- MegaLinter: <https://megalinter.io>
- Semgrep: <https://semgrep.dev>
- GitHub Pages: <https://pages.github.com>

## Conclusion

The recommended free stack provides:
- ✅ **No rate limits** on any service
- ✅ **No external dependencies** (can be 100% self-hosted)
- ✅ **Better performance** (MegaLinter, parallel testing)
- ✅ **More features** (Semgrep patterns, detailed reports)
- ✅ **Full control** (GitHub Pages hosting)

Your data stays in your control, and you'll never hit usage limits.
