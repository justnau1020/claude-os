---
paths:
  - "**"
---

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
