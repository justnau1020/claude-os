---
name: review-pr
description: Review a pull request for correctness, convention compliance, and test coverage. Use when you want to review a PR, check code quality, or get feedback on changes before merging.
disable-model-invocation: true
context: fork
agent: Explore
argument-hint: <pr-number>
allowed-tools: Bash(gh *)
---

# Review Pull Request

Review PR #$ARGUMENTS for correctness and convention compliance.

## PR Context

- PR diff: !`gh pr diff $ARGUMENTS 2>/dev/null || echo "Could not fetch PR diff"`
- PR description: !`gh pr view $ARGUMENTS 2>/dev/null || echo "Could not fetch PR"`
- Changed files: !`gh pr diff $ARGUMENTS --name-only 2>/dev/null || echo "Could not list files"`

## Review Checklist

For each changed file, verify:

### Correctness
- Does the code do what the PR description claims?
- Are there any logic errors or edge cases missed?
- Are error paths handled properly?

### Conventions
- Are datetimes handled consistently (UTC internally)?
- Are error messages specific and actionable?
- Is async used properly (no sync I/O in async paths)?
- Are type hints present on all new functions?
- Are typed models used for data structures (not raw dicts)?

### Tests
- Are new features covered by tests?
- Are edge cases tested?
- Are external APIs mocked (no real network calls)?

### Security
- Are authorization checks enforced on new endpoints?
- Are there any secrets or API keys in the diff?
- Is input validation present?

## Output

Provide a structured review:
1. **Summary**: One-line assessment (approve/request changes)
2. **Issues**: Specific problems with file paths and line numbers
3. **Suggestions**: Optional improvements (clearly marked as non-blocking)
