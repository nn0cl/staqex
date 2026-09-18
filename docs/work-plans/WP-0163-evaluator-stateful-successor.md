# WP-0163: Evaluator stateful evolution/operator successor

| Field | Value |
|---|---|
| Status | review — Phase 2 Unit A Green complete; Phase 3 review pending |
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

## Current next action

Request typed approval for:
`Feature Path / Phase 3 Refactor / LISS-0566 Unit A evolution execution
承認`.
