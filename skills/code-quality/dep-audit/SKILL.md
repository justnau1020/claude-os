---
name: dep-audit
description: Run a security audit and dependency check on project dependencies. Use when you want to check for vulnerabilities, audit packages, or update outdated dependencies.
disable-model-invocation: true
allowed-tools: Bash(pip *), Bash(pip-audit *), Bash(uv *), Bash(npm *), Bash(npx *)
---

# Dependency Audit

Run a security and freshness audit of project dependencies.

## Steps

### 1. Check for known vulnerabilities

For Python projects:
```bash
pip-audit
```
If pip-audit is not installed: `pip install pip-audit`

For Node.js projects:
```bash
npm audit
```

### 2. Check for outdated packages

For Python:
```bash
pip list --outdated
```

For Node.js:
```bash
npm outdated
```

### 3. Report

For each issue found:
- **Vulnerability**: Package name, CVE ID, severity, affected version, fixed version
- **Outdated**: Package name, current version, latest version, whether upgrade is safe

### 4. Fix recommendations

- For vulnerabilities: upgrade to the fixed version immediately
- For outdated packages: check changelog for breaking changes before upgrading
- Update dependency config (pyproject.toml, package.json, etc.) with new version constraints
- Run the full test suite after any dependency change
