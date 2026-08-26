---
name: process-review
description: Run the same-context development-process review when marking a local issue or work plan done. Use when closing LISS or WP work, after verification and status sync, before reporting completion.
---

# Completion process review

Canonical policy: `docs/collaboration/process-review.md`. Follow that file.
This skill does not replace typed Adjudicator approval or product review.

## When

In the same context that is closing the issue or work plan, after
deterministic verification and issue-status synchronization, before reporting
completion. Do not spawn a subagent solely for this review unless
`docs/collaboration/runtime-routing.toml` already requires `separate_context`
for agent review.

## Inspect

Ask only process questions in the Canonical policy. Do not turn this into a
second product-code review or a session incident log.

## Record

- No deviation: write the Canonical one-line process-review record in the
  issue or work plan.
- Deviation or operational problem: stop, agree disposition with the
  Adjudicator, follow `.agents/skills/process-lessons/SKILL.md` when
  reusable, and write template feedback under
  `docs/collaboration/template-feedback/` only when they so decide.
