# LISS-0437 formal Limit provenance review 02

## Result

- Context: fresh independent read-only reviewer.
- Verdict: **READY for the formal Limit source-preserving rejection
  provenance scope**.
- Reviewer: agent `01a0011f-fa80-71c0-ba47-3ddc4e0b198c`.
- No editing, implementation, or approval was performed by the reviewer.

## Evidence

- `CompileResult.evolution_provenance` retains the required envelope:
  `compiler/staqex/pipeline.py:203-221, 663-682`.
- `Limit` is rejected with `EVOLUTION_REALIZATION_REQUIRED` and is not
  rewritten to `exp`:
  `compiler/staqex/backend/qasm/lower.py:169-203`.
- Rejection occurs before allocation and returns no gates or partial program:
  `compiler/staqex/backend/qasm/lower.py:809-818` and
  `tests/test_liss_0437_phase3_red.py:71-78`.
- Finite `Limit` execution remains explicitly outside the scope:
  `docs/issues/LISS-0437-explicit-evolution-surface.md:86-93` and
  `docs/architecture/adr/0209-explicit-blackboard-evolution-surface.md:414-422`.
- Deterministic project checks: Phase 3 bounded suite `6/6 GREEN`, explicit
  evolution surface `GREEN`, evolve-until runtime `OK`, compilation and diff
  checks passed.

## Reusable perspectives

- Preserve the written formal expression and reject only at the target
  realization boundary.
- Verify rejection order and absence of all partial artifacts.
- Keep source provenance and target capability rejection in one envelope.
- Treat source-preserving rejection readiness separately from finite execution
  approval.

## Terminal state

- `COMPLETE` for this approved limited scope.
- Remaining separate work: finite `Limit` realization, S02 numerical
  migration, and live QPU deployment.
