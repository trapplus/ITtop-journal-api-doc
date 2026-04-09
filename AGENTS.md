# Agent Guidelines

> Read this before doing anything. No exceptions.

## Project Context

<!-- TODO: Fill in before using this template -->
- **Project:** [Name]
- **Language / Stack:** [e.g. C++20 / CMake / SFML, Python / uv / FastAPI]
- **Test runner:** [e.g. pytest, catch2, cargo test]
- **Linter / formatter:** [e.g. clang-tidy, ruff, clippy]

---

## Non-Negotiables

- Zero compiler/linter warnings on every commit
- Tests before implementation (RED → GREEN → REFACTOR)
- No magic numbers — constants go in a dedicated config/constants file
- English comments only, conversational ("why not what")
- One problem per commit, descriptive commit messages

---

## Workflow

### Before Writing Any Code

1. **Clarify the task.** Ask one focused question if the spec is ambiguous. Don't guess.
2. **Check existing code.** Don't reinvent what's already there.
3. **Write the plan.** For anything >1 file or >30 min of work, write a plan to `docs/plans/YYYY-MM-DD-feature.md` first.

### Implementation Loop

```
Write failing test → confirm it fails → implement minimal code → confirm it passes → commit
```

Never skip the "confirm it fails" step. It proves the test actually catches the bug.

### Before Marking a Task Done

- [ ] All tests pass
- [ ] No new warnings introduced
- [ ] Linter/formatter clean
- [ ] Committed with a clear message

---

## Debugging Protocol

**Find root cause before touching anything.**

1. Read the full error — stack trace, line numbers, error codes
2. Reproduce it reliably
3. Check recent changes (`git diff`, recent commits)
4. Form one hypothesis: *"X is broken because Y"*
5. Make the smallest possible change to test it
6. If 3+ fixes failed → stop, the architecture is wrong, discuss

Red flags — stop and re-investigate if you're thinking:
- "Just try this and see what happens"
- "Quick fix for now"
- "It's probably X" (without evidence)

---

## File Structure

```
src/        # Source code
tests/      # Tests — mirror src/ structure
docs/
  design/   # Design docs
  plans/    # Implementation plans (YYYY-MM-DD-name.md)
skills/     # Agent skill references (see below)
.codex/     # Codex-specific config
```

<!-- Adjust per project, e.g. for C++ add include/ -->

---

## Skills

When tackling a specific type of task, read the relevant skill file first:

| Situation | Skill file |
|-----------|-----------|
| Something is broken | `skills/systematic-debugging.md` |
| Planning a feature | `skills/writing-plans.md` |
| Code review | `skills/code-review.md` |

---

## What Not To Do

- Don't add dependencies without asking
- Don't refactor unrelated code "while you're there"
- Don't open PRs without human review of the full diff
- Don't leave TODOs without a linked issue or explanation
- Don't assume — ask
