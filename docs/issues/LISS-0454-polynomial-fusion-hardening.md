# LISS-0454: Polynomial Fusion Type and Numeric Closure

## Status

- Status: done
- Phase: done
- Note: ADR-0215 and all approved implementation/review phases complete

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

## Phase 0 design intake and acceptance

### [DESIGN CHECK]

- Scope: harden the already-shipped internal polynomial-fusion optimization;
  preserve the existing supported scalar State carriers and sequential
  semantics.
- Authority inspected: ADR-0157, proposed ADR-0215, WP-0117, the current
  evaluator fusion paths, and the existing polynomial/algebraic fusion tests.
- Boundary: normal type/dimension validation remains authoritative; fusion is
  an evaluator optimization only and does not select finite realization or
  cross a QPU/backend port.
- Required evidence: supported-carrier positive equivalence, invalid/effectful
  fallback, preservation of every nonzero finite coefficient, overflow and
  non-finite fallback, and diagnostic fields remaining evidence only.
- Omitted context: new carriers, language syntax, symbolic coefficients,
  provider/QPU work, OpenQASM, and finite-realization policy.
- Applied lessons: authority-boundary and fail-closed lessons are preserved;
  optimizer evidence cannot become semantic authority.

Phase 0 acceptance is recorded as `LISS-0454 Phase 0 acceptance`, received
2026-09-16. The scope is ready for Architecture review, but no Phase 1 Red,
test modification, or implementation is authorized until ADR-0215 is accepted.

### Next gate

Request `ADR 0215 Architecture 承認`.

## Architecture approval result

- Adjudicator approval: `ADR 0215 Architecture 承認`, received 2026-09-16.
- ADR-0215 is accepted. The evaluator-only type, dimension, coefficient,
  fallback, and diagnostic-evidence boundaries are now authoritative.
- No Phase 1 tests or implementation permission is inferred from the ADR.

### Next gate

Request `LISS-0454 Phase 1 Red 承認`.

## Phase 1 Red result

- Adjudicator approval: `LISS-0454 Phase 1 Red 承認`, received 2026-09-16.
- Added only the focused Red suite
  `tests/test_liss_0454_polynomial_fusion_hardening_red.py`.
- The suite exposes two numeric-closure gaps without changing production code:
  near-zero nonzero coefficients are trimmed from the composed polynomial, and
  non-finite coefficients are accepted into a fused polynomial instead of
  selecting the safe fallback.
- Result: **2 failed**; no implementation or existing assertion was changed.

## Phase 1 Red review result

- Adjudicator approval: `LISS-0454 Phase 1 Red テストレビュー承認`, received
  2026-09-16.
- The two Red tests are accepted unchanged. They isolate coefficient trimming
  and non-finite coefficient acceptance in polynomial composition.
- Review evidence is recorded in
  `docs/collaboration/reviews/2026-09-16-liss-0454-phase1-red-review.md`.
- No implementation permission is inferred from this review.

### Next gate

Request `LISS-0454 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation result

- Adjudicator approval: `LISS-0454 Phase 2 Green / Implementation 承認`,
  received 2026-09-16.
- `_compose_poly` preserves finite nonzero coefficients and rejects
  non-finite inputs or intermediate results before fused projection. The
  additive and multiplicative helpers propagate the fail-closed result.
- The focused suite and existing polynomial-fusion regression suite passed:
  **7 passed**. Active-Red entries were removed after the exact nodes passed.

### Next gate

Request `LISS-0454 Phase 3 Refactor 承認`.

## Phase 3 Refactor result

- Adjudicator approval: `LISS-0454 Phase 3 Refactor 承認`, received
  2026-09-16.
- Exact-zero tail trimming is shared by polynomial composition and addition;
  finite-value validation remains explicit at input and intermediate-result
  boundaries.
- Assertions and behavior were preserved. The focused suite, compile check,
  and lifecycle/document checks all passed.
- Reviewer empathy summary: the numeric closure is now visible in small
  helpers and the safe fallback propagation is explicit at each composition
  boundary, making future changes easier to audit.

### Next gate

Request `LISS-0454 Phase 3 最終レビュー 承認`.

## Phase 3 final review result

- Adjudicator approval: `LISS-0454 Phase 3 最終レビュー 承認`, received
  2026-09-16.
- Final review found no blockers within the approved evaluator-only scope.
- Review Summary: `docs/collaboration/reviews/2026-09-16-liss-0454-phase3-final-review.md`.
- Completion process review: no deviation; status and evidence are synchronized
  in this Issue and WP-0117.
