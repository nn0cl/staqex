# LISS-0549 Phase 2 Green Review

## Review packet

- Scope: QASM lowering family boundaries and public facade compatibility.
- Canonical documents: core decomposition spec, backend target architecture,
  canonical QASM projection spec, real-QPU readiness acceptance, and
  LISS-0549 Issue/trace.
- Changed files re-read: `backend/qasm/lower.py`, all files under
  `backend/qasm/lowering/`, structural tests, Active-Red ledger, and nearest
  QASM tests.

## Findings and dispositions

1. Six family entrypoints exist and the public facade preserves the prior
   import surface. **Already closed with evidence:** LISS-0549 structure tests
   pass and existing tests collect.
2. Internal lowering code does not import the public `lower.py` facade.
   **Already closed with evidence:** dependency-direction test passes and
   relocated imports compile.
3. The implementation remains in `legacy.py` behind thin family wrappers.
   **Accepted bounded disposition:** this fixes the public ownership seam
   without claiming that all lowering bodies were moved; body migration is
   successor scope.
4. Relocating the file exposed relative-import hazards. **Applied:** all
   affected static and dynamic imports were corrected and the nearest QASM
   suite was rerun.

## Blockers and known failures

- No decomposition blocker remains.
- One pre-existing rotation-diagnostic expectation fails with
  `E_QPU_CANONICAL_PROVENANCE` instead of `QASM_ROTATION_ANGLE_UNRESOLVED`.
- Live QPU/provider tests are not applicable.

## Deterministic verification

- LISS-0549 structural suite: 4 passed.
- Nearest QASM suite: 40 passed, 1 pre-existing failure.
- `py_compile`, `git diff --check`, document lifecycle, and coverage-ledger
  checks: passed.
- Review isolation: `same_context`, weaker than `separate_context`.

## Next approval

Request: `LISS-0549 Phase 3 Refactor 承認`.
