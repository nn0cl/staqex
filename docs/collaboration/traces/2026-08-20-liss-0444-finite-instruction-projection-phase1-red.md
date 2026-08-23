# LISS-0444 finite Suzuki/binder instruction projection — Phase 1 Red

## Approved scope

The user approved Phase 1 Red for canonical finite Suzuki/binder QPU
instruction projection. The scope excludes provider SDK/live QPU, S02
numerical migration, solver work, and unrelated Symbolic IR retirement.

## Red contract

File: `tests/test_liss_0444_finite_instruction_projection_red.py`

The tests cover:

- canonical Suzuki instructions and source provenance;
- canonical binder instructions;
- no `lower_unit_to_circuit()` compatibility fallback for Suzuki;
- no `lower_unit_to_circuit()` compatibility fallback for binder.

The Suzuki case migrates the existing source-visible `using Suzuki(...)`
finite surface; it does not add implicit finiteization. The formal-limit
conversion boundary remains source-visible `Realize`.

Verification returned **4 failed**, with no collection errors. The failures
cover the missing Suzuki/binder gate instructions and the two intended
compatibility fallback calls. The canonical policy/binder metadata remains
available as the input to the upcoming Green implementation.

## Gate

Phase 1 Red only. No production implementation or fallback removal was
performed. Phase 2 Green requires explicit approval after independent review.
