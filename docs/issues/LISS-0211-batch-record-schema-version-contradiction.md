# LISS-0211: `CLAUDE.md` mandates `schema_version: 2`; the validator rejects anything but `1`

## Metadata

- Local issue ID: LISS-0211
- Status: **proposed** (investigation intake — no edit to `CLAUDE.md` in this batch)
- Phase: process-only
- Type: bug
- Priority: P0
- Planning size: S
- Program: [WP-0069](../work-plans/WP-0069-operations-review-intake.md)
- Related: ADR 0006 (instruction change control), ADR 0112, ADR 0113
- Blocks: every Claude Code bounded-execution batch

## Intent

Claude Code cannot produce a valid bounded execution batch record today. The
operating contract and the CI validator disagree about the schema version, and
the validator wins.

## Evidence (reproduced 2026-08-01)

`CLAUDE.md` §Claude Code Issue-Level and Work-Plan Autonomy:

> When the Adjudicator approves a bounded execution batch record
> (`docs/collaboration/reviews/execution-batch-<id>.json`, `schema_version: 2`
> with `work_plan_id`) …

`scripts/check-execution-batch-reviews.py`:

```python
if data["schema_version"] != 1:
    fail(path, "schema_version must be 1")
```

[`docs/templates/execution-batch-review.md`](../templates/execution-batch-review.md)
agrees with the validator (`"schema_version": 1`, and states `work_plan_id` is
optional in the shared schema while Claude Code must set it).

So a record written to the contract fails CI, and a record written to pass CI
violates the contract. The draft record filed with this batch
(`execution-batch-BATCH-0001.json`) uses `1` and notes the contradiction.

## Adjudicator decision points

1. Which is authoritative — is there a real schema v2 that was never
   implemented, or is `2` a typo in `CLAUDE.md`?
2. If the contract is right, the validator and template need a v2 shape defined
   (what changes in v2?). If the validator is right, `CLAUDE.md` line ~363
   changes to `1`.
3. `CLAUDE.md` is an agent operating contract: any edit needs Adjudicator
   review, a stated reason, and an AI work trace (ADR 0006 / ADR 0112), and
   CI job "agent operating contract change traceability" enforces the trace.
   That is why this Issue only *files* the contradiction — the edit is a
   separate, reviewed change.

## Exit

- [ ] Ruling on which side is authoritative
- [ ] `CLAUDE.md`, template, and validator agree
- [ ] Trace recorded for the contract edit
- [ ] A batch record written to the contract passes
      `scripts/check-execution-batch-reviews.py`

## Non-goals

Changing what a batch approval authorizes; porting the Claude-only autonomy
section into `AGENTS.md` or the other agent rule files (ADR 0112 forbids it).
