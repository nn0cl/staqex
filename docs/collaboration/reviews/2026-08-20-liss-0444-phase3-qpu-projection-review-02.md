# LISS-0444 Phase 3 QPU projection review 02

## Trigger and boundary

- Trigger: re-review after the approved QPU consumer migration batch
  corrections.
- Date: 2026-08-20.
- Scope: canonical provenance fail-closed behavior, direct QPU canonical-body
  validation, and projection-error rejection.
- Independent context: fresh, read-only reviewer; no implementation or
  approval authority.

## Findings and disposition

- `accepted / resolved`: unresolved instruction provenance now raises at the
  projection boundary and becomes `projection_error`; QASM consumes that error
  as an empty rejection and does not use the legacy fallback.
- `accepted / resolved`: QPU IR carries the canonical semantic body and a
  fingerprint covering schema, authority, node fields, relations, provenance,
  and explicit-Realize state. The emitter rejects mismatches.
- `accepted / resolved`: tests cover authority mutation, forged node identity,
  canonical-body mutation, unresolved instruction provenance, and projection
  error without fallback.
- `deferred / recorded`: AST-authority complete migration, QASM fallback
  retirement, Symbolic IR retirement, and exhaustive decomposition coverage
  remain consumer-wide work outside this batch.

## Evidence

- Bounded regression after final correction: `34 passed`.
- Full regression after final correction: `1628 passed in 292.11s`.
- `git diff --check`: passed.
- Implementation evidence: `compiler/staqex/qpu_ir.py`,
  `compiler/staqex/scientific_semantic_ir.py`, and
  `compiler/staqex/backend/qasm/emitter.py`.
- Test evidence: `tests/test_scientific_semantic_core_red.py`.

## Verdict and terminal state

- Verdict: `READY` for the approved representative QPU projection batch.
- Review loop terminal state: `COMPLETE`.
- The WP remains open for the explicitly deferred consumer-wide migration.
- No provider SDK, live QPU, S02 numerical migration, or solver expansion was
  performed.
