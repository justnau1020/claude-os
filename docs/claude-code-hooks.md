---
tags: [claude-code, hooks, automation, development]
keywords: PreToolUse, PostToolUse, UserPromptSubmit, SessionStart, Stop, hook development, additionalContext, permissionDecision
aliases: [hook system, event hooks, claude hooks]
priority: high
---

# Claude Code Hooks

Hooks are event-driven scripts that execute in response to Claude Code events. They provide deterministic control over a probabilistic system.

## Hook Events
- **SessionStart** — Session begins. Load context, set environment.
- **UserPromptSubmit** — User sends message, before Claude sees it. Can inject additionalContext or block.
- **PreToolUse** — Before tool execution. Can allow/deny/modify input/inject context.
- **PostToolUse** — After tool returns. Can provide feedback.
- **Stop** — Agent considers stopping. Can block if work incomplete.

## Output Schema (PreToolUse)
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "reason here",
    "additionalContext": "optional context string"
  }
}
```

## Output Schema (UserPromptSubmit)
```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "optional context string"
  }
}
```

## Key Rules
- Hook output capped at 10,000 characters
- Always exit 0 unless intentionally blocking (exit 2 blocks)
- Command hooks receive JSON via stdin. Confirmed field names (snake_case):
  - UserPromptSubmit: session_id, transcript_path, cwd, permission_mode, hook_event_name, prompt
  - PreToolUse: session_id, transcript_path, cwd, permission_mode, hook_event_name, tool_name, tool_input
- Hooks configured in ~/.claude/settings.json
- Changes require session restart to take effect
