---
tags: [claude-code, memory, persistence, CLAUDE.md]
keywords: CLAUDE.md, memory system, MEMORY.md, persistent context, project instructions, auto memory
aliases: [memory system, claude md, persistent instructions]
priority: normal
---

# Claude Code Memory & Persistence

## CLAUDE.md Files (Primary Persistence)
Auto-loaded at session start. Walks upward from CWD toward root. Subdirectory CLAUDE.md files lazy-loaded when Claude accesses files in that directory.

### Locations (in priority order)
1. ~/.claude/CLAUDE.md — Global instructions for all projects
2. {project-root}/CLAUDE.md — Project-specific instructions
3. {project-root}/.claude/CLAUDE.md — Alternative location
4. {subdirectory}/CLAUDE.md — Lazy-loaded when that dir is accessed

### What Goes in CLAUDE.md
- Coding conventions, style rules
- Project architecture overview
- Non-negotiable rules
- Tool usage preferences

### Survives Compaction
CLAUDE.md content is re-injected after context compaction. Put critical rules here, not in conversation.

## Auto Memory System
File-based memory at ~/.claude/projects/{project-path}/memory/

### Memory Types
- **user** — Role, preferences, knowledge level
- **feedback** — Corrections and confirmed approaches
- **project** — Ongoing work, goals, deadlines
- **reference** — Pointers to external systems

### Structure
- MEMORY.md — Index file (always loaded, keep under 200 lines)
- Individual .md files with frontmatter (name, description, type)
- Organized by topic, not chronologically

## Context Compaction
Auto-triggers at ~95% context usage. Retains ~20-30% of detail. Summaries focus on "what happened", lose "why" and subtle details.

### Survival Strategy
- CLAUDE.md: survives (re-injected)
- Memory files: survive (re-loaded on access)
- Conversation history: compressed to summary
- Tool outputs: cleared first, then conversation summarized

## Tasks (Session-Scoped Persistence)
TaskCreate/TaskUpdate for tracking work in current session. NOT persistent across sessions — use memory for cross-session information.
