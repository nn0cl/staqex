# ADR 0227: Legacy `when` binding module boundary

## Status

Accepted — Adjudicator approved the `Architecture approval` on 2026-09-27.

## Context

The evaluator facade still owns the AST implementation of `_bind_when` and
its control-mass/pattern helpers. Canonical `control_mixture` execution uses
the deferred State/Measure executor when the complete main body is eligible.
When that eligibility check fails, the canonical control-mixture executor
explicitly falls back to `_run_legacy_ast_body`; its binder dispatcher reaches
`Evaluator._bind_when`. The old body is therefore still reachable from a
canonical entrypoint and cannot be retired based only on canonical happy-path
tests.

## Decision

Keep the existing legacy AST control-mixture behavior and extract its
implementation from `runtime/evaluator.py` into a clearly named
`runtime/evaluation/legacy_control_binding.py` module. The successor owns the
branch-control mass resolution, pattern matching, and state transformation
algorithm. `Evaluator` remains the sole owner of mutable runtime state and
provides the live values/callbacks required by the successor. The existing
private `_bind_when` entrypoint remains as compatibility wiring for the binder
dispatcher; this is a structural split only.

Do not retire the legacy path or alter canonical eligibility/fallback,
language meaning, collapse, normalization, or diagnostics in this work.

## Consequences

Positive:

- The Evaluator facade loses a cohesive implementation body without creating
  a second state owner.
- The module name distinguishes fallback AST mechanics from canonical plan
  orchestration.
- The required fallback can be tested independently from canonical fast-path
  behavior.

Negative:

- A private compatibility callback remains until all actual consumers are
  separately inventoried and a retirement decision is approved.
- The structural size reduction is bounded; this ADR does not claim to solve
  the broader large-file problem.

## Enforcement

Code review should reject:

- retiring the callback without proving and approving that the canonical
  fallback no longer reaches it;
- copying evaluator-owned mutable maps or constructing another Evaluator;
- changing branch, amplitude, phase, coalescing, or diagnostic behavior as
  part of this extraction;
- a structural test that checks only forwarding text instead of successor
  ownership, facade-body absence, exact compatibility installation, and live
  callable identity.

## Follow-up

- [LISS-0580](../../issues/LISS-0580-legacy-when-binding-extraction.md) and
  [WP-0173](../../work-plans/WP-0173-legacy-when-binding-extraction.md) define
  the proposed Phase 0 acceptance and subsequent structural work.
- This ADR accepts the module boundary only. Phase 0 acceptance, Phase 1 Red,
  implementation, and refactor remain separate approval gates.
