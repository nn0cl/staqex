# LISS-0568: Evaluator value and continuous body successor

## Metadata

- Local issue ID: LISS-0568
- Status: done — Phase 3 final review accepted 2026-09-19
- Phase: done
- Type: Architecture Path bounded structural decomposition
- Planning size: XL
- Parent: WP-0165
- Depends on: WP-0164 / LISS-0567 complete
- Blocks: none

## [DESIGN CHECK]

### Scope and expected behavior

Complete the implementation-body migration for the accepted evaluator
classical/frame successor. `classical.py` will own classical value recursion,
unit conversion, and attribute/receiver support; `continuous.py` will own
finiteization and continuous field/compose binding. Existing runtime meaning,
diagnostics, provenance, fixed-seed behavior, and public compatibility must
remain unchanged.

### Specifications and files inspected

- `docs/specs/staqex-core-module-decomposition.md`
- `docs/work-plans/WP-0164-evaluator-classical-frame-successor.md`
- `docs/issues/LISS-0567-evaluator-classical-frame-successor.md`
- `compiler/staqex/runtime/evaluator.py`
- `compiler/staqex/runtime/evaluation/classical.py`
- `compiler/staqex/runtime/evaluation/frames.py`
- `compiler/staqex/runtime/evaluation/calls.py`
- `compiler/staqex/runtime/evaluation/values.py`
- `compiler/staqex/runtime/evaluation/context.py`
- existing classical/unit/continuous characterization tests

### Component boundaries, ports, and DTO candidates

- `Evaluator` remains the mutable state owner.
- `ContinuousFieldPort` remains the existing external port; no new adapter is
  introduced.
- DTO classes and enum identity remain evaluator-owned by default. The Phase 0
  inventory must expose predicates/callbacks instead of importing the facade.
- `classical.py` and `continuous.py` receive explicit callbacks and return
  existing runtime values/Joints; neither becomes semantic authority.

### Applicable constraints

- No Phase 1/2/3 implementation without separate approval.
- No new language behavior, provider/QPU/network work, or public API removal.
- Preserve unit conversion, finiteization approximation/provenance, seed
  handling, diagnostics, and continuous-port boundaries.
- Keep successor modules below 1,200 lines and avoid generic `utils.py`.

### Decisions, assumptions, and unresolved ambiguities

- Classical and continuous bodies are separate because their dependency and
  port boundaries differ.
- `_bind`, `_run_unit_body`, `_bind_inner`, and `_materialize_outer` remain out
  of scope for this Issue.
- DTO predicate/callback design and exact helper placement are Phase 0
  decisions; no facade import is an allowed shortcut.

### Included and omitted AI context

- Included: accepted LISS-0567 successor, evaluator value/continuous methods,
  context/compatibility contracts, existing characterization consumers, and
  canonical decomposition rules.
- Omitted: external provider data, credentials, live QPU, parser/typechecker,
  Semantic IR, QASM, and historical decomposition records.

### Task routing

- Phase 0: host agent, deterministic repository inspection.
- Phase 1–3: host agent after typed approvals.
- Review: same-context per runtime routing; weaker than separate-context.

### Verification plan

Phase 0 produces the call graph, mutation map, consumer manifest, DTO/port
callback inventory, and exact allowed paths. Later phases run focused Red /
Green characterization, fixed-seed/provenance checks, nearest regressions,
full pytest, compileall, Spec Verification, lifecycle, coverage-ledger, and
diff checks.

## Requested decision

Requested approval type: **Architecture Path Phase 0 acceptance**.
The current scope approval does not authorize Phase 1 Red or implementation.

Next approval:
`WP-0165 / LISS-0568 Architecture Path Phase 0 acceptance 承認`.

## Phase 0 acceptance

Accepted on 2026-09-19:
`WP-0165 / LISS-0568 Architecture Path Phase 0 acceptance 承認`.

The accepted boundary is classical/value body migration into the existing
`classical.py` successor plus a new `continuous.py` successor for finiteize,
continuous field/compose, and provenance mechanics. `Evaluator` remains the
only mutable state owner; `_bind`, `_run_unit_body`, `inner`, and `outer` stay
outside this issue. The consumer/import inventory, DTO/port callback boundary,
and exact Phase 1 allowed paths are recorded in WP-0165.

This acceptance authorizes Phase 1 Red tests only. No production extraction,
public API retirement, or language behavior change is authorized.

Next approval:
`WP-0165 / LISS-0568 Phase 1 Red 承認`.

## Phase 1 Red

Approved on 2026-09-19:
`WP-0165 / LISS-0568 Phase 1 Red 承認`.

Added `tests/test_liss_0568_value_continuous_red.py` with five intentional
structural failures and three characterization guards for existing classical
and continuous behavior. The issue-linked Active-Red entry is registered. The
exact run produced **5 failed, 3 passed**; the failures are the expected
structural gaps and all characterization guards pass. A nonexistent evaluator
runner in the initial fixture was corrected to `run_source()` before the final
Red run. No production source or reviewed assertion was changed.

Next approval:
`WP-0165 / LISS-0568 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review

Accepted on 2026-09-19:
`WP-0165 / LISS-0568 Phase 1 Red テストレビュー承認`.

Review packet:
`docs/collaboration/reviews/2026-09-19-liss-0568-phase1-red-review.md`.
The five structural failures are intentional pre-Green gaps; the three
classical/continuous characterization cases pass. The exact run is
**5 failed, 3 passed** and lifecycle, document, coverage-ledger, and diff
checks passed. No production source or reviewed assertion changed.

Phase 2 remains separately gated. Next approval:
`WP-0165 / LISS-0568 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation

Approved and implemented on 2026-09-19:
`WP-0165 / LISS-0568 Phase 2 Green / Implementation 承認`.

The continuous/finiteization body now runs through `evaluation/continuous.py`
and its explicit context callbacks. Classical successor entrypoints for value,
unit, and attribute evaluation are installed without removing private legacy
consumer names. `Evaluator` remains the sole mutable-state owner and the
ContinuousFieldPort remains the only external boundary.

Verification passed: LISS-0568 plus continuous/classical adjacent suites
**24 passed**; compileall, lifecycle, document, coverage-ledger, and diff
checks passed. The Active-Red entry was retired. No new language behavior or
external integration was added.

Next approval:
`WP-0165 / LISS-0568 Phase 3 Refactor 承認`.

## Phase 3 Refactor

Approved and completed on 2026-09-19:
`WP-0165 / LISS-0568 Phase 3 Refactor 承認`.

Refactored continuous seed/port validation and compatibility presentation
without changing behavior. `Evaluator` remains the only mutable state owner;
the remaining `_legacy_evaluate_value` body is explicitly deferred to a new
bounded scope.

Verification: focused/adjacent suites **24 passed**, full pytest **2,171
passed**, and compileall, lifecycle, document, coverage-ledger, and diff checks
passed.

Next approval:
`WP-0165 / LISS-0568 Phase 3 最終レビュー 承認`.

## Phase 3 final review

Accepted on 2026-09-19:
`WP-0165 / LISS-0568 Phase 3 最終レビュー 承認`.

Review packet:
`docs/collaboration/reviews/2026-09-19-liss-0568-phase3-final-review.md`.
The final review confirms the accepted continuous/value boundary, existing
port/provenance behavior, and single mutable-state owner. Focused/adjacent
tests passed (**24**), full pytest passed (**2,171**), and all lifecycle,
coverage, compile, and diff checks passed.

Process review: no operating-contract deviation or operational problem found.

LISS-0568 is complete. Further classical legacy-body migration requires a new
Issue/WP and approval.
