---
name: same-context-review
description: Run an in-session agent review when review isolation is same_context or the routing file is missing. Use when producing a review packet, Review Summary, or Phase 3 reviewer pass without a separate-context subagent.
---

# Same-context review

Canonical procedure: `docs/templates/same-context-review.md`. Follow that
file. This is weaker isolation than a separate-context subagent. It does not
replace the human Adjudicator.

## When

Use this skill when an agent review packet is already required and:

- `docs/collaboration/runtime-routing.toml` sets `[review].isolation` to
  `same_context`, or
- that file is missing.

If isolation is `separate_context`, request a host subagent launch instead.
If isolation is `ask`, stop for the Adjudicator.

Contract-file changes still require Adjudicator review under
`docs/collaboration/prompt-instruction-change-control.md`.

## Role

Switch to reviewer. Re-read artifacts from disk. Do not use prior author
reasoning as evidence. Do not continue implementing while reviewing.

After the packet, follow `.agents/skills/process-lessons/SKILL.md`.
