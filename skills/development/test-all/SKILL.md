---
name: test-all
description: Run the full CI pipeline locally -- linting, type checking, and tests. Use before commits or deployments to verify everything passes.
disable-model-invocation: true
allowed-tools: Bash(pytest *), Bash(ruff *), Bash(mypy *), Bash(npm *), Bash(npx *)
---

# Run Full CI Pipeline

Run the complete CI pipeline locally in the same order as CI/CD.

## Pipeline Steps (run in order, stop on first failure)

### 1. Lint

Run the project's linter. Examples:
```bash
# Python
ruff check {source_dir}/ tests/

# JavaScript/TypeScript
npx eslint src/
```

If there are auto-fixable issues, report them but do NOT auto-fix unless asked. Show the exact errors.

### 2. Type check

Run the project's type checker. Examples:
```bash
# Python
mypy {source_dir}/ --ignore-missing-imports

# TypeScript
npx tsc --noEmit
```

Report any type errors with file paths and line numbers.

### 3. Run test suite

```bash
# Python
pytest tests/ -v --tb=short

# JavaScript/TypeScript
npm test
```

If `$ARGUMENTS` is provided, pass it as additional arguments:
```bash
pytest tests/ -v --tb=short $ARGUMENTS
```

## Reporting

After all steps complete, provide a summary:

```
CI Pipeline Results:
  Lint:  PASS/FAIL (N issues)
  Types: PASS/FAIL (N errors)
  Tests: PASS/FAIL (N passed, N failed, N skipped)
```

If any step fails, explain what failed and suggest specific fixes. Include file paths and line numbers for all failures.
