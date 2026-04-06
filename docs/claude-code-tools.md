---
tags: [claude-code, tools, reference]
keywords: Read, Write, Edit, Bash, Grep, Glob, Agent, TaskCreate, TaskUpdate, TaskList, SendMessage, WebSearch, WebFetch, EnterPlanMode, ExitPlanMode, Skill, ToolSearch
aliases: [tools reference, available tools, tool list]
priority: high
---

# Claude Code Tools Reference

## File Operations
- **Read** — Read file contents. Supports images, PDFs (with pages param), notebooks. Use instead of cat/head/tail.
- **Write** — Create new files or complete rewrites. Must Read first for existing files.
- **Edit** — Exact string replacement in files. Must Read first. Use old_string/new_string. Prefer over Write for modifications.
- **Glob** — Fast file pattern matching (e.g., "**/*.ts"). Use instead of find/ls.
- **Grep** — Ripgrep-based search. Regex, glob filters, output modes (content/files_with_matches/count). Use instead of grep/rg.

## Execution
- **Bash** — Execute shell commands. Use for system commands only. Prefer dedicated tools for file operations.

## Planning & Tasks
- **EnterPlanMode** — Enter read-only planning phase. Explore codebase, design approach, get user approval.
- **ExitPlanMode** — Exit planning, request approval to implement.
- **TaskCreate** — Create tasks with subject, description, activeForm (spinner text).
- **TaskUpdate** — Update task status (pending→in_progress→completed), add dependencies.
- **TaskList** — List all tasks with current status.
- **TaskGet** — Get detailed task info.

## Agent & Team Tools
- **Agent** — Spawn subagent for complex tasks. Parameters: prompt, subagent_type (Explore/Plan/general-purpose + custom agents), isolation ("worktree"), run_in_background, team_name, model.
- **TeamCreate** — Create agent team with shared task list and mailbox.
- **SendMessage** — Send message to named agent or team member.

## Web & Research
- **WebSearch** — Web search with domain filtering. Results include links and summaries.
- **WebFetch** — Fetch URL contents.

## Other
- **Skill** — Invoke user-defined skills (slash commands like /commit, /review-pr).
- **ToolSearch** — Fetch schemas for deferred tools. Query by name or keywords.
- **NotebookEdit** — Edit Jupyter notebook cells.

## Key Rules
- Prefer dedicated tools over Bash equivalents (Read over cat, Grep over grep)
- Multiple independent tool calls should be made in parallel
- Agent tool for complex multi-step research; direct tools for simple lookups
- ToolSearch needed before using deferred tools (they only have names until fetched)
