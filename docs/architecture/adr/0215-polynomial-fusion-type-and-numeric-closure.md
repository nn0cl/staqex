# ADR 0215: Polynomial Fusion Type and Numeric Closure

## Status

**Proposed — Architecture approval required**

## Context

ADR-0157 shipped a bounded polynomial optimization for pure unary pipes. Its
current evaluator recognizes polynomial AST shapes and stores coefficients as
`f64`. The follow-up must make two boundaries explicit: type/dimension
validation is authoritative, and finite coefficient representation must not
silently erase source meaning.

## Decision proposal

1. Polynomial fusion is an optimization after normal parsing, typing, and
   dimension validation. AST shape recognition cannot widen the accepted
   scalar State domain.
2. Unsupported carriers, invalid dimensions, effects, non-polynomial forms,
   unsupported operators, non-finite coefficients, and degree/resource overflow
   use the existing safe fallback before fused executable projection.
3. Executable coefficient vectors preserve every nonzero finite `f64`
   coefficient. Near-zero treatment may be used for diagnostics only unless a
   future ADR defines an explicit approximation/evidence contract.
4. Fusion must preserve source-derived State semantics and sequential
   equivalence for the accepted deterministic domain. It does not choose a
   finite realization or cross the QPU/backend port boundary.
5. Fusion evidence fields are diagnostics, never a second semantic authority.

## Non-goals

No division, rational powers, symbolic coefficients, operator-matrix
multiplication, new scalar/dimension families, trait specialization, effect
rows, QPU lowering, or finite realization selection.

## Consequences

- The existing ADR-0157 implementation remains the baseline; this ADR proposes
  only hardening of its type and numerical closure.
- A future implementation must add negative tests for type/dimension and
  non-finite/overflow fallback before changing the evaluator.
- Any need to change the supported domain or approximation policy requires a
  new architecture decision rather than an optimizer-only patch.
