---
name: deploy
description: Deploy to production. Runs pre-deploy safety checks, pushes to trigger CI/CD, and monitors the deployment.
disable-model-invocation: true
allowed-tools: Bash(git *), Bash(gh *), Bash(curl *), Bash(pytest *), Bash(ruff *), Bash(mypy *), Bash(npm *)
---

# Deploy to Production

**WARNING: This deploys to the live production environment.**

## Pre-Deploy Checklist

Before pushing, verify ALL of these pass:

1. **Tests pass**: Run the full test suite
2. **Lint clean**: Run the project's linter with no errors
3. **Types clean**: Run the type checker with no errors (if applicable)
4. **On deploy branch**: `git branch --show-current` must be the deploy branch (usually `main`)
5. **Working tree clean**: `git status` shows no uncommitted changes
6. **Up to date**: `git pull origin main` has no conflicts

If ANY check fails, stop and report the issue. Do NOT proceed with deployment.

## Deploy

Push to the deploy branch to trigger the CI/CD pipeline:

```bash
git push origin main
```

## Monitor

1. **Watch CI**: `gh run list --limit 1` -- wait for the run to complete
2. **Check run status**: `gh run view <run-id>` -- verify all jobs pass
3. **Health check**: After CI completes, wait 60 seconds then:
   ```bash
   curl -sf https://{PRODUCTION_URL}/health
   ```
4. Expected healthy response includes a status field indicating the service is running

## If Deployment Fails

1. Check CI logs: `gh run view <run-id> --log-failed`
2. If the app is down, refer to the project's runbook for rollback procedures
3. Quick rollback: revert the commit and push again

## Reference

Check the project's `deploy/` directory or ops documentation for full operational procedures.
