# ADR 0224: POVM rejection-evidence projection boundary

## Status

Accepted — Adjudicator approved `ADR 0224 Architecture / LISS-0556 Phase 0
acceptance 承認` on 2026-09-14.

## Context

The accepted LISS-0485 bridge contract requires explicit evidence when a
POVM observation is rejected. The active-Red regression test currently reaches
the expected `POVM_DOMAIN_MISMATCH` compile failure, but then cannot inspect
the rejection because `CompileResult.povm_observation_rejections` is absent.
The measurement resolver already creates a diagnostic containing the code,
source span, requested effect-set identity, and source state domain.

The missing surface is a result-projection regression, not a request to add
general POVM mathematics. The compiler must continue to reject a domain
mismatch and must not turn rejection evidence into a measurement result.

## Dependency Adoption Evidence

Not applicable. This decision selects no dependency, provider, framework, or
runtime service.

## Decision

Phase 2 restores `CompileResult.povm_observation_rejections` as a collection
of rejection records derived from the canonical compiler diagnostics. For each
POVM rejection, the record contains:

- `code`, `line`, `col`, and `message` from the diagnostic;
- `requested_effect_set` and `state_domain` when present on the diagnostic;
- `repaired: False`; and
- `fabricated_outcome: False`.

The collection is result evidence only. It does not contain an outcome,
post-state, finite target, provider artifact, effect matrix, or numerical
validity result. Existing diagnostic ordering and `compiled.ok` semantics are
preserved. Valid computational-basis measurement remains unchanged.

The projection belongs at the compiler `CompileResult` boundary. POVM
resolution remains responsible for producing the diagnostic; adapters,
providers, QPU targets, and runtime execution do not gain business logic.

## Consequences

Positive:

- Callers can distinguish an intentional POVM rejection from a missing or
  fabricated result without reparsing diagnostics.
- The accepted LISS-0485 rejection contract is observable at the public local
  compile boundary.
- The implementation remains provider-neutral and does not imply POVM
  numerical support.

Negative:

- The result exposes a small diagnostic-shaped compatibility surface that must
  remain synchronized with the canonical diagnostic contract.
- General effect validation, sampling, and execution remain unavailable and
  require separate reviewed work.

## Enforcement

Code review should reject:

- repairing a domain mismatch or changing its diagnostic code to make the
  result compile;
- adding sampled outcomes, post-states, finite targets, provider artifacts,
  or effect-matrix calculations to a rejection record;
- constructing rejection records in an adapter or provider; and
- changing valid computational-basis behavior as part of this regression fix.

## Approval boundary

This ADR records Architecture approval and LISS-0556 Phase 0 acceptance. Phase
1 Red, Phase 2 implementation, and Phase 3 review require separate typed
approvals.
