# LISS-0574: Evaluator state construction and algebra successor

## Metadata

- Local issue ID: LISS-0574
- Status: done
- Phase: complete
- Type: Architecture Path structural decomposition
- Planning size: L
- Parent: WP-0167
- Depends on: LISS-0571 / Unit A2 complete; LISS-0572 / Unit B complete;
  LISS-0573 / Unit C complete
- Blocks: none

## [DESIGN CHECK]

### Scope and expected behavior

Extract the runtime evaluator's state construction and state-algebra family
into `evaluation/state_ops.py` without changing ket support, ket-sum literal
semantics, explicit scalar scaling, explicit norm division, selection
preparation, `inner`, `outer`, diagnostics, State/Operator boundaries, or
`Joint` mutation order. Evaluator remains the single mutable state owner.

### Specifications and files inspected

- `docs/architecture/agent-quickstart.md`
- `docs/architecture/implementation-readiness.md`
- `docs/collaboration/project-conventions.md`
- `docs/collaboration/runtime-routing.toml`
- `docs/collaboration/process-lessons-log.md`
- `docs/collaboration/source-code-quality.md`
- `docs/specs/staqex-core-module-decomposition.md`
- `docs/specs/staqex-v1-liss-0229-inner-outer-joint-runtime-call.md`
- `docs/specs/staqex-v1-s01-coverage-scorecard.md`
- `docs/issues/LISS-0229-inner-outer-joint-runtime-call.md`
- `docs/issues/LISS-0324-s02-prepare-selection.md`
- `docs/issues/LISS-0420-sigma-pi-unification.md`
- `docs/issues/LISS-0422-sigma-literal-unnormalized-correction.md`
- `docs/issues/LISS-0426-norm-and-state-division.md`
- `compiler/staqex/runtime/evaluator.py`
- `compiler/staqex/runtime/evaluation/binding.py`
- `compiler/staqex/runtime/evaluation/calls.py`
- `compiler/staqex/runtime/evaluation/execution.py`
- `compiler/staqex/runtime/evaluation/observation.py`
- `compiler/staqex/runtime/evaluation/context.py`

### Component boundaries, ports/adapters, and VO/DTO candidates

- Successor: `compiler/staqex/runtime/evaluation/state_ops.py`.
- Runtime inputs: `Joint`, `World`, ket/normalization AST nodes, `Call`, and
  existing runtime expression/value types.
- Context callbacks: bind nested state expressions, evaluate classical scalar
  expressions, resolve scientific bindings, and materialize the outer-product
  operator through an explicit runtime boundary.
- State/DTO ownership: Evaluator retains mutable maps, `Joint` lifecycle,
  runtime DTO identity, and object/scalar environments. `state_ops.py` may
  construct returned `Joint` values or pure `DenseMatrixOp` values but does not
  own those types or a second store.
- No external port, provider adapter, QPU, persistence, or new value object is
  required for this structural slice.

### Applicable constraints

- Architecture Path scope only; no Phase 1 Red or implementation yet.
- No parser, typechecker, Semantic IR, QASM, provider, network, credential,
  Rust, language syntax, or public API changes.
- Preserve the distinction between unnormalized `Sigma` ket-sum and explicit
  normalization; do not reintroduce implicit project renormalization.
- Preserve `inner` as a State-to-classical overlap and `outer` as an
  Operator-only materialization path. Do not make `outer` a State binder.
- Do not move `Joint` internals, runtime DTO classes, wavepacket generation,
  evolution, observation-family mechanics, or generic linear algebra.
- Every successor must remain below the 1,200-line guardrail and have a
  focused Red contract before implementation.

### Current inventory

Measured from `compiler/staqex/runtime/evaluator.py` at intake:

| Family | Methods | Lines |
|---|---|---:|
| Ket/state construction | `_bind_ket`, `_bind_ket_sum_binder` | 50 |
| State classification/scaling | `_is_state_producing_bind_expr`, `_bind_scaled_state`, `_bind_state_divided_by_norm`, `_compute_norm` | 80 |
| Selection preparation | `_bind_prepare_selection` | 19 |
| Inner/outer algebra | `_bind_inner`, `_materialize_outer` | 43 |
| **Total** | **9** | **192** |

### Consumer and compatibility inventory

- `evaluation/binding.py`: ket, ket-sum, norm, state classifier, scalar
  scaling, and explicit norm division.
- `evaluation/calls.py`: `prepare_selection` and `inner` runtime calls.
- `evaluation/execution.py`: Operator declaration handling and `outer`
  materialization.
- `evaluation/observation.py`: deferred Operator observation and `outer`
  materialization.
- Direct consumers: LISS-0229 inner/outer runtime tests, S02 selection tests,
  Sigma/ket-sum normalization tests, norm/state-division tests, operator
  algebra tests, and State/Operator negative-boundary tests.
- Static search must be supplemented by runtime import smoke, direct private
  helper discovery, and nested state/Operator characterization.

### Decisions and ambiguity boundaries

- Decision proposed: keep ket construction, explicit normalization, selection,
  and inner/outer in one `state_ops.py` because all operate at the State/
  Operator-to-Joint boundary and share state-preserving semantics.
- Decision proposed: retain `outer` in this successor even though it returns a
  dense Operator DTO; its call-site policy is part of the State/Operator
  boundary and must remain explicit.
- Decision proposed: expose the existing `Joint`/World construction behavior
  through narrow callbacks or direct pure runtime types, without moving their
  implementation or ownership.
- Ambiguity to resolve during scope/Red preparation: exact callback needed for
  scientific binding resolution and whether `DenseMatrixOp` construction is a
  direct pure dependency or an Evaluator callback. Phase 0 must resolve this
  from actual imports and tests before Red.

### Included and omitted AI context

- Included: Unit A/B/C successor boundaries, evaluator state-operation bodies,
  binding/call/execution/observation consumers, accepted inner/outer,
  selection, Sigma, and norm specifications, context protocol, project
  conventions, and applicable process lessons.
- Omitted: parser/typechecker implementation, provider/QPU code, historical
  records, unrelated evolution/observation bodies, and private data not
  required for this boundary.

### Task routing

- Phase 0 design: host agent with deterministic AST, import, and consumer
  measurements.
- Phase 1–3: host agent after typed per-phase approvals.
- Review: `same_context` under current routing, weaker than
  `separate_context`.

### Verification plan

- Phase 0: method-family map, consumer/import manifest, state/DTO ownership,
  State/Operator boundary map, exact paths, and callback ambiguity resolution.
- Phase 1 Red: structural failures plus positive ket, ket-sum, scaling,
  normalization, selection, inner/outer, and negative-boundary tests.
- Phase 2 Green: minimum `state_ops.py` extraction, compatibility wiring,
  runtime import smoke, focused suites, adjacent regression, and full pytest.
- Phase 3: remove duplicate Evaluator bodies, preserve compatibility, run
  structure/lifecycle/coverage/diff checks, and same-context review.

## Phase 0 acceptance boundary

This document is a design intake record. It requested:

`WP-0167 / Unit D state construction・algebra Architecture Path scope approval`

No Phase 1 Red, implementation, or compatibility rewrite is authorized by
this document.

## Architecture Path scope approval

- Approval: `WP-0167 / Unit D state construction・algebra Architecture Path
  scope approval` (2026-09-22).
- Scope is accepted for investigation and design refinement only. No Phase 1
  Red, production implementation, compatibility rewrite, or active-Red entry
  is authorized.
- Consumer inspection resolved the callback ambiguity: `state_ops.py` may
  directly import the pure `resolve_scientific_binding` helper and the pure
  `DenseMatrixOp` DTO definition, but must not import or instantiate
  `runtime.evaluator`. `Joint` mutation and nested binding remain explicit
  context boundaries.
- `outer` remains in Unit D because its Operator-only policy is inseparable
  from the State/Operator boundary; it is not a generic matrix utility.
- Next approval:
  `WP-0167 / LISS-0574 Phase 0 acceptance 承認`.

## Phase 0 acceptance

- Approval: `WP-0167 / LISS-0574 Phase 0 acceptance 承認` (2026-09-22).
- Accepted boundary: extract the nine state-construction and State/Operator
  algebra methods into `evaluation/state_ops.py`, while keeping Evaluator as
  the sole owner of mutable stores, `Joint` lifecycle, runtime DTO identity,
  and compatibility wiring.
- Accepted dependency boundary: direct use of the pure
  `resolve_scientific_binding` helper and `DenseMatrixOp` DTO definition is
  allowed; importing or instantiating `runtime.evaluator` is forbidden.
  Nested binding and Joint mutation must be explicit context operations.
- Accepted semantic contracts: unnormalized Sigma ket-sums, explicit norm
  division, State-to-classical `inner`, and Operator-only `outer` remain
  unchanged. Parser, typechecker, Semantic IR, QASM, provider/QPU,
  evolution, observation mechanics, and generic linear algebra remain out of
  scope.
- Phase 0 evidence: actual consumers were inventoried across binding, calls,
  execution, observation, and direct characterization tests; the callback
  ambiguity was resolved from source imports and DTO ownership.
- No production implementation, compatibility rewrite, or Phase 1 Red test
  was performed by this acceptance update.
- Next approval: `WP-0167 / LISS-0574 Phase 1 Red 承認`.

## Phase 1 Red

- Approval: `WP-0167 / LISS-0574 Phase 1 Red 承認` (2026-09-22).
- Added only `tests/test_liss_0574_state_ops_successor_red.py` and the
  issue-owned active-Red manifest entry. No production module or compatibility
  wiring was added.
- Structural contract: five intended failures for successor existence,
  Evaluator body retirement, compatibility wiring, narrow context callbacks,
  and no public-facade dependency.
- Passing characterizations: ket literal, normalized selection preparation,
  State-to-classical `inner`, Operator-only `outer`, unnormalized Sigma, and
  explicit norm division.
- Exact bounded run: `.venv/bin/python -m pytest -q
  tests/test_liss_0574_state_ops_successor_red.py` produced **5 failed, 6
  passed** in 0.17s. The five failures are the declared structural gaps;
  all six behavior characterizations passed. Environment: repository
  worktree, Python 3.14 virtual environment; no production files changed.
- Document lifecycle, coverage-ledger consistency, and `git diff --check`
  passed after the Red run.
- Next approval: `WP-0167 / LISS-0574 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review

- Approval: `WP-0167 / LISS-0574 Phase 1 Red テストレビュー承認`
  (2026-09-22).
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0574-phase1-red-review.md`.
- Same-context review reproduced **5 failed, 6 passed**. The five failures
  are the declared structural gaps; the six passing nodes preserve the
  approved state-construction and algebra behavior.
- The initial review command omitted `.py` and ran no tests; the exact suite
  was then rerun successfully as a bounded Red result. Lifecycle, document,
  coverage-ledger, and diff checks passed.
- No production implementation was added. Next approval:
  `WP-0167 / LISS-0574 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation

- Approval: `WP-0167 / LISS-0574 Phase 2 Green / Implementation 承認`
  (2026-09-22).
- Added `compiler/staqex/runtime/evaluation/state_ops.py` with the nine
  approved state construction/algebra functions. The successor is 168 lines,
  below the 400-line target and the 1,200-line repository guardrail.
- Removed the nine implementation bodies from `runtime/evaluator.py` and
  installed compatibility wiring through `evaluation/compatibility.py`.
  Evaluator remains the mutable state, Joint lifecycle, and DTO identity
  owner. The successor does not import or instantiate Evaluator.
- Added explicit context contracts for scientific binding resolution and
  outer materialization. Pure `resolve_scientific_binding` and
  `DenseMatrixOp` remain the only direct pure dependencies.
- The Phase 1 Red suite is now **11 passed** and its active-Red entry was
  retired. Focused/adjacent state and operator suites passed **25 tests**.
- All-blocking verification on dirty tested SHA
  `39e995f900574bf63db546a5cee4b89aa872cb39`: **2,227 passed in 315.50s**.
  `compileall`, Active-Red lifecycle, document lifecycle, coverage-ledger
  consistency, and `git diff --check` passed. A final post-commit blocking
  rerun remains required by verification policy.
- Next approval: `WP-0167 / LISS-0574 Phase 3 Refactor 承認`.

## Phase 3 Refactor

- Approval: `WP-0167 / LISS-0574 Phase 3 Refactor 承認` (2026-09-22).
- Refactored the successor for clear responsibility boundaries and removed an
  unused dependency. `state_ops.py` is 167 lines with nine functions;
  `evaluator.py` is 2,048 lines and contains none of the nine Unit D bodies.
- Focused/adjacent verification: **36 passed**. All-blocking verification:
  **2,227 passed in 313.88s**. Compileall, lifecycle, coverage-ledger, and
  diff checks passed.
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0574-phase3-review.md`.
- Next approval: `WP-0167 / LISS-0574 Phase 3 最終レビュー 承認`.

## Phase 3 Final Review

- Approval: `WP-0167 / LISS-0574 Phase 3 最終レビュー 承認` (2026-09-22).
- Final review found no blocking issue. The accepted state-operations
  successor, compatibility facade, consumer inventory, and semantic
  boundaries are complete.
- Final evidence remains **36 focused/adjacent passed** and **2,227
  all-blocking passed**. No test exclusions or unresolved failures remain.
- Process review: no operating-contract deviation or operational problem
  found.
- LISS-0574 is complete. Post-commit blocking rerun remains required if this
  work is committed again under the verification policy.
