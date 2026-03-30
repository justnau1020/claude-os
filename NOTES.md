# Things I learned building with Claude Code

These are patterns I picked up building a full product with Claude Code over hundreds of hours. They're not rules. They're notes -- things that worked for me, things that surprised me, things I wish someone had told me on day one. Take what's useful, ignore what isn't.

The product in question is [Finlet](https://finlet.dev) -- a financial simulation platform I built almost entirely with Claude Code. Backend, frontend, plugins, database, deployment, the whole stack. These patterns weren't designed in advance. They emerged from getting burned enough times to change behavior.

If you want the formalized version of these ideas, check out the [framework](./framework/) directory. What follows is the informal, opinionated version.

---

**Check your context, don't trust the counter.**
Ask the model "how's your context?" periodically. I've found that the model's self-assessment of what it can still recall is a better signal than the token count in the corner. Performance degrades before you hit the limit -- responses get vaguer, it starts re-reading files it already read, instructions from earlier in the session get ignored. Catching it early saves you from subtle errors that are hard to trace back to context exhaustion.

**Your main agent is a team lead, not a worker.**
The single biggest improvement to my workflow was stopping the main agent from doing any actual work. It reads your intent, delegates to subagents, and keeps summaries. The moment your main context fills with raw grep output or file contents, quality drops everywhere -- not just on the task that produced the output, but on every subsequent task in the session. Keep it lean.

**Delegate even recon.**
Your instinct is to "just quickly check" a file or grep for something. Don't. Spawn an Explore agent. The 5 seconds you save reading inline costs you context space that compounds over the session. I resisted this for weeks because it felt like overkill. It isn't. The difference between a 2000-line main context and a 200-line main context is the difference between a session that lasts 30 minutes and one that lasts 3 hours.

**Parallel by default, sequential only when forced.**
If two tasks don't depend on each other, launch them at the same time. I routinely run 3-5 agents in parallel. The wall-clock time improvement is dramatic, but the real win is that each agent gets a clean context. A fresh agent with a focused task outperforms a fatigued agent juggling three things every single time.

**Worktree isolation for anything that writes code.**
Multiple agents editing the same repo will cause merge conflicts that waste more time than the parallelism saves. Worktrees give each agent its own working copy of the repo. They write their changes, commit, and the results get merged back. This is non-negotiable for me now -- I've lost too many agent-hours to conflicts that could have been avoided.

**Error messages are interfaces.**
"API error" helps nobody -- not you, not the agent trying to recover from it. "Service X rate limit exceeded: 0/60 calls remaining, resets in 42 seconds" lets the agent (or you) make a decision. I treat error messages like I treat UI copy -- they should be specific, actionable, and tell you exactly what happened and what to do about it.

**Skills over prompts.**
Anything you've typed more than twice belongs in a skill file. Skills are version-controlled, shareable, and consistent. Prompts are ephemeral -- they live in your clipboard or your memory, both of which are unreliable. I have 20+ skills now and my prompts are usually just "do /thing." The upfront cost of writing a skill pays for itself after the second use.

**Memory is for surprises, not facts.**
Don't save things to memory that you can derive from the code or git history. Save the stuff that would surprise a future agent -- decisions that went against convention, user preferences that aren't obvious, lessons from failures that won't show up in a diff. A memory file full of "the project uses Python 3.12" is useless. A memory file that says "we tried caching plugin responses and it caused stale data bugs, so we don't do that anymore" is gold.

**Search before asserting.**
The model will confidently tell you something doesn't exist or isn't possible. Make it search first. I've lost hours to false negatives where the model said "that API doesn't support X" when it absolutely did. I now have a rule in my global config that forces a web search before any negative assertion. It catches the model's blind spots before they become your blind spots.

**Compaction will eat your context -- plan for it.**
Long sessions trigger automatic context compression. If you don't explicitly tell the model what to preserve (active task, files modified, key decisions), it will lose track of things that matter. I include compaction preservation rules in my CLAUDE.md -- a short list of things that must survive compression. Without this, I'd come back from compaction to find the model had forgotten which branch it was working on or which files it had already modified.

**The framework scales down.**
These patterns work best with high token budgets, but the core idea -- keep main context lean, delegate, summarize -- helps on any plan. Start with single-agent delegation: instead of reading a file yourself, spawn one agent to read it and summarize. That alone will extend your sessions. Add parallelism and agent teams when your budget allows it.

**The lean context framework.**
Tips 2 through 5 above are pieces of a single idea that changed how I work. I call it the lean context framework, and the formalized version lives in the [framework directory](./framework/). The short version: your main Claude Code session is a team lead. It understands what you want, decides who does the work, and keeps summaries. It never reads files, never writes code, never runs tests. Every task -- even a quick file check -- gets delegated to a subagent or agent team that works in its own context. The result comes back as a summary, not raw output. This means your main context stays small, focused, and high-quality for the entire session. I've had 3-hour sessions stay sharp because the main context never exceeded a few hundred lines. Before this pattern, quality would degrade after 30 minutes. If you take one thing from these notes, take this.

---

These notes will grow as I learn more. If you want the formalized version, check out the [framework](./framework/). If you want to see the skills these patterns produced, browse the [skills](./skills/) directory.
