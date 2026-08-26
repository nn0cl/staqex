---
name: execution-batch
description: Write or execute a bounded execution-batch review record. Use when the Adjudicator pre-approves a named set of low-risk issues, when filling execution-batch JSON, or when working on a batch/ branch.
---

# Bounded execution batch

Canonical template: `docs/templates/execution-batch-review.md`. Follow that
file. Standing Approval Model rules in the contract files still apply.

## Record

Write one JSON record under
`docs/collaboration/reviews/execution-batch-<id>.json`. It must name:

- issue IDs
- allowed paths, phases, and operations
- expiry
- invalidating architecture triggers
- whether post-review is required
- `execution_branch` using `batch/<batch-id>`
- the approval commit

The record is an execution boundary, not a blanket approval. Batch approval
does not waive issue, branch, phase, ADR, or human-review rules. CI success
is not Adjudicator approval.

## After execution

The agent may move the record to `awaiting_post_review`. Only the Adjudicator
may move it to `post_reviewed`. If an architecture-reassessment trigger
appears, stop; the batch authorization is invalid for that work.
