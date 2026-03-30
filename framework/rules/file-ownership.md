---
paths:
  - "**"
---

## File Ownership (Agent Teams)

Map your project's directories to team names. When agents are spawned with file ownership rules, they stay in their lane -- preventing merge conflicts during parallel execution.

### Template (customize for your project)

```
- {project}/core/ + tests/core/           -> engine
- {project}/api/ + tests/api/             -> api
- {project}/plugins/ + tests/plugins/     -> plugins
- {project}/db/ + pyproject.toml          -> infra
- deploy/ + .github/                      -> ops
- docs/                                   -> docs
- frontend/                               -> frontend
```

### How It Works

Each team name maps to a set of files. When a skill like `/plan-features` generates an execution plan, it uses this ownership map to:
1. Assign agents to non-overlapping file sets
2. Detect shared-file conflicts that force sequential execution
3. Determine merge order when parallel agents complete

### Rules
- An agent MUST NOT modify files outside its ownership scope
- If a task requires touching files owned by multiple teams, it must be split into separate agents or run sequentially
- The infra team owns cross-cutting config files (package manager configs, CI configs, README)
- The ops team owns deployment and CI/CD infrastructure
