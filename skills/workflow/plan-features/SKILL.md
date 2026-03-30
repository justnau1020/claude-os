---
name: plan-features
description: Generate execution plan documents for multi-team agent work. Analyzes file conflicts, builds dependency graphs, and produces structured plans that drive flawless parallel execution.
user_invocable: true
---

# Plan Features

Generate a structured execution plan document that enables multi-team agent work with worktree isolation. The plan is the product -- execution is mechanical downstream.

## Invocation

```
/plan-features [description of features/changes] [--doc path/to/requirements.md] [--output path/to/plan.md]
```

Examples:
- `/plan-features "add WebSocket support for real-time updates"`
- `/plan-features --doc docs/brainstorms/SECURITY_ROADMAP.md --output docs/brainstorms/EXECUTION_PLAN.md`
- `/plan-features "refactor plugin system to support async initialization and health checks"`

## What This Skill Produces

A single markdown document containing everything an executor needs to run teams without ambiguity:

1. **File Conflict Table** -- which files each team touches (determines merge order)
2. **Dependency Graph** -- what blocks what (determines parallelism)
3. **Critical Path** -- the longest sequential chain
4. **Per-Team Specs** -- files, deliverables, validation, "read these first" lists
5. **Risk Register** -- what could break and how to mitigate
6. **Session Grouping** -- how to batch teams for execution

## Process

### Step 1: Understand the Scope

Read the user's feature description or requirements doc. If the scope is ambiguous, ask clarifying questions BEFORE proceeding:
- What's in scope vs out of scope?
- Any hard constraints (prohibited libraries, deadline, legal)?
- Any prior decisions already made?
- What test infrastructure exists?

### Step 2: Codebase Reconnaissance

Spawn an Explore agent to map the affected areas:
- Which files/modules will be touched?
- What are the existing patterns in those files?
- What test coverage exists for those areas?
- What's the current middleware/hook/plugin stack order?

This is the most important step. The file list drives everything.

### Step 3: Decompose into Teams

Break the work into teams where each team:
- Has a single, clear deliverable
- Touches a bounded set of files
- Can be validated independently
- Maps to one worktree agent

**Sizing rule:** If a team touches >8 files, it's too big. Split it.

**Naming rule:** Teams get letter codes (A, B, C) for the main plan or numbered codes (Team 1, Team 2) for sub-plans. Names should be descriptive: "Team J: httpOnly Cookie Auth" not "Team J".

### Step 4: Build the File Conflict Table

This is the MOST CRITICAL artifact. It determines merge order.

```markdown
### Shared File Conflicts
| File | Touched by Teams |
|------|-----------------|
| `path/to/shared_file.py` | A, C, D |
| `path/to/other_file.js` | B, C |
```

**Rule:** If two teams touch the same file, they CANNOT run in parallel (worktree merge conflicts). They must be sequenced, and the merge order matters.

### Step 5: Build the Dependency Graph

Two types of dependencies:
1. **Logical** -- Team B's work requires Team A's output to exist
2. **File conflict** -- Teams touch the same files (from Step 4)

```markdown
### Dependency Chain
- Team A (independent) -- can start immediately
- Team B (blocked by A) -- A's output is B's input
- Team C (blocked by A, B) -- touches files modified by both
```

### Step 6: Identify the Critical Path

The longest chain of sequential dependencies. This determines minimum execution time.

```markdown
### Critical Path
Team A -> Team C -> Team D -> Team F
```

### Step 7: Write Per-Team Specs

Each team spec MUST include ALL of the following:

```markdown
### Team X: [Descriptive Name]
**Blocked by:** [Team(s) or "none -- can start immediately"]

**Read these files first:** (CRITICAL -- prevents agents from building on stale assumptions)
- `path/to/file.py` -- [why: current auth system]
- `path/to/other.py` -- [why: middleware stack order]

**Files touched:**
- New: `path/to/new_file.py` -- [description]
- Modified: `path/to/existing.py` -- [what changes]

**Deliverable:** [One sentence: what exists after this team finishes]

**Validation:**
- [ ] `specific test command` passes
- [ ] `specific lint command` passes
- [ ] [Manual check if applicable]

**Agent instructions:**
- You MUST `git add` + `git commit` before finishing
- Follow existing patterns in [specific file]
- [Any team-specific constraints]
```

**The "Read these files first" section prevents the #1 execution failure:** agents building on assumptions from their training data instead of the actual codebase state.

**The "Agent instructions" section prevents the #2 failure:** agents not committing their work, causing it to be lost when the worktree is cleaned up.

### Step 8: Risk Register

```markdown
## Risk Register
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Team X breaks Y | Medium | High | [specific mitigation] |
```

Focus on:
- Merge conflicts between teams
- Breaking existing functionality
- Test regressions
- External dependency issues

### Step 9: Session Grouping

Group teams into execution sessions based on:
- Dependency chains (sequential teams in the same session)
- Parallel opportunities (independent teams in the same session)
- Natural breakpoints (good commit points between sessions)

```markdown
## Session Plan

### Session 1
**Sequential:** Team A -> Team C -> Team D (shared file conflicts)
**Parallel after D:** Teams E, F, G (no shared files)
**Validation gate:** Full test suite between sessions

### Session 2
**Sequential:** Team H -> Team I (depends on Session 1 output)
```

## Output Format

The plan document MUST follow this structure:

```markdown
# [Feature Name] -- Execution Plan

> Generated from [source]. Last updated: [date]

## Constraints
- [Hard constraints from user]
- [Discovered constraints from recon]

## File Conflict Table
[Step 4 output]

## Dependency Graph
[Step 5 output]

## Critical Path
[Step 6 output]

---

## Teams

### Team A: [Name]
[Step 7 spec]

---

### Team B: [Name]
[Step 7 spec]

---

[...more teams...]

## Risk Register
[Step 8 output]

## Session Plan
[Step 9 output]
```

## Quality Checklist (verify before delivering)

- [ ] Every team has a "Read these files first" list
- [ ] Every team has "You MUST git add + git commit" in agent instructions
- [ ] Every team has specific validation commands (not "run tests")
- [ ] File conflict table accounts for ALL shared files
- [ ] No team touches >8 files
- [ ] Dependencies match the file conflict table (no hidden conflicts)
- [ ] Critical path is actually the longest chain
- [ ] Session grouping respects all dependency constraints

## Anti-Patterns (Learned from Execution Failures)

1. **Missing file conflict table.** Without it, parallel agents create merge conflicts that take longer to resolve than sequential execution would have.

2. **No "read these first" list.** Agents build on training-data assumptions. An agent implementing cookie auth that doesn't read the current auth.py will produce incompatible code.

3. **No commit instruction.** Worktree agents that don't commit lose ALL their work when the worktree is cleaned up. This has happened on every execution without explicit instructions.

4. **Vague validation.** "Tests pass" is not a validation criterion. "`pytest tests/api/test_session_auth.py -x -q` -- 21 tests pass" is.

5. **Teams that are too large.** A team touching 15 files across 4 modules will produce a messy diff that's hard to review and merge. Split it.

6. **Ignoring existing code patterns.** The plan must reference specific files that show the pattern to follow. "Follow existing patterns" is useless without a pointer.

7. **Parallel teams that share files.** The file conflict table exists to prevent this. If two teams touch `security_middleware.py`, they are SEQUENTIAL, period.

8. **Estimated counts without grep verification.** Every numeric claim in the plan (importers, duplicates, exception instances) MUST be backed by `grep -c` or `wc -l` output -- never eyeballed. An audit that says "20 importers" when the real count is 51 produces plans with wrong blast-radius estimates. Recon agents must run the count command and include the exact number.
