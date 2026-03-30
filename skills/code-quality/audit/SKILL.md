---
name: audit
description: Orchestrate a full-project consistency audit using a parallel agent team. Spawns lane-specific auditors to cross-reference docs vs code vs tests vs infra, deduplicates findings, and writes a severity-scored audit report.
disable-model-invocation: true
argument-hint: "[--lanes infra,frontend,arch,tests,deps,security] [--previous docs/AUDIT_FINDINGS.md] [--include-stash] [--drop-stashes] [--fix] [--fix-only] [--deep]"
---

# Full-Project Consistency Audit

Orchestrate a comprehensive project audit by spawning a team of parallel research agents, deduplicating their findings, and producing a scored audit report.

## Argument Parsing

Parse `$ARGUMENTS` for these flags:

- `--lanes <comma-separated>`: Which audit lanes to run. Valid values: `infra`, `frontend`, `plugins`, `arch`, `tests`, `deps`, `security`. Default: all lanes.
- `--previous <path>`: Path to a previous audit report. When provided, the writer agent adds Fixed Since Last Audit, New Findings, and Regressions sections.
- `--include-stash`: When present, also spawn the git-stash-auditor agent.
- `--drop-stashes`: Used with `--include-stash` during the fix phase. Tells the ops-cleanup agent to `git stash drop` all stashes instead of just cataloging them.
- `--fix`: After the audit completes, automatically run the planning + fix pipeline (Phase 2.5 through Phase 6).
- `--fix-only`: Skip audit recon entirely. Read the existing `docs/AUDIT_FINDINGS.md` and go straight to the planning + fix pipeline. Requires a prior audit report to exist.
- `--deep`: Enhanced audit using installed CLI tools. The default audit uses grep/glob (fast). `--deep` adds tool-assisted scanning per lane.

## Severity Scoring Rubric

All research agents MUST use this rubric when categorizing findings:

- **Critical** = breaks at runtime OR creates legal liability
- **Major** = silent failure OR affects >1 subsystem
- **Minor** = cosmetic, tech debt, no user impact

## Output Format for All Research Agents

Each research agent produces a markdown table (max 50 lines) with these columns:

| Finding | Severity | Location | Expected | Actual |
|---------|----------|----------|----------|--------|

Rules for all research agents:
- Read selectively -- grep/glob first, then read only relevant lines
- Never read entire files at once
- Keep context lean
- Update your task to completed when done

## Team Architecture

Create a team called `project-audit`. The main agent (team lead) stays lean -- it only spawns agents, routes messages, and summarizes. It never reads files or does research itself.

### Phase 1: Research Agents (All Parallel)

Spawn all applicable research agents with `run_in_background: true`. Each agent gets the severity rubric and output format above in their prompt.

---

### Agent 1: infra-auditor
**Lane**: `infra`
**Task**:
Audit infrastructure configs against documentation.

1. Glob deployment configs, CI/CD workflows, and package manager configs
2. Cross-reference CI pipeline documented in architecture docs against actual workflow YAML
3. Check if deployment scripts match documented procedures
4. Verify package manager config metadata is consistent with docs
5. Check for orphaned config files or scripts

---

### Agent 2: frontend-auditor
**Lane**: `frontend`
**Task**:
Audit the frontend against the backend API.

1. Glob frontend files to catalog all frontend assets
2. Grep for API calls (fetch, axios, endpoint URLs) in frontend code
3. Glob API route files to catalog all actual routes
4. Cross-reference: flag phantom endpoints (called by frontend but don't exist in API)
5. Cross-reference: flag dead endpoints (exist in API but never called by frontend)
6. Check for HTTP method mismatches (frontend sends POST but route expects GET, etc.)

---

### Agent 3: plugins-auditor
**Lane**: `plugins`
**Task**:
Audit the plugin system for compliance and completeness.

1. Glob plugin files to catalog all plugins
2. Grep for plugin class definitions or registration patterns
3. Cross-reference registered plugins against documented plugins in architecture docs
4. Cross-reference against test files
5. Verify each plugin follows the defined interface/base class
6. Verify each plugin returns the expected response model
7. Check error handling -- are error messages specific and actionable?

---

### Agent 4: arch-doc-accuracy-auditor
**Lane**: `arch`
**Task**:
Verify that claims in architecture documentation match actual code.

1. Read architecture docs in chunks (50 lines at a time)
2. For each architectural claim, verify against actual code:
   - Module structure claims: glob to verify directories/files exist
   - API route claims: grep route definitions
   - Database model claims: grep model definitions
   - Plugin system claims: grep plugin implementations
   - Configuration claims: read config files
3. Flag any claim that does not match reality (doc says X, code does Y)
4. Flag any deprecated or removed features still documented

---

### Agent 5: arch-doc-coverage-auditor
**Lane**: `arch`
**Task**:
Find code that exists but is NOT documented in architecture docs.

1. Glob the actual module tree
2. List all API routes: grep for route decorator patterns
3. List all database models: grep for model base class subclasses
4. List all CLI commands: grep for CLI command decorators
5. Read architecture docs and check which of the above are mentioned
6. Flag everything that exists in code but has NO mention in the architecture doc

---

### Agent 6: test-coverage-auditor
**Lane**: `tests`
**Task**:
Audit test coverage against the actual module tree.

1. Run test collection (e.g., `pytest --co -q`) to list all collected test cases
2. Glob source files to list all source modules (excluding `__init__.py`)
3. For each source module, check if there is a corresponding test file or test functions that import/test it
4. Flag modules with zero test coverage
5. Flag test files that test modules which no longer exist
6. Count total test cases per module area

---

### Agent 7: dependency-auditor
**Lane**: `deps`
**Task**:
Audit declared dependencies against actual usage.

1. Read package manager config to extract all declared dependencies (both main and dev)
2. Grep the codebase for import statements matching each declared dependency
3. Flag declared but unused dependencies
4. Grep all source files for imports, then check if each imported package is declared
5. Flag undeclared dependencies (imported in code but not in config)
6. Check for version conflicts or pinning issues

---

### Agent 8: git-stash-auditor (Only if --include-stash)
**Lane**: N/A (optional)
**Task**:
Audit git stash entries. RECON ONLY -- never pop or apply stashes.

1. Run `git stash list` to enumerate all stash entries
2. For each entry, run `git stash show <stash-ref>` to see what files are affected
3. Cross-reference stashed files with current working tree changes (from `git status`)
4. Flag stash entries that may conflict with current uncommitted work
5. Flag stale stashes (old entries that likely are no longer relevant)
6. **CRITICAL: Never run `git stash pop` or `git stash apply`. Read-only operations only.**

---

### Agent 9: security-auditor (Only if --deep or `security` in --lanes)
**Lane**: `security`
**Task**:
Perform security-focused auditing of the codebase.

1. Run `gitleaks detect` to scan for leaked secrets (if available)
2. Run `semgrep --config auto {source_dir}/` for SAST findings (if available)
3. Run `bandit -r {source_dir}/` if available
4. Check for OWASP top 10 patterns: SQL injection, XSS, command injection, hardcoded secrets
5. Review security middleware configuration (CORS, CSP, rate limiting, auth)
6. Cross-reference findings with existing suppression files
7. Flag any hardcoded API keys, tokens, passwords, or connection strings

**Activation**: This agent only runs when `--deep` flag is set OR when `security` is explicitly included in `--lanes`.

---

### Stall Detection (Team Lead Responsibility)

The team lead tracks agent completion. If 75% of research agents have reported back and any agent has NOT reported:

1. Send one ping message to the stalled agent asking for status
2. Wait for a response. If the agent responds, let it finish
3. If the agent does not respond or remains idle without delivering findings, spawn a replacement agent (same lane, same prompt, name suffixed with `-v2`) and shut down the original
4. Do NOT block consolidation waiting indefinitely -- replace and move on

---

## Phase 2: Deduplication (After All Research Agents Complete)

### Agent 10: dedup-agent
**Blocked by**: All Phase 1 research agent tasks

**Task**:
Deduplicate and cross-reference findings from all research agents.

1. Read all completed research agent task outputs / findings
2. Identify duplicate findings (same issue reported by multiple lanes)
3. Merge duplicates, keeping the most detailed description and noting all lanes that found it
4. Add cross-references between related findings
5. Produce a clean deduplicated list, still using the severity rubric
6. Output format: same markdown table format but with an additional "Lanes" column showing which auditors found each issue

---

## Phase 3: Report Writing (After Dedup Completes)

### Agent 11: writer-agent
**Blocked by**: dedup-agent task

**Task**:
Write the final audit report to `docs/AUDIT_FINDINGS.md`.

**Report structure**:

```markdown
# Project Audit Findings

**Date**: [current date]
**Lanes**: [which lanes were run]
**Agents**: [count of research agents that completed]

## Executive Summary

[5-6 lines max. Overall project health assessment. Count of findings by severity.]

## Critical Findings

[Runtime breaks or legal liability. Each finding includes: description, location, expected behavior, actual behavior, recommended fix.]

## Major Findings

[Silent failures or multi-subsystem impact. Same format as Critical.]

## Minor Findings

[Cosmetic, tech debt, no user impact. Same format but can be more concise.]

## Git Stash Cleanup

[Only if --include-stash was used. List stash entries with recommendations: keep, drop, or apply-and-resolve.]

## What's Working Well

[Positive findings -- things that are correctly implemented, well-tested, or properly documented. Important for morale and to avoid audit fatigue.]
```

**If `--previous` flag was provided**, also add these sections after "What's Working Well":

```markdown
## Fixed Since Last Audit

[Findings from the previous report that are now resolved.]

## New Findings

[Findings in this audit that were NOT in the previous report.]

## Regressions

[Findings that were marked as fixed in the previous report but have reappeared.]
```

---

## Task Dependency Graph

Create all tasks upfront with proper `blockedBy` dependencies:

```
Phase 1 (parallel):
  infra-auditor-task
  frontend-auditor-task
  plugins-auditor-task
  arch-accuracy-task
  arch-coverage-task
  test-coverage-task
  dependency-auditor-task
  security-auditor-task    (only if --deep or security in --lanes)
  git-stash-task           (only if --include-stash)

Phase 2:
  dedup-task               (blocked by all Phase 1 research tasks)

Phase 2.5 (only if --fix):
  priority-planner-task    (blocked by dedup-task)
  execution-planner-task   (blocked by dedup-task)
  -> human-decision-gate   (blocked by both planners)

Phase 3:
  writer-task              (blocked by dedup-task)

Phase 3-fix (only if --fix, after human decision gate):
  batch-1-fix-agents       (Critical fixes, parallel + watchdog)
  batch-1-validation       (blocked by batch-1-fix-agents)

Phase 4-fix:
  batch-2-fix-agents       (Major fixes, parallel + watchdog)
  batch-2-validation       (blocked by batch-2-fix-agents)

Phase 5-fix:
  batch-3-fix-agents       (Minor fixes, parallel + watchdog)
  batch-3-validation       (blocked by batch-3-fix-agents)

Phase 6-fix:
  final-validation-task    (blocked by all batch validations)
```

## Team Lead Responsibilities

The team lead (main agent) MUST:

1. Parse arguments and determine which lanes to run
2. Create the team with all applicable agents
3. Create all tasks upfront with correct dependencies
4. Send each agent their specific instructions plus the severity rubric and output format
5. Monitor progress via stall detection
6. When all research agents complete, trigger the dedup agent
7. When dedup completes, trigger the writer agent
8. When the writer completes, report the final audit location to the user

The team lead MUST NOT:
- Read any project files directly
- Do any research or analysis itself
- Accumulate raw tool output in its context

---

## Deep Audit Tools (--deep flag)

When `--deep` is set, research agents augment their grep/glob analysis with installed CLI tools:

| Tool | Command | Lane(s) | What it finds |
|------|---------|---------|---------------|
| vulture | `vulture {source_dir}/` | arch, deps | Dead/unused code |
| gitleaks | `gitleaks detect` | security | Leaked secrets in git history |
| deptry | `deptry .` | deps | Missing/unused/transitive dependencies |
| complexipy | `complexipy {source_dir}/` | arch | Cognitive complexity scoring per function |
| semgrep | `semgrep --config auto {source_dir}/` | security | SAST rule violations |
| bandit | `bandit -r {source_dir}/` | security | Python security issues |

Research agents in the corresponding lanes should run these tools when `--deep` is active and incorporate findings into their standard output tables.

---

## Fix Pipeline

Activated by `--fix` flag (runs after audit) or `--fix-only` flag (reads existing report, skips audit).

### Phase 2.5: Planning

Spawn 2 planner agents that collaborate:

**priority-planner**: Reads deduplicated findings (or `docs/AUDIT_FINDINGS.md` for `--fix-only`) and batches them into 3 tiers using the severity rubric:
- **Batch 1 (Critical)**: Runtime breaks, legal liability -- must fix first
- **Batch 2 (Major)**: Silent failures, multi-subsystem impact -- fix after critical
- **Batch 3 (Minor)**: Tech debt, docs, cosmetic -- fix last

**execution-planner**: Takes the priority planner's batched list and produces:
- Agent assignments per file ownership
- Dependency graph between fixes (which fixes must happen before others)
- Parallelization plan (which fixes within a batch can run concurrently)
- Human decisions list (findings tagged "needs design" or "needs human input")

Both planners produce their output as structured markdown.

### Human Decision Gate

After both planners complete, the team lead collects the human decisions list and presents ALL decisions that need user input BEFORE spawning any fix agents. Format:

```
## Decisions Needed Before Fixing

1. [Finding description] -- [What needs deciding] -- Options: A / B / C
2. [Finding description] -- [What needs deciding] -- Options: A / B / C
...

Please answer each decision so fix agents can proceed.
```

Wait for the user's answers. Incorporate them into the fix plan before proceeding.

### Phase 3/4/5: Batch Execution

Execute batches sequentially (Batch 1 -> Batch 2 -> Batch 3). Within each batch:

1. Spawn parallel fix agents according to the execution plan and file ownership rules
2. Spawn a **watchdog agent** for the batch -- monitors progress, pings stalled agents
3. Fix agents use `isolation: "worktree"` UNLESS the target file has unstaged changes (detected via `git status`), in which case route to main tree
4. When all fix agents in the batch complete, run mandatory validation (lint + tests)
5. If validation fails, the batch is NOT complete -- fix agents must address validation failures before proceeding to the next batch
6. Merge agents only merge branches; validation agents only validate (never combine these roles)

### Phase 6: Final Validation

After all 3 batches complete and pass validation:
1. Run the full validation suite one final time
2. Update `docs/AUDIT_FINDINGS.md` to mark fixed items
3. Report summary to user: what was fixed, what was skipped, what needs follow-up

---

## Fix Pipeline Rules

- **Auto-batching**: The severity rubric maps directly to 3 sequential batches (Critical -> Major -> Minor)
- **Human decision gate**: Findings tagged "needs design" or "needs human input" are collected and presented to the user before fix execution begins. Never auto-fix these.
- **Watchdog agent**: Every batch gets one. It monitors progress, pings stalled agents after reasonable delay, and reports blockers to the team lead.
- **Worktree detection**: Before assigning a fix agent to a worktree, check `git status` for unstaged changes in the target file. If unstaged changes exist, route that agent to the main tree instead.
- **Validation between batches is mandatory, not optional.** No batch proceeds until the previous batch passes all validation checks.
- **Role separation**: Merge agents only merge. Validation agents only validate. Fix agents only fix. Never combine these roles in a single agent.

---

## --fix-only Flow

When `--fix-only` is passed:

1. Skip all Phase 1 research agents and Phase 2 dedup
2. Read `docs/AUDIT_FINDINGS.md` directly
3. Parse findings into the severity rubric format
4. Proceed to Phase 2.5 (Planning) and continue through the fix pipeline normally
5. If `docs/AUDIT_FINDINGS.md` does not exist, abort with error: "No existing audit report found. Run audit first or use --fix instead of --fix-only."
