# LISS-0454: Polynomial Fusion Type and Numeric Closure

## Status

**Design intake — implementation not approved**

## Context

ADR-0157 / LISS-0190 polynomial pipe fusion is already shipped in main via
PR #216. The historical WP-0063 branch is not a source of new behavior. This
follow-up closes two review boundaries before any future maintenance or
extension: the optimizer must rely on the authoritative type/dimension gate,
and its finite `f64` coefficient representation must not silently change the
meaning represented by the source.

## Acceptance specification

1. Given a source program that passes normal type and dimension validation,
   when a pure unary pipe is eligible for polynomial fusion, the optimizer may
   fuse only the currently supported scalar State carrier domains. It must not
   widen the accepted domain by recognizing an AST shape alone.
2. Given an unsupported carrier, dimension-invalid expression, effectful
   function, non-polynomial expression, or unsupported operator, the evaluator
   must retain the existing sequential/fallback path and must not emit a
   partial fused result.
3. Given a supported polynomial chain, the fused result must preserve the
   source-derived operation and match the sequential evaluator under the same
   deterministic inputs. The source spelling, State lifetime, and terminal
   measurement boundary remain unchanged.
4. Executable coefficients must preserve every nonzero finite `f64` coefficient
   needed by the accepted polynomial. Degree classification and diagnostic
   evidence must not silently delete a coefficient merely because it is close
   to zero. Any future tolerance-based canonicalization requires an explicit
   error/evidence contract.
5. If composition exceeds the accepted degree/resource bound, or produces a
   non-finite coefficient, the evaluator must fall back before emitting the
   fused executable projection.
6. `last_algebraic_fusion` and `last_poly_fusion` remain diagnostic evidence
   only; they cannot be used as an independent semantic input or as proof that
   a QPU/backend projection is valid.
7. The change remains an internal classical evaluator optimization. It does not
   add division, rational powers, symbolic coefficient domains, operator-matrix
   multiplication, trait specialization, effect rows, QPU lowering, or finite
   realization selection.

## Out of scope

- Reopening or merging `feature/wp-0063-poly2-fusion`.
- New language surface or blackboard notation.
- Provider SDKs, QPU adapters, OpenQASM policy, or target realization.
- New scalar carrier or dimension families.

## Dependencies and evidence

- Existing authority: ADR-0157 / PR #216, DEC-0005, and current evaluator
  regression tests.
- Follow-up design: ADR-0215 and WP-0117.
- Required implementation evidence: focused tests for supported scalar domains,
  invalid type/dimension fallback, effectful/non-polynomial fallback, finite
  coefficient preservation, degree overflow, and diagnostic-only evidence.
