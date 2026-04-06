---
tags: [claude-code, agent-teams, TeamCreate, SendMessage, coordination]
keywords: TeamCreate, SendMessage, agent teams, team lead, teammates, shared task list, split-pane, worktree isolation
aliases: [agent teams, team create, multi-agent, team coordination]
priority: high
---

# Claude Code Agent Teams

Coordinate multiple Claude Code instances working together. Requires v2.1.32+ and CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 in settings.json.

## Enabling
Set in ~/.claude/settings.json under "env":
```json
"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
```

## Core Tools

### TeamCreate
Creates a team. Parameters: team_name, description.
Creates ~/.claude/teams/{team-name}/config.json and ~/.claude/tasks/{team-name}/.

### SendMessage
Direct peer-to-peer messaging between teammates. Message types: direct, broadcast, shutdown, plan approval. Use `to` parameter with agent name.

### TaskCreate / TaskUpdate / TaskList / TaskGet
Shared task list at ~/.claude/tasks/{team-name}/. Tasks have statuses (pending, in_progress, completed), ownership, and dependency relationships (blocks/blockedBy).

## Architecture
- **Team Lead** — Main session. Analyzes tasks, creates team, orchestrates.
- **Teammates** — Independent Claude Code processes. Own context window, full tool access. Spawned via Agent tool with team_name parameter.
- **Shared Task List** — Coordination backbone. Dependency tracking. When blocking task completes, downstream tasks auto-unblock.
- **Mailbox System** — SendMessage for direct peer-to-peer messaging.

## Display Modes
- **In-process** (default) — All teammates in single terminal
- **Split-pane** — Each teammate in separate terminal pane (tmux/iTerm2). STRONGLY RECOMMENDED for 3+ teammates.

## When to Use Teams vs Subagents
- **Subagents (Agent tool):** Quick, focused workers that report back. Short-lived.
- **Teams (TeamCreate):** Teammates share findings, challenge each other, coordinate independently. Long-lived. Use for: research+review, parallel features, competing debug hypotheses, cross-layer work.

## Worktree Isolation
Teammates can work in isolated git worktrees to avoid file conflicts. Set isolation: "worktree" on Agent tool calls. Changes merged back when complete.

## Common Patterns
- Research team: 3 agents investigate different aspects, synthesize into shared findings
- Build team: frontend + backend + tests agents working in parallel worktrees
- Review team: one agent builds, another adversarially reviews
