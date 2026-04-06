---
tags: [claude-code, skills, SKILL.md, commands, automation]
keywords: skills, SKILL.md, slash commands, dynamic context injection, frontmatter, user-invocable
aliases: [skill system, slash commands, custom commands]
priority: normal
---

# Claude Code Skills System

Skills extend Claude with custom capabilities. They live as SKILL.md files and are invoked via /skill-name or automatically by Claude when relevant.

## Location
- Project skills: .claude/skills/{skill-name}/SKILL.md
- Global skills: ~/.claude/skills/{skill-name}/SKILL.md

## SKILL.md Structure
```markdown
---
name: deploy
description: Deploy the application to production
disable-model-invocation: false
allowed-tools: [Bash, Read, Write]
---

# Deploy Skill

Instructions for Claude when this skill is invoked...
```

### Frontmatter Fields
- **name** — Skill name (used in /name invocation)
- **description** — When Claude should use this skill
- **disable-model-invocation** — If true, only invocable via /name (not auto-triggered)
- **allowed-tools** — Restrict which tools the skill can use

## Dynamic Context Injection
Embed shell commands in SKILL.md using `!` backtick syntax:

```markdown
## Current PR Diff
!`gh pr diff`

## Test Results  
!`npm test 2>&1 | tail -20`
```

Commands execute BEFORE Claude sees the skill content. Output replaces the command. Claude only sees results, never the commands.

## Invocation
- User types /skill-name in chat
- Claude auto-invokes when description matches task (unless disable-model-invocation: true)
- Use the Skill tool programmatically: `Skill(skill="deploy", args="--prod")`

## Progressive Loading
- Skill descriptions loaded at session start (lightweight)
- Full SKILL.md content loaded only when invoked
- Supporting files read only when needed
