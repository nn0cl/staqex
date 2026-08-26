# AI work trace: independent review loop policy

## Trigger and approval

- Trigger: user requested that independent-context review operate as a loop
  with finding acceptance/rejection, re-review, and `COMPLETE`/`ABORT`
  terminal states.
- Date: 2026-08-14
- Scope: reusable collaboration-process documentation only.
- User approval: the user explicitly stated that approval is granted now if
  the policy change requires it. This is treated as Adjudicator approval for
  this process-policy change, not as approval for any application phase,
  ADR, implementation, or technology selection.

## Changes

- `AGENTS.md`: required finding disposition, authority, re-review, and
  terminal-state rules.
- `docs/collaboration/ai-human-scheme.md`: state machine and separation of
  review completion from typed phase approval.
- `docs/templates/independent-context-review.md`: disposition and terminal
  decision fields.

## Operational contract

1. A fresh context performs read-only review.
2. The primary agent normally marks each finding `accepted`, `rejected`, or
   `deferred` under the existing accepted design, with authority and rationale.
   The agent accepts only design-preserving corrections and rejects only
   unsupported, duplicate, non-applicable, or already-contract-conflicting
   findings.
3. Accepted in-scope findings are corrected, then a fresh context re-reviews.
4. Rejected findings require recorded evidence and rationale; deferred findings
   remain blockers.
5. The loop ends only at `COMPLETE` or `ABORT`.
6. `COMPLETE` never grants phase or implementation approval.
7. The user is asked only when accepting or rejecting would deviate from the
   accepted design, introduce a new architecture/technology/scope/phase,
   conflict with physics or safety requirements, or require guessing intent.
8. `ABORT` records why no action is required or which user decision is needed.

## Verification

- Deterministic check: `git diff --check`.
- Required future contract review: an independent review of this policy
  change must verify that dispositions cannot silently bypass human approval
  and that both terminal states are recorded.
- No application source, tests, Spec, or ADR were changed by this policy
  change.
