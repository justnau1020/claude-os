---
name: launch-review
description: Structured debate -> plan -> execute pipeline for evaluating feature readiness. Runs 5-agent debate, creates action plan with review, then executes fixes.
user_invocable: true
---

# Launch Review Pipeline

A structured, multi-phase agent pipeline that evaluates feature readiness through adversarial debate, creates a reviewed action plan, and executes fixes. Each phase runs as an isolated team to prevent context bloat.

## Invocation

```
/launch-review [topic] [--scope "focus areas"] [--constraints "known constraints"]
```

Examples:
- `/launch-review "checkout experience" --scope "cart, payment, confirmation"`
- `/launch-review "v2 API launch" --constraints "backwards compatible, feature flag gated"`

## Phase 0: Constraints Gathering (No Team)

Before spawning any agents, the main agent MUST:

1. **Ask the user** for known constraints:
   - Legal restrictions (prohibited libraries, data sources, licenses)
   - Business rules (budget limits, timeline, must-have vs nice-to-have)
   - Scope boundaries (what's in/out of this review)
   - Any prior decisions already made
2. **Check memory** for relevant project constraints
3. **Compile a constraints block** that gets injected into every agent's prompt

Format:
```
CONSTRAINTS (non-negotiable):
- [constraint 1]
- [constraint 2]
DO NOT propose solutions that violate these constraints.
```

**This phase prevents the #1 failure mode: agents recommending something that's already been ruled out.**

## Phase 1: Debate Team

**Create team:** `TeamCreate` with name `{topic}-debate`

**Agents (5):**
| Agent | Role | Type |
|-------|------|------|
| `arch-critic` | Code auditor -- finds gaps, bugs, half-baked features | general-purpose |
| `comp-critic` | Competitive benchmarker -- researches competitors, holds us to that bar | general-purpose |
| `code-defender` | Argues launch readiness from actual code evidence | general-purpose |
| `industry-defender` | Argues competitive positioning from market research | general-purpose |
| `moderator` | Synthesizes all 4 reports, writes verdict | general-purpose |

**Flow:**
1. Spawn all 5 agents. The 4 debaters run in parallel. Moderator is blocked by all 4.
2. Each debater sends their report to `moderator` via SendMessage.
3. Moderator writes the report to `docs/{TOPIC}_READINESS_REPORT.md`.
4. Moderator sends summary to `team-lead`.

**Handoff artifact:** `docs/{TOPIC}_READINESS_REPORT.md`

**Team transition checklist:**
- [ ] Report file exists on disk
- [ ] Moderator confirmed report is written
- [ ] Shutdown all agents
- [ ] `TeamDelete`

## Phase 2: Planning Team

**Create team:** `TeamCreate` with name `{topic}-planning`

**Agents (2):**
| Agent | Role | Type |
|-------|------|------|
| `planner` | Reads report, creates action plan with team structure | general-purpose |
| `reviewer` | Audits plan against code, verifies file references, checks for gaps | general-purpose |

**Flow:**
1. Spawn `planner` first. It reads the report from disk, creates `docs/{TOPIC}_ACTION_PLAN.md`.
2. Once planner delivers, shut it down and spawn `reviewer`.
3. Reviewer reads the plan, verifies against actual code, appends review section.
4. Reviewer sends summary to `team-lead`.

**The plan MUST include:**
- All issues from the report, prioritized
- Specific files/lines affected
- Agent team structure for execution (using TeamCreate, NOT standalone subagents)
- Phasing and dependencies
- Acceptance criteria per task

**Handoff artifact:** `docs/{TOPIC}_ACTION_PLAN.md` (with review section)

**Team transition checklist:**
- [ ] Plan file exists on disk with review section
- [ ] Reviewer confirmed approval (with or without changes)
- [ ] Shutdown all agents
- [ ] `TeamDelete`

## Phase 3: Execution Team

**Create team:** `TeamCreate` with name `{topic}-execution`

**Agents:** Per the plan's team structure. Typically:
- One engineer per workstream (worktree isolation)
- Each reads the action plan from disk

**Critical rules:**

### Agents MUST commit their work
Every code-writing agent must `git add` + `git commit` in their worktree before reporting done. Uncommitted worktree changes are lost on cleanup.

### Merge before delete
Before `TeamDelete`, a merge agent MUST:
1. List all worktrees with `git worktree list`
2. For each agent worktree:
   - Verify changes are committed
   - Merge the worktree branch into main
   - Remove the worktree
3. Run `git worktree prune`
4. Delete merged branches
5. Confirm `git status` is clean

**NEVER call TeamDelete while worktrees contain unmerged work.**

### Failure recovery
If an agent fails or auth drops:
- Check if worktree has uncommitted changes before re-running
- If changes exist, commit them first
- Respawn the agent pointing at the same worktree branch

**Handoff artifact:** Clean main branch with all fixes merged.

## Phase 4: Backlog (No Team)

Main agent writes `docs/{TOPIC}_BACKLOG.md` capturing:
- What was completed
- What remains (with priority)
- Action items requiring human intervention
- Known constraints for future sessions

## Anti-Patterns (Learned the Hard Way)

1. **Never TeamDelete before merging worktrees.** This destroyed completed work in the first run of this pipeline.
2. **Never skip Phase 0.** Three layers of agents all recommended a legally prohibited library because no one told them the constraint.
3. **Decision agents must wait for all inputs.** The manager made a call before receiving the legal report. Use `addBlockedBy` on tasks to enforce sequencing.
4. **Don't create teams you don't need yet.** One-team-at-a-time constraint means premature creation forces premature deletion.
5. **Debaters and planners don't need worktrees.** They write docs, not code. Only execution agents need worktree isolation.
6. **Keep the main agent's context lean.** It delegates, routes, and summarizes. It does not read files, grep code, or write implementations.
