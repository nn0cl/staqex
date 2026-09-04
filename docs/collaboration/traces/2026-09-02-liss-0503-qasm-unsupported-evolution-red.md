# AI Work Trace — LISS-0503

## Scope

Reject unsupported explicit-evolution input at the canonical QASM boundary
without provider selection, finite inference, or allocation.

## Phase 1 Red

- Acceptance test: `tests/test_liss_0503_qasm_unsupported_evolution_rejection_red.py`
- Result before implementation: **3 failed, 1 passed**.
- No production implementation was changed in Phase 1.

## Phase 2 Green

- Added a guard in `compiler/staqex/backend/qasm/emitter.py` after canonical
  IR construction and before QASM realization.
- The guard rejects explicit evolution with no executable canonical
  instruction using `E_QPU_CANONICAL_PROVENANCE`.
- Rejection is atomic: empty QASM, no gates, and no allocation.
- Verification: **35 passed** across the dedicated acceptance and regression
  slices; compile and diff checks passed.

## Next gate

Phase 3 same-context review. Target-specific evolution realization remains a
separate issue and is not implied by this change.
