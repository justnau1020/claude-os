# Lean Context Framework

## Agent Execution Model -- Non-Negotiable

The main chat agent is a **team lead**, not a worker. Its context window must stay as lean as possible.

### Rules
1. **Never do work inline.** Every task -- coding, research, exploration, testing, file reads beyond a quick glance -- MUST be delegated to a subagent (`Agent` tool) or an agent team (`TeamCreate` + `SendMessage`).
2. **Use `TeamCreate` for multi-step or collaborative work.** When a task involves 2+ agents that need to coordinate (e.g., backend + tests, research + implementation), create a named team with a team-lead agent that owns the deliverable.
3. **Use `Agent` (subagent) for one-shot, isolated tasks.** Quick searches, single-file edits, running a test suite -- these can be standalone subagents. But they still run outside the main context.
4. **Even recon is delegated.** Exploring the codebase, grepping for patterns, reading architecture docs -- spawn an `Explore` agent or a `general-purpose` agent. The main agent should receive a summary, not raw tool output.
5. **Prefer `isolation: "worktree"` for any agent that writes code.** This prevents conflicts when multiple agents work in parallel.
6. **Main agent responsibilities are limited to:**
   - Understanding the user's intent
   - Deciding which agents/teams to spawn
   - Routing messages between teams
   - Summarizing results back to the user
   - Saving memories when appropriate
7. **Parallel by default.** If tasks are independent, launch agents concurrently in a single message. Sequential only when there's a true dependency.

### Anti-Patterns (Do NOT Do)
- Reading large files directly in the main context
- Running grep/glob searches inline when an Explore agent can do it
- Writing or editing code in the main context
- Accumulating tool output that could have been summarized by a subagent

---

## Tech Stack (EXAMPLE -- customize for your project)

```
- Python 3.12+, async throughout, type hints everywhere
- FastAPI for REST API
- SQLite via aiosqlite for persistence
- pytest + pytest-asyncio for tests
- ruff for linting, mypy for type checking
```

Replace this section with your actual tech stack. The framework is language-agnostic -- the agent execution model works with any stack.

---

## File Ownership (TEMPLATE -- customize for your project)

Map directories to team names so agents know which files they own:

```
- {project}/core/ + tests/core/           -> engine
- {project}/api/ + tests/api/             -> api
- {project}/plugins/ + tests/plugins/     -> plugins
- {project}/db/ + pyproject.toml          -> infra
- deploy/ + .github/                      -> ops
- docs/                                   -> docs
- frontend/                               -> frontend
```

When agents are spawned with file ownership rules, they stay in their lane. This prevents merge conflicts during parallel execution and keeps diffs clean.

---

## Code Rules (TEMPLATE -- customize for your project)

- All datetimes in UTC internally, convert for display only
- Error responses must be specific and actionable (e.g., "Rate limit exceeded: 0/60 calls remaining, resets in 42 seconds" not "API error")
- One file per module, no god files
- Use typed models (Pydantic, dataclasses, etc.) for all shared data structures
- Async functions everywhere -- no sync I/O in the hot path

---

## Testing (TEMPLATE -- customize for your project)

- Mock external APIs in tests -- no real network calls
- Test categories:
  - **E2E tests**: Full workflow from user action to observable result
  - **Property-based tests**: Hypothesis for invariants and guarantees
  - **Resilience tests**: Timeout, 500, malformed-data handling
  - **Edge cases**: Boundary conditions, empty inputs, concurrent access

---

## Documentation -- Non-Negotiable

After EVERY set of code changes (commit, PR, phase completion), update all affected documentation before considering the work done. This includes:
- Architecture docs -- if any architectural component changed
- Task tracking -- mark completed items, add newly discovered items
- Decision records -- if a non-trivial technical decision was made

Delegate doc updates to a subagent if needed, but they MUST happen. Stale docs are worse than no docs -- they actively mislead future agents and humans.

---

## Token Budget Considerations

This framework is optimized for high-throughput usage (Max plan or equivalent with large token budgets). The lean-context pattern helps on ANY budget by keeping the main agent's context small, but some skills are inherently token-intensive:

- **Multi-agent skills** (`/audit`, `/debate`, `/launch-review`) spawn 5-12 agents. Each agent consumes its own context window.
- **On lower-tier plans**, start with single-agent skills (`/fix-issue`, `/test-all`, `/dep-audit`) and scale up as you understand your token budget.
- **The core insight** -- keeping the main agent lean -- saves tokens regardless of plan tier. A main agent that reads 10 files uses 10x more tokens than one that delegates to an Explore agent and receives a 20-line summary.

---

## Compaction Preservation

When compacting, always preserve: list of files modified in this session, active task context, module boundary rules, and the agent execution model.
