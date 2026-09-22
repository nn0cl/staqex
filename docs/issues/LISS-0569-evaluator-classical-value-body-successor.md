# LISS-0569: Evaluator classical value body successor

## Metadata

- Local issue ID: LISS-0569
- Status: done — Phase 3 final review accepted
- Phase: done
- Type: Architecture Path bounded structural decomposition
- Planning size: XL
- Parent: WP-0166
- Depends on: WP-0165 / LISS-0568 complete
- Blocks: none

## [DESIGN CHECK]

### Scope and expected behavior

Complete the classical value body migration into `evaluation/classical.py`.
Move recursive value, unit, attribute, receiver, and constructor routing while
preserving existing runtime DTO identity, diagnostics, classical calls,
OpBinder behavior, and public compatibility.

### Specifications and files inspected

- `docs/specs/staqex-core-module-decomposition.md`
- `docs/work-plans/WP-0165-evaluator-value-continuous-body-successor.md`
- `docs/issues/LISS-0568-evaluator-value-continuous-body-successor.md`
- `compiler/staqex/runtime/evaluator.py`
- `compiler/staqex/runtime/evaluation/classical.py`
- `compiler/staqex/runtime/evaluation/values.py`
- `compiler/staqex/runtime/evaluation/context.py`
- `compiler/staqex/runtime/evaluation/compatibility.py`
- `compiler/staqex/runtime/evaluation/evolution.py`
- classical/unit/constructor characterization tests

### Component boundaries, ports, and DTO candidates

- `Evaluator` remains the only mutable runtime-state owner and DTO authority.
- `classical.py` receives explicit context callbacks and returns existing
  runtime values; it does not create a parallel DTO hierarchy.
- `_eval_classical_call` and `_eval_classical_op_binder` remain evaluator
  callbacks because they cross family boundaries.
- No external port is added; continuous/provider work is already complete and
  excluded.

### Phase 0 acceptance record

Approved target:
`WP-0166 / LISS-0569 Architecture Path Phase 0 acceptance 承認`

The Phase 0 inventory closes the design ambiguities:

- `evaluation/values.py` remains the stable value-family entrypoint, but the
  recursive body will be owned by `evaluation/classical.py` after Green.
- Unit-aware recursion and conversion remain in the classical/value boundary;
  evolution consumes them through the context protocol.
- `_eval_classical_call` and `_eval_classical_op_binder` remain explicit
  evaluator callbacks because they cross family boundaries.
- Receiver resolution and constructor routing remain callbacks over the single
  `Evaluator` state owner. No copied environment or replacement DTO is
  permitted.
- The successor modules have no facade import and no direct mutable state
  access. This is a structural contract, not a new language feature.

Exact allowed paths are the five runtime files
`evaluator.py`, `evaluation/classical.py`, `evaluation/context.py`,
`evaluation/compatibility.py`, and `evaluation/values.py`, the existing
`evaluation/evolution.py` callback surface, the new Red test, the active-Red
ledger, and linked WP/Issue/Trace/review records. Parser, typechecker,
Semantic IR, QASM, provider, network, public API retirement, and unrelated
tests are excluded.

Phase 1 Red will make the body-extraction contract executable: the classical
module must contain the bounded dispatch surface without a legacy-body
delegation, `values.py` must route through the successor, context callbacks
must cover environments/units/receiver/constructors/cross-family calls, and
the facade must retain no duplicate value body. Existing literal, attribute,
unit, constructor, `when`, and binder behavior will be characterization
guards. No production implementation is authorized by this record.

## Phase 1 Red execution

- Approval: `WP-0166 / LISS-0569 Phase 1 Red 承認` (2026-09-19).
- Test: `tests/test_liss_0569_classical_value_red.py`.
- Active-Red ownership: registered in `docs/testing/active-red-tests.toml`.
- Result target: five structural assertions fail because the legacy value
  body still owns dispatch, while three characterization cases pass against
  the current behavior. The exact pytest result is recorded in the trace.
- No production source was changed. Phase 2 Green remains unauthorized.
- Next approval:
  `WP-0166 / LISS-0569 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review

- Approval: `WP-0166 / LISS-0569 Phase 1 Red テストレビュー承認`
  (2026-09-19).
- Review packet:
  `docs/collaboration/reviews/2026-09-19-liss-0569-phase1-red-review.md`.
- Result: accepted. The exact bounded run reproduced **5 failed, 3 passed**;
  all five failures are the intended extraction gaps and all three
  characterization cases pass.
- The Red test and active-Red manifest entry remain unchanged for Green.
- No implementation permission is granted by this review.
- Next approval:
  `WP-0166 / LISS-0569 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation

- Approval: `WP-0166 / LISS-0569 Phase 2 Green / Implementation 承認`
  (2026-09-19).
- Implementation: `evaluation/classical.py` now owns classical value
  dispatch, unit conversion, unit-aware arithmetic, attribute/receiver
  lookup, and constructor routing through explicit callbacks.
- Compatibility: private evaluator aliases remain available, while the
  `Evaluator` class no longer contains the legacy recursive value body.
- Active-Red entry: retired after all eight approved Red contracts passed.
- Verification: focused/adjacent **38 passed**; full pytest **2,179 passed**.
- No parser, typechecker, Semantic IR, QASM, provider, network, or public API
  retirement changes were made.
- Phase 3 remains required for readability, consumer compatibility review,
  compile/lifecycle checks, and final structural cleanup.
- Next approval:
  `WP-0166 / LISS-0569 Phase 3 Refactor 承認`.

## Phase 3 Refactor

- Approval: `WP-0166 / LISS-0569 Phase 3 Refactor 承認` (2026-09-20).
- Review packet:
  `docs/collaboration/reviews/2026-09-20-liss-0569-phase3-review.md`.
- Result: readability and responsibility boundaries were improved without
  changing the accepted value/unit/receiver contracts.
- Verification: focused/adjacent **38 passed**, full pytest **2,179 passed**,
  compileall, lifecycle, coverage-ledger, and diff checks passed.
- Structural budget: `evaluator.py` 3,790 lines; `classical.py` 425 lines.
- No active-Red entries remain. Final review is required before completion.
- Next approval:
  `WP-0166 / LISS-0569 Phase 3 最終レビュー 承認`.

## Phase 3 final review

- Approval: `WP-0166 / LISS-0569 Phase 3 最終レビュー 承認`
  (2026-09-20).
- Review packet:
  `docs/collaboration/reviews/2026-09-20-liss-0569-phase3-review.md`.
- Result: accepted. The classical value successor, compatibility boundary,
  state ownership, and characterization behavior are closed for this scope.
- Verification: focused/adjacent **38 passed**, full pytest **2,179 passed**,
  compileall, lifecycle, coverage-ledger, and diff checks passed.
- Process review: no operating-contract deviation or operational problem
  found.
- Completion: LISS-0569 is done; it owns no active-Red entry.

### Applicable constraints

- No Phase 1/2/3 implementation without separate approval.
- No new syntax, semantics, provider/QPU/network work, or public API removal.
- Preserve units, receiver restoration, constructor errors, diagnostics, and
  classical binder behavior.
- Keep the expanded classical module below 1,200 lines.

### Decisions, assumptions, and unresolved ambiguities

- The existing `classical.py` is the target; no generic helper module is
  allowed.
- DTO predicates and exact callback names are Phase 0 decisions.
- Pure helper movement is optional and cannot expand scope.

### Included and omitted AI context

- Included: accepted LISS-0568 boundary, evaluator classical value/unit body,
  context/compatibility contracts, values/evolution consumers, and tests.
- Omitted: continuous implementation, parser/typechecker, Semantic IR, QASM,
  provider/network, and historical decomposition records.

### Task routing

- Phase 0: host agent, deterministic repository inspection.
- Phase 1–3: host agent after typed approvals.
- Review: same-context per runtime routing; weaker than separate-context.

### Verification plan

Phase 0 produces the value call graph, mutation/DTO map, consumer manifest,
callback inventory, and exact allowed paths. Later phases run focused Red /
Green classical/unit/constructor tests, nearest regressions, full pytest,
compileall, Spec Verification, lifecycle, coverage-ledger, and diff checks.

## Requested decision

Requested approval type: **Architecture Path Phase 0 acceptance**.
The current scope approval does not authorize Phase 1 Red or implementation.

Next approval:
`WP-0166 / LISS-0569 Phase 1 Red 承認`.
