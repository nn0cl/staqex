# LISS-0568 evaluator value/continuous body successor design trace

## Architecture Path scope approval

- Date: 2026-09-19
- Scope approval: `Architecture Path scope approval`
- Parent: completed WP-0164 / LISS-0567 successor.
- Evidence: `evaluator.py` is 4,026 lines with 114 methods. The largest
  remaining body families are `_legacy_evaluate_value`, unit/attribute value
  support, finiteize/continuous field binding, and continuous compose.
- Proposed boundary: expand `evaluation/classical.py` for classical/value
  bodies and add `evaluation/continuous.py` for finiteization and continuous
  port/provenance mechanics.
- Retained facade responsibilities: mutable state ownership, DTO identity,
  cross-family `_bind`/`_run_unit_body`, and state-algebra `inner`/`outer`.
- Omitted: parser/typechecker, Semantic IR, QASM, provider/network, public API
  retirement, and language behavior changes.
- Next approval:
  `WP-0165 / LISS-0568 Architecture Path Phase 0 acceptance 承認`.

## Phase 0 acceptance

- Date: 2026-09-19
- Approval: `WP-0165 / LISS-0568 Architecture Path Phase 0 acceptance 承認`
- Result: accepted the classical/value body boundary, new continuous
  finiteization/port boundary, single `Evaluator` state owner, consumer
  inventory, exact Phase 1 allowed paths, and Red contracts.
- Excluded: `_bind`, `_run_unit_body`, `inner`/`outer`, parser/typechecker,
  Semantic IR, QASM, provider/network, and public API retirement.
- Scope: Phase 1 Red test work only; implementation remains unauthorized.
- Next approval: `WP-0165 / LISS-0568 Phase 1 Red 承認`.

## Phase 1 Red

- Date: 2026-09-19
- Approval: `WP-0165 / LISS-0568 Phase 1 Red 承認`
- Result: added eight bounded structural and characterization contracts; the
  exact Red run produced **5 failed, 3 passed**. Five structural gaps fail as
  intended and three characterization cases pass. The initial fixture's
  nonexistent `Evaluator.run()` call was corrected to `run_source()` before
  this final run.
- Scope discipline: only the approved Red test, lifecycle registration, and
  linked status records changed. No production implementation started.
- Checks: test lifecycle, document lifecycle, coverage-ledger consistency, and
  `git diff --check` passed.
- Next approval: `WP-0165 / LISS-0568 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review

- Date: 2026-09-19
- Approval: `WP-0165 / LISS-0568 Phase 1 Red テストレビュー承認`
- Route: `same_context`, weaker than `separate_context`.
- Evidence: exact focused run **5 failed, 3 passed**. Five expected
  structural gaps fail; classical value, continuous finiteize, and provenance
  characterizations pass.
- Checks: test lifecycle, document lifecycle, coverage-ledger consistency,
  and `git diff --check` passed. No production implementation was added.
- Review packet:
  `docs/collaboration/reviews/2026-09-19-liss-0568-phase1-red-review.md`.
- Next approval: `WP-0165 / LISS-0568 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation

- Date: 2026-09-19
- Approval: `WP-0165 / LISS-0568 Phase 2 Green / Implementation 承認`
- Result: moved continuous finiteization, host-field, composition, and
  provenance mechanics into `evaluation/continuous.py`; added explicit
  classical value/unit/attribute successor entrypoints and context callbacks.
- Verification: LISS-0568 plus adjacent continuous/classical suites **24
  passed**; compileall, lifecycle, document, coverage-ledger, and diff checks
  passed.
- Scope discipline: `Evaluator` remains the only mutable state owner; no
  parser, Semantic IR, QASM, provider, public API, or language behavior
  change. Active-Red ownership was retired after all eight contracts passed.
- Next approval: `WP-0165 / LISS-0568 Phase 3 Refactor 承認`.

## Phase 3 Refactor

- Date: 2026-09-19
- Approval: `WP-0165 / LISS-0568 Phase 3 Refactor 承認`
- Result: factored shared continuous seed/port validation and improved
  compatibility/readability boundaries without behavior changes.
- Verification: focused/adjacent **24 passed**, full pytest **2,171 passed**,
  compileall, lifecycle, document, coverage-ledger, and diff checks passed.
- Scope discipline: no assertion, fixture, provenance, language, provider, or
  public API change. The remaining classical legacy value body is future
  scope.
- Next approval: `WP-0165 / LISS-0568 Phase 3 最終レビュー 承認`.

## Phase 3 final review

- Date: 2026-09-19
- Approval: `WP-0165 / LISS-0568 Phase 3 最終レビュー 承認`
- Result: accepted the continuous/value successor, compatibility boundary,
  provenance behavior, and state ownership.
- Verification: focused/adjacent **24 passed**, full pytest **2,171 passed**,
  compileall, lifecycle, document, coverage-ledger, and diff checks passed.
- Process review: no operating-contract deviation or operational problem
  found.
- Status: WP-0165 / LISS-0568 complete. Remaining classical legacy-body
  migration requires a new approved scope.
