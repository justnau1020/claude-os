---
tags: [claude-code, features, CLI, configuration]
keywords: settings.json, permissions, bypass, compact, MCP servers, plugins, effort level, context window, 1M tokens
aliases: [claude code config, cli features, claude code settings]
priority: normal
---

# Claude Code Features & Configuration

## Settings File
~/.claude/settings.json — Global settings. Project-level at .claude/settings.json.

### Key Settings
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1",
    "CLAUDE_CODE_EFFORT_LEVEL": "max"
  },
  "permissions": {
    "allow": ["Bash", "Edit", "Write", "Read", "WebFetch", "Agent", "mcp__*"],
    "defaultMode": "bypassPermissions"
  },
  "hooks": { ... },
  "enabledPlugins": { ... }
}
```

## Permission Modes
- **default** — Ask for each tool use
- **acceptEdits** — Auto-approve file edits
- **bypassPermissions** — Auto-approve everything
- **plan** — Read-only until plan approved

## Context Window
- Opus 4.6 and Sonnet 4.6: 1M token context window (standard, no beta header)
- Auto-compaction at ~95% capacity
- /compact — Manual compaction command

## MCP Servers
Configured in .claude.json or settings.json. Claude defers tool loading (only names at start, full schemas on demand via ToolSearch). Well-written tool descriptions (20+ words) critical for auto-discovery.

## CLI Commands
- /compact — Compress conversation context
- /clear — Clear conversation history
- /help — Show help
- /fast — Toggle fast output mode (same Opus model, faster output)
- /{skill-name} — Invoke a skill

## Plugins
Marketplace plugins in enabledPlugins. Examples: imessage, codex, discord, telegram.

## Agent Subagent Types
Built-in: general-purpose, Explore (codebase search), Plan (architecture design).
Custom: defined in .claude/agents/{name}.md with YAML frontmatter.

## Model Info
- Claude Opus 4.6 (claude-opus-4-6) — Most capable, 1M context
- Claude Sonnet 4.6 (claude-sonnet-4-6) — Fast, 1M context
- Claude Haiku 4.5 (claude-haiku-4-5-20251001) — Fastest, cheapest
- Default to latest Opus/Sonnet for AI applications
