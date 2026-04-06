---
tags: [mcr, writeup, post, context-engineering]
keywords: MCR writeup, blog post, announcement
aliases: [mcr post, mcr announcement]
priority: low
---

# I built a "subconscious brain" for Claude Code — it knows things without searching for them

Every Claude Code session starts with amnesia. It doesn't know your project architecture, your conventions, where your creds are stored, or even how its own features work. I was re-explaining TeamCreate, my project's time engine, and basic config every single conversation.

So I built MCR (Model Context Retrieval) — a system that automatically injects relevant knowledge into Claude Code sessions using hooks. No RAG, no vector databases, no MCP servers. Just Python scripts and markdown files.

## How it works

**Layer 1:** When you send a message, a `UserPromptSubmit` hook fires before Claude sees it. It tokenizes your prompt, matches against a knowledge vault index, and injects relevant files as context. Claude receives your message with knowledge already attached.

**Layer 2 (the interesting part):** When Claude reaches for a tool — Read, Grep, WebSearch — that's a *need signal*. It's the model saying "I need information I don't have." A `PreToolUse` hook intercepts the tool call, analyzes what Claude is looking for, and injects relevant vault context alongside the tool results. Claude never knows it was helped. Context just... appears.

## Results

Before MCR: "summarize the Finlet time engine" → Claude launches an Explore agent, reads 14 files, takes a minute.

After MCR: Same prompt → instant answer. The hook injected the time engine docs before Claude even started thinking.

The wildest part: Claude became **self-aware of the system**. I asked about our Terraform setup (which isn't in the vault), and it said: *"Had to search. The MCR vault has docs on the engine, plugins, API, and portfolio — but nothing covering the Terraform setup. If you want instant recall next time, I can add a vault doc."*

It knows what it knows, knows what it doesn't know, and offers to fix the gap. I didn't program that — it just emerged from Claude having the MCR docs in the vault.

## Tech details

- 4 Python scripts, pure stdlib (no pip install)
- ~20ms per hook execution
- Markdown vault with YAML frontmatter (Obsidian-compatible)
- Weighted keyword matching: keywords 5x, tags 3x, title 2x, body 1x
- 10K char output cap forces selectivity
- Graceful degradation — missing vault = silent pass-through

## Why not RAG?

At <500 files, keyword matching with weighted frontmatter is more than enough. No infrastructure, no embedding model, no vector DB. When you outgrow it, swap the matching layer — the hook architecture stays the same.

## The idea that makes this different

Every RAG system and knowledge base I found (including Karpathy's LLM Knowledge Base from 3 days ago) uses either prompt-time injection or model-initiated retrieval. The model has to consciously decide to look something up.

MCR Layer 2 uses **tool calls as implicit need signals**. The model doesn't ask for vault knowledge — it reaches for a tool, and the hook augments the response silently. It's the difference between giving someone a search engine and whispering the answer before they think to ask.

Open source, Apache 2.0: https://github.com/justnau1020/claude-os/tree/main/hooks/mcr

---

*Built in one session. The whole thing is ~200 lines of Python.*
