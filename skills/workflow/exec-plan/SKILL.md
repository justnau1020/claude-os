---
name: exec-plan
description: Execute an execution plan document by orchestrating worktree agents, enforcing commit/merge/test gates, and tracking progress. Main agent stays lean -- all work delegated.
user_invocable: true
---

# Execute Plan

State machine that reads an execution plan document and mechanically executes it -- launching worktree agents, enforcing commit gates, merging, running validation, and tracking progress.

## Invocation

```
/exec-plan [path to execution plan]
```

Examples:
- `/exec-plan docs/brainstorms/EXECUTION_PLAN.md`
- `/exec-plan docs/brainstorms/WEBSOCKET_PLAN.md`

## Core Principle: Main Agent Does Nothing

Main is a coordinator. It:
- Reads the plan doc (once, at the start)
- Launches agents
- Receives status messages
- Routes decisions
- Reports to the user

Main does NOT:
- Read source files
- Run tests
- Resolve merge conflicts
- Grep or explore the codebase
- Write or edit code

ALL of that is delegated to specialized agents.

## Pipeline

### Step 0: Parse the Plan

Read the execution plan document. Extract:
- Team list with dependencies
- Session grouping
- File conflict table
- Per-team specs (files, validation, agent instructions)

If the plan is missing required sections (file conflict table, validation commands, "read these first" lists), STOP and tell the user: "This plan is missing [X]. Run `/plan-features` to generate a complete plan."

### Step 1: Pre-Flight Check

Spawn a **pre-flight agent** (general-purpose type) to:
- Verify all files referenced in the plan actually exist
- Check no uncommitted changes in the working tree
- Run the full test suite on current main branch
- **Update `docs/KNOWN_FAILURES.md`** -- if the file exists, read it first, then add any NEW pre-existing failures and remove any that now pass. If the file doesn't exist, create it. This is a living reference file shared across all execution runs -- not regenerated from scratch each time.

Format for `docs/KNOWN_FAILURES.md`:
```markdown
# Known Test Failures
> Last updated: [date] by pre-flight check

| Test | File | Reason | Since |
|------|------|--------|-------|
| test_name | path/to/test.py | One-line reason | [date first seen] |
```

Agent returns: READY + known failures count, or BLOCKED + reason.

If BLOCKED, report to user and stop. Known failures are pre-existing, not blockers -- execution proceeds.

### Step 2: Execute Session Groups

For each session group in the plan:

#### Sequential Teams (shared file conflicts)

Process one at a time, in dependency order:

```
For each team in sequence:
  1. LAUNCH  -- spawn code agent in worktree
  2. VERIFY  -- spawn watchdog to check the worktree
  3. MERGE   -- spawn merge agent to bring changes to main
  4. GATE    -- spawn test agent to validate
```

**1. LAUNCH: Code Agents + Live Watchdog**

For each batch of agents (parallel or sequential), spawn:
- All **code agents** with `isolation: "worktree"` and their team specs
- One **live watchdog agent** that monitors the batch concurrently

Code agent prompt template:
```
You are [Team Name].

[Paste the team's spec from the plan: blocked-by, read-these-first,
files-touched, deliverable, validation, agent instructions]

CRITICAL RULES:
- Read `docs/KNOWN_FAILURES.md` first -- do NOT report these as issues
- Read the "Read these files first" list BEFORE writing any code
- Follow existing patterns in those files
- You MUST `git add` and `git commit` all your changes before finishing
- Your commit message must start with "[Team X]:"
- Run the validation commands from your spec before finishing
- If validation fails, fix the issue and re-commit

When done, report: DONE + commit hash + validation results
OR: BLOCKED + what went wrong
```

Live watchdog prompt:
```
You are the batch watchdog. Your job is to monitor code agents for this session.

Active agents: [list of agent names]

Every 3 minutes, check TaskList for tasks that are in_progress but whose
owner has gone idle. If an agent has gone idle without sending a report
to team-lead, send them a nudge:

"You appear idle without reporting. Please send your status to team-lead:
DONE + commit hash + validation results, or BLOCKED + what went wrong."

When all agents in the batch have reported DONE or BLOCKED, send a summary
to team-lead and wait for shutdown.

Do NOT do any code work. Your only job is monitoring and nudging.
```

**Important:** The watchdog is spawned WITH the code agents and shut down WITH them. Fresh watchdog per batch -- do not persist across sessions.

**2. GATE: Test Agent (per-session, not per-team)**

After all teams in a session complete, spawn a test gate agent to run the session's validation:

```
You are a test gate agent. Run these validation commands on main:

[paste validation commands from the session's team specs]

Read `docs/KNOWN_FAILURES.md` -- do NOT report pre-existing failures as regressions.

Report:
- PASS: all N tests passed, lint clean
- FAIL: [which command failed] + [error output summary] + whether failure is new or pre-existing

Do NOT attempt to fix failures. Just report.
```

If FAIL with NEW failures: report to user. Options:
- Spawn a fix agent
- Revert specific commits
- Continue anyway (user's call)

### Step 3: Session Checkpoint

After all teams in a session complete:

1. Spawn a **checkpoint agent** to:
   - Run the FULL test suite (not just per-team validation)
   - Update the plan doc (mark completed teams)
   - Report overall status

2. Report to user:
   ```
   Session N complete.
   Teams merged: [list]
   Tests: X passed, Y failed
   Next session: [teams] -- proceed? (y/n)
   ```

3. Wait for user confirmation before starting next session.

### Step 4: Finalize

After all sessions complete:

1. Spawn a **finalize agent** to:
   - Run full test suite one more time
   - Run linter and type checker
   - Update the plan doc (mark all COMPLETED, add completion date)
   - Clean up any remaining worktrees (`git worktree prune`)
   - List any orphaned branches

2. Spawn a **doc update agent** to update ALL affected project documentation. This is **non-negotiable** -- stale docs actively mislead future agents and humans. The agent must:
   - Read architecture docs and update any sections affected by the execution
   - Read task tracking docs and mark completed items, add newly discovered items
   - Check if any non-trivial technical decisions were made -- if so, add/update decision records
   - Update `docs/KNOWN_FAILURES.md` -- remove any failures that were fixed during execution
   - Commit all doc changes with message: "Update docs after [plan name] execution"

3. Report final summary to user.

## Agent Roster

| Agent | When | Isolation | Purpose |
|-------|------|-----------|---------|
| Pre-flight | Step 1 | None | Verify codebase ready + generate KNOWN_FAILURES.md |
| Code agent | Step 2.1 | Worktree | Implement team spec |
| Live watchdog | Step 2.1 | None | Monitor batch for idle/silent agents, nudge stragglers |
| Test gate | Step 2.2 | None | Run validation per-session, filter known failures |
| Checkpoint | Step 3 | None | Full test suite + doc update |
| Finalize | Step 4 | None | Final validation + cleanup |
| Doc update | Step 4 | None | Update architecture docs, task tracking, decision records, KNOWN_FAILURES.md |

**Main agent spawns all of these. Main never does their work.**
**Watchdog lifecycle:** Spawned WITH each batch of code agents, shut down WITH them. Fresh watchdog per batch.

## Error Recovery

### Code agent doesn't commit
Watchdog catches this. Send message back to code agent: "You have uncommitted changes. Run `git add -A && git commit -m '[Team X]: [deliverable]'` now."

### Merge conflict
Merge agent attempts resolution. If it can't:
- Report the conflicting files and both versions
- Ask user: resolve manually, or skip this team?

### Test gate fails
Report the failure. Ask user:
- Revert the merge?
- Spawn a fix agent?
- Continue anyway?

### Agent goes silent / times out
After 10 minutes with no response from a code agent:
- Spawn a watchdog to check the worktree state
- If changes exist but uncommitted: spawn a new agent to commit + finish
- If no changes: respawn the code agent

## Main Context Budget

For a 6-team execution plan:
- Plan doc read: ~200 lines (once)
- Per team: ~10 lines (launch + status messages)
- Session checkpoints: ~20 lines each
- Total: ~300 lines

This leaves the vast majority of main's context window available for the user to request follow-up work in the same session.

## Anti-Patterns

1. **Main reading files.** Never. That's what Explore agents and watchdogs are for.
2. **Main running tests.** Never. Test gate agents exist for this.
3. **Main resolving conflicts.** Never. Fix agents handle this.
4. **Skipping the live watchdog.** Agents go idle without reporting -- they don't choose to stop, their turn ends. A live watchdog catches this while there's still time to nudge them. Always spawn one per batch.
5. **Persisting the watchdog across batches.** All teammates must be shut down before spawning a new team. Fresh watchdog per batch -- spawn with the code agents, shut down with them.
6. **Reporting known failures as regressions.** Pre-flight generates `docs/KNOWN_FAILURES.md`. Every agent and gate must read it. If they keep reporting the same pre-existing failures, the system wastes context on noise.
7. **Launching agents from stale base.** Sequential teams must wait for the previous team to land on main before their worktree is created. Otherwise they fork from pre-merge code and produce conflicts.
