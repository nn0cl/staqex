# WP-0163: Evaluator stateful evolution/operator successor

| Field | Value |
|---|---|
| Status | in_progress — LISS-0566-A/B Green complete; Unit B Phase 3 pending |
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
