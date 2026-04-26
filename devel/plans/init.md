# Plans

> Write a plan before starting work on a feature.
> Don't jump here without completing the design documents first.

---

## When to Write a Plan

1. Fill [`devel/design/01-idea.md`](../design/01-idea.md) — did the idea survive?
2. Fill design docs 02 through 07 sequentially
3. **Now** write the plan here

Don't skip design docs. Plans build on them.

---

## Format

File name: `YYYY-MM-DD-feature-name.md`. One file per feature.

For detailed plan structure with bite-sized tasks, see [`skills/writing-plans.md`](../../skills/writing-plans.md).

```
# Plan: [Title]

## References
- Idea: `devel/design/01-idea.md`
- Requirements: `devel/design/02-functional-requirements.md`
- Architecture: `devel/design/04-architecture-highlevel.md`

## What we're doing
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Files affected
- `src/...`
- `tests/...`

## Done when
How do we know it's done?
```
