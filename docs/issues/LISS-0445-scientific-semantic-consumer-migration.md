# LISS-0445: Scientific Semantic Consumer-Wide Migration

| Field | Value |
|---|---|
| Status/phase | **done — bounded binder canonical-projection slice complete; LISS-0446 and LISS-0503 remain separate boundaries** |
| WorkPlan | [WP-0108](../work-plans/WP-0108-scientific-semantic-consumer-migration.md) |
| Specification | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md) |
| Parent design | [LISS-0444](LISS-0444-scientific-semantic-core.md) / [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| ADR authority | [ADR 0211](../architecture/adr/0211-scientific-semantic-core-and-ir-authority.md) |
| Approval status | Scope/design, Phase 1 Red, Phase 2 Green, and binder-slice implementation approved; follow-up boundaries remain separately gated |

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

The approved bounded binder slice is complete. The canonical projection is
compile-owned and is reused by pipeline, diagnostics, QPU, and direct QASM
consumers without a hidden rebuild or cache. The former excluded Red cases
have been separated into their own boundaries: public QASM facade ownership is
tracked by LISS-0446, and unsupported explicit-evolution QASM rejection is
closed by LISS-0503.

Same-context review re-read this Issue, WP-0108, the migration specification,
the binder implementation, the fixed Red suite, and the follow-up records.
No blocking finding remains within the approved slice. Isolation was
`same_context`, which is weaker than `separate_context`.

Verification: `./.venv/bin/pytest -q
tests/test_liss_0445_consumer_migration_red.py` — **12 passed**;
`git diff --check` passed.

Reviewer empathy summary: the canonical binder ownership boundary is explicit
at the compile result and consumer call sites, while future public-facade and
unsupported-realization work remains visibly separate.

Process review: no operating-contract deviation or operational problem found.

Issue complete for the approved bounded binder slice. No implementation
approval is implied for LISS-0446 or other follow-up families.
