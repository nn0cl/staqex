# LISS-0437 Phase 3 design re-review

## Review status

Initial review: **NOT READY**. Four P1 findings were raised and addressed in
the acceptance Spec, ADR 0209, WorkPlan, and Phase 3 design trace.

## Resolutions

- Binder-aware QPU now has a closed capability witness: binder kind/domain,
  bound symbols, acting register, operator family, and register mapping.
- A target-neutral provenance envelope now requires source span, source
  transform, state shape, realization kind/policy, approximation fields,
  error budget, resource estimate, and capability rejection.
- S02 source/compiler completion is explicitly separated from numerical
  migration; fixed-seed distribution and benchmark comparison are required.
- Limit, binder, and resource-budget rejection scenarios now require
  allocation-before-rejection safety and prohibit hidden rewrites.

## Final independent re-review

The fresh review returned **READY**. Binder capability witness, typed
`AST → EvolutionIR → TargetPlan → Circuit | TargetRejection` provenance,
allocation-before-rejection safety, Limit/S02 boundaries, and implementation
approval separation are closed.

## Remaining gates

No Phase 3 Red test, production implementation, QPU implementation, or S02
numerical migration is authorized by this design review. Each workstream still
requires its own explicit Phase 3 Red approval; implementation requires a
separate Phase 3 implementation approval. A finite realization of `Limit`
requires a separate Architecture decision.
