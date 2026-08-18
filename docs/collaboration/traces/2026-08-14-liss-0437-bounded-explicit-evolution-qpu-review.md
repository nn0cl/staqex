# AI work trace — bounded explicit evolution QPU/target review

## Request

User requested a read-only independent review of the bounded explicit
evolution design intake, focused on QPU/target boundary, compatibility, QPU
IR, static/dynamic termination, resource estimation, fail-closed behavior,
legacy shorthand retirement, and the `main_fuel_search.sqx` migration plan.

## Context boundary

Included the bounded design intake, explicit-evolution Spec/ADR/WP/Issue,
provider-neutral QPU IR, QASM lowering, pipeline compatibility behavior,
parser shape, and the current fuel example. Excluded implementation changes,
Red-test creation, phase approval, vendor selection, and QPU deployment.

## Routing and evidence contract

- Requested a fresh read-only reviewer context with no edits, no implementation,
  no approval, prioritized P0/P1/P2 findings, evidence paths, readiness verdict,
  and reusable perspectives.
- The app-side delegated response was unavailable during this turn. The main
  context therefore performed deterministic read-only repository inspection
  and recorded the limitation explicitly in the review record.
- Output artifact:
  `docs/collaboration/reviews/2026-08-14-liss-0437-bounded-explicit-evolution-qpu-review.md`

## Review lenses applied

- Realization and fail-closed behavior
- Source-to-domain fidelity
- Contract completeness
- Migration/compatibility safety
- Phase and approval discipline

## Result

The bounded design intake is **not ready** for acceptance-spec amendment, Red,
or implementation. The primary blocker is that “finite static realization” is
not defined tightly enough to prevent a target from replacing predicate-
dependent repetition with one or a fixed number of propagator applications.
Additional P1 findings cover resource/error accounting, static-vs-dynamic
termination classification, and legacy retirement semantics. A P2 finding
covers the fuel example’s migration acceptance packet.

## Next condition

Correct the design documents, then run a fresh independent read-only review.
Do not infer architecture, phase, technology, or implementation approval from
this review.
