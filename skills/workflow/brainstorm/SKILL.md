---
name: brainstorm
description: Guided ideation with built-in feasibility research. Conversation with the user to explore ideas, research agents validate practicality, then resolve into a requirements doc for /plan-features.
user_invocable: true
---

# Brainstorm

Guided ideation pipeline that turns rough ideas into a validated requirements document. Alternates between conversation with the user and delegated research to keep main context lean.

## Invocation

```
/brainstorm [topic or idea]
```

Examples:
- `/brainstorm "real-time notifications system"`
- `/brainstorm "mobile-responsive dashboard"`
- `/brainstorm "plugin marketplace monetization"`

## Pipeline

### Phase 1: Idea Exchange (Main + User)

NO agents. NO file reads. Just conversation.

Main's job:
1. Listen to the user's idea
2. Ask clarifying questions to understand intent (not implementation):
   - What problem does this solve?
   - Who benefits?
   - What does success look like from the user's perspective?
3. Rephrase the idea back to confirm understanding
4. If the user has multiple ideas, list them all before researching any

**Output:** A numbered list of candidate ideas, each 1-2 sentences.

**Context budget:** This phase should use <500 tokens of main's context.

### Phase 2: Research Gates (Parallel Agents)

For EACH candidate idea from Phase 1, spawn research agents in parallel. Main does NOT read their raw output -- agents return a structured verdict.

**Agents per idea (launch all in parallel):**

| Agent | Question | Method | Verdict format |
|-------|----------|--------|---------------|
| `feasibility` | "Can our stack do this?" | Read architecture docs, relevant source files | FEASIBLE / RISKY / INFEASIBLE + 2-line reason |
| `prior-art` | "How do serious players solve this?" | Web search for established approaches | 3 bullet points: who does it, how, what we can learn |
| `conflict-check` | "Does this break or duplicate anything we have?" | Read architecture docs, grep for overlapping features | CLEAR / CONFLICT + what it conflicts with |

**Agent prompt template:**
```
You are a research agent. Answer ONE question and return a structured verdict.

QUESTION: [question]
IDEA: [idea description]
PROJECT: [brief context from Phase 1]

Research approach:
- [specific files to read or searches to run]

Return your verdict in EXACTLY this format:
VERDICT: [FEASIBLE|RISKY|INFEASIBLE] or [CLEAR|CONFLICT] or [bullet points]
REASON: [2-3 lines max, be specific, cite what you found]

Do NOT return raw file contents or search results. Only the verdict.
```

**Main receives:** ~10 lines per idea (3 verdicts x ~3 lines each). For 4 ideas, that's ~40 lines. Context stays lean.

### Phase 3: Resolution (Main + User)

Present research findings as a summary table:

```
## Research Results

| Idea | Feasible? | Prior Art | Conflicts? | Recommendation |
|------|-----------|-----------|------------|----------------|
| Real-time updates | RISKY -- WebSocket complexity | Competitors use SSE | CLEAR | Worth it if we use SSE instead |
| Mobile dashboard | FEASIBLE -- CSS-only responsive | Every competitor has this | CLEAR | Low effort, high impact |
```

Then ask the user:
- Which ideas to pursue?
- Any to kill or defer?
- Priority order of survivors?

### Phase 4: Requirements Capture (Main + User)

For each surviving idea, resolve these 6 questions through conversation. Do NOT proceed to output until all 6 are answered for every idea.

Track internally -- check off as each is answered:

- [ ] **What are we building?** Feature description, not implementation
- [ ] **Priority order?** If we run out of time, what ships first?
- [ ] **What's out of scope?** Prevents agents from gold-plating
- [ ] **Hard constraints?** Legal, budget, timeline, prohibited approaches
- [ ] **Decision-required items?** Things that need the user's call before agents can plan
- [ ] **Success criteria?** How do we know it's done?

If the user hasn't addressed one, ask directly: "We haven't nailed down [X] yet -- any constraints there, or should I leave it open for the planner?"

### Phase 5: Output

Write the requirements doc to `docs/brainstorms/{TOPIC}_REQUIREMENTS.md`.

Format:
```markdown
# [Topic] -- Requirements

> Brainstormed: [date]
> Status: Ready for /plan-features

## Constraints
- [Hard constraints from Phase 4]

## Features (priority order)

### 1. [Feature Name]
**Description:** [What, not how]
**Success criteria:** [Observable outcome]
**Out of scope:** [What this does NOT include]
**Research notes:** [Key findings from Phase 2 -- feasibility, prior art]
**Open decisions:** [Anything the planner needs to resolve]

### 2. [Feature Name]
[same structure]

## Deferred Ideas
- [Idea] -- deferred because [reason from Phase 3]

## Killed Ideas
- [Idea] -- killed because [reason from Phase 2/3]
```

Tell the user: "Requirements doc written. Run `/plan-features --doc docs/brainstorms/{TOPIC}_REQUIREMENTS.md` to generate the execution plan."

## Rules

### Main Agent Context Discipline
- **Phase 1:** No tools. Just conversation.
- **Phase 2:** Only Agent tool. Never read files, grep, or search inline. Receive only verdicts.
- **Phase 3:** Only text output. Summarize verdicts, don't relay raw research.
- **Phase 4:** Only conversation. Track the 6-question checklist internally.
- **Phase 5:** One Write call for the output doc. That's it.

**Main's total context growth for a 4-idea brainstorm should be under 200 lines.** This leaves room to run `/plan-features` and `/exec-plan` in the same session.

### Research Agent Discipline
- Agents return verdicts, not dumps
- Max 5 lines per verdict
- Cite specific files or URLs, don't paste contents
- If unsure, say "UNCERTAIN -- would need deeper investigation during planning"

### Conversation Discipline
- Don't ask all 6 questions at once -- weave them into natural conversation
- If the user gives a constraint unprompted, check it off silently
- Don't repeat back everything -- the doc captures it
- If the user wants to skip an item, that's fine -- note it as "open" in the doc
