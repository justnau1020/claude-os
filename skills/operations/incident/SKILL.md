---
name: incident
description: Guide through security incident or outage response. Use when there is a security incident, the service is down, or there is a production emergency.
disable-model-invocation: true
---

# Incident Response

**This is an emergency procedure. Follow steps carefully.**

## Steps

### 1. Assess

- What is the nature of the incident? (outage, security breach, data corruption)
- When did it start?
- What is the blast radius? (single user, all users, data integrity)

### 2. Contain

- If security breach: rotate all API keys and secrets immediately
- If outage: check health endpoint and CI status
- If data corruption: stop the service, take a backup immediately

```bash
# Take immediate backup (adjust for your database)
# SQLite
cp database.db database.db.incident-backup

# PostgreSQL
pg_dump dbname > incident-backup.sql
```

### 3. Diagnose

```bash
# Check service status
curl -sf https://{PRODUCTION_URL}/health

# Check recent CI
gh run list --limit 5

# Check recent commits for the cause
git log --oneline -10
```

### 4. Remediate

Follow the relevant procedure from the project's runbook or operational docs.

### 5. Recover

- Verify service is healthy
- Verify data integrity
- Notify affected users if applicable

### 6. Document

Create an incident report with:
- Timeline of events
- Root cause
- Resolution steps taken
- Prevention measures for the future
