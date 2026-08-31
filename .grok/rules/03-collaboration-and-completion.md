# Grok Agent Instructions: Collaboration and Completion

## Adjudicator Interaction

When a decision affects architecture, capture it as an ADR. When a decision
is unknown, list it in the path-appropriate design note as an ambiguity
boundary.

Every request starts from design intake. Load
`.agents/skills/design-intake/SKILL.md` and output its `[DESIGN CHECK]`
scaffold for Feature Path and Architecture Path work. Fast Path uses the
compact note in that skill.

## Decision Gates

Stop for Adjudicator decision when:

- phase is neither explicitly selected nor uniquely established by the
  immediately preceding exchange.
- issue dependencies are unclear or unresolved.
- requirements imply a new architecture decision.
- a payload would need unrelated large context.
- a task requires secrets, full source documents, or full private data
  exports.
- an external provider, SDK, model, DB product, or schema convention must be
  chosen.
- a change would alter accepted tests.
- deterministic verification contradicts AI assumptions.
- a bounded execution batch is missing named Issue IDs, allowed paths and
  phases, expiry, or invalidating architecture triggers.
- CI success is treated as Adjudicator approval.

Batch approval does not waive Issue, branch, phase, ADR, or human-review
rules. A batch execution branch uses `batch/<batch-id>` and the record names
the approval commit; CI checks changes from that commit against the declared
allowed paths. CI success is not Adjudicator approval. When writing or
executing a bounded batch, follow `.agents/skills/execution-batch/SKILL.md`.

## Handoff and Completion

When handing off or stopping before completion, follow
`.agents/skills/agent-handoff/SKILL.md`. When asking the Adjudicator for
approval, follow `.agents/skills/adjudicator-review/SKILL.md`.
When an agent review packet is already required, honor
`docs/collaboration/runtime-routing.md`: follow
`.agents/skills/same-context-review/SKILL.md` for `same_context`, request a
host subagent launch for `separate_context`, and ask the Adjudicator when
the setting is `ask`.

Generated source code must minimize human cognitive load. Prefer clear
responsibility boundaries, small functions, straightforward names, and
reviewable tests. Do not compress implementation into dense code just to be
minimal.

Before reporting completion, check `docs/collaboration/definition-of-done.md`.
When the trace policy requires a trace, follow
`.agents/skills/ai-work-trace/SKILL.md`. Use feature-unit branches for feature
work; do not implement issue work directly on `main` or the trunk branch, per
`docs/collaboration/branch-commit-pr-discipline.md`.

For feature work, identify local issue (`docs/issues/LISS-*`) or GitHub
issue dependencies before creating the branch, per
`docs/collaboration/local-issue-planning.md`.

When an agent review packet is produced, or at the next design intake and
before implementation, follow `.agents/skills/process-lessons/SKILL.md`.
When marking a local issue or work plan `done`, follow
`.agents/skills/process-review/SKILL.md`.
