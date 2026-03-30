---
name: doc-architecture
description: Update architecture documentation after code changes to keep docs in sync with reality. Use when structural changes have been made and documentation needs updating.
disable-model-invocation: true
context: fork
---

# Update Architecture Documentation

Update the project's architecture documentation to reflect recent code changes.

## Steps

### 1. Review recent changes

```bash
git diff HEAD~5 --stat
git log --oneline -10
```

### 2. Read current architecture doc

Read the architecture documentation in full. Common locations:
- `docs/ARCHITECTURE.md`
- `docs/architecture/`
- `ARCHITECTURE.md`

### 3. Identify gaps

Compare the code changes against the architecture doc:
- Are new modules documented?
- Are changed interfaces reflected?
- Are removed features cleaned up?
- Are new invariants captured?
- Are new dependencies mentioned?

### 4. Update the doc

Make targeted updates to the architecture documentation:
- Add sections for new components
- Update descriptions for changed components
- Remove references to deleted components
- Keep the existing structure and tone

### 5. Verify accuracy

Cross-reference updated doc against actual code to ensure accuracy. The architecture doc is the source of truth -- it must be correct.
