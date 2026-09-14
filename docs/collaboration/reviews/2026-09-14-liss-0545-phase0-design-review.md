# LISS-0545 Phase 0 Design Review

- Date: 2026-09-14
- Scope: evaluator domain-family decomposition
- Path: Feature Path, Phase 0 design
- Review isolation: `same_context` (per runtime routing)
- Approval received: `LISS-0545 Phase 0 acceptance 承認`

## Review basis

This design was checked against WP-0160, the accepted core-module-decomposition
specification, LISS-0544's completed orchestration boundary, the current
`runtime/evaluator.py` method inventory, project conventions, and the process
lessons log.

## Accepted design

The remaining evaluator responsibilities are divided into four meaningful
families: values, operators, evolution, and calls. The public `Evaluator`
facade and its mutable state remain in place. The extraction uses explicit
callbacks/protocols and does not introduce a generic helper module, provider
dependency, or second semantic authority.

The 491-line `_bind_call` is divided by call family and binding mechanics. The
Hamiltonian one-step implementation remains an evolution concern and may call
operator resolution through a narrow callback. Extraction order is values,
operators, evolution, then calls, with separate phase gates for every unit.

## Acceptance and risk boundaries

- Preserve fixed-seed RNG order, Joint coordinate order, numerical exactness,
  units, approximation obligations, diagnostic order, and public imports.
- Do not repair unrelated active-Red failures or alter language semantics.
- Do not move measurement, dynamic-lane, or deferred stateful bodies into this
  issue; those are existing LISS-0544 follow-up seams.
- Return to Architecture review if public DTOs, ports, dependencies, or
  semantic authority must change. Return to Feature Path if characterization
  exposes a behavior defect.

## Reviewer empathy summary

A maintainer can identify where a value, operator, evolution, or call behavior
belongs without following an arbitrary utility layer. The plan preserves one
state owner and makes the two highest-risk boundaries—call dispatch and
Hamiltonian stepping—explicit enough to test independently.

## Next approval required

`LISS-0545 Phase 1 Red 承認`
