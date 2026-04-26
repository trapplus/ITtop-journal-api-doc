# GEMINI.md

> Gemini CLI-specific mandates. Shared rules are in [`AGENTS.md`](AGENTS.md) — read it first.

## Core Principles

- **Context-First**: Before any action, read `AGENTS.md` for project-specific stack and constraints.
- **TDD**: Never write production code without a failing test first. No exceptions.
- **Systematic Debugging**: Find root cause before fixing. Use `skills/systematic-debugging.md`.
- **Zero Warnings**: Every commit must leave the codebase with zero compiler/linter warnings.

## Lifecycle Phases

### Phase 1: Design (`devel/design/`)

- Start with `01-idea.md`, progress through all 7 docs sequentially.
- Don't skip. Document decisions in `07-tradeoffs.md`.

### Phase 2: Planning (`devel/plans/`)

- For tasks >30 min or >1 file, create a plan: `YYYY-MM-DD-feature-name.md`.
- Follow format in `skills/writing-plans.md`.

### Phase 3: Implementation

- **Files**: `src/` for logic, `tests/` for tests (mirroring `src/` structure).
- **Red Phase**: Write minimal failing test. Run it. Confirm it fails for the expected reason.
- **Green Phase**: Write minimal code to pass.
- **Refactor**: Clean up.

## Commit & Verification

- **Format**: `type: short description` (feat, fix, refactor, test, docs, chore).
- **Verify**: Run full test suites and linters before claiming completion. See `skills/verification-before-completion.md`.

## Decision Making

- Ambiguous task? **Ask, don't guess.**
- 3+ fix attempts failed? **Stop. Re-evaluate architecture.** Discuss with the user.
