---
name: design-intake
description: Output the path-appropriate design note before Feature Path or Architecture Path work. Use when starting a task, before tests, implementation, review summaries, or design-only markdown. Also use for Fast Path compact design notes.
---

# Design intake

Load this skill before generating Feature Path or Architecture Path markdown,
tests, production code, or review summaries. Standing rules in `AGENTS.md`
still apply.

Follow `.agents/skills/process-lessons/SKILL.md` to apply matching lessons.
Do not expose hidden chain-of-thought.

## Feature Path and Architecture Path

Output this scaffold, then stop if path, phase, or an authoritative spec
(or explicit Architecture Path scope) is missing:

```markdown
[DESIGN CHECK]
- Scope and expected behavior:
- Specifications and files inspected:
- Component boundaries, ports/adapters, and VO/DTO candidates when applicable:
- Applicable constraints:
- Decisions, assumptions, and unresolved ambiguities:
- Included and omitted AI context:
- Task routing (model/assistant/tool):
- Input/output evidence contract when AI output is involved:
- Verification plan:
```

Fill from inspected artifacts. Do not guess ambiguity boundaries.

For a longer design-only session, also use `docs/templates/design-intake.md`.

## Fast Path

Use a compact design note instead of the full scaffold when the task is
mechanical, local, and does not change behavior, architecture, tests, or
agent instructions. State scope, omitted context, deterministic checks, and
why the full scaffold is unnecessary.
