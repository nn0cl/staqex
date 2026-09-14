# ADR 0223: Interfer canonical-meaning selector boundary

## Status

Accepted — Adjudicator approved `ADR 0223 Architecture / LISS-0555 Phase 0
acceptance 承認` on 2026-09-14.

## Context

The active-Red interfer tests select `kind == "Call"`, an AST-era shape. The
current parser and canonical Scientific Semantic IR represent the construct as
`InterferenceExpr`. The canonical node already preserves coherent meaning,
operand identity, relative-phase metadata, branch relationship, provenance,
and relation membership. Keeping the old selector misclassifies a healthy
canonical representation as a missing feature.

## Decision

Interfer consumers and acceptance tests select the canonical node by
`meaning_kind == "interference"`, not by parser or AST node kind. The
canonical meaning contract requires:

- `state_role == "interference_state"` and `intent == "interference"`;
- exactly the accepted operand lineage and source node IDs;
- relative-phase metadata and coherent branch relationship;
- an interference relation containing the canonical node; and
- explicit fail-closed behavior for unsupported finite QPU projection.

`INTERFER_INDEPENDENT_STATE_ERROR` remains a semantic diagnostic when the
fixture violates shared coherent history. It must not be hidden by changing
the selector, and it does not authorize classical-mixture or unitary fallback.

## Consequences

- The two stale active-Red selectors can be corrected without production code.
- Canonical meaning remains independent from syntax representation.
- Unsupported interfer projection remains atomic and produces no QPU artifact.
- New coherent execution or finite synthesis requires a separate reviewed
  contract; LISS-0555 does not add it.

## Approval boundary

This ADR records Architecture approval and LISS-0555 Phase 0 acceptance.
Phase 1 Red, Phase 2 Green, and Phase 3 require separate typed approvals.
