---
name: deploy-status
description: Check the current deployment status, health, and recent CI runs. Use when you want to know if the service is up, check recent CI/CD activity, or diagnose deployment issues.
disable-model-invocation: true
allowed-tools: Bash(curl *), Bash(gh *)
---

# Check Deployment Status

Check the current state of the production deployment.

## Steps

### 1. Health check

```bash
curl -sf https://{PRODUCTION_URL}/health
```

Check for a healthy response (status field, database connectivity, etc.).

### 2. Recent GitHub Actions runs

```bash
gh run list --limit 5
```

Check for any recent failures.

### 3. Report

Provide a clear status summary:
- Is the service up and healthy?
- What was the last deployment and its status?
- Any recent failures in CI?
- If unhealthy, suggest checking the project's runbook for troubleshooting
