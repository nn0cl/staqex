# LISS-0569 evaluator classical value body successor design trace

## Architecture Path scope approval

- Date: 2026-09-19
- Scope approval: `Architecture Path scope approval`
- Parent: completed WP-0165 / LISS-0568 successor.
- Evidence: `evaluator.py` is 4,050 lines with 114 class methods. The broad
  remaining classical body is `_legacy_evaluate_value`, supported by unit,
  attribute, receiver, and conversion helpers.
- Proposed boundary: migrate those bodies into the existing
  `evaluation/classical.py` through explicit context callbacks.
- Retained facade responsibilities: mutable state and DTO ownership,
  cross-family `_eval_classical_call` / `_eval_classical_op_binder`, and pure
  helper decisions unless mechanically proven safe.
- Omitted: continuous (completed), parser/typechecker, Semantic IR, QASM,
  provider/network, public API retirement, and language behavior changes.

## Architecture Path Phase 0 acceptance

- Approved on 2026-09-19:
  `WP-0166 / LISS-0569 Architecture Path Phase 0 acceptance 承認`.
- Call graph closed: `values.py` delegates the recursive value body;
  classical dispatch recursively reaches unit conversion, constructors,
  classical calls, and classical OpBinder; evolution consumes unit-aware
  evaluation; calls/operators consume receiver resolution.
- State ownership closed: `Evaluator` remains the sole owner of objects,
  scalars, units, frame state, type environments, DTO identity, and
  constructor/assignment mutation. The successor receives callbacks and
  never copies maps or defines DTOs.
- Import boundary closed: `classical.py` and the allowed successor modules do
  not import or instantiate the public evaluator facade.
- Exact allowed paths: evaluator facade, classical/context/compatibility/
  values modules, the evolution callback surface, LISS-0569 Red test and
  active-Red ledger, plus linked lifecycle/review records. No parser,
  typechecker, Semantic IR, QASM, provider, network, or public API changes.
- Phase 1 Red contract: executable structural assertions for successor-owned
  dispatch, values routing, context callback coverage, no duplicate legacy
  body, no copied state, plus characterization for literals, attributes,
  units, constructors, `when`, and classical binders.
- Implementation permission: none. Phase 1 Red requires its own approval.
- Next approval:
  `WP-0166 / LISS-0569 Phase 1 Red 承認`.

## Phase 1 Red execution

- Approval: `WP-0166 / LISS-0569 Phase 1 Red 承認` (2026-09-19).
- Added only the approved Red test and active-Red manifest entry, plus linked
  status records; no production implementation was started.
- The test contract covers successor entrypoints, no legacy delegation,
  values routing, context callbacks, facade body retirement, and
  literal/attribute/unit/constructor/binder characterization.
- Verification: `PYTHONPATH=. ./.venv/bin/pytest -q
  tests/test_liss_0569_classical_value_red.py` -> **5 failed, 3 passed**.
  The five failures are the intended structural gaps: missing unit/receiver
  successor entrypoints, legacy delegation in `classical.py` and `values.py`,
  missing context unit callback, and the remaining evaluator legacy body.
  The three characterization cases pass.
- Lifecycle, document, coverage-ledger, and diff checks are run after this
  record update.
- Next safe action: request
  `WP-0166 / LISS-0569 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review

- Approval: `WP-0166 / LISS-0569 Phase 1 Red テストレビュー承認`
  (2026-09-19).
- Review packet:
  `docs/collaboration/reviews/2026-09-19-liss-0569-phase1-red-review.md`.
- Result: accepted. Focused evidence is **5 failed, 3 passed** with the five
  structural failures classified as intended extraction gaps and the three
  behavior guards passing.
- Process lesson applied: `red-contract-scope`; structural and
  characterization nodes remain separately identified.
- Implementation permission: none. Active-Red ownership remains with
  LISS-0569.
- Next safe action: request
  `WP-0166 / LISS-0569 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation

- Approval: `WP-0166 / LISS-0569 Phase 2 Green / Implementation 承認`
  (2026-09-19).
- Extracted classical recursive value dispatch and unit/attribute/receiver
  mechanics into `evaluation/classical.py`; state and DTO ownership stayed in
  `Evaluator`.
- Added context callbacks for unit lookup, enum construction, and
  cross-family call/binder delegation. Existing private evaluator names remain
  compatibility aliases installed after class definition.
- Red suite: **8 passed** after implementation. Focused/adjacent suite:
  **38 passed**. Full pytest: **2,179 passed in 323.00s**.
- Active-Red entry was removed because all approved Red nodes passed.
- Phase 3 risk is limited to readability/formatting and compatibility-surface
  review; no known behavior failure remains.
- Next safe action: request
  `WP-0166 / LISS-0569 Phase 3 Refactor 承認`.

## Phase 3 Refactor

- Approval: `WP-0166 / LISS-0569 Phase 3 Refactor 承認` (2026-09-20).
- Refactored dense classical evaluation branches into named helpers while
  preserving state ownership, DTO identity, compatibility aliases, and all
  accepted diagnostics/units/receiver behavior.
- Verification: focused/adjacent **38 passed**; full pytest **2,179 passed in
  317.81s**; compileall, lifecycle, coverage-ledger, and diff checks passed.
- Structural measurements: `evaluator.py` 3,790 lines;
  `evaluation/classical.py` 425 lines; guardrail 1,200 lines.
- Same-context review packet:
  `docs/collaboration/reviews/2026-09-20-liss-0569-phase3-review.md`.
- No active-Red entries remain. The WP/Issue stay in progress until final
  review approval.
- Next safe action: request
  `WP-0166 / LISS-0569 Phase 3 最終レビュー 承認`.

## Phase 3 final review

- Approval: `WP-0166 / LISS-0569 Phase 3 最終レビュー 承認`
  (2026-09-20).
- Result: accepted after re-reading the canonical scope, implementation,
  Phase 1 review, Phase 3 review packet, and current source boundaries.
- Final evidence: focused/adjacent **38 passed**, full pytest **2,179 passed**
  on the current implementation tree, compileall, lifecycle,
  coverage-ledger, and diff checks passed.
- Process review: no operating-contract deviation or operational problem
  found.
- WP-0166 and LISS-0569 are complete; no active-Red entry remains.
- Future evaluator decomposition requires a new approved scope.
