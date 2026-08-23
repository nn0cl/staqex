# LISS-0448 Phase 3 Refactor Trace

- Approval: user approved Phase 3 Refactor on 2026-08-24.
- Branch: `codex/liss-0448-canonical-qasm-coin-mix-projection`.
- Issue/WorkPlan: LISS-0448 / WP-0111.
- Scope: readability and responsibility cleanup after Green; no behavior
  change, no new architecture, and no provider/QPU integration.

## Refactor performed

- Added `_reject_mixture_projection` in the legacy QASM lowerer to own the
  shared Coin/Mix rejection payload.
- Reused the canonical rejection code/reason constants instead of duplicating
  string literals in the legacy adapter boundary.
- Removed `_is_copy_when` and `_is_dirac_or_lit`, which represented the retired
  unitary fallback and were no longer reachable after fail-closed Green.

## Reviewer empathy summary

- A reviewer can now find the complete legacy rejection contract in one named
  helper instead of comparing two payload copies.
- The absence of a copy-pattern detector makes the no-unitary-fallback rule
  visible in the control flow.
- The helper remains in the adapter boundary and does not move physics policy
  into a new layer.

## Verification

- Focused LISS-0448 tests: **8 passed**.
- Full spec verification: **161/161 passed (100%)**.
- `py_compile` passed for all modified Python modules.
- `git diff --check` passed.
- Reviewed tests and assertions were unchanged.

## Final review correction

The first final review found two evidence/readability issues: report timestamps
predated the refactor and one explicit-evolution preflight path duplicated the
mixture rejection literals. Both are in-scope preserving corrections and are
being re-verified. The legacy-caller inventory remains deferred follow-up work
and is explicitly recorded in ADR 0213.

## Remaining risks

- Direct legacy lowerer callers still require inventory and eventual
  migrate/retire disposition; this refactor preserves the fail-closed boundary.
- No final-review or merge/completion claim is made in this trace.

## State

`final-review-ready` — final review and completion packet remain required.
