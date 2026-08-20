# LISS-0444 Phase 2 Green trace

## Gate and scope

- User approval: Phase 2 Green and implementation approved 2026-08-20.
- Implemented paths: `compiler/staqex/scientific_semantic_ir.py`,
  `compiler/staqex/pipeline.py`, `compiler/staqex/qpu_ir.py`,
  `compiler/staqex/quantum_semantic_ir.py`.
- Test contract: `tests/test_scientific_semantic_core_red.py` and its nine
  approved fixtures.
- Excluded: Phase 3 removal/rewiring of all legacy consumers, provider SDK,
  live QPU, S02 numerical migration, and solver expansion.

## Implementation

- Added source-derived `ScientificSemanticIR` nodes with structural children,
  role/lane, type, dimensions, exactness, intent, and source provenance.
- Added `SemanticInspectionResult`, `SemanticRejection`, and explicit
  realization-plan provenance fields.
- Exposed the canonical IR and inspection/rejection contracts through
  `CompileResult`; added source identity hooks to existing downstream roots.
- Existing Physics/Symbolic/QSEM/AST paths remain documented migration targets;
  they are not silently declared migrated by this slice.

## Verification

- `.venv/bin/pytest tests/test_scientific_semantic_core_red.py -q` → `17 passed`.
- `.venv/bin/pytest tests/test_physics_ir_lower_c_red.py tests/test_liss_0437_limit_realization_red.py tests/test_liss_0437_realize_surface_red.py tests/test_liss_0440_namespace_execution_boundary_red.py -q` → `14 passed`.
- `git diff --check` passed.
- No provider/network/live-QPU/S02 operation was performed.
- Required next step: independent implementation review. Phase 3 migration is
  not approved by this trace.

## Corrective review response

- Corrected unconditionally fabricated Algorithm Plans: plans now exist only
  when source structure contains explicit `Realize`.
- Moved canonical rejection construction after the complete diagnostic pass and
  suppresses plans for non-Realize rejected inputs.
- Full consumer rewiring remains Phase 3 and was not attempted.
- Final strict-`Realize(...)` corrective bounded regression: 32 passed.
- Full regression before that final predicate-only correction: 1,620 passed.
- Final independent verification: `COMPLETE`; no Phase 3 approval granted.

## Subsequent gate amendment

On 2026-08-20 the user separately approved a bounded Phase 3 representative
QPU IR/QASM projection slice. That approval is recorded in
`2026-08-20-liss-0444-phase3-qpu-projection.md`; it does not retroactively
change this Phase 2 trace or authorize consumer-wide legacy retirement.
