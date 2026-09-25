# Work Plan: Classical Operator-expression evaluation decomposition

## Goal

Remove the remaining classical Operator-expression evaluator bodies from the
large facade without changing language behavior or creating a second runtime
state owner.

## Scope

- In: LISS-0578 classical Operator expression and binder evaluation; a
  narrow callback boundary; private consumer inventory; test and verification
  planning.
- Out: operator projection implementation; parser/typechecker; other runtime
  families; provider/QPU behavior; public language changes.

## Issue Graph

| Issue | Status | Initial size | Current size | Planning record | Depends on | Blocks | Branch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LISS-0578 | done — final review accepted; commit and local blocking verification passed | M | M | AIP-0578-001 | WP-0170 / LISS-0577 (done on parent branch) | - | `codex/liss-0578-classical-op-eval` |

## Recommended Order

1. Phase 1 Red was approved; the bounded structural contract is added, with
   structural failures separated from existing passing characterizations.
2. Phase 1 Red test review found bounded gaps. The correction was approved;
   exact AST mapping, installer invocation and runtime-identity tests were
   added, and classical value-dispatch plus Operator-resolution consumers were
   added to the named evidence. The corrected suite was reviewed and accepted
   by the Adjudicator on 2026-09-24.
3. Phase 2 Green/Implementation was approved and implemented: the accepted
   algorithms now live in the successor module, compatibility hooks preserve
   the legacy Evaluator entrypoints, and duplicate method bodies are removed.
4. The Adjudicator approved the verification-baseline snapshot update scope
   on 2026-09-24. The snapshot now includes the pre-existing public
   `MutableMapping` symbol, and a fresh capture byte-compares successfully.
5. Phase 3 Refactor was approved and reviewed on 2026-09-24. The successor
   meets the readability target without additional abstraction; consumer
   compatibility and all local blocking suites passed. Review evidence is in
   `docs/collaboration/reviews/2026-09-24-liss-0578-phase3-review.md`.
6. Adjudicator accepted the Phase 3 final review; commit
   `8ba8b865705f5703de32aa9f5028810c58a61250` passed all local blocking
   suites. Same-context process review found no operating-contract deviation.

## Current Next Issue

- Issue: none remaining within WP-0171.
- Next action: identify the next unblocked evaluator decomposition scope from
  the active backlog; a new issue/scope approval is required before starting
  additional implementation.

## Risks

- Dynamic compatibility installation and underscore-prefixed helpers can hide
  consumers from a simple call-site search.
- Set-comprehension evaluation is dispatched through binding but relies on the
  same expression evaluator; callback ownership must remain explicit.
- Moving `project` handling into the same module would conflate pure classical
  AST evaluation with `Joint` mutation and Hamiltonian compilation; projection
  is therefore excluded pending its own scope decision.

## Verification Plan

- Phase 1: focused structural Red contract (AST mapping, setup invocation and
  runtime identity) and positive characterizations for
  binder folds, expression forms, nested/guarded domains, arrays/indexing,
  short-circuiting, rejection diagnostics, classical value dispatch, and
  Operator-resolution lookup; report structural and passing nodes separately.
- Phase 2: focused and all-root suites plus spec verification; baseline
  snapshot regenerated and byte-compared after separate scope approval.
- Phase 3: consumer smoke for `binding.py`, set-comprehension/operator
  resolution, compatibility installation and adjacent regression passed;
  root/spec suites passed on the dirty tree. Rerun all blocking suites after
  the final commit, with tested SHA and environment.
- Phase 0: only static inventory; no runtime test run.

## Process Review

- Outcome: Process review: no operating-contract deviation or operational problem found.
- Lesson written: no new reusable lesson; existing status-drift and
  decomposition lessons were applied.
- Template-feedback path: none
