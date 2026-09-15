# LISS-0549 Phase 0 Design Review

## Review packet

- Scope: QASM lowering decomposition before Phase 1 Red.
- Canonical documents: core module decomposition spec, backend target
  architecture, canonical Coin/Mix QASM spec, real-QPU readiness acceptance,
  LISS-0549 Issue, and its trace.
- Files re-read: `compiler/staqex/backend/qasm/lower.py`, QASM emitter,
  circuit/QPU IR contracts, direct consumers, and readiness/lifecycle policy.

## Findings and dispositions

1. The six-unit graph separates capability facts, preflight, canonical
   lowering, AST compatibility, evolution, and resource checks. **Already
   closed with evidence:** the ownership matches the accepted backend and
   decomposition boundaries.
2. `semantic.py` is the only executable meaning producer and `ast_compat.py`
   cannot authorize a circuit or implicit finiteization. **Already closed with
   evidence:** the authority rule is explicit and treated as a blocker.
3. Preflight precedes allocation and resource validation cannot create meaning.
   **Already closed with evidence:** artifact atomicity is a named acceptance
   contract, not an incidental implementation detail.
4. `lower.py` remains the public compatibility facade and emitter formatting is
   excluded. **Already closed with evidence:** no public retirement or output
   change is included.

## Blockers and risks

- No Phase 0 design blocker found.
- Main Phase 1 risk is accidental authority leakage through an old AST helper;
  tests must inspect both direct legacy entrypoints and delegated callers.
- A second risk is allocation before rejection; tests must assert an empty
  artifact envelope for unsupported programs.
- Provider SDK/live-QPU execution is not applicable.

## Verification

- `git diff --check`: passed.
- Document lifecycle check: passed.
- Coverage-ledger consistency check: passed.
- Review isolation: `same_context`, weaker than `separate_context`.

## Reviewer empathy summary

A maintainer can start at the stable `lower.py` facade and trace canonical
meaning through preflight into circuit construction, while the legacy AST path
is visibly diagnostic-only. The design names allocation atomicity and
authority leakage as executable risks instead of leaving them implicit.

## Next approval

Request: `LISS-0549 Phase 1 Red 承認`.
