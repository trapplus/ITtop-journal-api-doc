# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Read First

Shared rules for all agents are in [`AGENTS.md`](AGENTS.md). This file adds Claude Code-specific guidance only.

## What This Is

Automatic OpenAPI documentation for the IT Top Academy Journal API. The pipeline collects real API responses, validates them with Pydantic, anonymizes sensitive data with Faker, and publishes `openapi.json` + Swagger UI to GitHub Pages.

## Claude Code Workflow

1. **Design** — Fill `devel/design/` docs sequentially (01-idea → 07-tradeoffs). Don't skip ahead.
2. **Plan** — Write implementation plan to `devel/plans/YYYY-MM-DD-name.md` before coding anything >1 file or >30 min.
3. **Implement** — TDD cycle: failing test → confirm failure → minimal code → confirm pass → commit.

## TDD Is Non-Negotiable

No production code without a failing test first. Write test → run it → confirm it fails for the right reason → implement → confirm pass. If code was written before the test, delete it and start over.

## Before Claiming Anything Is Done

Run the actual verification command and read the full output. No "should pass" or "looks correct" — fresh evidence only. See `skills/verification-before-completion.md`.

## Skills

Read the relevant skill file before starting work of that type:

| Situation | File |
|-----------|------|
| Something is broken | `skills/systematic-debugging.md` |
| Planning a feature | `skills/writing-plans.md` |
| Code review | `skills/code-review.md` |
| About to claim done | `skills/verification-before-completion.md` |
| Implementing anything | `skills/test-driven-development.md` |
