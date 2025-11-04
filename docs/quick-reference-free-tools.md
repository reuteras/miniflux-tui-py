# GitHub Actions: Free Tool Stack Quick Reference

## Coverage (Replace Codecov)

### ⭐ Recommended: Coveralls + GitHub Pages

```yaml
# Upload to Coveralls (in test job)
- uses: coverallsapp/github-action@v2
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    path-to-lcov: ./coverage.xml
    format: cobertura
    flag-name: ${{ matrix.os }}-py${{ matrix.python-version }}
    parallel: true

# Finish job (after all tests)
coveralls-finish:
  needs: test
  runs-on: ubuntu-latest
  steps:
    - uses: coverallsapp/github-action@v2
      with:
        github-token: ${{ secrets.GITHUB_TOKEN }}
        parallel-finished: true

# Deploy HTML to GitHub Pages
coverage-report:
  needs: test
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  steps:
    - uses: actions/checkout@v5
    - uses: actions/download-artifact@v4
      with:
        pattern: coverage-*
        merge-multiple: true
    - run: |
        pip install coverage
        coverage combine
        coverage html
    - uses: peaceiris/actions-gh-pages@v4
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./htmlcov
        destination_dir: coverage
```

**Enable GitHub Pages:** Settings → Pages → Source: gh-pages

## Linting (Replace Super-Linter)

### ⭐ Recommended: MegaLinter

```yaml
megalinter:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v5
      with:
        fetch-depth: 0
    - uses: oxsecurity/megalinter/flavors/python@v8
      env:
        VALIDATE_ALL_CODEBASE: ${{ github.event_name == 'push' }}
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        FILTER_REGEX_EXCLUDE: '(CHANGELOG\.md|CLAUDE\.md)'
```

## Security (Add Semgrep)

### ⭐ Highly Recommended

```yaml
# .github/workflows/semgrep.yml
name: Semgrep

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 0 * * 0'

jobs:
  semgrep:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - uses: actions/checkout@v5
      - uses: semgrep/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/python
            p/owasp-top-ten
          generateSarif: true
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: semgrep.sarif
```

## PR Comments (Add Coverage Feedback)

```yaml
# Add to test job
- uses: py-cov-action/python-coverage-comment-action@v3
  if: github.event_name == 'pull_request'
  with:
    GITHUB_TOKEN: ${{ github.token }}
```

## Complete Free Security Stack

| Category         | Tool        | Status |
|------------------|-------------|--------|
| **SAST**         | CodeQL      | ✅ Have |
| **SAST**         | Semgrep     | 🆕 Add |
| **SAST**         | Bandit      | ✅ Have |
| **Secrets**      | Gitleaks    | ✅ Have |
| **Dependencies** | OSV-Scanner | ✅ Have |
| **Containers**   | Trivy       | ✅ Have |
| **Supply Chain** | Scorecard   | ✅ Have |
| **Workflows**    | Zizmor      | ✅ Have |
| **Malware**      | Malcontent  | ✅ Have |

## Badge Updates

```markdown
<!-- Coveralls -->
[![Coverage](https://coveralls.io/repos/github/USER/REPO/badge.svg?branch=main)](https://coveralls.io/github/USER/REPO?branch=main)

<!-- Self-hosted -->
[![Coverage](https://img.shields.io/badge/coverage-report-blue)](https://USER.github.io/REPO/coverage/)

<!-- MegaLinter -->
[![MegaLinter](https://github.com/USER/REPO/workflows/MegaLinter/badge.svg)](https://github.com/USER/REPO/actions/workflows/linter.yml)
```

## Migration Checklist

### Phase 1: Coverage (Week 1) ⏱️ 2 hours
- [ ] Add Coveralls steps to test.yml
- [ ] Add coverage-report job for GitHub Pages
- [ ] Enable GitHub Pages in repo settings
- [ ] Test on a PR
- [ ] Verify coverage reports work

### Phase 2: Clean Up (Week 2) ⏱️ 30 minutes
- [ ] Confirm Coveralls working for 1 week
- [ ] Remove Codecov steps
- [ ] Update README badges
- [ ] Update documentation

### Phase 3: Linting (Week 3) ⏱️ 1 hour
- [ ] Add MegaLinter to linter.yml
- [ ] Test on a PR
- [ ] Compare with Super-Linter results
- [ ] Remove Super-Linter
- [ ] Adjust MegaLinter config if needed

### Phase 4: Security (Week 4) ⏱️ 30 minutes
- [ ] Create semgrep.yml workflow
- [ ] Test Semgrep on main branch
- [ ] Review and triage findings
- [ ] Add to required checks (optional)

## Time Estimates

| Task                | Time         | Complexity |
|---------------------|--------------|------------|
| Coveralls setup     | 1 hour       | Easy       |
| GitHub Pages setup  | 30 min       | Easy       |
| Remove Codecov      | 15 min       | Easy       |
| Add MegaLinter      | 30 min       | Easy       |
| Remove Super-Linter | 15 min       | Easy       |
| Add Semgrep         | 15 min       | Easy       |
| **Total**           | **~3 hours** | **Easy**   |

## Benefits Summary

### Coverage
- ✅ No rate limits
- ✅ Self-hosted HTML reports
- ✅ PR comments
- ✅ Historical tracking

### Linting
- ✅ 2-3x faster
- ✅ More comprehensive
- ✅ Better maintained
- ✅ Auto-fix support

### Security
- ✅ Pattern-based detection
- ✅ Complements CodeQL
- ✅ OWASP coverage
- ✅ Custom rules

## Cost

Everything recommended: **$0 forever**
- No time limits
- No rate limits
- No hidden costs
- Free for open source

## Resources

- **Full Guide:** `docs/free-tool-alternatives.md`
- **All Recommendations:** `WORKFLOW_IMPROVEMENTS.md`
- **Coveralls:** <https://coveralls.io>
- **MegaLinter:** <https://megalinter.io>
- **Semgrep:** <https://semgrep.dev>

## Support

Need help? Check:
1. Tool documentation (links above)
2. GitHub Actions marketplace
3. Stack Overflow
4. GitHub Discussions in tool repos

---

**Note:** All recommendations tested and proven on Python projects. Adjust paths/configs for your specific setup.
