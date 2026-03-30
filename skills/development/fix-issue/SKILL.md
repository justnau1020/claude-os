---
name: fix-issue
description: Fix a GitHub issue end-to-end -- read the issue, implement the fix, write tests, and create a commit. Use when you want to fix a specific GitHub issue, resolve a bug report, or implement a feature request.
disable-model-invocation: true
argument-hint: <issue-number>
allowed-tools: Bash(gh *), Bash(pytest *), Bash(git *)
---

# Fix GitHub Issue

Fix issue #$ARGUMENTS end-to-end.

## Steps

### 1. Read the issue

```bash
gh issue view $ARGUMENTS
```

Understand the problem, expected behavior, and any reproduction steps.

### 2. Research the codebase

Find the relevant files using the issue description. Read the code to understand the current behavior and what needs to change.

### 3. Implement the fix

- Follow the project's existing conventions and patterns
- Make minimal, focused changes -- fix the bug, don't refactor surrounding code
- Add type hints to any new code

### 4. Write or update tests

- Add a test that would have caught this bug
- Verify existing tests still pass
- Mock external APIs -- no real network calls

### 5. Verify

Run the project's CI pipeline locally:
```bash
# Adjust these commands to match your project's tooling
pytest tests/ -v --tb=short
# lint check
# type check
```

### 6. Create a commit

Stage only the files you changed and commit with a message referencing the issue:

```
Fix #$ARGUMENTS: <brief description of what was fixed>
```

Do NOT push -- let the user decide when to push.
