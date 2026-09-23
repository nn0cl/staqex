# LISS-0571: Evaluator binder dispatch successor

## Metadata

- Local issue ID: LISS-0571
- Status: done
- Phase: complete
- Type: Architecture Path structural decomposition
- Planning size: XL
- Parent: WP-0167
- Depends on: LISS-0570 / Unit A1 complete
- Blocks: none

## [DESIGN CHECK]

### Scope and expected behavior

Extract only the evaluator binder dispatchers `_bind_names` and `_bind` into a
cohesive successor module. Preserve dispatch order, error/diagnostic text,
logs and inspection sinks, `Joint` identity/ordering, private consumer
compatibility, and the single mutable `Evaluator` state owner.

### Evidence inspected

- `compiler/staqex/runtime/evaluator.py`: `_bind_names` 111 lines;
  `_bind` 143 lines; 114 class methods after Unit A1.
- `runtime/evaluation/execution.py`, `observation.py`, `dynamic_lane.py`, and
  `evolution.py`: actual runtime private-hook consumers.
- Direct private-hook characterization tests for dynamic, continuous,
  finiteize, method-returned state, and binder behavior.
- `runtime/evaluation/context.py` and `compatibility.py`: existing callback and
  alias boundaries.
- WP-0167/LISS-0570 final artifacts and process lessons.

### Component boundary

- New `runtime/evaluation/binding.py` owns dispatcher control flow only.
- `Evaluator` remains the sole owner of mutable maps, `Joint` lifecycle, DTO
  identity, units/scalars, and compatibility installation.
- Family bodies remain in place or in their already-owned successor modules;
  A2 does not absorb tensor, ket, block, when, state-scaling, pipe, evolution,
  or continuous implementations.
- `binding.py` receives an `EvaluatorContext`, never imports
  `runtime.evaluator`, and does not create a second state store.

### Consumer and compatibility inventory

Actual runtime consumers are `execution.py`, `observation.py`,
`dynamic_lane.py`, and `evolution.py`. Direct tests call `_bind_names` and
exercise dynamic arms, continuous finiteize/weight/mask paths, nested receiver
dispatch, classical multi-bind, and state/binder expressions. Static search
also finds parser/typechecker/legacy-QASM symbols and test helper functions;
these are false-positive or out-of-scope candidates unless runtime import or
execution evidence proves otherwise.

### Allowed and excluded paths

Allowed: `evaluator.py`, new `runtime/evaluation/binding.py`,
`runtime/evaluation/context.py`, `runtime/evaluation/compatibility.py`, the
LISS-0571 Red test, active-Red ledger, and linked WP/Issue/Trace/review files.

Excluded: parser, typechecker, Semantic IR, QASM lowering, providers,
network/credentials, Units B–D, and public API retirement.

### Phase and verification plan

- Phase 1 Red: structural gaps plus dispatcher/order/consumer
  characterizations; no production module.
- Phase 2 Green: minimum dispatcher extraction and compatibility aliases,
  followed by actual consumer import/runtime smoke and adjacent regressions.
- Phase 3: readability, callback boundary, compileall, lifecycle,
  coverage-ledger, diff, and same-context review.
- Each phase requires its own typed approval. This scope approval authorizes
  design only, not tests or implementation.

## Phase 0 acceptance

- Approval: `WP-0167 / Unit A2 binder dispatch Architecture Path scope approval`
  (2026-09-21).
- Design intake is complete. Next gate:
  `WP-0167 / LISS-0571 Phase 1 Red 承認`.

## Phase 1 Red

- Approval: `WP-0167 / LISS-0571 Phase 1 Red 承認` (2026-09-21).
- Added `tests/test_liss_0571_binder_dispatch_red.py` and registered its
  issue-owned active-Red entry.
- Contract: five structural failures for successor existence, facade body
  retirement, compatibility wiring, context callbacks, and no-public-facade
  dependency; three passing characterizations for simple, classical multi-bind,
  and coin binder execution.
- No production module or compatibility implementation was added.
- Next approval:
  `WP-0167 / LISS-0571 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review

- Approval: `WP-0167 / LISS-0571 Phase 1 Red テストレビュー承認`
  (2026-09-21).
- Review packet:
  `docs/collaboration/reviews/2026-09-21-liss-0571-phase1-red-review.md`.
- Result: accepted. The focused suite reproduced **5 failed, 3 passed**;
  the five failures are the declared structural gaps and the three passing
  tests are the approved binder characterizations.
- Active-Red lifecycle, document lifecycle, coverage-ledger consistency, and
  `git diff --check` passed. No production implementation was added.
- Review isolation was `same_context`, weaker than `separate_context`.
  LISS-0571 remains issue-owned in active Red until Green implementation
  satisfies the structural contract.
- Next approval:
  `WP-0167 / LISS-0571 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation

- Approval: `WP-0167 / LISS-0571 Phase 2 Green / Implementation 承認`
  (2026-09-22).
- Added `compiler/staqex/runtime/evaluation/binding.py` with the approved
  dispatcher functions `bind_names` and `bind`. The module depends only on
  `EvaluatorContext`, `Joint`, AST contracts, and existing call/error ports;
  it does not import or construct `runtime.evaluator`.
- Installed the two dispatchers through
  `install_binding_compatibility`. Evaluator remains the single mutable state,
  DTO, `Joint` lifecycle, unit-store, and diagnostic owner. Existing family
  bodies (tensor, ket, state scaling, block, when, pipe, and related helpers)
  remain callback-owned and were not opportunistically moved.
- Extended `EvaluatorContext` with the narrow binder callbacks and scalar/unit
  mutation contract required by the successor.
- Active-Red entry retired after the complete Red contract passed: **8 passed**.
- Focused consumer smoke and adjacent regression: **41 passed**.
- All-blocking suite: **2,195 passed in 318.31s**.
- `compileall`, test lifecycle, document lifecycle, coverage-ledger
  consistency, and `git diff --check` passed.
- Tested SHA: `39e995f900574bf63db546a5cee4b89aa872cb39`; dirty worktree,
  macOS, repository virtualenv, Python 3.14. The implementation is not yet
  commit-specific because no commit was requested or created.
- Next approval:
  `WP-0167 / LISS-0571 Phase 3 Refactor 承認`.

## Phase 3 Refactor

- Approval: `WP-0167 / LISS-0571 Phase 3 Refactor 承認` (2026-09-22).
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0571-phase3-review.md`.
- Removed the duplicated `_legacy_bind_names` and `_legacy_bind` dispatcher
  bodies from `Evaluator`. The successor in `evaluation/binding.py` is now the
  sole binder dispatcher implementation; tensor, ket, state-scaling, block,
  when, pipe, and other family bodies remain explicit callbacks.
- Measurements after refactor: `evaluator.py` **3,117 lines**,
  `binding.py` **244 lines**, `context.py` **215 lines**.
- Compileall and focused/consumer/adjacent verification passed; all-blocking
  verification passed with **2,195 tests**. Lifecycle, document,
  coverage-ledger, and diff checks passed.
- Result: Phase 3 Refactor accepted by same-context review. LISS-0571 remains
  open until final review approval.
- Next approval:
  `WP-0167 / LISS-0571 Phase 3 最終レビュー 承認`.

## Phase 3 final review

- Approval: `WP-0167 / LISS-0571 Phase 3 最終レビュー 承認` (2026-09-22).
- Final review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0571-final-review.md`.
- Result: accepted. No blocker was found in dispatcher ownership,
  state/DTO ownership, private consumer compatibility, ordering, diagnostics,
  excluded scope, or verification evidence.
- Final evidence: focused/consumer/adjacent **49 passed**; all-blocking
  **2,195 passed in 314.09s**; compileall, active-Red lifecycle, document
  lifecycle, coverage-ledger, and diff checks passed.
- Structure: `evaluator.py` **3,117 lines** and binder successor
  `binding.py` **244 lines**. No duplicate dispatcher definitions remain in
  `Evaluator`.
- Process review: no operating-contract deviation or operational problem
  found.
- LISS-0571 is complete. WP-0167 remains open for separately approved Units
  B–D.
