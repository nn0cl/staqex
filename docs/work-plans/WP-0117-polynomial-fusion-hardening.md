# WP-0117: Polynomial Fusion Type and Numeric Closure

| Field | Value |
|---|---|
| Status | Design intake — implementation not approved |
| Issue | LISS-0454 |
| Parent | WP-0063 / ADR-0157 |
| Proposed ADR | ADR-0215 |
| Allowed phase | Design only; Phase 1 requires separate approval |
| Branch | `codex/liss-0454-poly-fusion-hardening-design` |

## Work units

1. Freeze the supported scalar State carrier/domain inventory from the current
   type checker and evaluator; do not add a new carrier.
2. Specify and test the optimizer's reliance on normal type/dimension
   validation, including fail-closed fallback cases.
3. Replace implicit coefficient trimming semantics with an explicit executable
   coefficient contract, preserving finite nonzero coefficients.
4. Verify degree/resource overflow and non-finite coefficient fallback before
   executable fused projection.
5. Verify diagnostic fusion fields remain evidence and do not become a second
   semantic authority.

## Review gates

- Architecture approval of proposed ADR-0215.
- Phase 1 approval for failing tests only.
- Independent review lenses: contract completeness, architecture/boundaries,
  source-to-domain fidelity, type/dimension closure, state/physics safety,
  realization/fail-closed behavior, regression safety, and canonical authority.
- Implementation approval only after Phase 1 review and an updated readiness
  record.

## Verification matrix

| Scenario | Required result |
|---|---|
| Supported scalar polynomial | one fused evaluator path; sequential equivalence |
| Invalid type/dimension | existing diagnostic or fallback; no fused projection |
| Effectful or non-polynomial stage | existing sequential/fallback path |
| Tiny but nonzero coefficient | executable coefficient retained; evidence explicit |
| Degree/resource overflow | fail closed to existing safe path |
| Diagnostic field inspection | evidence only; no semantic reconstruction |
