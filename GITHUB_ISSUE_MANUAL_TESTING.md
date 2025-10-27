# GitHub Issue: Manual Testing Checklist for Pre-Release

**Use this content to create a GitHub issue manually**

---

## Title

Pre-Release Manual Testing Checklist

---

## Labels

`testing`, `documentation`, `process`, `quality assurance`

---

## Assignee

@reuteras (or your GitHub username)

---

## Issue Body

### Summary

This issue tracks the manual testing checklist that must be completed before each minor (0.x.0) or major (x.0.0) release of miniflux-tui-py. This ensures all critical functionality works correctly before publishing to PyPI.

**Note:** Patch releases (0.0.x) for bug fixes do not require the full checklist unless they involve significant changes.

### Testing Materials

Two testing checklists are available in the repository:

1. **`PRE_RELEASE_TEST_CHECKLIST.md`** - Essential tests for minor/major releases (~45-60 min)
    - Critical functionality verification
    - Major features testing
    - Cross-platform checks
    - Performance benchmarks
    - Documentation verification

2. **`MANUAL_TEST_CHECKLIST.md`** - Comprehensive testing guide (~2-4 hours)
    - Complete feature coverage
    - Edge cases and error handling
    - Performance testing
    - Accessibility checks
    - Useful for major releases or significant refactors

### Testing Requirements

#### Before Each Minor/Major Release:

- [ ] Complete `PRE_RELEASE_TEST_CHECKLIST.md`
- [ ] Test on at least 2 platforms (Linux, macOS, or Windows)
- [ ] Verify all critical functionality passes
- [ ] Document any issues found
- [ ] Ensure all CI/CD checks pass
- [ ] Update CHANGELOG.md with test results summary

#### Test Environments:

**Required:**
- Python 3.11, 3.12, 3.13
- At least 2 different operating systems
- At least 2 different terminal emulators

**Recommended:**
- Test with different Miniflux server versions
- Test with various feed counts (small: <10, medium: 10-50, large: 50+)
- Test with different network conditions (fast, slow, intermittent)

### Testing Process

1. **Pre-Testing Setup:**
    - [ ] Ensure test Miniflux server is accessible
    - [ ] Have feeds with various states (unread, starred, errors)
    - [ ] Clear any local config to test fresh installation
    - [ ] Document testing environment details

2. **Execute Tests:**
    - [ ] Follow `PRE_RELEASE_TEST_CHECKLIST.md` step by step
    - [ ] Mark items as complete
    - [ ] Document any failures or issues
    - [ ] Record performance metrics

3. **Document Results:**
    - [ ] Fill out "Test Results" section in checklist
    - [ ] Create GitHub issues for any bugs found
    - [ ] Add test summary to release notes
    - [ ] Update this issue with test results

4. **Sign-Off:**
    - [ ] Tester approval
    - [ ] Maintainer approval
    - [ ] All critical issues resolved or documented
    - [ ] Ready for release

### Success Criteria

A release is ready when:

✅ All items in "Critical Functionality" section pass
✅ All items in "Major Features" section pass
✅ Testing completed on at least 2 platforms
✅ No critical issues found, or all critical issues resolved
✅ Documentation is accurate and up-to-date
✅ CI/CD pipeline passes all checks
✅ Performance benchmarks within acceptable ranges

### Test Results Log

#### Version 0.x.0 (Target Release: YYYY-MM-DD)

**Tester:** [Name]
**Date Tested:** [Date]
**Platforms:** [Linux/macOS/Windows]
**Result:** [ ] PASS / [ ] FAIL

**Issues Found:**
- Issue #XXX: [Brief description]
- Issue #YYY: [Brief description]

**Notes:**
[Any additional observations]

---

#### Version 0.x+1.0 (Target Release: YYYY-MM-DD)

**Tester:** [Name]
**Date Tested:** [Date]
**Platforms:** [Linux/macOS/Windows]
**Result:** [ ] PASS / [ ] FAIL

**Issues Found:**
- Issue #XXX: [Brief description]

**Notes:**
[Any additional observations]

---

### Related Documentation

- `PRE_RELEASE_TEST_CHECKLIST.md` - Essential pre-release tests
- `MANUAL_TEST_CHECKLIST.md` - Comprehensive manual testing guide
- `RELEASE.md` - Release process documentation
- `CHANGELOG.md` - Version history and changes
- `CONTRIBUTING.md` - Contribution guidelines

### Automation Goals (Future)

While manual testing is currently required, we aim to automate more tests over time:

- [ ] Automated integration tests for critical paths
- [ ] Automated UI testing with Textual test framework
- [ ] Performance regression testing in CI/CD
- [ ] Cross-platform testing in GitHub Actions

However, manual testing will always be needed for:
- User experience validation
- Visual/rendering checks
- Real-world usage scenarios
- Exploratory testing

### Questions or Issues?

If you have questions about the testing process:
- Comment on this issue
- Check `CONTRIBUTING.md` for testing guidelines
- Review past test results in this issue's log

### Checklist Template

For each release, copy this template and fill it out:

```markdown
### Testing for Version X.Y.Z

**Target Release Date:** YYYY-MM-DD
**Tester:** @username
**Platforms Tested:** [ ] Linux [ ] macOS [ ] Windows

#### Pre-Testing
- [ ] Test environment prepared
- [ ] Fresh installation tested
- [ ] Documentation reviewed

#### Critical Tests
- [ ] All critical functionality tests pass
- [ ] All major features work correctly
- [ ] Error handling tested
- [ ] Performance acceptable

#### Platform-Specific
- [ ] Linux: All tests pass
- [ ] macOS: All tests pass (if applicable)
- [ ] Windows: All tests pass (if applicable)

#### Documentation
- [ ] README accurate
- [ ] CHANGELOG updated
- [ ] Help screen matches functionality

#### Final Status
**Result:** [ ] APPROVED FOR RELEASE [ ] NOT READY

**Critical Issues:** None / See issues #X, #Y
**Notes:** [Any observations]
```

---

### References

- Related to release process: See `RELEASE.md`
- Testing framework: Pytest (see `tests/` directory)
- CI/CD: `.github/workflows/test.yml`

---

**This issue should remain open** to track testing across all releases. Add new test results as comments for each version.
