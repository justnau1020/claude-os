---
name: debate
description: Adversarial 5-agent debate to evaluate what you have. Critics attack, defenders respond, moderator writes verdict. Produces a readiness report -- feed into /plan-features to act on findings.
user_invocable: true
---

# Debate

Adversarial evaluation of the current state of a feature, system, or codebase area. Five agents argue from different angles, a moderator synthesizes a verdict. The output is a readiness report -- not a plan, not code.

Use this when you don't know if what you have is good enough.

## Invocation

```
/debate [topic] [--scope "focus areas"] [--constraints "known constraints"]
```

Examples:
- `/debate "API security posture"`
- `/debate "onboarding experience" --scope "auth, setup, first use"`
- `/debate "launch readiness" --constraints "feature X is gated behind flag"`

## Pipeline

### Phase 0: Constraints Gathering (Main + User)

Before spawning agents, main MUST:

1. **Ask the user** for known constraints:
   - What's in scope for this review?
   - Any decisions already made that agents should respect?
   - Known limitations or trade-offs to evaluate against?
2. **Check memory** for relevant project constraints
3. **Compile a constraints block:**

```
CONSTRAINTS (non-negotiable):
- [constraint 1]
- [constraint 2]
DO NOT propose solutions that violate these constraints.
```

**This prevents the #1 failure mode:** agents recommending something already ruled out.

### Phase 1: Debate (Parallel Agents)

Spawn 5 agents. The 4 debaters run in parallel. Moderator waits for all 4.

| Agent | Role | Method |
|-------|------|--------|
| `arch-critic` | Code auditor -- finds gaps, bugs, half-baked features | Reads source code, tests, architecture docs |
| `comp-critic` | Competitive benchmarker -- holds us to industry bar | Web search for competitors, best practices |
| `code-defender` | Argues readiness from actual code evidence | Reads source code, test coverage, recent commits |
| `industry-defender` | Argues competitive positioning from market context | Web search for market context, user expectations |
| `moderator` | Synthesizes all 4 reports into a verdict | Receives reports via SendMessage, writes report |

**Agent prompt template for debaters:**
```
You are [ROLE] in an adversarial debate about: [TOPIC]
Scope: [SCOPE]

CONSTRAINTS:
[constraints block]

Your job: [ATTACK gaps / DEFEND readiness] with EVIDENCE.
- Read the actual code, don't guess
- Cite specific files, functions, line numbers
- Compare against [competitors / best practices]
- Be brutal -- no hedging, no "it depends"

Send your report (max 50 lines) to the moderator agent when done.
Format:
## [Your Role] Report
### Key Findings (numbered, max 10)
### Verdict: [READY / NOT READY / CONDITIONAL]
### Evidence: [file:line citations]
```

**Moderator prompt:**
```
You are the moderator. Wait for all 4 debate reports.

Once you have all 4, write the readiness report to:
docs/brainstorms/{TOPIC}_READINESS_REPORT.md

Report format:
# [Topic] -- Readiness Report
> Generated: [date] | Debate agents: 4 | Moderator synthesis

## Verdict: [READY / NOT READY / CONDITIONAL]
[2-3 sentence summary]

## Consensus Points (both sides agree)
- [point]

## Contested Points (sides disagree)
| Point | Critics Say | Defenders Say | Moderator Assessment |
|-------|------------|---------------|---------------------|

## Critical Issues (must fix before launch)
1. [issue] -- [evidence] -- [severity]

## Improvement Opportunities (nice to have)
1. [opportunity] -- [effort estimate]

## Raw Reports
[Append all 4 reports for reference]
```

### Phase 2: Handoff (Main)

Once the moderator writes the report:

1. Read the verdict line only (1 line, not the full report)
2. Report to user:
   ```
   Debate complete. Verdict: [VERDICT]
   Report: docs/brainstorms/{TOPIC}_READINESS_REPORT.md

   To act on findings: /plan-features --doc docs/brainstorms/{TOPIC}_READINESS_REPORT.md
   ```
3. Clean up the team

That's it. Debate produces a report. Planning and execution are separate skills.

## Main Context Discipline

- **Phase 0:** Conversation only. No tools except memory check.
- **Phase 1:** Only Agent/TeamCreate/SendMessage. Main does NOT read code, grep, or search.
- **Phase 2:** Read one line from the report (the verdict). Summarize to user.

**Main's total context growth: ~30 lines.** The entire debate happens outside main's context.

## Anti-Patterns

1. **Main reading the full report.** The report can be 200+ lines. Main reads the verdict line, tells the user where the file is. The user or `/plan-features` reads the rest.
2. **Debaters being polite.** The whole point is adversarial tension. Critics should be harsh. Defenders should push back hard. Moderate positions produce useless reports.
3. **Skipping Phase 0.** Without constraints, agents will recommend prohibited libraries, impossible timelines, or solutions that violate business rules.
4. **Bundling planning/execution.** This skill produces a REPORT. If you want to act on it, run `/plan-features`. Separation keeps each skill focused and composable.
5. **Moderator taking sides.** The moderator synthesizes, doesn't advocate. If critics found 8 issues and defenders addressed 3, the moderator says "5 unresolved issues remain" -- not "defenders made a strong case."
