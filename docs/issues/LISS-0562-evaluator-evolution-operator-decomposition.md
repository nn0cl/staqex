# LISS-0562: Evaluator evolution and operator decomposition

## Metadata

- Local issue ID: LISS-0562
- Status: Phase 1 Red complete — test review pending
- Type: Feature Path structural decomposition
- Initial planning size: L
- Current planning size: L
- Parent: WP-0162
- Depends on: LISS-0560
- Blocks: LISS-0565

## Summary

Extract evolution, Hamiltonian, explicit propagator, unitary, QFT, apply/capply,
operator tree, binder, and projection mechanics into cohesive internal families.

## Acceptance Notes

- Evolution outputs, dimension diagnostics, Suzuki/QASM lowering, and operator
  provenance remain unchanged.
- No operator evaluator becomes a second semantic authority.
- Existing host coefficient and finite-binder ports remain the same.
- Unsupported evolution remains fail-closed and atomic.

## Allowed boundary

Candidate modules are `runtime/evaluation/evolution.py` and
`runtime/evaluation/operators.py`. Shared pure numeric helpers may move only
when their owner and import direction are explicit; no vague `utils.py`.

## AI Planning Record

See `AIP-WP-0162-001` in WP-0162. Phase 1 must capture QASM and diagnostic
goldens before any extraction.

## Verification

Evolution/operator characterization, QASM goldens, provenance checks,
finite-binder consumer tests, Spec Verification, and blocking pytest.

## Phase 1 Red acceptance

Accepted on 2026-09-19:
`Feature Path / Phase 1 Red / LISS-0562 evaluator evolution and operator
decomposition 承認`.

This approval authorizes the Phase 1 Red test contract only. It does not
authorize production extraction or Phase 2 Green implementation.

## Phase 1 Red result

Added `tests/test_liss_0562_evaluator_evolution_operator_red.py` with six
contracts:

- internal `evolution` and `operators` entrypoints exist;
- the profiled evolution/operator methods leave the public `Evaluator`
  facade;
- extracted modules depend on explicit context rather than the facade or a
  second mutable state owner;
- the context declares the required evolution/operator callbacks;
- explicit Suzuki QASM output remains characterized;
- finite-binder QPU projection remains provenance-linked to the canonical
  Scientific Semantic IR.

Verification: **1 failed, 5 passed**. The single failure is the intentional
structural Red: all 28 profiled evolution/operator methods still remain on
`Evaluator`. No production source, public API, or test-exclusion file was
changed. Phase 1 test review is required before Phase 2 Green.

## Phase 1 Red test review

Adjudicator approval received on 2026-09-19:
`Feature Path / Phase 1 Red テストレビュー / LISS-0562 evaluator evolution
and operator decomposition 承認`.

The six-test contract and the intentional `1 failed, 5 passed` Red evidence
are accepted. The next gate is typed approval for Phase 2 Green /
Implementation.
