# LISS-0445: Scientific Semantic Consumer-Wide Migration

| Field | Value |
|---|---|
| Status/phase | **done — binder canonical-projection slice complete; LISS-0446 parked** |
| WorkPlan | [WP-0108](../work-plans/WP-0108-scientific-semantic-consumer-migration.md) |
| Specification | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md) |
| Parent design | [LISS-0444](LISS-0444-scientific-semantic-core.md) / [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| ADR authority | [ADR 0211](../architecture/adr/0211-scientific-semantic-core-and-ir-authority.md) |
| Approval status | Scope/design, Phase 1 Red, Phase 2 Green, and binder-slice implementation approved; LISS-0446 not approved for implementation |

## Objective

Complete the next bounded migration slice so downstream consumers use the
source-derived Scientific Semantic IR as their semantic authority, while
preserving the distinction between exact/symbolic simulation and explicit
finite `Realize` projection.

## In scope

- migrate the remaining QASM finite compatibility path where canonical
  projection coverage is already available;
- define and test retirement of duplicated AST binder diagnostic lowering;
- migrate or replace the non-explicit `symbolic_ir` consumer path behind a
  canonical inspection projection;
- classify every remaining AST/DTO consumer as migrate, replace, retire, or
  explicitly defer, with owner and exit evidence;
- preserve source node identity, structure, provenance, role, dimensions,
  exactness, state safety, terminal measurement, and realization policy;
- the approved binder slice covers direct `QASM3Emitter.emit_unit(...,
  semantic_ir=...)` calls; public convenience QASM facades that compile from a
  `CompilationUnit` without retaining `CompileResult.scientific_semantic_ir`
  are deferred to a follow-up QASM-entry migration Issue;
- add Red tests and acceptance fixtures only after the independent design
  review accepts this specification.
- the initial Red file and fixture directory are fixed by WP-0108 so the
  phase cannot expand through an ambiguous `tests/` allowance.

## Explicit exclusions

- no provider SDK, credentials, network, or live QPU submission;
- no S02 numerical migration;
- no solver, automatic integration, or automatic differentiation;
- no implicit finiteization or direct `Limit` target lowering;
- no broad example rewrite unrelated to consumer authority;
- no deletion of a legacy path until a replacement projection and rollback
  evidence exist.

## Boundary and approval gates

This Issue does not authorize implementation. Phase 1 Red must name the exact
tests and allowed files. Phase 2 Green requires a separate typed approval.
Consumer-wide fallback retirement may be split into later phases if the
current acceptance specification cannot prove safe replacement.

## Exit conditions

- independently reviewed Spec and WP;
- Phase 1 Red tests fail for the intended missing migration, without changing
  production code;
- each targeted consumer has canonical source identity and provenance tests;
- unsupported or unresolved meaning produces no executable artifact;
- full regression and independent post-Green review pass;
- WP-0107/open-work register/Issue status agree on completed and deferred work.

## Completion review

- Completion review: [2026-08-29 completion review](../collaboration/reviews/2026-08-29-liss-0445-completion-review.md)
- Independent review: [2026-08-24 Phase 3 review](../collaboration/reviews/2026-08-24-liss-0445-phase3-review-02.md)
- Result: accepted for the bounded binder canonical-projection slice.
- LISS-0446 Public QASM facade ownership remains parked and is not included.
- Process review: no operating-contract deviation or operational problem found.
