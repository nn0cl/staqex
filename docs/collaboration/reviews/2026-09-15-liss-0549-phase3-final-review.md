# LISS-0549 Phase 3 Refactor Review

## Scope and role

- Scope: QASM lowering decomposition, public compatibility facade, and the
  canonical-versus-diagnostic authority boundary.
- Review mode: same-context reviewer; weaker isolation than
  `separate_context`. This packet is not a substitute for Adjudicator approval.
- Approval under review: `LISS-0549 Phase 3 Refactor 承認`, received
  2026-09-15.

## Canonical artifacts re-read

- `docs/specs/staqex-core-module-decomposition.md`
- `docs/architecture/agent-quickstart.md`
- `docs/architecture/implementation-readiness.md`
- QASM projection, target-boundary, and real-QPU readiness specifications
- `docs/issues/LISS-0549-qasm-lowering-decomposition.md`
- `compiler/staqex/backend/qasm/lower.py`
- every module under `compiler/staqex/backend/qasm/lowering/`
- `tests/test_liss_0549_qasm_lowering_red.py`
- `docs/testing/active-red-tests.toml`

## Findings and dispositions

1. The public `backend.qasm.lower` import surface remains available through a
   thin facade. **Already closed with evidence:** the structural suite passes
   and existing QASM consumers collect and execute their imports.
2. The extracted family modules do not import the public facade. **Already
   closed with evidence:** the dependency-direction contract and compilation
   checks pass.
3. Ownership is explicit for profiles, preflight, canonical semantic
   lowering, bounded AST compatibility, evolution, and resources. **Already
   closed with evidence:** the ownership contract passes.
4. The original implementation remains in `lowering/legacy.py`. **Accepted
   bounded disposition:** this phase establishes reviewable ownership seams
   and compatibility; it does not claim a body-by-body migration. A future
   issue may migrate legacy bodies family by family with separate behavior
   snapshots.
5. Relocation-sensitive relative and dynamic imports were corrected. **Already
   closed with evidence:** module compilation and the nearest QASM suite pass
   except for the documented pre-existing rotation diagnostic mismatch.
6. Canonical semantic lowering remains the executable meaning producer, while
   AST compatibility remains diagnostic-only. **Already closed with evidence:**
   the canonical-before-allocation/AST contract passes; no provider or live-QPU
   path is introduced.

## Blockers and out-of-scope findings

- No LISS-0549 decomposition blocker found.
- The nearest suite has one pre-existing failure: it expects
  `QASM_ROTATION_ANGLE_UNRESOLVED` but receives
  `E_QPU_CANONICAL_PROVENANCE`. This is outside the decomposition and is not
  altered here.
- Live QPU/provider verification is not applicable to this local refactor.

## Deterministic verification

- `tests/test_liss_0549_qasm_lowering_red.py`: **4 passed**.
- Nearest QASM suite: **40 passed, 1 pre-existing failure**.
- `py_compile` for facade and lowering modules: passed.
- `git diff --check`: passed.
- Active-Red lifecycle check: passed.
- Document lifecycle check: passed.
- Coverage-ledger consistency check: passed.

## Reviewer conclusion

The bounded Phase 3 decomposition is reviewable and preserves the accepted
public compatibility and authority boundaries. No blocker requires reopening
the implementation phase. The retained legacy bridge is explicit and should
not be mistaken for complete internal migration.

## Next requested approval

`LISS-0549 Phase 3 最終レビュー 承認`
