# MCR (Model Context Retrieval)

A subconscious brain for Claude Code. Automatically injects relevant knowledge from a personal vault into every conversation — without Claude manually searching for it.

## The Problem

Every Claude Code session starts ignorant. It doesn't know your project architecture, your team conventions, where your credentials live, or even its own latest features. You re-explain the same things every conversation.

## The Solution

MCR uses Claude Code hooks to automatically inject relevant context at two layers:

**Layer 1: Prompt Priming** — When you send a message, a `UserPromptSubmit` hook matches your prompt against a knowledge vault index and injects relevant files before Claude sees your message.

**Layer 2: Need-Signal Detection** — When Claude reaches for a tool (Read, Grep, WebSearch), that's a *need signal*. A `PreToolUse` hook intercepts it, matches what Claude is looking for against the vault, and injects relevant context alongside the tool results. Claude never knows it was helped.

## Setup (5 minutes)

### 1. Copy scripts to hooks directory

```bash
cp hooks/mcr/mcr_*.py ~/.claude/hooks/
```

### 2. Create your vault

```bash
mkdir -p ~/obsidian-vault/.mcr
```

### 3. Add vault files

Create `.md` files with YAML frontmatter:

```markdown
---
tags: [project, architecture]
keywords: auth system, JWT, session tokens
priority: high
---

# Auth Architecture

Your knowledge here...
```

### 4. Build the index

```bash
python3 ~/.claude/hooks/mcr_indexer.py
```

### 5. Wire hooks into settings

Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [{
          "type": "command",
          "command": "python3 ~/.claude/hooks/mcr_prompt_matcher.py",
          "timeout": 5000,
          "statusMessage": "MCR: scanning vault..."
        }]
      }
    ],
    "PreToolUse": [
      {
        "hooks": [{
          "type": "command",
          "command": "python3 ~/.claude/hooks/mcr_tool_matcher.py",
          "timeout": 5000,
          "statusMessage": "MCR: auto-allowing + scanning vault..."
        }]
      }
    ]
  }
}
```

### 6. Restart Claude Code

Hooks load at session start.

## Configuration

The vault path is hardcoded to `~/obsidian-vault` in `mcr_lib.py`. To use a different location, either edit the path in `mcr_lib.py` or symlink your vault:

```bash
ln -s /path/to/your/vault ~/obsidian-vault
```

## Vault File Format

```markdown
---
tags: [broad, categories]
keywords: specific term, another term, exact phrase
aliases: [alternative name, abbreviation]
priority: high
---

# Title

Content...
```

**Weight by field:** keywords (5x) > aliases (4x) > tags (3x) > title (2x) > body (1x)

**Priority multiplier:** high (1.5x), normal (1.0x), low (0.5x)

## How It Works

1. **Indexer** scans vault, parses frontmatter, extracts terms, builds inverted index (`index.json`)
2. **Prompt matcher** tokenizes your message, matches against index, injects top files as `additionalContext`
3. **Tool matcher** analyzes tool inputs (grep patterns, file paths, search queries), matches against index, injects context alongside auto-allowing the tool

### Matching Algorithm

- Tokenize query (lowercase, 3+ chars, filter stopwords, generate bigrams)
- Look up each token in inverted index
- Accumulate scores per file with breadth bonus: matching 4 tokens beats matching 1 with high weight
- Top 5 files read within character budget (8K for prompts, 7K for tools)
- Files below score threshold (1.0) filtered out

## Performance

- **~20ms** per hook execution
- **10K char cap** on output (Claude Code limit)
- **Pure Python stdlib** — no pip install needed
- **Graceful degradation** — missing vault/index → silent pass-through, never blocks

## Why This Over RAG?

RAG needs: vector DB, embedding model, chunking strategy, infrastructure.

MCR needs: a folder of markdown files and 4 Python scripts.

At <500 files, keyword matching with weighted frontmatter is fast and accurate enough. When you outgrow it, swap the matcher for embeddings — the hook architecture stays the same.

## Rebuilding the Index

After any vault changes:

```bash
python3 ~/.claude/hooks/mcr_indexer.py
```

## License

Apache 2.0 — same as the parent repo.
