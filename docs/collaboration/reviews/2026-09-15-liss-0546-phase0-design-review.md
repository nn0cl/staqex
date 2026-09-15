# LISS-0546 Phase 0 Design Review

- Date: 2026-09-15
- Scope: TypeChecker family decomposition
- Path: Feature Path, Phase 0 design
- Review isolation: `same_context` (per runtime routing)
- Approval received: `LISS-0546 Phase 0 acceptance 承認`

## Review basis

The design was checked against WP-0160, the accepted core decomposition
specification, project conventions, implementation readiness, testing strategy,
the current TypeChecker method/state inventory, and the process lessons log.

## Accepted design

The approximately 4,668-line checker is divided into context, declarations,
operators, dimensions, inference, and evolution. `TypeChecker` remains the
public facade and sole mutable environment/diagnostic owner. Each unit receives
explicit callbacks or a narrow `TypeCheckContext`; no unit copies environment,
metadata, or diagnostics.

`check_unit()` retains sequencing and delegates family work. Scoped environment
changes must restore prior state. Operator, dimension, inference, and evolution
boundaries are explicit and do not alter semantic authority or language
behavior.

## Acceptance and risk boundaries

- Preserve inferred `Ty`, dimensions, effects, AST annotations, diagnostic code,
  span, ordering, and public imports.
- Do not fix unrelated type behavior, parser behavior, or active-Red failures.
- Do not add dependencies, ports, provider code, or generic utility modules.
- Return to Architecture review if public DTOs, state ownership, or dependency
  direction must change. Return to Feature Path if characterization finds a
  semantic defect.

## Reviewer empathy summary

A maintainer can locate declaration, operator, dimension, inference, and
evolution rules without searching an undifferentiated checker. The design also
makes environment mutation and diagnostic ownership visible, which are the two
main risks of splitting TypeChecker.

## Next approval required

`LISS-0546 Phase 1 Red 承認`
