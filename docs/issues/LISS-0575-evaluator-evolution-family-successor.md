# LISS-0575: Evaluator evolution-family successor

## Metadata

- Local issue ID: LISS-0575
- Status: in_progress — Phase 3 final review approved; commit and SHA-specific verification pending
- Phase: phase-3-final-review-approved
- Type: Architecture Path structural decomposition
- Planning size: L
- Parent: WP-0168
- Depends on: WP-0167 / evaluator decomposition complete
- Blocks: none

## [DESIGN CHECK]

### Scope and expected behavior

Split the active runtime evolution family currently held in
`compiler/staqex/runtime/evaluation/evolution.py` into cohesive successors
without changing evolution semantics, ordering, diagnostics, private hook
compatibility, or Evaluator state ownership.

The intended boundary covers unitary application, explicit propagators,
Hamiltonian evolution, convergence/until control, QFT/grid evolution, and
multi-wire compatibility entrypoints. It does not add provider/QPU behavior,
QASM lowering, parser/typechecker behavior, or a new public language surface.

### Specifications and files inspected

- `docs/architecture/agent-quickstart.md`
- `docs/architecture/implementation-readiness.md`
- `docs/collaboration/project-conventions.md`
- `docs/collaboration/runtime-routing.toml`
- `docs/collaboration/process-lessons-log.md`
- `docs/collaboration/source-code-quality.md`
- `docs/specs/staqex-language-specification.md`
- `docs/specs/staqex-runtime-execution-model.md`
- `docs/issues/LISS-0437-explicit-evolution-surface.md`
- `docs/issues/LISS-0562-evaluator-evolution-operator-decomposition.md`
- `docs/issues/LISS-0566-evaluator-stateful-evolution-operator-successor.md`
- `compiler/staqex/runtime/evaluation/evolution.py`
- `compiler/staqex/runtime/evaluation/compatibility.py`
- `compiler/staqex/runtime/evaluation/context.py`
- `compiler/staqex/runtime/evaluation/binding.py`
- `compiler/staqex/runtime/evaluation/calls.py`
- `compiler/staqex/runtime/evaluation/execution.py`
- `compiler/staqex/runtime/evaluation/observation.py`

### Current inventory

- `evolution.py`: **1,106 lines / 21 def declarations**.
- Direct runtime consumers: `binding.py`, `calls.py`, `execution.py`,
  `observation.py`, and `compatibility.py`.
- Private compatibility hooks include unitary resolution, multi-wire apply,
  CNOT/C-apply, explicit evolution, Hamiltonian evolution, QFT family
  matrices, precomputed grid evolution, and until/convergence helpers.
- Direct characterization consumers include explicit evolution, tuple
  coordinate Hamiltonian evolution, QFT/unitary application, C-apply/CNOT,
  and prior LISS-0562 successor tests.

### Proposed component boundaries

- Candidate A1: `evaluation/unitary_ops.py` — named gates, unitary matrix
  resolution, QFT family matrices, multi-wire apply, CNOT, and C-apply.
- Candidate A2: `evaluation/evolution_ops.py` — explicit propagator
  recognition, evolve dispatch, bounded/until control, and convergence
  predicates.
- Candidate A3: `evaluation/hamiltonian_evolution.py` — Hamiltonian one-step,
  tuple-coordinate evolution, precomputed grids, and grid provenance.
- Existing `EvaluatorContext` remains the only mutable runtime boundary.
- `Joint`, `World`, runtime DTOs, operator definitions, and provider-neutral
  ports remain owned by their current modules.

### Applicable constraints

- Architecture Path scope only; no Phase 1 Red or implementation yet.
- No import or instantiation of `runtime.evaluator` from successors.
- No second mutable state store, copied maps, or duplicate Joint lifecycle.
- No provider/QPU, QASM, parser, typechecker, Semantic IR, Rust, network,
  credential, or public API changes.
- Each successor must remain below the 1,200-line guardrail and preferably
  below 500 lines.
- Existing private hooks remain callable until a separate compatibility
  retirement decision is accepted.

### Decisions and ambiguity boundaries

- Scope decision: evolution-family decomposition is separate from parser,
  typechecker, and legacy-module cleanup.
- Scope decision: Unit A is divided into A1/A2/A3 candidates for Phase 0
  measurement; Phase 0 may merge candidates only with evidence of cohesion.
- Ambiguity: whether `explicit_propagator` belongs with unitary resolution or
  evolution dispatch.
- Ambiguity: whether QFT matrix construction is a unitary service or a shared
  pure math helper; duplication is forbidden.
- Ambiguity: exact callback set required for Hamiltonian/grid execution and
  provenance ownership.

### Included and omitted AI context

- Included: active evolution implementation, compatibility installation,
  EvaluatorContext, direct runtime consumers, private test hooks, accepted
  explicit-evolution specifications, and process lessons.
- Omitted: parser/typechecker internals, provider/QPU adapters, QASM emitter
  internals, historical legacy implementations, and unrelated observation
  semantics.

### Task routing

- Phase 0: host agent with deterministic AST, import, call-graph, and
  consumer measurements.
- Phase 1–3: host agent after typed per-phase approvals.
- Review: `same_context` under current runtime routing, weaker than
  `separate_context`.

### Verification plan

- Phase 0: method-family map, consumer/import manifest, state/DTO mutation
  inventory, callback ambiguity resolution, and exact allowed paths.
- Phase 1 Red: structural successor/body-retirement contracts plus existing
  evolution characterizations.
- Phase 2 Green: minimum extraction, compatibility wiring, runtime import
  smoke, focused/adjacent regression, and all-blocking suite.
- Phase 3: readability, private consumer compatibility, structure budget,
  lifecycle/coverage/diff checks, and same-context review.

## Architecture Path scope approval

- Approval: `WP-0168 / Unit A evolution-family decomposition Architecture Path
  scope approval` (2026-09-22).
- Scope accepted for design refinement only. Phase 0 acceptance, Phase 1 Red,
  production implementation, and compatibility retirement remain
  unauthorized.
- The three candidate boundaries are accepted for measurement; the exact
  split and callback contracts remain Phase 0 decisions.
- Next approval: `WP-0168 / LISS-0575 Phase 0 acceptance 承認`.

## Phase 0 acceptance

- Approval: `WP-0168 / LISS-0575 Phase 0 acceptance 承認` (2026-09-22).
- Method-family inventory is closed at **1,106 lines / 21 def declarations**.
- Accepted split:
  - A1 `unitary_ops.py`: multi-wire apply, CNOT/C-apply, named/operator
    unitary resolution, QFT family, and unitary-name detection; measured
    source family is approximately 328 lines.
  - A2 `evolution_ops.py`: `ExplicitPropagator`, explicit propagator
    recognition, ordinary/explicit evolve orchestration, until/convergence,
    and Hamiltonian dispatch entrypoint; measured source family is
    approximately 237 lines.
  - A3 `hamiltonian_evolution.py`: Hamiltonian one-step, tuple-coordinate,
    and precomputed-grid evolution; measured source family is approximately
    417 lines.
- Accepted callback boundary: successors use `EvaluatorContext` for operator
  and scalar environments, static register sizes, nested binding, time/unit
  evaluation, Joint operations, provenance, and cross-family dispatch. No
  successor imports or instantiates `runtime.evaluator`.
- Accepted ownership: Evaluator retains mutable maps, Joint lifecycle,
  `evolution_provenance`, runtime DTO identity, and compatibility aliases.
  `ExplicitPropagator` may move with A2 as an immutable runtime record.
- Accepted consumer inventory: binding, calls, execution, observation,
  compatibility wiring, LISS-0437 explicit-evolution tests, LISS-0404 tuple
  Hamiltonian tests, QFT/unitary tests, CNOT/C-apply tests, and LISS-0562/
  0566 successor tests.
- Accepted allowed paths for Phase 1–3:
  `compiler/staqex/runtime/evaluation/evolution.py`,
  `compiler/staqex/runtime/evaluation/unitary_ops.py`,
  `compiler/staqex/runtime/evaluation/evolution_ops.py`,
  `compiler/staqex/runtime/evaluation/hamiltonian_evolution.py`,
  `compiler/staqex/runtime/evaluation/compatibility.py`,
  `compiler/staqex/runtime/evaluation/context.py`, the bounded LISS-0575
  tests, the active-Red ledger, and the linked Issue/WP/Trace/review files.
- Parser, typechecker, Semantic IR, QASM, provider/QPU, Rust, and legacy
  modules remain explicitly out of scope.
- Next approval: `WP-0168 / LISS-0575 Phase 1 Red 承認`.

## Phase 1 Red

- Approval: `WP-0168 / LISS-0575 Phase 1 Red 承認` (2026-09-23).
- Added only `tests/test_liss_0575_evolution_family_successor_red.py` and the
  issue-owned active-Red manifest entry. No production successor or
  compatibility wiring was added.
- Structural contract: five intended failures for A1/A2/A3 symbol ownership,
  compatibility successor imports, and context callbacks.
- Passing characterizations: unitary apply, explicit and bounded evolution,
  CNOT/C-apply, ordinary and tuple-coordinate Hamiltonian evolution,
  precomputed-grid evolution, Joint distance, and QFT.
- Exact bounded run: `.venv/bin/python -m pytest -q
  tests/test_liss_0575_evolution_family_successor_red.py` initially produced
  **5 failed, 8 passed**. Review corrections replaced a vacuous facade check
  with source-ownership assertions, replaced substring matching with AST import
  checks, and added four missing family characterizations.
- Active-Red, document lifecycle, coverage-ledger, and `git diff --check`
  verification passed.

## Phase 1 Red test review

- Approval: `WP-0168 / LISS-0575 Phase 1 Red テストレビュー承認`
  (2026-09-23).
- Review packet:
  `docs/collaboration/reviews/2026-09-23-liss-0575-phase1-red-review.md`.
- Result: accepted after review findings were corrected. The suite checks
  actual implementation ownership in successor files, confirms compatibility
  imports from those files, and covers ten positive runtime characterizations.
- Corrected bounded run: **5 failed, 10 passed**. The five expected failures
  are three successor ownership gaps, compatibility wiring, and one missing
  context callback. All ten characterizations passed.
- Active-Red lifecycle, document lifecycle, coverage-ledger consistency, and
  `git diff --check` passed. Review isolation: `same_context`, weaker than
  `separate_context`. No production implementation was added or authorized.
- Next approval: `WP-0168 / LISS-0575 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation

- Approval: `WP-0168 / LISS-0575 Phase 2 Green / Implementation 承認`
  (2026-09-23).
- Extracted unitary/CNOT/QFT operations to
  `compiler/staqex/runtime/evaluation/unitary_ops.py`, explicit and bounded
  evolution orchestration to `evolution_ops.py`, and Hamiltonian, tuple, and
  precomputed-grid evolution to `hamiltonian_evolution.py`.
- `compatibility.py` now installs the retained Evaluator hooks from the three
  successor modules. `evolution.py` is a 27-line import-compatible facade.
  `EvaluatorContext` declares the live state references and callbacks used by
  these services; Evaluator remains the sole mutable state/provenance owner.
- The reviewed Phase 1 suite was unchanged and passes **15/15**. Actual
  consumer import/hook smoke passed; adjacent explicit-evolution, tuple,
  operator-successor suites passed **46 tests**. Spec verification passed
  **161/161**.
- CI-equivalent all-blocking suite on the final implementation tree passed
  **2,242 tests** in 308.09s. Before implementation, the comparable baseline
  passed **2,227 tests**; the difference is the 15 now-blocking LISS-0575 tests.
  One intermediate full run exposed a compatibility-import assertion after
  `ExplicitPropagator` was omitted from the compatibility module; restoring
  that import resolved it, and the final full suite passed.
- Active-Red entry removed after the reviewed contract went Green. Active-Red
  lifecycle (`entries=0`), document lifecycle, coverage-ledger consistency,
  `py_compile`, and `git diff --check` passed.
- Measurements: `evolution.py` reduced from 1,106 to 27 lines;
  `unitary_ops.py` 329, `evolution_ops.py` 318,
  `hamiltonian_evolution.py` 426, and `context.py` 275 lines.
- Verification ran on branch `codex/liss-0575-evolution-family`, tested
  commit base `e8e63ec25420660a28556eeab5ba3a605ef45812`, dirty working tree,
  macOS / Python 3.14.6. Final blocking command:
  `.venv/bin/python -m pytest tests/ -q`; final run window approximately
  2026-09-23 18:30:38–18:35:46 +09:00. Results are provisional until a final
  commit SHA is established and retested.
- Next approval: `WP-0168 / LISS-0575 Phase 3 Refactor 承認`.

## Phase 3 Refactor

- Approval: `WP-0168 / LISS-0575 Phase 3 Refactor 承認` (2026-09-23).
- Extracted duration normalization, single-Pauli evolution, operator
  resolution, and non-qubit-basis execution from the Hamiltonian dispatcher.
  `hamiltonian_evolve_one_step` decreased from 326 to 137 lines; its module is
  467 lines, below the preferred 500-line split threshold. The split remains
  within the accepted Hamiltonian successor instead of adding another layer.
- Consolidated bounded-evolution provenance construction and tightened the
  Joint type annotations. The reviewed Phase 1 test file and all assertions
  were unchanged. Evaluator remains the sole mutable-state owner.
- Reviewer disposition: no unresolved findings or blockers. One transient
  refactor regression in bare-Identity `apply` was caught by specification
  verification, corrected, and followed by passing focused, specification,
  and full-suite reruns. Review used `same_context`, weaker than
  `separate_context`.
- Verification on dirty worktree at base SHA
  `e8e63ec25420660a28556eeab5ba3a605ef45812`, macOS / Python 3.14.6:
  focused+adjacent **63 passed**; consumer import/hook smoke passed; spec
  verification **161/161**; all-blocking `.venv/bin/python -m pytest tests/ -q`
  with `PYTHONPATH=compiler:.` **2,242 passed in 316.58s**. Run window
  2026-09-23 19:54:06–19:59:22 +09:00. No final commit SHA exists; evidence is
  provisional until commit and SHA-specific blocking rerun.
- Active-Red lifecycle, document lifecycle, coverage-ledger consistency,
  `compileall`, and `git diff --check` passed. Static consumer inventory remains
  bounded to the previously recorded import/call-site inventory; dynamic
  plugin loading was not exhaustively enumerated.
- Review Summary:
  `docs/collaboration/reviews/2026-09-23-liss-0575-phase3-refactor-review.md`.

## Phase 3 final review approval

- Approval received: `WP-0168 / LISS-0575 Phase 3 最終レビュー 承認`
  (2026-09-23).
- The Phase 3 review result is accepted. No further phase approval is pending.
- Finalization remains open because the implementation is uncommitted and the
  verification policy requires rerunning all blocking suites against the final
  commit SHA. Process review will be recorded when the issue is closed.
- Next action: commit the approved changes when requested, then rerun all
  blocking suites against that SHA before marking this issue done.
