---
name: hygiene-audit
description: Run a comprehensive codebase hygiene audit. Spawns a team of recon and research agents to analyze structure, dependencies, inconsistencies, and industry best practices, then synthesizes findings into an actionable refactoring plan with phased implementation.
disable-model-invocation: true
argument-hint: "[focus-area] -- optional: structure, dependencies, duplication, all (default: all)"
---

# Codebase Hygiene Audit

Run a full codebase hygiene audit. This skill coordinates a team of agents to analyze the codebase from multiple angles and produce an actionable refactoring plan.

## Phase 1: Reconnaissance (Parallel Agents)

Create a team using `TeamCreate` with a team lead and the following agents. All recon agents run in parallel.

### Team Structure

**Team name**: `hygiene-audit`
**Team lead task**: Coordinate recon agents, collect reports, synthesize findings, present recommendations.

### Agent 1: Structure & Size Recon

**Name**: `structure-recon`
**Task**:
Analyze the codebase structure, file sizes, and module organization.

1. Map the full directory tree of source and test directories with file counts per directory
2. Identify files over 300 lines -- these are candidates for splitting
3. Identify files over 500 lines -- these are urgent split candidates
4. Count classes and functions per file to find "god files"
5. Check for proper `__init__.py` exports vs star imports
6. Verify the one-file-per-module convention
7. Check test file organization mirrors source file organization
8. Look for orphaned files (source files with no corresponding test, or vice versa)

**Output format**:
```
## Structure & Size Report

### File Size Distribution
- Files > 500 lines: [list with line counts]
- Files > 300 lines: [list with line counts]
- Files > 200 lines: [list with line counts]

### God Files (5+ classes or 10+ functions)
[list with counts]

### Module Organization Issues
[list of violations]

### Orphaned Files (no matching test or source)
[list]

### Directory Tree Summary
[tree with file counts]
```

### Agent 2: Dependency & Coupling Recon

**Name**: `dependency-recon`
**Task**:
Analyze import graphs, coupling between modules, and dependency health.

1. Map internal imports between subpackages
2. Identify circular imports or circular dependency chains
3. Find modules with high fan-in (many importers -- fragile to change)
4. Find modules with high fan-out (imports many things -- too many responsibilities)
5. Check for layering violations (lower-level modules importing from higher-level ones)
6. Audit package manager config for unused or missing dependencies
7. Check for vendored or duplicated utility code that should be shared
8. Identify tightly coupled module pairs (always imported together)

**Expected layering** (customize for your project -- lower layers should NOT import from higher layers):
```
core (lowest) -> plugins -> api/cli (highest)
              -> db (sideways, used by all)
```

**Output format**:
```
## Dependency & Coupling Report

### Import Graph Summary
- Total internal imports: N
- Cross-package imports: N

### Layering Violations
[list with file:line references]

### High Fan-In Modules (imported by 5+ files)
[list with importer counts]

### High Fan-Out Modules (imports 5+ internal modules)
[list with import counts]

### Circular Dependencies
[list or "None found"]

### Unused/Missing Dependencies
[list or "All clean"]

### Tightly Coupled Pairs
[list of module pairs that are always co-imported]
```

### Agent 3: Inconsistency & Duplication Recon

**Name**: `inconsistency-recon`
**Task**:
Find code inconsistencies, duplicated logic, and convention violations.

1. Check for inconsistent error handling patterns across the codebase
2. Find duplicated logic (same or very similar code in multiple places)
3. Check for inconsistent naming conventions (snake_case vs camelCase, abbreviations)
4. Verify datetime handling conventions (UTC internally, convert for display)
5. Check for sync I/O in async code paths (blocking calls in async functions)
6. Find bare `except:` or overly broad `except Exception:` catches
7. Check for inconsistent use of logging (structured logging vs print statements)
8. Verify typed models used for all shared data structures (not raw dicts)
9. Check for hardcoded values that should be configuration
10. Look for TODO/FIXME/HACK/XXX comments and categorize them

**Output format**:
```
## Inconsistency & Duplication Report

### Duplicated Logic
[list with file pairs and description]

### Convention Violations
- Datetime: [issues]
- Error handling: [issues]
- Naming: [issues]
- Sync I/O in async: [issues]
- Logging: [issues]

### Bare/Broad Exception Catches
[list with file:line]

### Raw Dicts Instead of Models
[list with file:line]

### Hardcoded Values
[list with suggested config extraction]

### TODO/FIXME/HACK Comments
[categorized list with file:line]
```

## Phase 2: Research (Parallel Agents, Web Search)

These agents run in parallel with each other, but AFTER Phase 1 completes (they need the recon findings as context).

### Agent 4: Splitting Patterns Research

**Name**: `splitting-research`
**Task**:
Research best practices for splitting the specific types of large files found in Phase 1.

1. Web search for best practices on splitting modules that match the patterns found:
   - API route files with many endpoints
   - Large test files
   - Plugin files with multiple responsibilities
   - Core engine files with mixed concerns
2. Search for module splitting patterns and project structure best practices for the project's framework
3. Look at how popular open-source projects organize similar code
4. Recommend specific splitting strategies for each large file identified in Phase 1

**Output format**:
```
## Splitting Patterns Research

### Best Practices Found
[summary of research with source links]

### Recommended Splits
For each large file from Phase 1:
- File: [path]
- Current size: [lines]
- Recommended split: [description]
- New file structure: [list of new files]
- Migration risk: low/medium/high
```

### Agent 5: Project Optimization Research

**Name**: `optimization-research`
**Task**:
Research optimization patterns specific to projects of this type.

1. Web search for architecture patterns relevant to the project's domain
2. Search for project structure best practices for the frameworks in use
3. Search for common pitfalls in projects at this stage (pre-launch, growing feature set)
4. Research testing patterns for the project's domain
5. Identify architectural smells common in projects at this growth stage

**Output format**:
```
## Project Optimization Research

### Architecture Patterns
[relevant patterns with applicability assessment]

### Common Pitfalls at This Stage
[list of anti-patterns to watch for]

### Recommended Optimizations
[prioritized list with effort/impact ratings]

### Testing Improvements
[specific to the project's domain and testing framework]
```

## Phase 3: Synthesis (Team Lead)

The team lead collects all 5 reports and produces the final audit document.

### Synthesis Format

```markdown
# Codebase Hygiene Audit

**Date**: [current date]
**Scope**: [all or focus-area from $ARGUMENTS]

## Executive Summary
[2-3 sentence overview of codebase health with a letter grade A-F]

## Critical Issues (Fix Now)
[Issues that block scaling or cause bugs -- from all recon reports]

## High Priority (Fix This Sprint)
[Issues that slow development or create tech debt]

## Medium Priority (Fix This Month)
[Issues that are annoying but not blocking]

## Low Priority (Backlog)
[Nice-to-haves and minor inconsistencies]

## Refactoring Plan

### Phase A: Quick Wins (< 1 hour each)
[Small fixes that improve quality immediately]
- [ ] Fix 1: [description] -- [file path]
- [ ] Fix 2: [description] -- [file path]

### Phase B: Module Splits (1-3 hours each)
[Large file splits with specific plans]
- [ ] Split 1: [file] into [new files] -- [strategy]
- [ ] Split 2: [file] into [new files] -- [strategy]

### Phase C: Architecture Improvements (half-day each)
[Structural changes to layering, dependency management, etc.]
- [ ] Improvement 1: [description]
- [ ] Improvement 2: [description]

### Phase D: Convention Alignment (ongoing)
[Gradual fixes to inconsistencies, can be done opportunistically]
- [ ] Convention 1: [description]
- [ ] Convention 2: [description]

## Metrics to Track
- Total lines of code: [N]
- Largest file: [path] ([N] lines)
- Average file size: [N] lines
- Test coverage estimate: [N]%
- Convention violation count: [N]
```

## Phase 4: Implementation (Optional)

If the user wants to proceed with fixes after reviewing the audit, spawn implementation teams per phase. Each implementation team gets:

1. **An implementation agent** (worktree isolation) that makes the changes
2. **A QA agent** that runs the project's test suite and linter after changes

### Implementation Team Pattern

For each phase (A, B, C, D), when the user approves:

1. Create a feature branch: `refactor/hygiene-phase-X-[description]`
2. Spawn implementation agent with worktree isolation
3. Make changes according to the audit plan
4. Run QA pipeline (lint + types + tests)
5. If QA fails, fix issues and re-run
6. Report results to team lead
7. Team lead creates PR with the audit findings as context

### Agent Spawning Rules
- Only the team lead spawns agents (never delegate spawning to sub-agents)
- Implementation agents use `isolation: "worktree"` to avoid conflicts
- QA agents validate after each change, not just at the end
- If a phase has independent sub-tasks, parallelize them

## Scope Filtering

If `$ARGUMENTS` specifies a focus area, limit the audit scope:
- **structure**: Only run Agent 1 (Structure & Size) and Agent 4 (Splitting Patterns)
- **dependencies**: Only run Agent 2 (Dependency & Coupling)
- **duplication**: Only run Agent 3 (Inconsistency & Duplication)
- **all** (default): Run all 5 agents
