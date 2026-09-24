# WP-0167: Evaluator successor decomposition

| Field | Value |
|---|---|
| Status | done — Units A1/A2/B/C/D consolidated; WP-0168 successor complete |
| Size | XL |
| Parent | WP-0166 / completed LISS-0569 |
| Scope approval | accepted 2026-09-20 — evaluator-only decomposition |
| Implementation permission | none |
| Canonical specification | [Core module decomposition](../specs/staqex-core-module-decomposition.md) |
| Candidate issues | LISS-0570–LISS-0574; follow-on WP-0168 / LISS-0575 |

## [DESIGN CHECK]

### Scope and expected behavior

Continue shrinking `compiler/staqex/runtime/evaluator.py` by extracting
remaining cohesive runtime families into dedicated modules under
`compiler/staqex/runtime/evaluation/`. Preserve all language behavior,
diagnostics, ordering, private consumer compatibility, DTO identity, and the
single mutable `Evaluator` state owner. Do not add logic to unrelated existing
dependency files merely to reduce a line count.

This is a structural decomposition program, not a language or provider change.
The target is to make each extracted module independently reviewable and keep
the evaluator facade as orchestration, state ownership, and compatibility
wiring.

### Current evidence and ranked decomposition candidates

Current measurements:

- `runtime/evaluator.py`: **3,790 lines / 116 class methods**.
- `runtime/evaluation/evolution.py`: **1,106 lines / 21 methods**.
- `runtime/evaluation/classical.py`: **425 lines** after LISS-0569.
- `typecheck.py`: **4,678 lines**, but it is a separate compiler phase and is
  not a dependency of the runtime evaluator.
- `parser.py`: **3,679 lines** and legacy modules remain separately tracked.

The remaining evaluator families are ranked by cohesion and direct size:

| Unit | Current bodies | Proposed owner | Why this is a separate unit |
|---|---|---|---|
| A | `_run_legacy_ast_body`, `_bind`, `_bind_names`, `_run_unit_body`, foreach/control dispatch | `evaluation/execution.py` | runtime fallback execution and statement routing; must retain one state context |
| B | `_legacy_bind_method`, `_legacy_bind_user_fun`, `_legacy_construct_instance`, `_legacy_construct_struct`, `_run_init`, `_exec_assign` | `evaluation/frames.py`, new `constructors.py`, new `assignments.py` | frame/constructor/assignment responsibilities are distinct and should not be enlarged into one existing module |
| C | `_bind_block_expr`, pipe fusion, polynomial helpers, `_piped_call` | new `evaluation/pipes.py` | pure classical/pipeline mechanics with no provider or DTO ownership |
| D | `_bind_ket`, state scaling/normalization, `inner`, `outer`, ket-sum/selection | new `evaluation/state_ops.py` | state algebra and state construction are a separate runtime family from evolution |

Each unit must be independently phased and reviewed. No unit may introduce a
second state store or move `Joint`, `ClassInstance`, `StructValue`,
`EnumValue`, or `PartialValue` definitions without a separate decision.

### Component boundaries and dependency policy

- `Evaluator` remains the only owner of mutable maps, runtime DTO identity,
  `Joint` lifecycle, injected ports, and compatibility aliases.
- New evaluation modules receive `EvaluatorContext` callbacks and may use pure
  AST/value helpers. They must not import or instantiate `runtime.evaluator`.
- `execution.py` may call narrow family callbacks but must not absorb the
  implementation bodies of classical, evolution, observation, or operators.
- `constructors.py` and `assignments.py` may perform evaluator-owned mutation
  only through explicit callbacks; they must not retain copied maps.
- `pipes.py` must remain pure with respect to evaluator state except for
  explicit value-evaluation callbacks.
- `state_ops.py` may operate on `Joint` through an explicit context/operation
  boundary; provider/QPU and Semantic IR code remain out of scope.
- `typecheck.py` and `parser.py` are not touched by WP-0167. Their future
  decomposition is a separate planning item because it does not directly
  reduce evaluator size.

### Consumer and compatibility inventory

Before each unit's Phase 1 Red, inventory must cover:

- internal `Evaluator` private names and compatibility aliases;
- imports from `runtime.evaluator` and `runtime.evaluation.*`;
- orchestration, host, CLI, call/frame, evolution, observation, operator,
  QASM-adjacent, and direct test consumers;
- dynamic method installation in `evaluation/compatibility.py`;
- diagnostic/error ordering, state/DTO identity, and mutation ordering.

Static search is necessary but insufficient; each unit must run a consumer
import smoke and the nearest characterization suite.

### Applicable constraints

- Architecture Path Phase 0 only until scope acceptance and per-unit phase
  approvals are given.
- No parser, typechecker, Semantic IR, QASM, provider, network, credential,
  Rust, language syntax, or public API retirement changes.
- No speculative modules solely to satisfy a line-count target.
- No implementation in `typecheck.py` or `parser.py` as a side effect.
- Every unit must retain the accepted `EvaluatorContext` state boundary.
- Each new module must remain below the 1,200-line guardrail and have a
  focused Red contract before implementation.

### Phase 0 inventory and Unit A1 acceptance boundary

The current evaluator call graph identifies these Unit A1 edges:

- `run_canonical_unit` and runtime-plan handlers call
  `_run_legacy_ast_body` as the legacy AST execution fallback.
- `_run_legacy_ast_body` initializes evaluator-owned run state, routes main
  statements, delegates binding through `_bind_names`, and assembles
  `EvalResult` and measurement evidence.
- `_run_unit_body` is a compatibility name used by structural tests and must
  remain callable until its consumer decision is separately closed.
- `_bind_names` is called by dynamic-lane, observation, continuous, and direct
  characterization tests; it is a consumer boundary, not an implementation
  detail that may disappear during Unit A.
- `_bind` is the cross-family dispatcher for ket, binder, classical, call,
  pipe, state, and continuous expressions. It remains an explicit callback in
  the first execution slice; moving it with the shell would recreate a broad
  god-module.

Unit A therefore has two acceptance slices:

1. **A1 execution shell**: run-state initialization, main statement routing,
   terminal result assembly, and `_run_unit_body` compatibility wiring in
   `evaluation/execution.py`.
2. **A2 binder dispatch**: a separately approved slice for `_bind`,
   `_bind_names`, and direct private consumers after A1 proves callback and
   ordering contracts.

The A1 state/DTO inventory is closed: writes to scalar/type/object/frame,
measurement, and execution-lane state remain evaluator-owned; `Joint`
creation and `EvalResult`/`MeasureResult` identity remain callback-owned; no
runtime DTO or canonical Semantic IR authority is copied or redefined.

Private consumers include orchestration fallback calls, plan tests that
monkeypatch `_run_legacy_ast_body`/`_run_unit_body`, and dynamic/observation/
continuous tests that call `_bind_names`.

### Exact allowed paths for Unit A1 Phase 1–3

- `compiler/staqex/runtime/evaluator.py`
- `compiler/staqex/runtime/evaluation/execution.py` (new)
- `compiler/staqex/runtime/evaluation/context.py`
- `compiler/staqex/runtime/evaluation/compatibility.py`
- `tests/test_liss_0570_execution_red.py` (new)
- `docs/testing/active-red-tests.toml`
- this WP, LISS-0570, its Trace, and linked review packets

No Unit A2, Unit B–D, `typecheck.py`, `parser.py`, existing feature tests, or
other runtime modules are allowed in Unit A1 without a new scope decision.

### Decisions, assumptions, and unresolved ambiguities

- Decision: prefer new cohesive modules under `runtime/evaluation/` over
  adding unrelated responsibilities to existing files.
- Decision: evaluator decomposition and typechecker decomposition are separate
  work streams.
- Decision: units A–D are ordered A → B → C → D because execution routing and
  frame/constructor callbacks are shared prerequisites for later state-family
  extraction.
- Ambiguity: exact split of `_run_legacy_ast_body` between execution and state
  dispatch requires Phase 0 consumer/call-graph evidence for Unit A.
- Ambiguity: whether `evolution.py` itself should be split is a follow-up
  candidate, not an implicit WP-0167 change.
- Decision: Unit A1 is the first implementation slice; the next approval is
  `WP-0167 / LISS-0570 Unit A1 Phase 1 Red 承認`.

### Included and omitted AI context

- Included: current evaluator source, LISS-0569 final review, existing
  evaluation modules, compatibility wiring, context protocol, private
  consumer inventory, project conventions, and process lessons.
- Omitted: parser/typechecker internals, provider/QPU integrations, historical
  legacy records, unrelated feature semantics, and full private data exports.

### Task routing

- Phase 0: host agent with deterministic AST/search/import measurement.
- Phase 1–3: host agent after typed per-unit approvals.
- Review: same-context under current runtime routing unless routing changes.

### Verification plan

- Phase 0: method-family map, call graph, state/DTO mutation inventory,
  consumer/import manifest, exact allowed paths, and unit ordering.
- Phase 1 Red: one bounded structural/characterization suite per unit.
- Phase 2 Green: minimum extraction, consumer smoke, adjacent regressions,
  and full pytest after each approved unit.
- Phase 3: readability, compatibility wiring, compileall, lifecycle,
  coverage-ledger, diff, and same-context review checks.
- Final WP completion: process review and current source measurements.

## Phase 0 gate

Architecture Path scope is accepted for the evaluator decomposition and the
Unit A1 boundary above. No tests, new production modules, or implementation
are authorized until the next gate:

`WP-0167 / LISS-0570 Unit A1 Phase 1 Red 承認`

## Unit A1 Phase 1 Red

- Approval: `WP-0167 / LISS-0570 Unit A1 Phase 1 Red 承認` (2026-09-20).
- Added: `tests/test_liss_0570_execution_red.py`.
- Added the LISS-0570 active-Red manifest entry.
- Contract: five structural failures for the absent execution successor,
  facade method bodies, context callback boundary, and compatibility wiring;
  three passing characterization cases for execution, statement routing, and
  fail-closed diagnostics.
- No production module was added. Unit A1 Green remains unauthorized.
- Next approval:
  `WP-0167 / LISS-0570 Unit A1 Phase 1 Red テストレビュー承認`.

## Unit A1 Phase 1 Red test review

- Approval reviewed: `WP-0167 / LISS-0570 Unit A1 Phase 1 Red テストレビュー承認`
  (2026-09-20).
- Review packet: `docs/collaboration/reviews/2026-09-20-liss-0570-a1-phase1-red-review.md`.
- Result: **5 failed, 3 passed** in the bounded Red suite. The five failures
  are the declared structural gaps; the three passing nodes preserve runtime
  characterizations.
- Lifecycle, document, coverage-ledger, and diff checks passed.
- No production implementation was started. The active-Red entry remains
  issue-owned by LISS-0570.
- Next approval:
  `WP-0167 / LISS-0570 Unit A1 Phase 2 Green / Implementation 承認`.

## Unit A1 Phase 2 Green / Implementation

- Approval: `WP-0167 / LISS-0570 Unit A1 Phase 2 Green / Implementation 承認`
  (2026-09-21).
- Extracted the execution shell into
  `compiler/staqex/runtime/evaluation/execution.py` (442 lines). The
  evaluator facade no longer declares `_run_legacy_ast_body` or
  `_run_unit_body`; compatibility wiring in `evaluation/compatibility.py`
  preserves both private entrypoints without a second state owner.
- Added the explicit execution callback/type contract to `evaluation/context.py`.
  `Evaluator` continues to own mutable runtime maps, DTO classes, `Joint`
  lifecycle, and injected ports. The successor does not import or instantiate
  `runtime.evaluator`.
- Phase 1 Red contract: **8 passed**.
- Focused/adjacent verification: **40 passed**.
- All-blocking verification: **2,187 passed** in 310.23s.
- `compileall`, test lifecycle, document lifecycle, coverage-ledger
  consistency, and `git diff --check` passed.
- Tested SHA: `39e995f900574bf63db546a5cee4b89aa872cb39`; the worktree was
  dirty with the approved LISS-0569/LISS-0570 changes. Baseline comparison is
  unavailable because the prior implementation tree was not separately
  committed; the first full run exposed 15 import failures, all resolved by
  adding the missing `evaluate_value` successor import, and the rerun passed.
- Active-Red ownership was retired after all eight approved nodes passed.
- Phase 3 remains required for readability, consumer compatibility review,
  same-context review, and final structural checks.
- Next approval:
  `WP-0167 / LISS-0570 Unit A1 Phase 3 Refactor 承認`.

## Unit A1 Phase 3 Refactor

- Approval: `WP-0167 / LISS-0570 Unit A1 Phase 3 Refactor 承認`
  (2026-09-21).
- Refactored `evaluation/execution.py` by naming execution-context setup and
  terminal result assembly helpers. No assertions, runtime behavior,
  compatibility alias, state owner, or allowed path changed.
- Review packet: `docs/collaboration/reviews/2026-09-21-liss-0570-a1-phase3-review.md`.
- Final verification: focused/adjacent **23 passed**; all-blocking
  **2,187 passed**; compileall, lifecycle, document, coverage-ledger, and
  diff checks passed.
- Structural measurements: `evaluator.py` **3,371 lines**;
  `evaluation/execution.py` **463 lines**; successor remains below the
  1,200-line guardrail.
- Same-context review found no blocker. Final review approval remains
  required before closing Unit A1.
- Next approval:
  `WP-0167 / LISS-0570 Unit A1 Phase 3 最終レビュー 承認`.

## Unit A1 Phase 3 final review

- Approval: `WP-0167 / LISS-0570 Unit A1 Phase 3 最終レビュー 承認`
  (2026-09-21).
- Final review packet: `docs/collaboration/reviews/2026-09-21-liss-0570-a1-final-review.md`.
- Result: accepted. No scope, compatibility, state-ownership, ordering, or
  verification blocker was found.
- Final focused/adjacent verification: **23 passed**. Latest all-blocking
  verification on the unchanged implementation tree: **2,187 passed**.
- Process review: no operating-contract deviation or operational problem
  found.
- Unit A1 is complete. WP-0167 remains open for separately approved A2 and
  Units B–D; no later unit is implicitly authorized.

## Unit A2 design intake — binder dispatch successor

- Scope approval: `WP-0167 / Unit A2 binder dispatch Architecture Path scope approval`
  (2026-09-21).
- New design issue: LISS-0571.
- Current measurements: `_bind_names` is **111 lines** and `_bind` is
  **143 lines**. The Evaluator class currently has 114 methods after A1.
- Proposed owner: new `compiler/staqex/runtime/evaluation/binding.py` for
  dispatch and compatibility wiring through `evaluation/compatibility.py`.
  The module must not import or instantiate `runtime.evaluator`.
- A2 responsibility: move only the dispatcher bodies for `_bind_names` and
  `_bind`; delegate ket, tensor, evolution, pipe, block, state, classical,
  and continuous behavior through explicit `EvaluatorContext` callbacks.
- State boundary: `Evaluator` retains all mutable maps, `Joint` lifecycle,
  DTO identity, scalar/unit stores, and family implementation bodies not
  explicitly included in A2.
- Consumer inventory: orchestration fallback (`execution.py`), observation,
  dynamic-lane, and evolution call the private hooks; direct characterization
  tests call `_bind_names`. Static search has false positives from parser,
  typechecker, legacy QASM lowering, and test helper names, so Phase 1 must
  include actual import/runtime smoke rather than search counts alone.
- Exact proposed paths for A2 design/Red/Green/Refactor:
  `evaluator.py`, new `evaluation/binding.py`, `evaluation/context.py`,
  `evaluation/compatibility.py`, a new LISS-0571 Red test, active-Red ledger,
  and LISS-0571/WP/Trace/review records. No parser, typechecker, QASM,
  provider, or Units B–D changes.
- Phase 0 decisions: keep `_bind_tensor`, `_bind_ket`, `_bind_block_expr`,
  `_bind_when`, `_bind_scaled_state`, `_bind_state_divided_by_norm`, and
  `_bind_ket_sum_binder` as explicit callbacks or later family bodies; do not
  move them opportunistically with the dispatcher. Preserve
  `_verify_static_uncompute_bind` ordering and all `logs`/`inspect_out`
  arguments.
- Ambiguity boundary: the exact callback list and whether `_verify_static_
  uncompute_bind` belongs in `binding.py` must be resolved during the A2 Red
  contract; no implementation is authorized by this design intake.
- Next approval:
  `WP-0167 / LISS-0571 Phase 1 Red 承認`.

## Unit A2 Phase 1 Red

- Approval: `WP-0167 / LISS-0571 Phase 1 Red 承認` (2026-09-21).
- Added `tests/test_liss_0571_binder_dispatch_red.py` and the active-Red
  manifest entry owned by LISS-0571.
- Contract: five intended structural failures and three passing binder
  characterizations. No production module was added.
- Next approval:
  `WP-0167 / LISS-0571 Phase 1 Red テストレビュー承認`.

## Unit A2 Phase 1 Red test review

- Approval: `WP-0167 / LISS-0571 Phase 1 Red テストレビュー承認`
  (2026-09-21).
- Review packet:
  `docs/collaboration/reviews/2026-09-21-liss-0571-phase1-red-review.md`.
- Focused verification reproduced **5 failed, 3 passed**. The five failures
  cover successor existence, Evaluator facade retirement, compatibility
  wiring, context callbacks, and no-public-facade dependency. The three
  passing tests characterize simple, classical multi-bind, and Coin binder
  behavior.
- Active-Red lifecycle, document lifecycle, coverage-ledger consistency, and
  `git diff --check` passed. No production implementation was added or
  authorized; A2 state ownership, consumer inventory, and excluded-family
  boundaries remain unchanged.
- Review isolation: `same_context`, weaker than `separate_context`.
- Result: Phase 1 Red test review accepted. Next approval:
  `WP-0167 / LISS-0571 Phase 2 Green / Implementation 承認`.

## Unit A2 Phase 2 Green / Implementation

- Approval: `WP-0167 / LISS-0571 Phase 2 Green / Implementation 承認`
  (2026-09-22).
- Implemented `runtime/evaluation/binding.py` for the two approved dispatcher
  entrypoints and installed them through `evaluation/compatibility.py`.
  `EvaluatorContext` now declares the narrow binder, family, diagnostic, and
  scalar/unit callbacks used by the successor.
- The successor has no `runtime.evaluator` import or `Evaluator()`
  construction. Evaluator remains the sole live state owner; tensor, ket,
  state-scaling, block, when, pipe, and related family bodies remain outside
  A2 and are reached through callbacks.
- Red contract: **8 passed**. Focused consumer smoke and adjacent regression:
  **41 passed**. All-blocking: **2,195 passed in 318.31s**.
- Compileall, active-Red lifecycle, document lifecycle, coverage-ledger
  consistency, and `git diff --check` passed. The LISS-0571 active-Red entry
  was retired after Green.
- Tested SHA: `39e995f900574bf63db546a5cee4b89aa872cb39`; dirty worktree,
  macOS, repository virtualenv, Python 3.14; commit-specific verification is
  pending because no commit was requested.
- Next approval:
  `WP-0167 / LISS-0571 Phase 3 Refactor 承認`.

## Unit A2 Phase 3 Refactor

- Approval: `WP-0167 / LISS-0571 Phase 3 Refactor 承認` (2026-09-22).
- Removed the duplicate legacy dispatcher bodies from `Evaluator`; the
  installed `_bind_names` and `_bind` hooks now resolve only to
  `evaluation/binding.py`. Existing family implementations remain behind
  explicit context callbacks and were not broadened.
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0571-phase3-review.md`.
- Measurements: `evaluator.py` **3,117 lines**, `binding.py` **244 lines**,
  `context.py` **215 lines**; the binder successor is below the 1,200-line
  guardrail.
- Verification: compileall passed; focused/consumer/adjacent **49 passed**;
  all-blocking **2,195 passed in 314.09s**; lifecycle, document,
  coverage-ledger, and diff checks passed.
- Result: Phase 3 Refactor accepted. Final review approval remains required
  before closing Unit A2/LISS-0571.
- Next approval:
  `WP-0167 / LISS-0571 Phase 3 最終レビュー 承認`.

## Unit A2 Phase 3 final review

- Approval: `WP-0167 / LISS-0571 Phase 3 最終レビュー 承認` (2026-09-22).
- Final review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0571-final-review.md`.
- Result: accepted. No scope, state-ownership, consumer-compatibility,
  ordering, diagnostic, structure-budget, or verification blocker was found.
- Final verification: focused/consumer/adjacent **49 passed**;
  all-blocking **2,195 passed in 314.09s**; compileall, lifecycle,
  coverage-ledger, and diff checks passed.
- Process review: no operating-contract deviation or operational problem
  found.
- Unit A2 and LISS-0571 are complete. WP-0167 remains open for separately
  approved Units B–D; no later unit is implicitly authorized.

## Unit B design intake — frames, constructors, and assignments

- Scope approval: `WP-0167 / Unit B frames・constructors・assignments Architecture Path scope approval`
  (2026-09-22).
- New design issue: LISS-0572.
- Inventory: `_legacy_bind_method` **173 lines**,
  `_legacy_bind_user_fun` **145**, `_legacy_construct_instance` **59**,
  `_run_init` **47**, `_legacy_construct_struct` **65**, and `_exec_assign`
  **36**. Combined target body size is **525 lines**.
- Proposed owners: existing `evaluation/frames.py`, new
  `evaluation/constructors.py`, and new `evaluation/assignments.py`.
- Consumer inventory covers `calls.py`, `execution.py`, `classical.py`,
  `evolution.py`, `operators.py`, and direct private/structural tests.
- Evaluator remains the single state/DTO/receiver/frame owner. Successors must
  use `EvaluatorContext`, preserve exact diagnostics and mutation order, and
  contain no public-facade dependency.
- Phase 0 design is accepted. No Phase 1 Red test or implementation is
  authorized yet.
- Next approval:
  `WP-0167 / LISS-0572 Phase 1 Red 承認`.

## Unit B Phase 1 Red

- Approval: `WP-0167 / LISS-0572 Phase 1 Red 承認` (2026-09-22).
- Added `tests/test_liss_0572_frames_constructors_assignments_red.py` and the
  issue-owned active-Red manifest entry. No production implementation was
  added.
- Contract: six intended structural failures and four passing
  frame/constructor/assignment characterizations. Structural nodes cover
  successor files, facade body retirement, legacy frame delegation,
  compatibility wiring, and narrow context callbacks.
- Next approval:
  `WP-0167 / LISS-0572 Phase 1 Red テストレビュー承認`.

## Unit B Phase 1 Red test review

- Approval: `WP-0167 / LISS-0572 Phase 1 Red テストレビュー承認`
  (2026-09-22).
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0572-phase1-red-review.md`.
- Focused verification reproduced **6 failed, 4 passed**. The six failures
  cover successor existence, Evaluator body retirement, legacy frame
  delegation, compatibility wiring, and narrow context callbacks. The four
  passing tests characterize free-function frames, method receivers, class
  init/assignment, and struct construction.
- Active-Red lifecycle, document lifecycle, coverage-ledger consistency, and
  `git diff --check` passed. No production implementation was added or
  authorized; state ownership, consumer inventory, and excluded boundaries
  remain unchanged.
- Review isolation: `same_context`, weaker than `separate_context`.
- Result: Phase 1 Red test review accepted. Next approval:
  `WP-0167 / LISS-0572 Phase 2 Green / Implementation 承認`.

## Unit B Phase 2 Green / Implementation

- Approval: `WP-0167 / LISS-0572 Phase 2 Green / Implementation 承認`
  (2026-09-22).
- Added `evaluation/constructors.py` and `evaluation/assignments.py`; updated
  `evaluation/frames.py` and compatibility wiring with explicit successor
  entrypoints. Evaluator remains the single mutable state owner.
- Renamed the retained implementation bodies to explicit callbacks for the
  Phase 2 compatibility boundary. Phase 3 must remove those bodies from the
  facade after the successor behavior is reviewed; the rename is not claimed
  as complete body migration.
- Red contract: **10 passed**. Focused consumer/adjacent: **61 passed**.
  All-blocking: **2,205 passed in 314.28s**. Compileall, lifecycle,
  document, coverage-ledger, and diff checks passed.
- Active-Red ownership was retired after Green.
- Measurements: `evaluator.py` **3,121 lines**; `frames.py` **58**;
  `constructors.py` **24**; `assignments.py` **16**; `context.py` **219**.
- Next approval:
  `WP-0167 / LISS-0572 Phase 3 Refactor 承認`.

## Unit B Phase 3 Refactor

- Approval: `WP-0167 / LISS-0572 Phase 3 Refactor 承認` (2026-09-22).
- Completed body migration for frame invocation, class/struct construction
  and init, and field assignment. The three successor modules now own the
  corresponding behavior; Evaluator retains state ownership and thin
  compatibility wiring only.
- The migration added narrow context callbacks rather than moving mutable
  state or importing Evaluator into successor modules. `restore_frame` and
  operator resolution are explicit successor/context boundaries.
- Verification: focused consumer/adjacent **61 passed**; all-blocking
  **2,205 passed in 317.73s**; lifecycle, coverage-ledger, and diff checks
  passed.
- Measurements: `evaluator.py` **2,586 lines**; `frames.py` **364**;
  `constructors.py` **188**; `assignments.py` **52**; `context.py` **234**.
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0572-phase3-review.md`.
- Unit B is ready for final review; it is not marked done until approval.
- Next approval:
  `WP-0167 / LISS-0572 Phase 3 最終レビュー 承認`.

## Unit B Final Review

- Approval: `WP-0167 / LISS-0572 Phase 3 最終レビュー 承認` (2026-09-22).
- Re-read the Unit B design, successor modules, compatibility wiring, private
  consumer tests, and Phase 3 review packet.
- Result: no blocker; LISS-0572 is complete. Unit B preserves the accepted
  state boundary and behavior while removing the extracted bodies from the
  Evaluator facade.
- Verification remains **61 focused/adjacent passed** and **2,205
  all-blocking passed in 317.73s**; lifecycle, document, coverage-ledger, and
  diff checks passed.
- Review isolation: `same_context`, weaker than `separate_context`.
- Process review: no operating-contract deviation or operational problem
  found.
- Next scope: Unit C/D design intake under WP-0167.

## Unit C design intake — pipe and polynomial successor

- Design intake requested: `WP-0167 / Unit C pipe・block・polynomial
  Architecture Path scope approval` (2026-09-22).
- New design issue: LISS-0573.
- Current measurement: the Unit C family is **302 physical lines across 17
  Evaluator methods** in `runtime/evaluator.py`: block binding, fused pipe
  dispatch, stage resolution/evaluation, affine/polynomial composition and
  arithmetic, polynomial parsing, pipe flattening, simple-return eligibility,
  and piped-call hole filling.
- Proposed owner: new
  `compiler/staqex/runtime/evaluation/pipes.py`. Keeping the polynomial
  helpers with pipe fusion preserves one decision boundary: whether a pure
  unary pipe chain can be safely collapsed and how its exact numeric evidence
  is recorded.
- State boundary: `Evaluator` remains the owner of `Joint`, function/object
  environments, scalar evaluation, dead-coordinate tracing, and the public
  `last_algebraic_fusion` / `last_poly_fusion` observations. `pipes.py` may
  request those through explicit `EvaluatorContext` callbacks, but must not
  import or instantiate `Evaluator` or retain a copied state store.
- Consumer inventory required before Red: `evaluation/binding.py`, direct
  private helper tests for `_flatten_pipe`, `_parse_poly`, `_parse_affine`,
  `_compose_poly`, and the pipeline/block characterization suites including
  `tests/test_pipeline_operator_fusion_red.py`, `tests/test_poly2_fusion_red.py`,
  `tests/test_algebraic_operator_fusion_red.py`, and
  `tests/test_bare_block_trace_out_red.py`. Runtime import smoke must cover
  the compatibility installer and actual pipe/block execution.
- Proposed context boundary: bind/value evaluation, function/object lookup,
  live-coordinate tracing, and a single fusion-evidence setter. No new DTO,
  port, provider, QPU, parser, typechecker, or Semantic IR authority is
  introduced.
- Structure budget: target `pipes.py` below **500 lines** and keep all helpers
  readable; no speculative generic algebra module is proposed. Existing
  `typecheck.py` pipe lowering is excluded because Unit C is runtime-only.
- Phase 1 Red will distinguish structural migration failures from passing
  positive characterizations for: bare block trace-out, unary fusion, affine
  fusion evidence, polynomial fusion/evaluation, and hole-filling behavior.
- No tests, production implementation, compatibility rewiring, or active-Red
  entry is authorized by this intake.
- Review routing: `same_context` under the live runtime routing; this is
  weaker than `separate_context`.
- Next approval:
  `WP-0167 / Unit C pipe・block・polynomial Architecture Path scope approval`.

## Unit C Architecture Path scope approval

- Approval: `WP-0167 / Unit C pipe・block・polynomial Architecture Path scope
  approval` (2026-09-22).
- Scope accepted for investigation/design only. Unit C remains before Phase 1
  Red and has no implementation permission.
- Design boundary refined: `pipes.py` consumes existing live-coordinate and
  trace-out behavior through explicit context declarations and records fusion
  evidence through a narrow setter; mutable evidence fields remain on
  Evaluator. No duplicate trace-out policy or generic algebra module is
  authorized.
- Next approval: `WP-0167 / LISS-0573 Phase 0 acceptance 承認`.

## Unit C Phase 0 acceptance

- Approval: `WP-0167 / LISS-0573 Phase 0 acceptance 承認` (2026-09-22).
- Unit C design is accepted for the runtime pipe/block/polynomial successor.
  The exact paths, consumer inventory, Evaluator state boundary, callback
  contract, exclusions, and structure budget are now authoritative for Red.
- No production implementation is authorized. Phase 1 may add only the
  issue-owned structural/characterization contract and active-Red metadata.
- Next approval: `WP-0167 / LISS-0573 Phase 1 Red 承認`.

## Unit C Phase 1 Red

- Approval: `WP-0167 / LISS-0573 Phase 1 Red 承認` (2026-09-22).
- Added only the issue-owned pipe successor Red contract and active-Red
  metadata. Production implementation remains unauthorized.
- The suite separates five structural migration gaps from six passing positive
  characterizations covering block, affine/poly fusion, non-finite rejection,
  hole filling, and helper parsing.
- Exact bounded run: **5 failed, 6 passed**. A fixture API mismatch was found
  and corrected in the test only before the recorded rerun.
- Next approval: `WP-0167 / LISS-0573 Phase 1 Red テストレビュー承認`.

## Unit C Phase 1 Red test review

- Approval: `WP-0167 / LISS-0573 Phase 1 Red テストレビュー承認`
  (2026-09-22).
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0573-phase1-red-review.md`.
- Same-context rerun: **5 failed, 6 passed**. Structural failures and positive
  characterizations match the accepted Red contract. The test-only fixture
  correction was reviewed and rerun.
- Lifecycle, document, coverage-ledger, and diff checks passed. No production
  implementation was authorized by this review.
- Next approval: `WP-0167 / LISS-0573 Phase 2 Green / Implementation 承認`.

## Unit C Phase 2 Green / Implementation

- Approval: `WP-0167 / LISS-0573 Phase 2 Green / Implementation 承認`
  (2026-09-22).
- Added `evaluation/pipes.py` and compatibility wiring for block binding,
  unary fusion, polynomial helpers, and piped-call transformation. Evaluator
  remains the only mutable state and result-evidence owner.
- Retained bodies are explicit `*_body` callbacks only for the Phase 2
  compatibility boundary; Phase 3 must remove the duplicate bodies.
- Verification: Red contract **11 passed**; focused/adjacent **71 passed**;
  all-blocking **2,216 passed in 318.41s**; compile, lifecycle, coverage, and
  diff checks passed.
- Measurements: `evaluator.py` **2,596 lines**; `pipes.py` **346**;
  `context.py` **244**. Active-Red ownership retired after Green.
- Next approval: `WP-0167 / LISS-0573 Phase 3 Refactor 承認`.

## Unit C Phase 3 Refactor

- Approval: `WP-0167 / LISS-0573 Phase 3 Refactor 承認` (2026-09-22).
- Removed all retained Unit C bodies from Evaluator. `pipes.py` now owns
  block binding, pipe stage resolution/evaluation, polynomial composition,
  finite arithmetic, and piped-call transformation.
- Compatibility remains directional and thin; Evaluator retains mutable state,
  trace-out policy, and fusion evidence through explicit callbacks.
- Verification: focused/adjacent **71 passed**; all-blocking **2,216 passed in
  315.13s**; compile, lifecycle, coverage-ledger, and diff checks passed.
- Measurements: `evaluator.py` **2,246 lines**; `pipes.py` **346**;
  `context.py` **244**. No Unit C `*_body` duplicate remains in Evaluator.
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0573-phase3-review.md`.
- Unit C is ready for final review and is not marked done yet.
- Next approval: `WP-0167 / LISS-0573 Phase 3 最終レビュー 承認`.

## Unit C Final Review

- Approval: `WP-0167 / LISS-0573 Phase 3 最終レビュー 承認` (2026-09-22).
- Re-read the Unit C design, successor, compatibility wiring, private-consumer
  tests, and Phase 3 review packet. No blocker found.
- Result: LISS-0573 is complete. The accepted runtime boundary and behavior
  are preserved while the evaluator facade no longer contains Unit C bodies.
- Verification remains **71 focused/adjacent passed** and **2,216
  all-blocking passed in 315.13s**; compile, lifecycle, coverage-ledger, and
  diff checks passed.
- Review isolation: `same_context`, weaker than `separate_context`.
- Process review: no operating-contract deviation or operational problem
  found.
- Next scope: Unit D design intake under WP-0167.

## Unit D design intake — state construction and algebra successor

- Design intake requested: `WP-0167 / Unit D state construction・algebra
  Architecture Path scope approval` (2026-09-22).
- New design issue: LISS-0574.
- Current measurement: **9 Evaluator methods / 192 physical lines** covering
  ket literal construction, ket-sum, state-producing classification, scalar
  amplitude scaling, explicit norm division, norm calculation, selection
  preparation, `inner`, and `outer` materialization.
- Proposed owner: new
  `compiler/staqex/runtime/evaluation/state_ops.py`. These methods share one
  decision boundary: constructing or comparing state values while preserving
  explicit normalization and the distinction between State and Operator.
- Actual consumers: `evaluation/binding.py` calls ket, ket-sum, norm,
  state-classification, scaling, and norm-division; `evaluation/calls.py`
  calls `prepare_selection` and `inner`; `evaluation/execution.py` and
  `evaluation/observation.py` materialize `outer`; direct regression suites
  cover LISS-0229, LISS-0324, LISS-0420/0422, LISS-0426, and related operator
  algebra behavior.
- State boundary: Evaluator remains the owner of mutable maps, `Joint`
  lifecycle, runtime DTO identity, and object/scalar environments. The
  successor may call `Joint` operations supplied by the runtime boundary but
  must not copy state or import/instantiate Evaluator.
- Proposed context callbacks: `_bind`, `_evaluate_value`, scientific binding
  resolution, `Joint`/world construction boundary, and `DenseMatrixOp`
  materialization. Exact callback signatures are resolved during Phase 0
  consumer inventory; no provider, QPU, Semantic IR, or persistence port is
  introduced.
- Structure budget: target `state_ops.py` below **400 lines** and below the
  repository 1,200-line guardrail. Do not move `Joint` implementation,
  `ClassInstance`, `StructValue`, `EnumValue`, `PartialValue`, wavepacket
  generation, or evolution mechanics in this unit.
- Phase 1 Red will separate structural failures from positive
  characterizations for ket/ket-sum, explicit scaling/normalization,
  selection, inner/outer, and State/Operator boundary rejection.
- No tests, production implementation, compatibility rewiring, or active-Red
  entry is authorized by this intake.
- Review routing: `same_context` under the live runtime routing; weaker than
  `separate_context`.
- Next approval:
  `WP-0167 / Unit D state construction・algebra Architecture Path scope approval`.

## Unit D Architecture Path scope approval

- Approval: `WP-0167 / Unit D state construction・algebra Architecture Path
  scope approval` (2026-09-22).
- Scope accepted for investigation/design only. The pure scientific-binding
  helper and pure `DenseMatrixOp` DTO may be direct dependencies; Evaluator,
  Joint ownership, and nested binding remain context boundaries.
- No Unit D implementation or Phase 1 Red is authorized.
- Next approval: `WP-0167 / LISS-0574 Phase 0 acceptance 承認`.

## Unit D Phase 1 Red

- Approval: `WP-0167 / LISS-0574 Phase 1 Red 承認` (2026-09-22).
- Added only the bounded LISS-0574 Red suite and active-Red ledger entry.
- Contract: five structural failures and six passing state-algebra
  characterizations; production implementation remains unauthorized.
- Exact bounded run: **5 failed, 6 passed** in 0.17s under the repository's
  Python 3.14 virtual environment. Document lifecycle, coverage-ledger, and
  diff checks passed.
- Next approval: `WP-0167 / LISS-0574 Phase 1 Red テストレビュー承認`.

## Unit D Phase 1 Red test review

- Approval: `WP-0167 / LISS-0574 Phase 1 Red テストレビュー承認`
  (2026-09-22).
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0574-phase1-red-review.md`.
- Result: the declared five structural Red nodes and six passing
  characterizations were reproduced. No production implementation was
  introduced.
- Next approval: `WP-0167 / LISS-0574 Phase 2 Green / Implementation 承認`.

## Unit D Phase 0 acceptance

- Approval: `WP-0167 / LISS-0574 Phase 0 acceptance 承認` (2026-09-22).
- Accepted the Unit D boundary: state construction, ket-sum, scaling,
  explicit normalization, selection, `inner`, and Operator-only `outer`.
- Accepted the dependency boundary: pure scientific-binding and
  `DenseMatrixOp` helpers may be used directly; Evaluator, Joint mutation,
  nested binding, and mutable runtime ownership remain explicit boundaries.
- Phase 0 consumer/import inventory and callback ambiguity resolution are
  complete. No implementation or compatibility rewrite was performed.
- Next approval: `WP-0167 / LISS-0574 Phase 1 Red 承認`.

## Unit D Phase 2 Green / Implementation

- Approval: `WP-0167 / LISS-0574 Phase 2 Green / Implementation 承認`
  (2026-09-22).
- Added `runtime/evaluation/state_ops.py` (168 lines, nine functions) and
  compatibility wiring; removed the nine Unit D bodies from `evaluator.py`.
- Red contract: **11 passed**. Focused/adjacent state and operator suites:
  **25 passed**. All-blocking: **2,227 passed in 315.50s**.
- Compile, Active-Red lifecycle, document lifecycle, coverage-ledger, and
  diff checks passed. Final post-commit blocking rerun remains required.
- Next approval: `WP-0167 / LISS-0574 Phase 3 Refactor 承認`.

## Unit D Phase 3 Refactor

- Approval: `WP-0167 / LISS-0574 Phase 3 Refactor 承認` (2026-09-22).
- Refactored `state_ops.py` to a 167-line, nine-function successor and
  confirmed that all Unit D bodies are absent from `evaluator.py`.
- Focused/adjacent: **36 passed**; all-blocking: **2,227 passed in 313.88s**.
  Compileall, lifecycle, coverage-ledger, and diff checks passed.
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0574-phase3-review.md`.
- Next approval: `WP-0167 / LISS-0574 Phase 3 最終レビュー 承認`.

## Unit D Phase 3 Final Review

- Approval: `WP-0167 / LISS-0574 Phase 3 最終レビュー 承認` (2026-09-22).
- Final review packet found no blocking issue. Unit D preserves the accepted
  state/algebra semantics and compatibility boundary.
- Verification: **36 focused/adjacent passed**, **2,227 all-blocking passed**;
  compileall, lifecycle, coverage-ledger, and diff checks passed.
- Process review: no operating-contract deviation or operational problem
  found.
- LISS-0574 is complete. WP-0167 remained open only for consolidation and
  successor-program accounting.

## Consolidation and closure

- LISS-0570 through LISS-0574 completed the accepted Units A1/A2/B/C/D.
- Follow-on evolution-family work was planned and completed separately as
  WP-0168 / LISS-0575; it merged through PR #596 at
  `66da78c824b5e5ce97fdf35b0ff9c79d7eec9df3`.
- WP-0167's approved scope is complete. Further reduction of
  `runtime/evaluator.py` is a new successor decision, not an implicit
  extension of this work plan.
- Process review: no additional operating-contract deviation was found in
  WP-0167. The separate post-merge LISS-0575 status drift is recorded and
  remediated in LISS-0575 / WP-0168.
