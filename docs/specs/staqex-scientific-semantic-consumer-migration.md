# Staqex Scientific Semantic Consumer Migration Specification

| Field | Value |
|---|---|
| Status | **Accepted — Phase 2 Green binder slice complete; LISS-0446 follow-up parked** |
| Issue | [LISS-0445](../issues/LISS-0445-scientific-semantic-consumer-migration.md) |
| WorkPlan | [WP-0108](../work-plans/WP-0108-scientific-semantic-consumer-migration.md) |
| Parent authority | [Scientific Semantic Core](staqex-scientific-semantic-core.md), [ADR 0211](../architecture/adr/0211-scientific-semantic-core-and-ir-authority.md) |

## [DESIGN CHECK]

- **Scope and expected behavior:** migrate remaining bounded consumers from
  AST/DTO semantic authority to source-derived Scientific Semantic IR.
- **Inspected context:** WP-0107, LISS-0444, ADR 0211, open-work register,
  QASM emitter/QPU IR, symbolic/quantum semantic paths, binder lowering,
  implementation-readiness rules, and independent-review perspectives.
- **Component boundary:** front end produces source structure; Scientific
  Semantic IR owns meaning; simulator/inspection and finite-target consumers
  consume explicit projections; provider ports remain outside the Kernel.
- **Applicable constraints:** physicist-first source fidelity, Never Leave the
  State, terminal `measure`, explicit `Realize`, fail-closed rejection, and no
  hidden classicalization or finiteization.
- **Decisions:** ADR 0211 remains authoritative. This Spec does not select a
  new technology or alter language syntax.
- **Unresolved boundaries:** a consumer remains deferred when canonical
  structural/provenance preservation cannot yet be proven; fallback removal
  is not inferred from passing output-only tests.
- **Review lenses:** canonical authority, source fidelity, boundary integrity,
  realization/fail-closed behavior, projection conservation, migration safety,
  evidence hygiene, and phase discipline.
- **Verification:** Phase 1 Red contract tests, consumer-specific provenance
  tests, negative no-artifact tests, unchanged-neighbor regression, and an
  independent post-Green review.

## Normative requirements

1. A consumer may not derive executable semantic meaning directly from AST,
   caller DTOs, string equations, or soft diagnostics when a canonical
   Scientific Semantic IR projection is required.
2. Every migrated projection must preserve source node identity, structural
   children, role/lane, type, dimensions, exactness, intent, and provenance,
   or reject with an explicit lossy-projection diagnostic.
3. Exact/symbolic inspection must not allocate a finite target or choose gate
   steps. Finite target creation requires source-visible `Realize` policy.
4. Unresolved canonical meaning, unsupported capability, and resource failure
   must produce no executable artifact, allocation record, or fabricated
   result.
5. Compatibility paths may remain only when their owner, scope, diagnostic,
   exit condition, and retirement evidence are recorded.
6. A passing output snapshot alone is insufficient evidence of migration;
   tests must demonstrate canonical authority and negative legacy bypass.

## Planned migration matrix

| Consumer | Proposed disposition | Phase 1 Red evidence | Exit condition |
|---|---|---|---|
| QASM finite compatibility fallback | migrate/retire where canonical finite projection exists | fallback invocation and canonical-source tests | finite supported inputs never call AST lowerer; unsupported inputs reject honestly |
| public QASM convenience facades | defer | entry-point inventory and explicit boundary record | follow-up Issue passes compile-owned semantic IR through every public facade |
| diagnostic binder re-lowering | replace with canonical binder projection | monkeypatch/authority test | diagnostics consume canonical binder data only |
| non-explicit `symbolic_ir` | migrate to canonical inspection projection | parallel-authority and structure tests | symbolic inspection has canonical identity and no finiteization |
| remaining AST/DTO paths | classify individually | inventory completeness test | each path is migrate, replace, retire, or deferred with owner |

### Complete consumer inventory

| Path | Current consumer/owner | Disposition | Planned phase | Exit or deferral proof |
|---|---|---|---|---|
| `physics_ir` | `lower_hir_to_physics_ir` legacy projection / semantic-core owner | replace | Red, then representative Green | canonical node/provenance equivalence; diagnostic-only rollback |
| `physics_equation` / `EquationNode` | module-local verifier and caller-injected API | retire as authority | Red | separate caller-injection negative test and diagnostic-only rollback |
| `OpExpr` operator tree | parser/runtime operator carrier | migrate as front-end structure | Green | canonical children and operator identity preserved |
| `EquationNode` | tests/tools and caller-injected APIs | retire as authority | Red | caller-only values cannot authorize consumers |
| HIR | parser/type front end | migrate as input | Green prerequisite | source structure and spans survive |
| `quantum_semantic_ir` | quantum semantic consumer | migrate downstream | Green | canonical source IDs and state invariants |
| `symbolic_ir` | simulator/inspection compatibility | replace | Green/Refactor | canonical inspection, no allocation, deletion proof |
| evaluator AST dispatch | runtime evaluator | migrate behind boundary | later Green | State<T>, terminal measure, no early collapse |
| QASM AST/source lowering | QASM backend | migrate covered finite cases; defer unsupported | Green/Refactor | Realize-visible, no fallback for covered cases |
| `qpu_ir` source-AST DAG | QPU target projection | replace independent authority | Green | canonical instruction consistency |
| `algorithm_plan_ir.AlgorithmPlanModule` | stable finite-plan verifier | migrate downstream | Green/Refactor | explicit Realize policy/source identity; preserve verifier contract |
| `scientific_semantic_ir.AlgorithmPlan` | temporary canonical realization DTO | replace with one plan projection | Green | no two plan authorities; one compile-owned projection |
| finite binder lowering | binder/math and QPU consumers | migrate canonical binder projection | Green | one binder projection for diagnostics/execution |
| H1/synthetic authoring | examples/tools | retire authority | Red | diagnostics-only negative test |
| H1 compiler early-return | pipeline delivery shortcut | replace with canonical dispatch | Green | no early return bypasses semantic projection |
| continuous numerical adapter | `continuous_lowering.py` / `GridHamiltonian` | defer | separate Issue | explicit scope-boundary record |
| live submit | `QpuSubmitPort` / host provider | defer | separate Issue | separate port/technology approval |

### LISS-0486 evaluator semantic-authority migration

The runtime evaluator remains a downstream execution consumer, not a second
semantic authority. This slice defines the boundary for passing the
compile-owned `ScientificSemanticIR` into evaluator setup and for proving that
AST dispatch retains only operational structure. State values remain
`State<T>`, terminal `measure` remains the sole collapse boundary, and
unsupported meaning produces no fabricated runtime result.

Phase 1 must cover compile-owned IR identity, AST mutation/caller-injected
projection rejection, terminal measurement provenance, and no early collapse.
Phase 2 may add only the minimum evaluator entry boundary. Provider/QPU,
automatic finiteization, solver changes, and numerical semantic changes are
excluded.

Physics and Equation paths are tracked separately: `physics_ir` is the legacy
projection path, while `EquationNode` is the caller-injected/string-capable
path. They require separate no-authority tests and separate rollback proofs.

### Binder diagnostic boundary

`build_scientific_semantic_ir(unit)` may perform the single canonical binder
projection build owned by Scientific Semantic IR. After that boundary,
`qpu_ir_diagnostics()`, QASM diagnostics, and other consumers may read
`binder_lowering`, `binder_source_node_ids`, and `binder_provenance`, but may
not call `lower_finite_binders()` or `lower_finite_binder_operators()` again.
Phase 1 Red must monkeypatch both lowerer symbols at their defining and
importing modules, exercise diagnostics and QPU projection, and assert one
canonical build per `CompileResult` plus no diagnostic-side rebuild. The
`CompileResult.scientific_semantic_ir` object is the shared identity; consumers
must not reconstruct it. A failed call-count, object-identity, or authority
test blocks Green.

### Atomic rejection matrix

| Consumer | Rejection signal | Must be empty/absent |
|---|---|---|
| QASM | explicit capability/projection diagnostic | `qasm == ""`, `circuit.gates == []`, allocation absent |
| QPU IR | canonical projection diagnostic | `instructions == ()`, no allocation |
| Algorithm Plan | unresolved/unsupported realization diagnostic | `algorithm_plan is None`, steps/gates/allocation absent |
| symbolic inspection | unresolved semantic diagnostic | fixed empty/None symbolic result, no allocation |
| simulator/evaluator | state/measurement diagnostic | result absent, no fabricated value or early collapse |

The diagnostic code and empty fields must be asserted together; `None`, empty
tuple/list, and absent field are distinct contract choices and must be fixed by
the consumer's acceptance test.

### QASM fallback boundary

| Case | Policy in this Issue | Owner | Exit evidence |
|---|---|---|---|
| covered finite Suzuki/binder | no AST fallback | QPU/QASM | canonical instruction and no-call tests |
| unsupported finite operator | capability rejection or separately approved compatibility | QPU/QASM | diagnostic and no-artifact test |
| non-explicit exact/symbolic inspection | no finite QASM | simulator | no allocation and no hidden Realize test |
| ordinary legacy gate path | temporary compatibility only | QASM | owner, diagnostic, retirement milestone |
| provider/live QPU | excluded | host/provider | separate Issue and port approval |

The ordinary legacy gate path has a concrete exit milestone: it remains only
through the first approved Green slice that proves canonical projection for
the fixed fixture `tests/fixtures/semantic_consumer_migration/ordinary_gate.sqx`,
then a Refactor phase must remove the fallback and
retain an explicit unsupported-capability rejection for uncovered inputs.
The migration owner is QASM/backend; the exit proof is a no-call test plus
full unchanged-neighbor regression. Unsupported finite inputs do not extend
the ordinary compatibility window.

### Boundary acceptance scenarios

Where applicable, every migrated consumer must demonstrate: bare `Limit` is
inspection-only; source-visible `Realize(Limit(...), policy)` is the only
finite-plan route; intermediate values remain `State<T>`; terminal `Measure`
is the collapse boundary with preserved provenance; and unresolved meaning,
unsupported capability, or resource failure produces no result, plan, gate,
allocation, or QASM.

## Phase boundaries

- **Phase 1 Red:** tests, inventory, and fixtures only; no production
  migration or deletion.
- **Phase 2 Green:** smallest approved consumer migration slice only.
- **Phase 3 Refactor:** remove obsolete paths only after replacement,
  no-bypass, rollback, and full-regression evidence.

## Non-goals

Provider SDKs, live QPU, S02 numbers, solver families, automatic
finiteization, and broad example redesign remain separate work.
