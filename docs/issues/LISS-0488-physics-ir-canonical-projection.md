# LISS-0488: Physics IR canonical projection migration

| Field | Value |
|---|---|
| Status | **phase-2-green — minimum canonical Physics IR projection passes acceptance tests; awaiting Phase 3 approval** |
| Phase | phase-2-green |
| Parent | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| Related Issue | [LISS-0487](LISS-0487-equation-dto-authority-retirement.md) |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0488-physics-ir-canonical-projection-migration) |
| ADR authority | [ADR 0211](../architecture/adr/0211-scientific-semantic-core-and-ir-authority.md) |
| Architecture approval | Approved by Adjudicator 2026-08-31; ADR 0211 boundary retained |
| Implementation permission | Phase 2 minimum implementation approved; Phase 3 completion not yet approved |
| Next approval | Phase 3 approval for refactor and same-context review |

## Design intake

- Scope: replace Physics IR's implicit HIR/legacy projection authority with a
  compile-owned projection from Scientific Semantic IR.
- Included context: ADR 0211, the consumer-migration Spec, WP-0107,
  LISS-0487, `physics_ir.py`, `physics_ir_lower.py`, and the source-derived
  semantic projection tests.
- Omitted context: provider SDKs, live QPU submission, AWS credentials,
  Rust, S02 numerical lowering, solver implementation, and unrelated
  `symbolic_ir` or evaluator migration.
- Routing: architecture review and deterministic structural/authority tests;
  no external AI or provider is needed.
- Applicable lesson: retained compatibility DTOs must have explicit negative
  authorization metadata; this design treats legacy Physics IR nodes as a
  projection/diagnostic view, never as semantic authority.

## Objective

Make `ScientificSemanticIR` the only source-derived authority for the Physics
projection while preserving a stable, inspectable Physics IR DTO for current
diagnostics and downstream compatibility. The projection must be explicit,
source-backed, deterministic, and fail closed when a semantic node cannot be
represented without loss.

## Current boundary and problem

`lower_hir_to_physics_ir()` currently builds a Physics IR base from HIR and may
append caller-provided `EquationNode` values. LISS-0487 now marks those DTOs as
diagnostic-only, but the base projection still has no explicit compile-owned
Scientific Semantic IR input or node-conservation contract. A caller can
therefore observe a valid Physics DTO without a machine-checkable proof that
its meaning came from the canonical source projection.

## Proposed boundary

```text
CompileResult.scientific_semantic_ir
        │
        ▼
build_physics_projection(semantic_ir, diagnostic_equations=())
        │
        ├─ PhysicsModule canonical projection
        └─ explicit diagnostics for unsupported/lossy nodes
```

- The compile pipeline owns the Scientific Semantic IR object identity.
- Physics IR receives that object explicitly; it does not rebuild meaning from
  AST, HIR, strings, or caller DTOs.
- `EquationNode` may be carried in a separate diagnostic collection or in the
  existing compatibility node tuple, but it never participates in canonical
  node identity, execution authorization, finiteization, or allocation.
- The projection records `semantic_authority=scientific_semantic_ir` and a
  projection version/schema marker. The marker is metadata, not a second
  semantic authority.

## Canonical projection contract

| Scientific Semantic IR concern | Physics IR requirement | Failure policy |
|---|---|---|
| node identity | retain stable source node ID and source origin | reject lossy projection |
| structure/children | preserve ordered child references and operator/equation role | reject omitted required child |
| type and dimensions | retain validated references without coercion | explicit diagnostic, no module artifact |
| exactness and intent | preserve symbolic/exact versus finite intent | never infer finiteization |
| role/lane | preserve state, operator, relation, observation, and realization role | reject illegal role transition |
| provenance | retain source file/span and canonical source ancestry | no source-less canonical node |
| Equation DTO | diagnostic-only compatibility view | never authorize execution |

The projection must be pure for the same semantic IR snapshot and must not
perform parsing, evaluation, numerical solving, allocation, provider calls, or
automatic `Realize` conversion.

## Acceptance scenarios for Phase 1 Red

1. Given a compile-owned Scientific Semantic IR, when the Physics projection is
   built, then its canonical node IDs, roles, structure, dimensions, exactness,
   intent, and provenance match the source-derived nodes.
2. Given a caller-created HIR/Equation DTO that is not the compile-owned
   semantic IR, when it is supplied as a projection authority, then the API
   rejects it or treats it only as diagnostic input and emits no canonical
   execution artifact.
3. Given an unsupported or lossy semantic node, when projection is requested,
   then a named diagnostic is returned and no partial Physics module is
   published.
4. Given an exact or symbolic semantic node without source-visible `Realize`,
   when projection is requested, then no finite plan, gate sequence, or
   allocation is created.
5. Given a diagnostic Equation DTO, when the projected module is inspected,
   then its explicit diagnostic-only metadata remains false for execution and
   finiteization authorization.
6. Given the same semantic snapshot twice, when projected twice, then the
   canonical projection has equal identity/fingerprint and no duplicated
   semantic build occurs.

## Phase split and allowed files

- Phase 1 Red: add only the named acceptance tests, minimal semantic fixtures,
  and this Issue/spec/WP evidence. No production migration or deletion.
- Phase 2 Green: add the smallest explicit projection API and compile-owned
  wiring; preserve existing diagnostic compatibility only where tests prove it.
- Phase 3: remove the old HIR-authority path after no-bypass and unchanged-
  neighbor evidence; update documentation and review records.

Initial Phase 1 candidate files:

- `tests/test_liss_0488_physics_ir_canonical_projection_red.py`
- `tests/fixtures/semantic_consumer_migration/` only for a minimal source case
- this Issue and the linked Spec/WP records

Production files are not authorized until Phase 1 Red is reviewed and Phase 2
implementation approval is granted.

## Non-goals and stop conditions

This Issue does not change Physics IR DTO shape beyond the explicit projection
contract, does not implement a solver or numerical backend, and does not
remove the `physics_equation` module. It does not authorize QPU/provider/AWS,
Rust, or live hardware work. Stop for a new ADR if the projection requires a
new language semantic role, public API compatibility promise, storage schema,
or external execution boundary.

## Architecture approval request

Approve or reject the proposed compile-owned Scientific Semantic IR → Physics
IR projection boundary, the conservation/fail-closed contract, and the
diagnostic-only Equation DTO compatibility rule. Approval does not authorize
Phase 1 tests, Phase 2 implementation, or Phase 3 cleanup.

## Architecture approval result

- The compile-owned Scientific Semantic IR → Physics IR projection boundary is
  accepted for this Issue.
- The conservation, deterministic projection, and fail-closed contract is
  accepted as the Phase 1 acceptance target.
- Equation DTOs remain diagnostic-only and cannot authorize semantic execution,
  finiteization, allocation, or provider artifacts.
- No new ADR, technology selection, provider boundary, or implementation
  permission is created by this approval.

## Phase 1 Red readiness

The exact Phase 1 candidate is fixed to
`tests/test_liss_0488_physics_ir_canonical_projection_red.py` and the minimal
source fixture named in this Issue. The test batch contains the six acceptance
scenarios above and changes no production code. Phase 1 Red approval was
granted before creation.

## Phase 1 Red result

- Added `tests/test_liss_0488_physics_ir_canonical_projection_red.py` with the
  six approved acceptance scenarios.
- Added the minimal source fixture
  `tests/fixtures/semantic_consumer_migration/physics_ir_projection.sqx`.
- Red verification: **6 failed**, all at the missing canonical
  `build_physics_projection` contract; no collection errors.
- The lossy-projection scenario uses an incomplete Semantic IR (`nodes=()`),
  so successful projection and fail-closed rejection are tested with distinct
  inputs.
- No production code, legacy fallback, or DTO implementation was changed.
- Phase 2 Green must add only the minimum compile-owned projection API needed
  to satisfy the reviewed tests.

## Phase 2 Green result

- Added `build_physics_projection()` and the immutable `PhysicsProjection`
  result DTO in `compiler/staqex/physics_ir_lower.py`.
- The projection validates `ScientificSemanticIR` type and optional
  compile-owned identity, preserves canonical node IDs and source provenance,
  and emits explicit authority/schema metadata.
- Incomplete semantic input returns no Physics module and the named
  `PHYSICS_PROJECTION_LOSSY` diagnostic. No finite plan or allocation is
  created by this API.
- Verification: related LISS-0488/LISS-0487/LISS-0445 tests **21 passed**;
  Spec verification **161/161**; `py_compile` and `git diff --check` passed.
- No provider, QPU submission, AWS, Rust, solver, or automatic finiteization
  behavior was added.
