# Independent Context Review — LISS-0444 policy/evolution/binder projection

| Field | Value |
|---|---|
| Trigger | User-approved continuation of the bounded Phase 3 QPU projection batch |
| Boundary | Fresh read-only context; no phase or implementation approval granted |
| Scope | ScientificSemanticIR fields, QPU IR projection, provenance/fingerprints, tests |
| Excluded | QASM fallback retirement, old consumer retirement, Symbolic IR migration, provider SDK, live QPU, S02 |
| Verdict | **READY for this bounded batch; not completion of WP-0107** |
| Verification | Targeted 45 passed; full regression 1636 passed; `git diff --check` passed |

## Findings and disposition

| Priority | Finding | Disposition | Authority / rationale |
|---|---|---|---|
| P1 | Executable instruction mutation was not covered by the semantic fingerprint | accepted / resolved | In scope for provenance acceptance; executable fingerprint and emitter rejection were added with a negative test |
| P1 | Old AST helpers and QASM AST fallback remain reachable | deferred | Outside this bounded batch; WP-0107 records retirement conditions for a new reviewed consumer-wide phase |
| P2 | `symbolic_ir` remains a parallel compatibility projection | deferred | Existing Spec/WP boundary; no independent authority is granted and no retirement is implied |

## Evidence

- `compiler/staqex/scientific_semantic_ir.py` owns the three fields and their
  source provenance; `semantic_fingerprint` covers them.
- `compiler/staqex/qpu_ir.py` projects the fields from canonical IR and records
  the executable `instruction_fingerprint`.
- `compiler/staqex/backend/qasm/emitter.py` rejects semantic, provenance, or
  executable-projection fingerprint mismatch before QASM output.
- `tests/test_scientific_semantic_core_red.py` covers explicit evolution,
  binder, canonical mutation, and instruction mutation rejection.

## Reusable review perspectives

Canonical authority and implementation reality; projection conservation and
authority reachability; realization and fail-closed behavior; migration and
regression safety; executable projection integrity; phase and approval
discipline.

## Terminal state

`COMPLETE` for the bounded review loop. Deferred findings remain open work and
do not authorize the next phase. A future consumer-wide batch requires its own
scope, acceptance tests, independent review, and typed user approval.
