# Work Plan: Legacy `when` binding extraction

## Goal

Reduce Evaluator facade implementation by extracting the legacy AST control
mixture binder without changing canonical routing or runtime behavior.

## Scope

- In: LISS-0580; `_bind_when` and its private control-mass/pattern helpers;
  compatibility callback; canonical fallback characterization; structural
  and adjacent verification.
- Out: fallback retirement, language semantic changes, parser/typechecker,
  nested/dynamic-control feature work, QASM/QPU/provider behavior, unrelated
  Evaluator or large-file decomposition.

## Issue Graph

| Issue | Status | Initial size | Current size | Planning record | Depends on | Blocks | Branch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [LISS-0580](../issues/LISS-0580-legacy-when-binding-extraction.md) | done | M | M | AIP-0580-001 | ADR 0227 accepted | - | `test/liss-0580-legacy-when-binding-red` |

## Recommended Order

1. Obtain Phase 0 acceptance of
   [the specification](../specs/evaluator-legacy-when-binding.md), including
   a clause-to-test mapping and an exact non-deferred canonical fallback case.
2. Obtain Phase 1 Red approval; add only structural contracts and any missing
   fallback behavior characterization. Reuse existing passing behavior tests
   where they already assert the same clause. **Done 2026-09-27.**
3. Have the Phase 1 contract reviewed and accepted before implementation.
   The correction now proves plan-family dispatch, ineligible selection, and
   legacy-body entry from the canonical executor. Same-context re-review found
   no remaining blocker. Adjudicator accepted the test review on 2026-09-27.
4. Obtain Phase 2 Green/Implementation approval; move the body and only the
   helpers proven to be exclusively owned by it. Keep evaluator state in the
   Evaluator instance. **Done 2026-09-27.**
5. Execute Phase 3 Refactor under the approval received 2026-09-27; preserve the
   callback only as compatibility wiring, and review implementation bodies
   behind the facade. **Done 2026-09-27.**
6. Commit when authorized, then run all blocking suites on the final commit
   before closure.

## Current Next Issue

- Issue: none in WP-0173.
- Reason: the scoped extraction reached final Adjudicator approval and its
  final commit passed the blocking suite.
- Adjudicator approval: Phase 3 final review approved 2026-09-27.

## Risks

- Existing LISS-0495 coverage proves the eligible canonical path, not the
  canonical-to-legacy fallback boundary.
- A test that only asserts text installation could miss a wrong installer
  mapping or runtime hook identity.
- `_ctrl_masses` and `_pat_match` may have additional private consumers; their
  extraction is conditional on Phase 1 inventory.
- New module size is intentionally small; do not broaden it to unrelated
  binder helpers just to increase the line-count reduction.

## Verification Plan

- Phase 0: static consumer and test inventory only; no test execution.
- Phase 1: focused structural Red and established passing behavior nodes,
  reported separately; active-Red lifecycle check.
- Phase 2/3: exact compatibility installer/setup/runtime identity, canonical
  eligible path, canonical fallback smoke, existing when/enum/ket/nested
  consumers, adjacent runtime tests, all-blocking suites, and spec verification
  with tested SHA/environment evidence. After splits, report implementation
  body sizes and configured structure-budget disposition.

## Applicable Process Lessons

- `evaluator-state-ownership`: keep all mutable maps and execution state on
  Evaluator; successor receives explicit live callbacks/state access.
- `compatibility-hook-identity-contract`: verify actual installer mapping,
  setup invocation, and live callable identity, not textual presence alone.
- `private-consumer-inventory`: inspect private calls/imports and test hooks
  before moving the body.
- `decomposition-source-ownership`: prove successor ownership and facade-body
  removal.
- `acceptance-inventory-reconciliation`: map every explicit minimum evidence
  clause to a named existing or proposed test before Phase 1 acceptance.
- `status-drift`: synchronize spec, issue, work plan, and trace at each gate.

## Process Review

- Outcome: not yet
- Lesson written: not applicable
- Template-feedback path: none

## Phase 1 Red Result

- Approval: Phase 1 Red, Adjudicator, 2026-09-27.
- Focused: 3 expected structural failures, 1 passing canonical-fallback
  characterization; no collection errors.
- Existing consumer suites: 11 passed. Combined: 3 expected failures, 12
  passed.
- Lifecycle check, test `py_compile`, and `git diff --check` passed. Ruff was
  unavailable in `.venv`.
- Evidence was run from base SHA
  `98d71df0f553bc3c0b8173d7aeb2310fa40c7184` with the Phase 1 working tree
  dirty; macOS 27.0.0 arm64, Python 3.14.6.
- No production source changed. The review finding is corrected and the
  same-context re-review found no remaining test-contract blocker. Adjudicator
  acceptance was recorded; see
  `docs/collaboration/reviews/2026-09-27-liss-0580-phase1-red-review.md`.

## Phase 2 Green Result

- Approval: Phase 2 Green/Implementation, Adjudicator, 2026-09-27.
- Focused plus adjacent consumers: 15 passed. All 2,275 collected pytest
  cases passed across the initial 863-pass run before interruption, the
  isolated slow test (1 pass), and a continuation run (1,411 pass).
- Lifecycle, syntax, coverage-ledger consistency, and whitespace checks
  passed. Ruff was unavailable.
- Successor is 140 physical lines; `evaluator.py` is 1,305 lines. No
  quantitative source-structure budget is configured.
- Evidence SHA `98d71df0f553bc3c0b8173d7aeb2310fa40c7184`, dirty tree;
  macOS 27.0.0 arm64, Python 3.14.6, pytest 9.1.1.
- Phase 3 final review approved 2026-09-27. Commit
  `f50f116b7db287ad942d99bc9f4f38e5cb27cfb8` passed all 2,275 blocking tests.

Process review: no operating-contract deviation or operational problem found.
