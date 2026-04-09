---
tags: [mcr, knowledge-retrieval, hooks, automation, context-engineering]
keywords: MCR, Model Context Retrieval, subconscious brain, automatic context injection, UserPromptSubmit, PreToolUse, vault, indexer
aliases: [mcr system, model context retrieval, subconscious brain, automatic context]
priority: normal
---

# MCR (Model Context Retrieval) System

## What It Is
A hook-based system that automatically injects relevant knowledge into Claude Code conversations. Two-layer "subconscious brain" — Claude receives context without manually retrieving it. Built April 2026. Secondary benefit: each vault injection that preempts a search prevents 50k+ tokens of exploration from entering any context, significantly reducing session token consumption.

## Architecture

### Layer 1: Prompt Matching (UserPromptSubmit)
- Fires when user sends a message, before Claude sees it
- Analyzes prompt keywords against vault index
- Injects relevant vault content as additionalContext
- Claude sees the context as if it was always there

### Layer 2: Need-Signal Matching (PreToolUse)
- Fires when Claude reaches for a tool (Read, Grep, Glob, WebSearch, WebFetch)
- Tool calls ARE need signals — Claude expressing a knowledge gap
- Analyzes what Claude is looking for, matches against vault
- Injects relevant context alongside auto-allowing the tool
- Claude gets both tool results AND vault context without requesting it
- **This layer is novel — nobody else is doing this**

### Non-need-signal tools (Bash, Write, Edit, etc.)
Auto-allowed with no context injection. Only information-seeking tools trigger Layer 2.

## File Locations
- `~/.claude/hooks/mcr_lib.py` — Shared library (tokenizer, matcher, budget manager)
- `~/.claude/hooks/mcr_prompt_matcher.py` — Layer 1 hook
- `~/.claude/hooks/mcr_tool_matcher.py` — Layer 2 hook (also handles auto-allow)
- `~/.claude/hooks/mcr_indexer.py` — Builds search index from vault
- `~/obsidian-vault/` — Knowledge vault (markdown files with YAML frontmatter)
- `~/obsidian-vault/.mcr/index.json` — Inverted term index

## Vault File Format
```markdown
---
tags: [topic1, topic2]
keywords: specific term, another term
aliases: [alternative name]
priority: high
---

# Title

Content...
```

## Rebuilding the Index
After adding/editing vault files:
```bash
python3 ~/.claude/hooks/mcr_indexer.py
```

## Performance
- Hook execution: ~20ms total (Python startup ~15ms, MCR logic <2ms)
- Hook output cap: 10,000 characters (Claude Code limit)
- Content budget: 8,000 chars (Layer 1), 7,000 chars (Layer 2)
- Max 5 files per injection
- Graceful degradation: missing vault/index → silent pass-through, never blocks

## Matching Algorithm
1. Tokenize query (lowercase, 3+ chars, filter stopwords, generate bigrams)
2. Look up tokens in inverted index (terms weighted: keywords 5.0, tags 3.0, title 2.0, body 1.0)
3. Accumulate scores per file with breadth bonus for multi-token matches
4. Minimum threshold: files below score 3.0 filtered out
5. Relative threshold: only files scoring >= 30% of top match survive
6. Session dedup: files already injected this session are skipped (tracked in /tmp/mcr_sessions/)
7. Top files read within character budget, frontmatter stripped

## Priority Hierarchy
- `priority: high` (1.5x) — reserved for project overviews only
- `priority: normal` (1.0x) — all specific/detailed docs
- `priority: low` (0.5x) — supplementary content
- Keyword weight (5x) dominates priority (1.5x), so specific queries still surface normal-priority files

## Configuration
Hooks wired in ~/.claude/settings.json:
```json
"hooks": {
  "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "/opt/homebrew/bin/python3 /Users/justnau/.claude/hooks/mcr_prompt_matcher.py", "timeout": 5000}]}],
  "PreToolUse": [{"hooks": [{"type": "command", "command": "/opt/homebrew/bin/python3 /Users/justnau/.claude/hooks/mcr_tool_matcher.py", "timeout": 5000}]}]
}
```
