# Staqex Scientific Semantic Consumer Migration Specification

| Field | Value |
|---|---|
| Status | **Accepted — binder and public-QASM ownership slices complete; further migration is design-gated** |
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

### LISS-0487 Equation DTO authority retirement

`EquationNode` and `physics_equation` remain useful DTOs for module-local
validation and diagnostics, but caller-injected or string equation payloads
must not authorize semantic acceptance. This slice defines the negative
authority boundary: canonical source-derived nodes remain authoritative, while
Equation DTOs may be accepted only as explicitly typed diagnostic inputs.

Phase 1 must prove caller-only DTO rejection, source identity/provenance
preservation, and no finite artifact or execution authorization from an
injected equation. Phase 2 may add only the minimum validation/adapter guard.
Numerical equation solving, physics IR replacement, provider/QPU, and S02
migration are excluded.

### LISS-0488 Physics IR canonical projection migration

Physics IR is a projection DTO and is not a source-semantic authority. The
compile-owned `ScientificSemanticIR` object must be passed explicitly to the
Physics projection; the projection must not rebuild meaning from AST, HIR,
string equations, or caller-injected Equation DTOs. The projection preserves
canonical node identity, ordered structure, role/lane, type, dimensions,
exactness, intent, and provenance. A required field that cannot be preserved
causes a named diagnostic and no partial Physics artifact.

Equation DTOs remain available only for the explicitly typed diagnostic
compatibility role defined by LISS-0487. They cannot authorize execution,
finiteization, allocation, QPU artifacts, or implicit `Realize`. The projection
is deterministic for a given semantic snapshot and does not parse, evaluate,
solve, allocate, call providers, or create finite plans.

Phase 1 Red must cover canonical object identity, node/field conservation,
caller-authority rejection, lossy-projection no-artifact behavior, exact versus
finite boundary, diagnostic-only Equation metadata, and single-build identity.
Phase 2 is limited to compile-owned projection wiring. Phase 3 may retire the
old HIR-authority path only after no-bypass and unchanged-neighbor evidence.
Provider/live QPU, Rust, S02, solver, and broad `symbolic_ir` migration remain
separate work.

### LISS-0489 Symbolic IR canonical inspection migration

Exact/symbolic inspection must consume the compile-owned
`ScientificSemanticIR` through `SemanticInspectionResult`. The existing
`symbolic_ir` dictionary may remain only as a derived compatibility view; its
direct AST walk may not be a parallel semantic authority or rebuild canonical
meaning. Canonical source node IDs, structure, role lanes, type/dimensions,
exactness, intent, and provenance must be preserved or rejected explicitly.
The legacy `resolved.source_node_ids` field remains stable for existing
dictionary consumers; canonical IDs are exposed separately as
`resolved.canonical_source_node_ids` until those consumers migrate.

Inspection without source-visible `Realize` creates no finite plan, gates,
allocation, or collapse record. Unresolved meaning produces no partial
executable artifact while retaining diagnostic source IDs. Phase 1 covers
authority/no-bypass, binder/indexed-operator provenance, exact/symbolic
no-allocation, unresolved fail-closed behavior, and one-build identity. Phase 2
only wires the canonical inspection into current local compatibility surfaces;
Phase 3 may retire the direct AST walk after regression and no-bypass evidence.

### LISS-0490 Evaluator canonical execution boundary

The runtime evaluator must receive the compile-owned `ScientificSemanticIR`
through an explicit execution boundary. AST nodes may remain temporary
mechanics inside an execution adapter only when they match canonical source
node identity, role/lane, and provenance. AST-only execution is rejected
before state mutation, measurement, allocation, or result publication.

`State<T>` remains non-collapsed through pure evaluation and inspection;
terminal `Measure` remains the only collapse/sink boundary. Exact/symbolic
execution without source-visible `Realize` creates no finite artifact or
allocation. `RngPort` and `MeasureSinkPort` remain injected ports, and no
provider SDK or network adapter is part of this migration. Phase 1 covers
canonical identity/no-bypass, State/Measure transitions, no hidden
finiteization, port effects, and deterministic provenance; Phase 2 wires one
local path only.

### LISS-0491 Evaluator legacy `run_unit()` retirement

The legacy `Evaluator.run_unit(CompilationUnit)` entry is a compatibility-only
execution lane. Canonical local execution enters through
`run_canonical_unit(..., semantic_ir=...)`, where the compile-owned
`ScientificSemanticIR` supplies execution eligibility, source identity, and
provenance. Existing evaluator mechanics may remain behind that boundary
temporarily.

Retirement is staged: classify all direct and indirect callers; migrate
delivery callers (`host.py`, `run.py`, and CLI); migrate verification and
feature-test families; expose an observable compatibility/deprecation
classification; then remove the legacy entry only after the production caller
inventory is empty, no-bypass tests pass, State/Measure and injected-port
regressions remain green, and full local regression is green. A new production
direct caller must fail the migration guard. Canonical/source-provenance
divergence is a rollback trigger that keeps the compatibility lane available.

This migration does not define a release policy, provider/QPU/AWS integration,
Rust implementation, numerical solver, or new port contract. The exact
deprecation mechanism and final removal release remain Architecture decisions;
no implementation or API removal is authorized by this section alone.

### LISS-0492 Complete evaluator `run_unit()` removal

After LISS-0491, `Evaluator.run_unit()` is no longer used by production
delivery code, but remains referenced by local tests and specification
verification suites. Complete removal requires migrating those callers in
bounded families to `run_canonical_unit(..., semantic_ir=...)`, with the unit
and semantic IR derived from the same compile result. Tests may use a private
helper only when it obtains and passes that compile-owned IR; they may not
fabricate authority or preserve the public compatibility API.

The removal gate is: no callable public `run_unit`, no executable reference in
production or tests, canonical source identity and authority on every local
execution result, unchanged State/Measure and injected-port behavior, and
green targeted plus full local regression. Any provenance or scientific
behavior divergence retains the compatibility implementation and stops the
removal. This section does not choose public versioning, packaging, provider
integration, AWS/QPU behavior, Rust implementation, or solver policy.

The LISS-0492 removal gate is satisfied: the public `run_unit()` entry and
compatibility-only result metadata are removed, all local executable callers
use the canonical semantic IR entry, and targeted/API regressions plus Spec
Verification pass. The evaluator's internal AST mechanics remain an explicit
separate future migration candidate.

### LISS-0493 Evaluator internal AST mechanics retirement

The public evaluator entry is canonical-only after LISS-0492, but its internal
execution still dispatches directly over `CompilationUnit` and AST nodes. This
is an implementation concern, not a second language authority, yet it prevents
the runtime from consuming the canonical semantic structure directly.

Retirement must therefore use an internal, non-public runtime execution plan
lowered from `ScientificSemanticIR`. The plan preserves canonical source node
identity, provenance, role/lane, exactness, and realization status. AST objects
may remain temporary source metadata/mechanics during migration, but may not
decide scientific meaning, execution eligibility, or finiteization.

Migration proceeds by reviewed semantic families: state binding and terminal
measurement first; then pure transformations, control, evolution, binders,
functions/classes, and dynamic lanes. The retirement gate is no AST top-level
dispatch reachable from canonical execution, source/provenance conservation for
all migrated plan nodes, unchanged State/Measure and port behavior, and green
full local regression. This work does not select a provider, QPU/AWS path, Rust
implementation, solver, serialization format, or public runtime API.

#### LISS-0493 Phase 3 first-family result

The first runtime-plan family is now implemented for a main body consisting of
state bindings followed by terminal `Measure`. Its dedicated executor consumes
the canonical plan boundary and reuses only the existing state-binding and
terminal-measure primitives. Canonical execution does not enter
`_run_legacy_ast_body` for this family; unsupported families retain that
explicit migration fallback until their own reviewed plan contract exists.

The result preserves terminal collapse, RNG accounting, measurement-sink
effects, and `EvalResult` source/authority evidence. The next migration unit is
the pure-transformation family and requires its own Red contract and approval.

#### LISS-0494 Pure-transformation runtime-plan family

The next evaluator migration unit is the pure-transformation family: a
non-destructive State pushforward, including a closed unary transformation
chain, followed by terminal `Measure`. Its internal plan must classify the
family from canonical semantic structure and conserve transformation input and
output source node IDs, authority, and provenance. Canonical execution must
use a dedicated plan executor for this family and must not enter the legacy AST
body. `when`, `evolve`, operator/binder lowering, callable object mechanics,
and dynamic lanes remain separate migration units.

#### LISS-0495 Control-mixture runtime-plan family

The next control migration unit is a single-level `Mix`/`when` family driven
by an unmeasured State. Its canonical plan must preserve the control source
node ID, branch rules, authority, and provenance, and must retain eligible
branches in the joint until terminal `Measure`. Nested `Mix` and dynamic-lane
control remain separate migration units.

#### LISS-0496 Evolution runtime-plan family

The next evolution migration unit is explicit local `Evolve` execution. Its
canonical plan must conserve evolved State input/output source IDs, Hamiltonian
and duration evidence, authority, provenance, and realization status. Local
exact evolution must not imply target finiteization or early collapse.
Suzuki/QASM target realization, continuous/open-system evolution, and solver
policy remain separate consumers.

#### LISS-0497 Binder runtime-plan family

The next evaluator migration unit is the binder family represented by
canonical `OpBinder` nodes, including `Sigma` and `Pi`. Its runtime plan must
preserve the binder source identity, domain and body source identities, output
identity, authority, provenance, and realization status. Binder projection is
semantic-structure consumption only: it must not silently enumerate an
unbounded or symbolic domain, allocate a finite target, or imply `Realize`.
Canonical execution will later use a dedicated binder executor for the bounded
local operator path. Classical binder evaluation, multi-binder constraints,
symbolic domains, target/QASM finite lowering, and callable/dynamic binder
forms remain separate migration units.

LISS-0497 Phase 2 adds the internal `RuntimeBinderNode` projection and a
bounded local evaluator route. The projection preserves canonical source
identity and provenance while compile-time operator binders are excluded from
deferred State/Measure materialization. No finite domain enumeration or target
artifact is created by this route.

LISS-0498 Phase 2 adds the internal `RuntimeCallableNode` projection and a
bounded local evaluator route. The route preserves declaration, invocation,
receiver, and output source evidence while keeping target realization and
dynamic/cross-module dispatch outside this migration unit. Class construction
continues through the existing compatibility path until its mechanics receive
their own dedicated plan contract; this prevents a partial deferred executor
from changing established namespace/class behavior.

#### LISS-0499 Dynamic-lane runtime-plan family

The next evaluator migration unit is the dynamic lane: a dynamic region,
mid-circuit controller measurement, branch control, wire lifecycle, and
physical-outcome confirmation. Its runtime plan must preserve region,
controller, control-branch, and wire source identities, authority, provenance,
and execution status. The dedicated route must keep dynamic measurement and
feed-forward distinct from static mixture control and must not allocate a
target or imply `Realize`. Provider capability negotiation, OpenQASM emission,
and real-QPU execution remain separate consumers.

LISS-0499 Phase 2 adds the internal `RuntimeDynamicLaneNode` projection and a
dedicated capability-gated evaluator entry. The existing dynamic helper is
retained as the compatibility payload until provider-neutral dynamic mechanics
receive their own migration contract; canonical planning itself does not
select a provider or allocate a target.

#### LISS-0500 Symbolic legacy-builder retirement

The next consumer migration retires the direct AST walk in
`_build_symbolic_ir_legacy` from the canonical compatibility-view path. The
legacy dictionary may remain as an explicit compatibility API, but canonical
inspection must derive identity, structure, provenance, and no-allocation
evidence from `ScientificSemanticIR` without rebuilding meaning from AST.
Explicit legacy callers, unresolved semantics, and finite target realization
remain separately gated and must not be silently widened by this retirement.

LISS-0500 Phase 2 now builds the compatibility dictionary from canonical IR;
source-derived operator aliases retain the stable dictionary shape without
re-entering the direct AST builder. The explicit legacy API remains isolated
until its own callers and projection families are migrated.

#### LISS-0501 QASM fallback retirement proof

The next QASM migration retires the direct AST fallback branch from the
canonical `emit_unit()` entry. Canonical measure-only input already emits its
source-derived Measure projection; the remaining proof must ensure the entry
contains no direct `lower_unit_to_circuit()` call. The explicit lowerer symbol
remains available only for separately approved compatibility callers.

#### LISS-0502 QASM lowerer export retirement

The next cleanup removes the legacy lowerer re-export from the QASM emitter
module. Canonical callers already use QPU IR; explicit compatibility callers
must import `lower_unit_to_circuit` from its owning lowerer module. This is an
API-boundary cleanup only and does not delete the lowerer implementation or
change provider/QPU behavior.

#### LISS-0503 Unsupported evolution QASM rejection

Canonical QASM emission must fail closed when `ScientificSemanticIR` contains
an explicit evolution but `QpuProgram` contains no executable canonical
instructions. The rejection code is `E_QPU_CANONICAL_PROVENANCE`; the result
must have empty QASM, no gates, and no allocation side effect. This boundary
is provider-neutral and must not infer finite evolution or invoke the legacy
lowerer. Supported finite canonical projections remain on the existing QPU
realization path. Target-specific evolution realization is a separate future
consumer and is not part of this issue.

#### LISS-0498 Callable/object runtime-plan family

The next evaluator migration unit is callable and object mechanics: function
declarations, class declarations, method invocation, receiver identity, and
return flow. Its runtime plan must preserve declaration and invocation source
IDs, receiver identity, output identity, authority, provenance, and execution
status. Canonical execution will later route this family through a dedicated
plan executor without allowing AST dispatch to choose scientific meaning.
Operator binders, dynamic lanes, recursive/cross-module calls, and target
realization remain separate contracts; callable planning must not allocate a
finite target or imply `Realize`.
