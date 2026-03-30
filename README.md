# Lean Context Framework

A collection of battle-tested Claude Code skills and an agent execution framework for keeping your main context window clean while orchestrating complex, multi-agent workflows.

Born from hundreds of hours of real production use. Every anti-pattern documented here destroyed real work at least once before it was caught.

---

## The Framework

The core idea is simple: **your main chat agent is a team lead, not a worker.**

Every task -- coding, research, exploration, testing, even reading files -- gets delegated to subagents or agent teams. The main agent's context window stays lean, which means:
- You can run longer sessions without hitting context limits
- You can chain multiple skills in one session (`/brainstorm` -> `/plan-features` -> `/exec-plan`)
- Each delegated agent gets a fresh, focused context window

The framework lives in `framework/` and includes:
- **`CLAUDE.md`** -- Drop-in template for your project's `.claude/CLAUDE.md`. Includes the agent execution model, file ownership template, and code conventions template.
- **`rules/agent-execution.md`** -- Auto-loaded rule that enforces lean-context discipline on every conversation.
- **`rules/file-ownership.md`** -- Template for mapping directories to team names, preventing merge conflicts during parallel execution.

## Skills Catalog

### Workflow (High-Level Orchestration)

| Skill | Command | What It Does |
|-------|---------|-------------|
| Brainstorm | `/brainstorm` | Guided ideation with feasibility research agents. Turns rough ideas into validated requirements docs. |
| Debate | `/debate` | 5-agent adversarial evaluation. Critics attack, defenders respond, moderator writes verdict. |
| Launch Review | `/launch-review` | Full pipeline: debate -> plan -> execute. Evaluates readiness, plans fixes, executes them. |
| Plan Features | `/plan-features` | Generates execution plans with file conflict tables, dependency graphs, and per-team specs. |
| Execute Plan | `/exec-plan` | State machine that reads a plan and mechanically executes it with worktree agents, commit gates, and test validation. |

### Code Quality (Review and Auditing)

| Skill | Command | What It Does |
|-------|---------|-------------|
| Hygiene Audit | `/hygiene-audit` | 5-agent codebase analysis: structure, dependencies, duplication, splitting patterns, optimization research. |
| Review PR | `/review-pr` | Reviews a GitHub PR for correctness, convention compliance, test coverage, and security. |
| Full Audit | `/audit` | 8-10 parallel agents cross-referencing docs vs code vs tests vs infra. Produces severity-scored report with optional auto-fix pipeline. |
| Dep Audit | `/dep-audit` | Security vulnerability scan and dependency freshness check. |

### Development (Scaffolding and Dev Helpers)

| Skill | Command | What It Does |
|-------|---------|-------------|
| Fix Issue | `/fix-issue` | End-to-end GitHub issue resolution: read issue, implement fix, write tests, commit. |
| Test All | `/test-all` | Run the full CI pipeline locally (lint, types, tests) in CI order. |
| New Endpoint | `/new-endpoint` | Scaffold a new REST API endpoint following existing patterns. |
| New MCP Tool | `/new-mcp-tool` | Add a new tool to a FastMCP server with proper descriptions and tests. |
| DB Migration | `/db-migration` | Guide through database schema changes with backup, migration, and testing. |
| Doc Architecture | `/doc-architecture` | Update architecture docs after code changes to keep docs in sync. |

### Operations (Deploy, Monitoring, Incidents)

| Skill | Command | What It Does |
|-------|---------|-------------|
| Deploy | `/deploy` | Pre-deploy safety checks, push to trigger CI/CD, monitor deployment. |
| Deploy Status | `/deploy-status` | Health check, recent CI runs, deployment status summary. |
| Incident | `/incident` | Emergency response guide: assess, contain, diagnose, remediate, document. |

### Conventions (Reusable Templates)

| Skill | Command | What It Does |
|-------|---------|-------------|
| API Conventions | `/api-conventions` | Auth patterns, route organization, error responses, MCP tools, middleware. |
| Dashboard Conventions | `/dashboard-conventions` | Frontend patterns, theming, API integration, file organization. |

### Utilities (Automation and Memory)

| Skill | Command | What It Does |
|-------|---------|-------------|
| Dream | `/dream` | Memory consolidation. Scans session transcripts for corrections, decisions, and preferences, then merges into persistent memory files. |

---

## Installation

### Option A: Copy skills you want

Copy individual skill directories into your project's `.claude/skills/` directory:

```bash
# Copy a single skill
cp -r skills/workflow/brainstorm /path/to/project/.claude/skills/

# Copy a category
cp -r skills/code-quality/* /path/to/project/.claude/skills/
```

### Option B: Install the full framework

Copy the framework files and all skills:

```bash
# Copy framework to your project
cp framework/CLAUDE.md /path/to/project/.claude/
cp -r framework/rules/* /path/to/project/.claude/rules/

# Copy all skills
cp -r skills/*/* /path/to/project/.claude/skills/
```

### Option C: Global installation

Install skills globally so they're available in every project:

```bash
# Global skills directory
cp -r skills/*/* ~/.claude/skills/
```

After installing, customize:
1. Edit `CLAUDE.md` to replace template sections with your actual tech stack, file ownership map, and code conventions.
2. Replace `{PRODUCTION_URL}` in operations skills with your actual production URL.
3. Replace `{source_dir}` and `{project}` placeholders with your actual directory names.

---

## Usage and Token Budget

### Know your budget before you start

This framework is optimized for **high-throughput usage** (Anthropic Max plan with 20x token budget, or equivalent). The lean-context pattern helps on any plan, but some skills are inherently token-intensive.

### Token intensity by skill tier

**Light (single-agent, <10k tokens per run):**
- `/fix-issue`, `/test-all`, `/dep-audit`, `/deploy`, `/deploy-status`, `/review-pr`
- Safe on any plan. These are the starting point.

**Medium (2-5 agents, ~30-80k tokens per run):**
- `/brainstorm`, `/plan-features`, `/doc-architecture`, `/hygiene-audit`
- Fine on Pro/Team plans. Each research agent uses its own context window.

**Heavy (5-12 agents, ~100-300k tokens per run):**
- `/debate` (5 agents), `/launch-review` (5-10 agents across 3 phases), `/audit` (8-12 agents)
- Best on Max plan or equivalent. A full `/audit --fix --deep` run with 10 research agents + fix pipeline can use 200k+ tokens.

**Marathon (chains of heavy skills):**
- `/brainstorm` -> `/plan-features` -> `/exec-plan` in one session
- `/launch-review` (debate + plan + execute in one pipeline)
- These work because the main agent stays lean (~300 lines of context) while agents come and go. But the cumulative token usage across all spawned agents adds up.

### Scaling advice

1. **Start with light skills.** Get comfortable with `/fix-issue` and `/test-all` first.
2. **Graduate to medium.** Try `/brainstorm` and `/plan-features` to see agent delegation in action.
3. **Use heavy skills intentionally.** Run `/audit` or `/debate` when you need a thorough evaluation, not as a daily check.
4. **Monitor your usage.** Check your dashboard after running heavy skills to calibrate expectations.

---

## Cross-Agent Compatibility

These skills are markdown files that describe workflows. They work with any coding agent that supports skill/prompt files:

- **Claude Code** -- Native support via `.claude/skills/` directory
- **Codex CLI** -- Place in project prompts directory
- **Gemini CLI** -- Compatible as instruction files
- **Cursor** -- Use as `.cursorrules` or in the rules directory
- **Other agents** -- The skills are just structured markdown. Any agent that reads instruction files can use them.

The multi-agent orchestration skills (`/debate`, `/audit`, `/launch-review`, `/exec-plan`) require agent tooling that supports spawning subagents (TeamCreate, SendMessage, Agent tool, or equivalent).

---

## Contributing

Contributions welcome. The bar for inclusion:

1. **Battle-tested.** Skills should come from real usage, not theoretical design. If you haven't run it at least 10 times in anger, it's not ready.
2. **Anti-patterns documented.** Every skill should include failure modes you actually hit and how you fixed them.
3. **Generic.** No project-specific business logic, paths, or domain concepts. Use placeholders.
4. **Lean-context aware.** Skills should respect the main agent's context budget. If a skill grows the main context by 500+ lines, it needs restructuring.

### How to contribute

1. Fork the repo
2. Add your skill to the appropriate category directory
3. Include frontmatter (name, description, tags)
4. Document anti-patterns from real usage
5. Open a PR with examples of the skill in action

---

## License

Apache 2.0 -- same as Anthropic's official repos. See [LICENSE](LICENSE) for details.
