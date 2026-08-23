# Staqex Residual Semantic Consumer Reconciliation Specification

| Field | Value |
|---|---|
| Status | **Phase 3 Refactor final-review-ready** |
| Issue | [LISS-0447](../issues/LISS-0447-residual-semantic-consumer-reconciliation.md) |
| WorkPlan | [WP-0110](../work-plans/WP-0110-residual-semantic-consumer-reconciliation.md) |
| Authority | [ADR 0211](../architecture/adr/0211-scientific-semantic-core-and-ir-authority.md) |

## [DESIGN CHECK]

- **Scope:** reconcile AlgorithmPlan, H1 delivery, and ordinary QASM fallback
  contracts identified by LISS-0445 regression.
- **Inspected:** LISS-0445/LISS-0446 artifacts, `algorithm_plan_ir.py`,
  `scientific_semantic_ir.py`, `pipeline.py`, `h1_authoring.py`, QASM emitter,
  focused tests, and full regression results.
- **Authority:** Scientific Semantic IR remains the source-derived semantic
  authority; each consumer receives an explicit projection.
- **Boundaries:** no syntax, ADR 0211, State/Measure, Realize/Limit, provider,
  S02, or solver changes.
- **Review lenses:** canonical authority, projection conservation, consumer
  ownership, H1/source boundary, QASM fallback retirement, fail-closed
  behavior, migration safety, and phase discipline.

## Normative requirements

1. AlgorithmPlan has one executable consumer projection; the temporary
   `scientific_semantic_ir.AlgorithmPlan` cannot be passed to a module API that
   requires `AlgorithmPlanModule` fields.
2. H1 compilation must either produce the canonical semantic result or reject
   through an explicitly documented H1 boundary; it may not silently return a
   parallel semantic authority.
3. Ordinary QASM canonical inputs must not call the AST fallback. Inputs not
   covered by canonical projection must reject with no QASM, gates, allocation,
   or partial program.
4. Source node identity, provenance, role, dimensions, exactness, intent, and
   explicit realization policy remain observable at each projection.
5. Each subcontract has independent Red, Green, and review evidence.

## Subcontract contracts

### AlgorithmPlan projection

The canonical source is `CompileResult.scientific_semantic_ir`. The planned
consumer projection must map fields as follows, or reject atomically:

The canonical IR must explicitly own `realize_source_node_id` and a typed
`finite_realization_record` (or an explicit `None`), rather than asking a
consumer to infer them from `nodes`. The builder derives the identity from the
single source `Realize` call that owns the finite policy; multiple or missing
owners are canonical-projection errors. The finite record owns method, order,
steps, error budget, and source/provenance references. It is created by the
Scientific Semantic IR builder and is not reconstructed by AlgorithmPlan.
Missing owner, multiple owners, and missing finite record all use the exact
code `E_ALGORITHM_PLAN_CANONICAL_PROVENANCE` with a deterministic `reason`
detail (`missing_realize_owner`, `multiple_realize_owners`, or
`missing_finite_realization_record`).

| Consumer field | Canonical source | Missing-data behavior |
|---|---|---|
| `plan_id` | `ScientificSemanticIR.realize_source_node_id` | `E_ALGORITHM_PLAN_CANONICAL_PROVENANCE` |
| `PlanNode.semantic_id` / `origin.source_id` | canonical node ID and provenance | same rejection; no plan |
| `exactness`, `operation_kind` | canonical node exactness/kind | same rejection; no plan |
| `decisions`, `obligations`, `resources` | `finite_realization_record` and explicit `lowering_policy` | same rejection; no finite plan |
| `witnesses` | declared consumer witness set from the canonical projection | same rejection; unknown consumer rejected |

The projection must preserve the canonical object identity and must never
construct a second executable plan authority. A mismatched plan/projection
pair is rejected before gates, allocation, or resource materialization.

### H1 delivery

H1 compilation will retain H1-specific `physics_ir`, `quantum_semantic_ir`,
and state-transform data as diagnostic/authoring projections, but will also
produce the canonical `ScientificSemanticIR` for the same parsed unit. H1
must not return a `CompileResult` with a missing canonical authority while
exposing parallel executable meaning. If canonical construction fails, the
result carries an explicit H1 diagnostic and no executable artifact.

### Ordinary QASM fallback decision table

| Emitter branch | LISS-0447 disposition | Required result |
|---|---|---|
| canonical ordinary gate projection | retire AST fallback | canonical QASM, unchanged gate text, no AST lowerer call |
| finite Suzuki/binder compatibility projection | retain temporarily | canonical policy validation plus existing compatibility lowering |
| unresolved evolution | retain fail-closed rejection | explicit rejection, empty artifact envelope |
| unsupported ordinary input | no fallback | explicit capability rejection, empty artifact envelope |

The ordinary fixture is evidence for the first row, not a claim that every
fallback branch is retired.

## Phase boundaries

- **Phase 1 Red:** fixed tests and fixtures only for the three subcontracts.
- **Phase 2 Green:** one approved subcontract at a time; no deletion beyond
  that subcontract.
- **Phase 3 Refactor:** remove obsolete representations only after replacement,
  no-bypass, rollback, and full-regression evidence.

## Acceptance matrix

| Subcontract | Red evidence | Green exit |
|---|---|---|
| AlgorithmPlan | projection accepts compile-owned plan and rejects mismatched authority | one module/projection contract, source identity and policy preserved |
| H1 delivery | H1 compile result exposes canonical authority or explicit documented rejection | no early return bypass; H1 diagnostics remain intact |
| Ordinary QASM | fixed fixture fails if AST lowerer is called | canonical QASM output unchanged; unsupported path is artifact-free rejection |

For every rejection row, Red/Green tests assert `reject_code`, empty QASM,
empty gates/instructions, `allocation_started is False`, empty
`allocated_qubits`, and `partial_program is None`.

## Fixed Phase 1 Red cases

- `test_algorithm_plan_projection_preserves_canonical_fields`
- `test_algorithm_plan_projection_rejects_mismatched_or_incomplete_authority`
- `test_algorithm_plan_projection_rejects_mismatched_pair`
- `test_algorithm_plan_rejects_multiple_realize_owners`
- `test_algorithm_plan_rejects_missing_finite_record`
- `test_h1_compile_exposes_canonical_semantic_ir`
- `test_h1_diagnostics_remain_without_parallel_executable_authority`
- `test_ordinary_qasm_canonical_fixture_never_calls_ast_fallback`
- `test_ordinary_qasm_unsupported_input_rejects_atomically`

Phase 1 Red creates these fixture/source inputs:

- `tests/fixtures/residual_semantic_consumers/explicit_realize_plan.sqx`:
  exactly one explicit `Realize` with method/order/steps/error budget;
- `tests/fixtures/residual_semantic_consumers/missing_realize_policy.sqx`:
  finite consumer request without a canonical finite realization record;
- `tests/fixtures/residual_semantic_consumers/h1_canonical_dispatch.sqx`:
  H1 theory/experiment with terminal `Measure`;
- `tests/fixtures/semantic_consumer_migration/ordinary_gate.sqx`:
  canonical ordinary gate fixture already used by LISS-0445;
- inline unsupported ordinary-QASM source with an unresolved operator to
  exercise the atomic rejection envelope.

## Non-goals

Provider SDKs, live QPU, S02 numerical work, solver integration, dynamic QPU,
CH0, and broad fallback retirement remain outside this specification.
