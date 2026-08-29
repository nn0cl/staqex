# Staqex Scientific Semantic Core

| Field | Value |
|---|---|
| Status | Architecture-approved; Phase 1 Red and Phase 2 Green complete; Phase 3 representative QPU plus policy/evolution/binder projection complete; consumer-wide migration remains open |
| Issue | [LISS-0444](../issues/LISS-0444-scientific-semantic-core.md); [LISS-0476](../issues/LISS-0476-symbolic-ir-consumer-migration.md); [LISS-0477](../issues/LISS-0477-ast-dto-authority-retirement.md) |
| WorkPlan | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| ADR | [ADR 0211](../architecture/adr/0211-scientific-semantic-core-and-ir-authority.md) |

## [DESIGN CHECK]

- **Scope and expected behavior:** Define the authoritative source-derived
  semantic model for scientific expressions and their simulator/finite-target
  projections.
- **Specifications and files inspected:** AST, parser, typecheck, HIR,
  `physics_ir.py`, `physics_equation.py`, `physics_ir_lower.py`,
  `symbolic_ir.py`, `quantum_semantic_ir.py`, `algorithm_plan_ir.py`,
  evaluator, continuous lowering, recent LISS-0437–0443 artifacts, and the
  independent-review perspectives ledger.
- **Component boundaries:** Source syntax → type/HIR → Scientific Semantic IR
  → simulator/quantum semantic projection or explicit `Realize` → finite plan;
  provider and live-QPU ports remain outside the Kernel.
- **Applicable constraints:** physicist-first source fidelity, Never Leave the
  State, terminal `measure`, explicit finite realization, fail-closed
  capability rejection, no hidden Host fallback, and no provider SDK.
- **Decisions:** ADR 0211 is the proposed authority decision. Existing IR/DTO
  paths are migration candidates, not protected architecture.
- **Included context:** implementation audit evidence and representative
  source/tests needed to prove parser reachability and consumer wiring.
- **Omitted context:** credentials, provider behavior, live QPU capability,
  S02 numerical values, and unrelated historical DTOs without current use.
- **Task routing:** architecture review first; deterministic parser/type/HIR/IR
  tests for Red; implementation only after typed Architecture and Phase 1
  approvals.
- **Input/output evidence contract:** every review claim names a source path,
  structural node, consumer path, deterministic test, and uncertainty; no
  hidden chain-of-thought is requested or recorded.
- **Independent review lenses:** implementation-reality/canonical-authority;
  source-to-domain fidelity; architecture/boundary integrity; type/dimension
  closure; state/physics safety; realization/fail-closed behavior; migration
  safety; evidence hygiene; phase discipline.
- **Verification plan:** source reachability tests, structural IR golden tests,
  type/dimension diagnostics, consumer wiring tests, projection provenance,
  retirement checks for superseded paths, and full regression.

## Normative acceptance requirements

1. At least one `.sqx` source form creates each accepted semantic relation;
   caller-injected DTOs alone cannot satisfy acceptance.
2. Equation sides, operators, binders, coefficients, units, and conditions are
   structural nodes with source provenance.
3. Semantic roles are explicit: classical, mathematical, quantum, evolution,
   simulator, and finite realization.
4. A semantic node records its type/dimension validity and exactness or
   approximation status where applicable.
5. Quantum and classical carriers cannot cross roles through implicit coercion.
6. `Realize` is visible in source and provenance; no direct `Limit` lowering or
   hidden gate rewrite is accepted.
7. Quantum Semantic IR and Algorithm Plan are downstream projections, not
   alternate source authorities.
8. Existing Physics/Symbolic/Equation paths are each classified as migrate,
   replace, or retire with a test-backed reason.
9. Unsupported solver or target behavior is explicit and does not fabricate a
   numerical result or partial circuit.
10. No implementation phase begins until the ADR and this Spec receive
    independent review and typed Architecture approval.

## Structural and projection contract

The first semantic-core slice uses the following closed node families. This is
an implementation contract, not a requirement to expose these names as source
classes or namespaces.

| Family | Required structure | Required invariants |
|---|---|---|
| expression | literal, name, unary/binary operator, call, binder | ordered children, operator identity, source span, type/dimension result |
| relation | left, relation operator, right, conditions | both sides are structural expressions; compatible dimensions; provenance for both sides |
| quantum value | state/operator carrier and type | no implicit classicalization; `State<T>` remains a state carrier |
| evolution | operand, generator/parameter, time or evolution variable | evolution intent remains distinct from an identity or static relation |
| simulator projection | canonical node identity and exact/symbolic evaluation contract | no finite target allocation; approximation is explicit and cannot bypass `Realize` |
| realization | source-visible `Realize` policy, target, order/steps/error/resource contract | only this family may create a finite plan; unsupported or over-budget targets fail closed |

For every family, the canonical node carries provenance, role, type and
dimension validity, exactness/approximation status, and intent. A downstream
projection must either preserve those fields and structural children or reject
with a lossy-projection diagnostic. Provenance strings alone are insufficient.

The minimum acceptance corpus includes: a classical arithmetic relation, a
unit-bearing relation, a binder (`Sigma`/`Pi`), an operator/state relation, a
Hamiltonian evolution, an exact/symbolic simulator inspection, a direct
`Limit` rejection, and an explicit finite `Realize`. The corpus includes
negative cases for early `measure`, implicit role crossing, caller-only
`EquationNode`, unresolved canonical semantics, and hidden finiteization.

## Simulator and finite realization boundary

The simulator consumes a canonical semantic projection and may inspect exact
or symbolic meaning without allocating a finite target or returning an
evaluated-value result. It must not silently
choose a discretization, gate decomposition, qubit budget, or provider. A
finite approximation is only valid after source-visible `Realize`, and the
finite plan must retain the originating semantic node identity and policy.
Bare `Limit` is accepted for exact/symbolic inspection because that path does
not finiteize. The same bare `Limit` is rejected for finite-target realization;
only source-visible `Realize(Limit(...), ...)` may produce a finite plan. An
unsupported simulation or realization returns no fabricated value or partial
artifact.

## Authority migration matrix

The following is the Phase 0 baseline. These paths are not preserved as
independent semantic authorities merely for compatibility.

| Existing path | Planned disposition / owner / order | Compatibility and exit | Phase 1/3 proof ID |
|---|---|---|---|
| operational AST / `OpExpr` | migrate as parser/front-end input; Semantic Core owner; order 1 | no semantic consumer may remain AST-authoritative after Phase 3; rollback on source-structure loss | `SSC-PROOF-AST-01` |
| HIR | migrate as typed front-end input; front-end owner; order 1 | expand or replace if identity/structure cannot be retained; no independent domain authority | `SSC-PROOF-HIR-01` |
| `physics_ir` | replace with canonical projection; Semantic Core owner; order 2 | temporary diagnostic projection only; retire when projection tests pass | `SSC-PROOF-PHYS-01` |
| `physics_equation` / `EquationNode` | retire caller-injected authority; test owner; order 2 | no compatibility window for semantic acceptance; DTO-only tests become negative tests | `SSC-PROOF-EQ-01` |
| `symbolic_ir` | replace with simulator/inspection projection; simulator owner; order 3 | retire direct AST walk after canonical projection is wired | `SSC-PROOF-SYM-01` |
| Quantum Semantic IR | migrate as downstream projection; quantum consumer owner; order 3 | no direct Physics DTO input after migration; reject missing canonical identity | `SSC-PROOF-QSEM-01` |
| Algorithm Plan IR | migrate as downstream finite-plan projection; realization owner; order 4 | only explicit `Realize`; rollback on provenance or policy loss | `SSC-PROOF-PLAN-01` |
| evaluator AST dispatch | migrate behind semantic consumer boundary; runtime owner; order 4 | temporary AST handling only for unclassified legacy cases, which fail closed | `SSC-PROOF-EVAL-01` |
| QASM AST/source-shape lowering | migrate behind finite projection; backend owner; order 4 | direct `Limit` and partial-artifact paths retire after canonical gate tests | `SSC-PROOF-QASM-01` |
| H1/synthetic authoring | retire as independent dialect; authoring owner; order 2 | migrate source meaning or remain diagnostic-only; no compatibility authority | `SSC-PROOF-H1-01` |
| `qpu_ir` / source-AST DAG | replace as canonical-independent target input; backend owner; order 4 | diagnostic/legacy inspection only until canonical projection consumes it | `SSC-PROOF-QPU-01` |
| finite-binder executable lowering | migrate behind canonical binder projection; math owner; order 3 | no direct AST/DAG finiteization after binder proof passes | `SSC-PROOF-BINDER-01` |
| `continuous_lowering.py` / `GridHamiltonian` | remain an out-of-scope legacy numerical adapter; no semantic authority | unchanged in this Issue; future Issue required before migration | scope-boundary record, not SSC proof |
| `live_submit.py` / `QpuSubmitPort` | remain outside Kernel and this Issue | no live submission/provider work; future port Issue required | scope-boundary record, not SSC proof |

Default compatibility window: none for semantic authority. A temporary
diagnostic-only adapter must carry an explicit deprecation diagnostic and an
expiry milestone in its Issue. Rollback is triggered by loss of structural
children, source identity, state/measurement semantics, or explicit
`Realize` policy; rollback restores the last passing semantic snapshot and
does not restore an obsolete authority path.

## Consumer-wide follow-up design

### LISS-0476 — non-explicit `symbolic_ir` consumer migration

Simulator and inspection consumers must use one compile-owned canonical
projection exposed as a provenance-bearing inspection result. A caller-only
symbolic DTO is non-authoritative. Phase 1 measures build count, object
identity, source IDs, no finite allocation, and unresolved-meaning rejection;
Phase 2 changes only the named inspection consumers.

### LISS-0477 — AST/DTO semantic-authority retirement

Remaining evaluator, Equation/Physics DTO, H1, Algorithm Plan, and QASM helper
reads are classified as migrate, projection-only, retire, or defer. Each row
names owner, proof ID, replacement projection, rollback trigger, and deletion
condition. Phase 1 is inventory and negative tests only; deletion requires
replacement and rollback evidence. Changes to ADR 0211, `Realize`, `State<T>`,
or terminal `measure` stop for Architecture review.

## Acceptance corpus and artifact rules

Phase 0 names the initial corpus IDs and intended fixture locations:

| ID | Fixture | Required assertion |
|---|---|---|
| SSC-001 | `tests/fixtures/semantic_core/classical_relation.sqx` | `SSC-PROOF-AST-01`, `SSC-PROOF-HIR-01`; structural arithmetic relation and dimensions |
| SSC-002 | `tests/fixtures/semantic_core/unit_relation.sqx` | `SSC-PROOF-HIR-01`, `SSC-PROOF-PHYS-01`; unit compatibility and provenance |
| SSC-003 | `tests/fixtures/semantic_core/binder_relation.sqx` | `SSC-PROOF-BINDER-01`; `Sigma`/`Pi` binder structure |
| SSC-004 | `tests/fixtures/semantic_core/state_operator.sqx` | `SSC-PROOF-QSEM-01`; operator/state role and `State<T>` |
| SSC-005 | `tests/fixtures/semantic_core/hamiltonian_evolution.sqx` | `SSC-PROOF-PLAN-01`, `SSC-PROOF-QASM-01`; evolution role distinct from identity |
| SSC-006 | `tests/fixtures/semantic_core/symbolic_inspection.sqx` | `SSC-PROOF-SYM-01`; exact/symbolic projection without allocation or collapse |
| SSC-007 | `tests/fixtures/semantic_core/explicit_realize.sqx` | `SSC-PROOF-PLAN-01`, `SSC-PROOF-QASM-01`; explicit policy reaches finite plan with provenance |
| SSC-008 | `tests/fixtures/semantic_core/invalid_boundaries.sqx` | `SSC-PROOF-EQ-01`, `SSC-PROOF-EVAL-01`, `SSC-PROOF-QASM-01`; early measure, role crossing, bare `Limit`, and missing canonical meaning reject |
| SSC-009 | `tests/fixtures/semantic_core/dynamic_measurement.sqx` | `SSC-PROOF-QSEM-01`, `SSC-PROOF-EVAL-01`; dynamic lane remains distinct from static terminal collapse |

Snapshots use schema identifier `ssc-semantic-v1`; each case records source
node IDs, structural children, role/lane, type/dimensions, exactness, intent,
and projection/diagnostic outcome. Consumer artifacts are atomic: unresolved
canonical errors produce no simulator result, finite plan, gate list, QASM,
or allocation record. Soft diagnostics may be retained only as diagnostics;
they cannot authorize a consumer.

The snapshot encoding is a deterministic mapping with required fields
`schema`, `case_id`, `source_node_ids`, `nodes`, `projections`, and
`outcome`. `nodes` are ordered by source span start, then node kind, then
stable source ID; children are ordered by grammar position. Each node requires
`id`, `kind`, `children`, `role_lane`, `type`, `dimensions`, `exactness`,
`intent`, and `provenance`. `projections` records consumer name, source IDs,
preserved fields, intentionally omitted non-semantic fields, or diagnostic
`SSC_LOSSY_PROJECTION`. `outcome` is either `accepted` with artifacts or
`rejected` with `SemanticRejection`; the two forms are mutually exclusive.
Schema evolution requires a new schema identifier and migration note.

Schema scalar types are fixed: IDs, kinds, roles, lanes, intent, exactness,
diagnostic codes, and source spans are non-empty ASCII strings; `children`,
`source_node_ids`, and preserved/omitted fields are ordered string arrays;
`type` and `dimensions` are canonical strings from the type/dimension
normalizer; `projections` and `diagnostics` are ordered records. Optional
fields are only `conditions`, `allocation_record`, `collapse_record`, and
`omitted_nonsemantic_fields`; they are absent rather than null when unused.
Stable diagnostics include `SSC_LOSSY_PROJECTION`, `SSC_UNRESOLVED_MEANING`,
`SSC_IMPLICIT_ROLE_CROSSING`, `SSC_HIDDEN_FINITEIZATION`,
`SSC_EARLY_MEASURE`, and `SSC_DIRECT_LIMIT_TARGET`.

The only simulator contract in this Issue is `SemanticInspectionResult`,
containing
`source_node_ids`, `structural_tree`, `role_lanes`, `type_dimensions`,
`exactness`, `intent`, `allocation_record=None`, and `collapse_record=None`.
It is an inspection/proof object, not a finite circuit or measurement result.
No exact numeric or symbolic evaluated-value API is introduced by this Issue.
Only terminal `measure` may produce a static classical result. A dynamic-lane
measurement uses `role_lane=dynamic_measurement`, retains `State<T>` on the
quantum lane, and cannot be substituted for terminal static measurement.

The named fixture files, snapshot serializer/validator, and proof IDs are
Phase 1/3 deliverables and intentionally do not exist in the design phase.
Their absence is not implementation completion and does not authorize a
phase transition.

## Design-time current-versus-target inventory

The following distinction is normative during migration. “Current” records
what the repository does today; “target” records what Phase 1/2/3 must prove.

| Concern | Current implementation (not accepted authority) | Target acceptance |
|---|---|---|
| source meaning | AST/HIR plus several direct projections | one source-derived Scientific Semantic IR |
| simulator inspection | Symbolic/Physics DTOs and soft artifacts | `SemanticInspectionResult` from canonical IR |
| finite target | AST/QASM source-shape lowering exists | only canonical `Realize` projection may allocate |
| measurement | terminal and dynamic mechanisms exist in separate paths | one IR with static terminal and dynamic lanes distinguished |
| failure | some diagnostics/artifacts remain soft or partially shaped | diagnostic envelope with all consumer artifacts absent |
| migration | competing paths remain live | each matrix proof ID passes, then path is migrated/replaced/retired |

The current column is an audit fact and must not be presented as completed
support for the target. The target column is a Phase 1/2/3 acceptance contract.

## Role and lane transition contract

The initial legal transitions are: `classical → mathematical`,
`mathematical → quantum`, `quantum → evolution`, `evolution → simulator`, and
`evolution → realization` only through explicit `Realize`. `simulator` does not
transition to `realization` implicitly. `quantum → dynamic_measurement` is a
distinct dynamic-lane transition that preserves the quantum `State<T>` lane;
only terminal `measure` transitions to a static classical result. All other
role/lane crossings reject with no consumer artifact.

| Source lane/role | Operation | Result lane/role | Condition |
|---|---|---|---|
| classical | mathematical relation | mathematical | dimensions/type valid |
| mathematical | operator/state construction | quantum | valid quantum carrier |
| quantum | evolution | evolution | generator/time structure valid |
| evolution | exact/symbolic inspect | simulator | no finite allocation or collapse |
| evolution | `Realize` | finite realization | explicit policy and target capability |
| quantum | dynamic measurement | dynamic measurement + `State<T>` | dynamic lane explicitly selected |
| dynamic measurement | dynamic control/continuation | dynamic lane | state ownership and lane contract valid |
| quantum/evolution | terminal `measure` | classical result | terminal position only |
| any | implicit classicalization, hidden finiteization, bare `Limit` to target | rejected | `SemanticRejection`, no consumer artifact |
| terminal classical result | quantum/evolution reuse | rejected | no reusable post-collapse state |

Projection commit is atomic: validation completes before a simulator result,
finite plan, gate list, QASM, qubit allocation, or resource estimate is
published. During validation, estimates are transient and are not artifacts.
Rejection publishes only `SemanticRejection` with diagnostics and provenance;
it must not expose a success-shaped circuit containing a count or partial
allocation. Existing ADR 0210 resource-budget rejection tests are a required
regression precedent for this rule.

The design-only rejection envelope is `SemanticRejection`, containing
diagnostics, source provenance, and no simulator result, finite plan, circuit,
gate list, QASM, qubit allocation, or resource estimate. A backend may retain
an error code and source span, but must not return a partially populated
success-shaped artifact.

`SemanticInspectionResult` has required fields
`source_node_ids: ordered[str]`, `structural_tree: NodeSnapshot[]`,
`role_lanes: ordered[RoleLane]`, `type_dimensions: ordered[TypeDimension]`,
`exactness: Exactness`, `intent: Intent`,
`allocation_record: None`, and `collapse_record: None`. `SemanticRejection`
has required fields `code: DiagnosticCode`, `source_node_ids: ordered[str]`,
`spans: ordered[SourceSpan]`, `message_key: str`, and
`artifacts: None`. These two result forms are mutually exclusive and map
directly to snapshot outcomes `accepted` and `rejected`.

The closed role enum is `classical`, `mathematical`, `quantum`, `evolution`,
`simulator`, and `finite_realization`; the closed lane enum is `static`,
`dynamic_measurement`, and `terminal_classical`. Any role/lane pair not listed
in the transition table is rejected, including all transitions out of
`finite_realization` and `terminal_classical`.

## Proof-ID execution map (planned, not yet created)

The following map freezes the Phase 1 Red test names and the Phase 3 retirement
checks. The files do not exist until their separately approved phase begins.

| Proof ID | Planned test file / test name | Assertion boundary |
|---|---|---|
| `SSC-PROOF-AST-01` | `tests/test_scientific_semantic_core_red.py::test_ast_is_not_consumer_authority` | evaluator/QASM cannot execute from AST alone |
| `SSC-PROOF-HIR-01` | `tests/test_scientific_semantic_core_red.py::test_hir_retains_identity_and_structure` | parser/typecheck/HIR retention |
| `SSC-PROOF-PHYS-01` | `tests/test_scientific_semantic_core_red.py::test_physics_ir_is_projection_only` | no Physics authority |
| `SSC-PROOF-EQ-01` | `tests/test_scientific_semantic_core_red.py::test_caller_equationnode_cannot_satisfy_source_acceptance` | caller injection rejected |
| `SSC-PROOF-SYM-01` | `tests/test_scientific_semantic_core_red.py::test_symbolic_projection_conserves_nodes` | inspection projection |
| `SSC-PROOF-QSEM-01` | `tests/test_scientific_semantic_core_red.py::test_quantum_projection_requires_canonical_input` | canonical identity/fields |
| `SSC-PROOF-PLAN-01` | `tests/test_scientific_semantic_core_red.py::test_algorithm_plan_requires_realize` | explicit finite boundary |
| `SSC-PROOF-EVAL-01` | `tests/test_scientific_semantic_core_red.py::test_evaluator_has_no_independent_semantic_dispatch` | runtime authority gate |
| `SSC-PROOF-QASM-01` | `tests/test_scientific_semantic_core_red.py::test_qasm_rejects_direct_limit_and_partial_artifacts` | finite fail-closed |
| `SSC-PROOF-H1-01` | `tests/test_scientific_semantic_core_red.py::test_h1_cannot_create_second_semantic_dialect` | synthetic authority retirement |
| `SSC-PROOF-QPU-01` | `tests/test_scientific_semantic_core_red.py::test_qpu_ir_requires_canonical_projection` | QPU IR gate |
| `SSC-PROOF-BINDER-01` | `tests/test_scientific_semantic_core_red.py::test_finite_binder_requires_canonical_binder` | binder finiteization gate |
| `SSC-PROOF-BOUNDARY-01` | `tests/test_scientific_semantic_core_red.py::test_state_and_realization_boundaries_are_structural` with cases `SSC-PROOF-SYM-01`, `SSC-PROOF-PLAN-01`, `SSC-PROOF-QSEM-01` | exact inspection, explicit realization, and dynamic/static lane structure |

All proof IDs above are Phase 1 Red acceptance tests. Phase 3 adds a
same-ID retirement/deletion evidence record for each path; it does not alter
the Phase 1 test names or widen the Phase 1 implementation scope.

## Initial expression families

The design must cover, in one structural model, arithmetic, units, `Sigma`/`Pi`,
operator/state relations, Hamiltonian evolution, and `Realize`. Differential,
integral, variational, probability, Lindblad, ODE/PDE, field, and thermal
families are added only after the core relation model is proven; their solver
implementations are not implied.
