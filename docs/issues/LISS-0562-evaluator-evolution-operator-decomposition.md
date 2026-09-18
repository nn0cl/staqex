# LISS-0562: Evaluator evolution and operator decomposition

## Metadata

- Local issue ID: LISS-0562
- Status: proposed — blocked until LISS-0560 completes
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
