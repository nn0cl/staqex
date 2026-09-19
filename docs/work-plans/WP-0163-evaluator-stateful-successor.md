# WP-0163: Evaluator stateful evolution/operator successor

| Field | Value |
|---|---|
| Status | in_progress — LISS-0566-A/B/C complete; LISS-0566-D gated |
| Size | XL |
| Parent | WP-0162 |
| Scope approval | Architecture Path Phase 0 accepted 2026-09-19 |
| Implementation permission | none |
| Canonical specification | [Core module decomposition](../specs/staqex-core-module-decomposition.md) |

## Goal

Remove the remaining stateful evolution/operator lowering implementation from
`runtime/evaluator.py` without changing language meaning, runtime behavior,
QASM output, diagnostics, or canonical semantic authority.

## Issue graph

| Issue | Scope | Size | Candidate module | Order |
|---|---|---:|---|---:|
| LISS-0566-A | evolution execution and Hamiltonian loops | L | `evaluation/evolution.py` | first |
| LISS-0566-B | unitary/QFT/apply/capply gate mechanics | M | `evaluation/evolution.py` | after A |
| LISS-0566-C | operator resolution/tree/factory/method lowering | L | `evaluation/operators.py` | after A; may parallel B after boundary review |
| LISS-0566-D | successor facade and structure audit | M | `evaluator.py`, compatibility | last |

The four units are planned boundaries, not implementation permission. Phase 1
must confirm the measured manifests and may subdivide A or C if callback fan-out
is not reviewable.

## Invariants

- one mutable state owner: `Evaluator`;
- no public facade import from extracted modules;
- no new external dependency or provider boundary;
- private compatibility hooks remain available until D;
- local/QASM/diagnostic baselines remain unchanged;
- no behavior correction is hidden in structural extraction.

## Gates

1. Phase 0: profile, dependency graph, context contract, and allowed files.
2. Phase 1 Red: structural and characterization contracts only.
3. Phase 2 Green: one approved unit at a time.
4. Phase 3 Refactor: compatibility cleanup, import audit, and evidence.
5. Final review: process review and status synchronization.

## Phase 1 Red result

Added `tests/test_liss_0566_evaluator_stateful_successor_red.py` with six Unit A
structural and characterization contracts. Focused verification: **3 failed,
3 passed** as the intentional pre-extraction Red result. Unit B and Unit C are
not part of this Green gate. No production source was changed.

## Phase 1 Red test review

Approved on 2026-09-19:
`Feature Path / Phase 1 Red テストレビュー / LISS-0566 stateful evolution and
operator lowering successor 承認`.

The Red contract is accepted. The next execution scope is Unit A only;
unitary/gate and operator lowering remain separately gated.

## Phase 2 Green — Unit A

Implementation approval received on 2026-09-19. Ten evolution execution
methods were physically moved into `runtime/evaluation/evolution.py` and
compatibility aliases were preserved. `evaluator.py` decreased from 5,921 to
5,164 lines. Verification passed: focused **6**, adjacent **58**, and full
blocking **2,129** tests; public baseline, compileall, lifecycle, and diff
checks also passed.

The active-Red entry was removed after Green. Unit B and Unit C remain gated.

## Phase 3 Refactor — Unit A

Approved on 2026-09-19:
`Feature Path / Phase 3 Refactor / LISS-0566 Unit A evolution execution
承認`.

The extracted Unit A functions were renamed from extraction-era legacy names to
responsibility-oriented names, and each extracted context parameter now carries
the explicit `EvaluatorContext` contract. `evaluation/compatibility.py` keeps
the existing evaluator private hooks mapped to those functions; this preserves
consumer compatibility while removing legacy naming from the implementation
module. Unit B, Unit C, semantic authority, and mutable-state ownership were
not changed.

Verification passed: focused/adjacent characterization **12**, full blocking
**2,129**, public baseline, compileall, active-Red lifecycle,
document-lifecycle, coverage-ledger consistency, and diff checks. No behavior
change was introduced.

## Current next action

LISS-0566-A was approved through:
`LISS-0566 Phase 3 最終レビュー 承認`.

Current next action: prepare the separate Unit B acceptance/design intake;
this approval does not authorize Unit B, Unit C, or the successor facade audit.

## Unit B acceptance/design intake

Acceptance/design intake approved on 2026-09-19:
`WP-0163のUnit B acceptance/design intake承認`.

### Scope and measured surface

Unit B is the next slice of the large-`evaluator.py` decomposition. The
measured source is currently `runtime/evaluator.py` at 5,164 lines. The
implementation surface is four methods, approximately 250 body lines:

| Responsibility | Current method | Measured lines | Planned owner |
|---|---|---:|---|
| unitary resolution | `_evolution_legacy_resolve_unitary_matrix` | 65 | `evaluation/evolution.py` |
| QFT family matrix | `_evolution_legacy_qft_family_matrix` | 43 | `evaluation/evolution.py` |
| multi-wire `apply` | `_evolution_legacy_bind_apply` | 81 | `evaluation/evolution.py` |
| controlled `capply` | `_evolution_legacy_bind_capply` | 61 | `evaluation/evolution.py` |

The tightly coupled `_split_capply_args` helper is included in the structural
Red manifest unless the Phase 1 review demonstrates that a narrower helper
boundary is more reviewable. `_bind_cnot_multi` remains already extracted by
Unit A and is a compatibility dependency, not new Unit B implementation.

### Boundary and state contract

- `Evaluator` remains the sole mutable runtime-state owner.
- The extracted module must not import or construct `runtime.evaluator`.
- Unit B receives a typed `EvaluatorContext`; it may request operator
  definitions, scalar values, and static register sizes through narrow
  read-only callbacks, and may use existing pure gate/matrix helpers.
- Unitary resolution, QFT register-size validation, wire validation, polarity
  parsing, and controlled-unitary construction move together; no business
  policy is added to compatibility wiring.
- `evaluation/compatibility.py` continues to install `_resolve_unitary_matrix`,
  `_qft_family_matrix`, `_bind_apply`, `_bind_capply`, and existing private
  helper names until the later facade audit.
- Unit C operator resolution/lowering, Semantic IR ownership, provider SDKs,
  network, credentials, live QPU, and language-semantic changes are excluded.

### Acceptance contract for Phase 1 Red

The future Unit B Red suite must assert:

1. all four implementation bodies and the accepted `capply` helper manifest
   are owned by `evaluation/evolution.py`, not `Evaluator`;
2. the extracted module has no public-facade import or second state owner;
3. the context contract exposes only the required operator/scalar/register
   reads and state callbacks;
4. established private evaluator consumers remain resolvable through
   compatibility wiring;
5. fixed-seed local characterization preserves `apply`, `capply`, `ocapply`,
   mixed control polarity, QFT/IQFT/CQFT, identity, and invalid-wire
   diagnostics;
6. QASM3 output and rejected-input diagnostics remain unchanged, including
   atomic rejection and diagnostic ordering.

### Verification and gates

Phase 1 Red is test/design-only and requires its own typed approval. Phase 2
Green requires a separate Unit B implementation approval. Phase 3 will clean
up compatibility names and import boundaries after the focused and adjacent
regressions pass. Every phase must include private-consumer inventory, public
baseline, focused and nearest QASM/local tests, Spec Verification, full
blocking pytest, compileall/import-cycle, lifecycle, coverage-ledger, and
`git diff --check` evidence.

No Phase 1 Red tests, production source, or active-Red lifecycle entry were
created in this intake.

## Unit B Phase 1 Red

Added `tests/test_liss_0566_unit_b_red.py` with seven contracts. The focused
run intentionally reports **4 failed, 3 passed**:

- four structural contracts fail because the Unit B implementation remains on
  `Evaluator` and its extracted entrypoints/context/wiring do not exist yet;
- QFT and controlled-gate characterization contracts pass;
- no production source or reviewed assertion was changed.

The active-Red ownership is recorded for `LISS-0566-B` in
`docs/testing/active-red-tests.toml`.

## Unit B Phase 1 Red test review

Approved on 2026-09-19:
`WP-0163 / LISS-0566-B Phase 1 Red テストレビュー承認`.

The four structural contracts and three characterization contracts were
accepted. During review, the compatibility contract was tightened to assert
exact evaluator-to-extracted-function assignments. The suite remains **4
failed, 3 passed**, with no production change.

Current next action: request
`WP-0163 / LISS-0566-B Phase 2 Green / Implementation 承認`.

## Unit B Phase 2 Green

Implementation approval received on 2026-09-19:
`WP-0163 / LISS-0566-B Phase 2 Green / Implementation 承認`.

Extracted the Unit B gate mechanics into `evaluation/evolution.py` and added
typed context callbacks for operator definitions, scalar values, and static
register sizes. Compatibility wiring preserves the existing evaluator private
hooks. Unit B focused **7**, adjacent **20**, and full blocking **2,136** tests
passed; public baseline, Spec Verification, compileall, lifecycle,
coverage-ledger, and diff checks also passed. `evaluator.py` is now 4,953 lines
and `evolution.py` is 1,092 lines.

The active-Red entry for LISS-0566-B was removed after Green.

Current next action: request
`WP-0163 / LISS-0566-B Phase 3 Refactor 承認`.

## Unit B Phase 3 Refactor

Approved on 2026-09-19:
`WP-0163 / LISS-0566-B Phase 3 Refactor 承認`.

Cleaned up Unit B names, annotations, callback documentation, duplicate
operator lookup, and compatibility wiring without changing behavior. Focused
and nearest regression **27**, full blocking **2,136**, Spec Verification
**161/161**, baseline, compileall, lifecycle, coverage-ledger, and diff checks
passed. `evaluator.py` is 4,957 lines and `evolution.py` is 1,106 lines.

Current next action: request
`WP-0163 / LISS-0566-B Phase 3 最終レビュー 承認`.

## Unit B Phase 3 final review

Approved on 2026-09-19:
`WP-0163 / LISS-0566-B Phase 3 最終レビュー 承認`.

The Unit B bounded scope is complete. Unit C operator resolution/lowering and
Unit D successor facade/structure audit remain gated and require their own
acceptance and implementation approvals.

Current next action: prepare the separate Unit C acceptance/design intake.

## Unit C acceptance/design intake

Acceptance/design intake approved on 2026-09-19:
`WP-0163 / LISS-0566-C acceptance/design intake 承認`.

### Scope and measured surface

Unit C is the operator-resolution/lowering slice remaining in the large
`runtime/evaluator.py`. The current facade is **4,957 lines**. The measured
Unit C implementation surface is **11 methods / 507 physical lines**:

| Responsibility | Current method(s) | Lines | Planned owner |
|---|---|---:|---|
| operator-name and RHS classification | `_operator_legacy_operator_name`, `_operator_legacy_looks_like_operator_rhs` | 22 | `evaluation/operators.py` |
| top-level operator resolution and array context | `_operator_legacy_resolve_operator`, `_operator_legacy_array_context` | 52 | `evaluation/operators.py` |
| nested operator-call and recursive tree resolution | `_operator_legacy_resolve_op_call`, `_operator_legacy_resolve_operator_tree`, `_operator_legacy_lookup_set_comprehension_value` | 135 | `evaluation/operators.py` |
| finite-binder/operator materialization | `_operator_legacy_lower_operator_value` | 18 | `evaluation/operators.py` |
| Operator-returning function factory | `_operator_legacy_resolve_operator_factory_call` | 135 | `evaluation/operators.py` |
| Operator-returning class method | `_operator_legacy_resolve_operator_method_call` | 123 | `evaluation/operators.py` |
| second-quantized typed bind | `_operator_legacy_bind_second_quantized` | 22 | `evaluation/operators.py` |

The two pure helpers already in `evaluation/operators.py` remain the local
home for source-expression conversion and projector-sum construction. They are
not duplicated. The target module must remain below the 1,200-line normal
guardrail after this extraction; this is a reviewability constraint, not a
permission to introduce a generic utility layer.

### Design boundary and state contract

- `Evaluator` remains the only mutable state owner. The extracted functions
  receive a typed context or narrow callbacks and must not copy or retain
  `operators`, `scalars`, `objects`, `classes`, `structs`, `enums`,
  `second_quantized_operators`, `_this`, or resolved array maps.
- The operator service may read live maps through declared callbacks for
  operator/grid-Hamiltonian lookup, function/class/struct/enum lookup,
  scalar/object environments, second-quantized values, and merged finite-array
  context. It may request value evaluation, set-comprehension evaluation,
  receiver resolution, assignment execution, and recursive operator lowering
  only through the explicit context contract.
- Factory calls keep their parameter-rekeyed object/scalar/array locals local
  to that call. Method calls keep receiver binding and restore `_this` in a
  `finally`-equivalent boundary. No local frame becomes global evaluator state.
- Recursive tree resolution remains the canonical runtime Operator-tree pass:
  `OpAttr`, nested Operator-returning calls, finite binders, projector sums,
  and unchanged subtrees must retain their existing order and identity rules.
- `bind_second_quantized` retains the current semantic split: symbolic
  Fermion/Boson/Spin values stay symbolic; an explicit supported
  `QubitOperator` mapping may populate the existing ordinary operator map.
  No new mapping family or physics meaning is introduced.
- `evaluation/compatibility.py` continues to install established public and
  private evaluator hook names until Unit D. Compatibility is a thin bridge;
  it must not contain the operator policy or a second implementation body.
- Scientific Semantic IR remains the compile-owned semantic authority. This
  runtime extraction does not alter parser/typechecker/IR ownership, QASM
  projection, diagnostics, provider boundaries, or deployment behavior.

### Acceptance contract for Phase 1 Red

The future Unit C Red suite must assert:

1. all 11 implementation bodies leave `Evaluator` and are owned by
   `evaluation/operators.py`; the two existing pure helpers remain single
   implementations;
2. the extracted module has no public-facade import, `Evaluator` construction,
   copied mutable state, or provider/network/filesystem dependency;
3. the context contract exposes only the operator-specific environment reads
   and evaluation/assignment/receiver callbacks required by the measured
   call graph;
4. private consumers and the established `_resolve_operator_expr` alias still
   resolve through compatibility wiring, with exact function ownership checks;
5. factory and method calls preserve local scalar/object/operator bindings,
   receiver restoration, arity/type diagnostics, and finite-binder array
   materialization;
6. recursive Operator-tree behavior preserves nested calls, `OpAttr`, set
   projector sums, unchanged subtree identity, and supported second-quantized
   mapping behavior;
7. fixed-seed local execution, operator/binder characterization, QASM3 output,
   diagnostic code/span/order, and atomic rejection remain unchanged for both
   positive neighboring forms and unsupported forms;
8. Semantic IR and provider-neutral boundaries remain untouched, and no live
   QPU or external credential is needed.

### Included and omitted context

Included: the canonical decomposition specification, this work plan, the
current evaluator/operator/context/compatibility modules, the private-consumer
search, operator-resolution/binder/second-quantization characterization
suites, and the verification policy. Omitted: unrelated evaluator families,
provider SDKs, network/credentials/live QPU, Rust migration, broad semantic
changes, and the Unit D facade/structure audit.

### Verification plan and next gate

Phase 1 Red is test/design-only. Its issue-linked active-Red entry must be
created only with the Phase 1 approval. Phase 2 Green requires a separate
typed implementation approval. Phase 3 and final review must include the
private-consumer manifest, public import baseline, focused operator and
nearest binder/second-quantization/QASM regressions, Spec Verification,
full blocking pytest, compileall/import-cycle, lifecycle, coverage-ledger,
document lifecycle, and `git diff --check` evidence. The next approval is:
`WP-0163 / LISS-0566-C Phase 1 Red 承認`.

## Unit C Phase 1 Red

Approved on 2026-09-19:
`WP-0163 / LISS-0566-C Phase 1 Red 承認`.

Added `tests/test_liss_0566_unit_c_red.py` with eleven Unit C contracts and
registered issue-linked active-Red ownership. The focused run reports **4
failed, 7 passed**: structural extraction, callback, and exact compatibility
ownership contracts fail for the pre-Green implementation; facade dependency
and seven Operator/factory/binder/method/QASM/projector/second-quantized
characterizations pass. No production source or reviewed assertion was
changed.

## Unit C Phase 1 Red test review

Review packet: [LISS-0566-C Phase 1 Red test review](../collaboration/reviews/2026-09-19-liss-0566-c-phase1-red-test-review.md).

Approved on 2026-09-19:
`WP-0163 / LISS-0566-C Phase 1 Red テストレビュー承認`.

The review accepted the intentional four-test Red result and seven passing
characterizations. Two explicit projector-tree and second-quantized nodes
were added to close the initial coverage gap. Active-Red ownership remains
until Green.

Next approval:
`WP-0163 / LISS-0566-C Phase 2 Green / Implementation 承認`.

## Unit C Phase 2 Green

Implementation approval received on 2026-09-19:
`WP-0163 / LISS-0566-C Phase 2 Green / Implementation 承認`.

Extracted all eleven operator-resolution/lowering methods into
`runtime/evaluation/operators.py`. `Evaluator` remains the sole mutable state
owner; the new functions use explicit context callbacks for live environments,
receiver/assignment state, finite-array lookup, and recursive evaluation.
Compatibility assignments remain centralized in `evaluation/compatibility.py`,
with no second implementation body.

Measured result: `evaluator.py` **4,491 lines**; `operators.py` **617 lines**.
The extracted module remains below the 1,200-line guardrail.

Verification: Unit C focused **11 passed**, adjacent regressions **29 passed**,
combined structural suite **17 passed**, affected S02/benchmark/legacy suite
**20 passed**, and full blocking pytest **2,147 passed**. Whitespace validation
with `git diff --check` passed. The LISS-0566-C active-Red entry was removed.

Scope remained structural: Semantic IR, QASM projection, diagnostics,
provider/QPU boundaries, and external-resource behavior were not changed.

Current next action: request
`WP-0163 / LISS-0566-C Phase 3 Refactor 承認`.

## Unit C Phase 3 Refactor

Refactor approval received on 2026-09-19:
`WP-0163 / LISS-0566-C Phase 3 Refactor 承認`.

Performed behavior-preserving cleanup in `runtime/evaluation/operators.py`:
normalized extracted-function indentation and signatures, removed a duplicate
local import, restored the required `LitFloat` import, centralized numeric
receiver-field extraction, clarified class lookup and host-array merging, and
formatted long lowering/mapping calls. No acceptance assertion or compatibility
assignment changed.

Verification: Unit C and adjacent suites **46 passed**, full blocking pytest
**2,147 passed**, compileall, Active-Red lifecycle, document lifecycle,
coverage-ledger consistency, Spec Verification **161/161**, and
`git diff --check` passed. Sizes remain `evaluator.py` **4,491 lines** and
`operators.py` **617 lines**.

Current next action: request
`WP-0163 / LISS-0566-C Phase 3 最終レビュー 承認`.

## Unit C Phase 3 final review

Review packet: [LISS-0566-C Phase 3 final review](../collaboration/reviews/2026-09-19-liss-0566-c-phase3-final-review.md).

Approved on 2026-09-19:
`WP-0163 / LISS-0566-C Phase 3 最終レビュー 承認`.

Unit C is complete. The final review found no blocker across extracted
ownership, context/state boundaries, compatibility assignments, behavior
preservation, or size guardrails. Verification remained green: focused and
adjacent **46 passed**, full blocking **2,147 passed**, Spec Verification
**161/161**, compileall, lifecycle, coverage-ledger, and diff checks passed.

Process review: no operating-contract deviation or operational problem found.

Current next action: prepare the separate Unit D acceptance/design intake.
