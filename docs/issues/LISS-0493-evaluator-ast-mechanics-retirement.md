# LISS-0493: Evaluator internal AST mechanics retirement design

| Field | Value |
|---|---|
| Status | **phase-3-refactor-complete — first-family fallback retired** |
| Phase | phase-3-refactor-complete |
| Parent | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| Predecessor | [LISS-0492](LISS-0492-evaluator-run-unit-complete-removal.md) |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0493-evaluator-ast-mechanics-retirement) |
| Scope approval | Named continuation target received 2026-09-01 |
| Architecture approval | Approved by Adjudicator 2026-09-01 for the internal runtime-plan boundary |
| Implementation permission | Phase 3 refactor approved and completed |
| Next approval | Phase 1 Red approval for the pure-transformation family |

## [DESIGN CHECK]

- **Scope and expected behavior:** replace the evaluator's direct AST dispatch
  as the runtime's implementation driver with a canonical-semantic runtime
  plan, while preserving the existing local Joint semantics, State/Measure
  boundary, injected ports, and provider-neutral scope.
- **Specifications and files inspected:** LISS-0492, LISS-0491, evaluator
  entrypoints and `_run_unit_body`, `ScientificSemanticIR`, runtime execution
  model, backend targets, WP-0107, consumer-migration Spec, ADR 0211, project
  conventions, and process lessons.
- **Component boundaries, ports/adapters, and VO/DTO candidates:** the
  pipeline produces canonical semantic IR; a new internal runtime-plan
  projection is a candidate use-case representation; evaluator mechanics
  consume that plan; `RngPort`, `MeasureSinkPort`, and host-input ports remain
  adapters. The plan must not become a second semantic authority or public DTO.
- **Applicable constraints:** no language semantic change, no hidden
  classicalization/finiteization, terminal Measure remains collapse boundary,
  no provider/QPU/AWS, Rust, solver, persistence, or deployment work.
- **Decisions, assumptions, and unresolved ambiguities:** the evaluator is
  6,398 lines and contains many AST-specific expression helpers. A direct
  rewrite is unsafe. The plan must be extracted by semantic family, with AST
  nodes retained only as syntax metadata/mechanics during migration. The
  runtime-plan shape, supported family order, and final deletion boundary
  require Architecture approval.
- **Included and omitted AI context:** included evaluator dispatch, canonical
  node taxonomy, runtime Joint/ports, and local regression families. Omitted
  provider integration, Rust VM design, numerical solver, and historical
  feature details not needed for the first family.
- **Task routing:** host-agent architecture inventory and deterministic local
  tests; same-context review under current routing; no external AI/provider.
- **Input/output evidence contract:** input is one compile-owned
  `ScientificSemanticIR` plus explicit runtime ports and policy. Output is a
  canonical-authority `EvalResult` with source identity, terminal measurement,
  and transition provenance. Unresolved projections fail closed with no
  partial runtime plan.
- **Verification plan:** define semantic-family coverage; Red-test one runtime
  plan contract and AST no-bypass guard; Green one representative family;
  refactor only after unchanged-neighbor regression; repeat until AST dispatch
  is unreachable from canonical execution; then remove dead helpers with a
  final full local audit.

## Current architecture and problem

LISS-0492 removed the public legacy entry and made canonical execution call the
authority-neutral `_execute_unit()`. That method still calls `_run_unit_body`,
which initializes runtime state and dispatches directly over `CompilationUnit`
and AST node classes. Canonical authority is therefore enforced at the entry,
but the execution mechanics still interpret syntax objects as their immediate
input.

The evaluator currently combines at least these responsibilities:

| Responsibility | Current location | Proposed destination |
|---|---|---|
| runtime state / Joint lifecycle | `_run_unit_body` and evaluator fields | execution context owned by evaluator |
| top-level statement dispatch | `_run_unit_body` | runtime-plan executor |
| classical expression evaluation | `_eval_value*` family | typed plan/value evaluator by semantic family |
| State pushforward and collapse | Joint bindings and measure handlers | unchanged evaluator primitives behind plan executor |
| function/class/operator mechanics | many evaluator helpers | family-specific plan nodes, staged |
| port effects | evaluator calls to injected ports | unchanged explicit port boundary |

## Proposed staged design

```text
source -> parser/typecheck -> ScientificSemanticIR
                              |
                              v
                    RuntimeExecutionPlan (internal)
                              |
                              v
                    RuntimePlanExecutor -> Joint/ports

AST: source metadata and temporary mechanics only
```

1. **Plan contract:** define internal plan node categories for state binding,
   pure transformation, control/when, evolution, function application, and
   terminal measurement. Every plan node carries canonical source node ID,
   role/lane, provenance, and exactness/realization status. No public
   serialization is introduced.
2. **Lowering boundary:** build the plan only from `ScientificSemanticIR`.
   AST may be consulted for source spans or already-validated syntax details,
   but may not determine scientific meaning, eligibility, or realization.
3. **First family:** migrate state binding, pure pushforward, and terminal
   Measure. This gives a narrow proof for State/Measure and port behavior
   before touching evolution or callable dispatch.
4. **Subsequent families:** migrate when/control, classical expressions,
   operator/evolution, binders, functions/classes, and dynamic lanes as
   separately reviewed batches. Each batch has no-bypass and unchanged-neighbor
   evidence.
5. **Retirement gate:** canonical execution has no AST-dispatch entry, all
   supported plan families have source-ID/provenance conservation, and full
   local regression passes. Only then delete unreachable AST mechanics.

## Acceptance design for next phases

Phase 1 Red must establish: plan creation is compile-owned and single-source;
every plan node has canonical identity/provenance; missing or unresolved
meaning produces no partial plan; canonical execution cannot call the old AST
top-level dispatcher; State remains uncollapsed until terminal Measure; ports
observe only authorized effects; and one representative family preserves
existing results.

Phase 2 Green is limited to the plan contract and first state/measurement
family. Phase 3 may extract and delete only proven-dead dispatch helpers. No
phase may silently broaden into a full evaluator rewrite.

## Stop conditions

Stop and retain AST mechanics if a semantic family lacks canonical structure,
if source provenance diverges, if a plan would invent finiteization or classical
collapse, or if a new port/provider/concurrency/persistence decision is needed.
Request a new ADR if the runtime plan changes language meaning, public API,
serialization, scheduling, or the accepted execution model.

## Architecture approval request

Approve or reject the internal runtime-plan boundary, the semantic-family
migration order, AST-as-temporary-mechanics rule, and staged retirement gate.
Approval does not authorize Phase 1 tests or evaluator implementation.

## Architecture approval result

- The non-public runtime execution plan boundary lowered from
  `ScientificSemanticIR` is accepted.
- The semantic-family order (state/measurement, pure transforms, control,
  evolution, binders, functions/classes, dynamic lanes) and AST-as-temporary-
  mechanics rule are accepted.
- Source identity/provenance conservation, fail-closed unresolved planning,
  State/Measure and port invariants, and the no-AST-dispatch retirement gate
  are accepted.
- No public DTO, serialization format, provider, concurrency model, Rust
  design, or implementation permission is created by this approval.

## Phase 1 Red readiness

The fixed Phase 1 Red batch is:

- `tests/test_liss_0493_evaluator_runtime_plan_red.py`;
- `tests/fixtures/semantic_core/evaluator_runtime_plan.sqx` only if the
  existing semantic-core fixtures cannot express the first-family plan cases;
- this Issue, the linked migration Spec, WP-0107, and the Phase 1 review
  record.

The tests will specify the internal plan contract for one compile-owned
semantic snapshot, canonical source-ID/provenance conservation, unresolved
fail-closed behavior, absence of AST top-level dispatch from canonical
execution, and unchanged State/Measure plus injected-port effects. They will
not implement the plan or rewrite evaluator mechanics.

Phase 1 Red requires separate explicit approval before test creation.

## Phase 1 Red result

- Added `tests/test_liss_0493_evaluator_runtime_plan_red.py`.
- Verification: **4 failed**, with no collection errors.
- Failures expose the missing runtime-plan builder, missing source-ID and
  provenance-bearing plan nodes, missing unresolved fail-closed behavior, and
  canonical execution's remaining `_run_unit_body` dispatch dependency.
- No runtime-plan production code or evaluator mechanics were changed.

Phase 1 Red is complete; Phase 2 is limited to the minimum first-family plan
contract and state/terminal-measure execution path.

## Phase 2 Green result

- Added internal `RuntimeExecutionPlan` and `RuntimePlanNode` projections from
  `ScientificSemanticIR`, retaining authority, source identity, and
  provenance.
- Canonical execution now builds and consumes the plan and does not directly
  call `_run_unit_body`.
- Non-canonical authority fails closed with
  `E_RUNTIME_PLAN_CANONICAL_AUTHORITY`.
- Unmigrated families use the explicitly named `_run_legacy_ast_body` fallback;
  full AST mechanics retirement remains incomplete and visible.
- Verification: related semantic/API/port tests **35 passed**; `py_compile`
  and `git diff --check` passed.
- Review: `docs/collaboration/reviews/2026-09-01-liss-0493-phase2-review.md`.

Phase 3 must migrate and retire the first-family fallback before expanding to
the next semantic family.

## Phase 3 result

- Added a dedicated first-family runtime-plan executor for `StateBind*` plus
  terminal `Measure`.
- Canonical execution no longer reaches `_run_legacy_ast_body` for that family;
  the legacy path remains only for explicitly unsupported families.
- Existing deferred state-binding, terminal-collapse, RNG, measurement-sink,
  and result authority/source behavior are preserved.
- Verification: LISS-0493, LISS-0490, LISS-0492, LISS-0491, and port regressions
  **47 passed**; `py_compile` and `git diff --check` passed.
- Review: `docs/collaboration/reviews/2026-09-01-liss-0493-phase3-review.md`.
- Next step is a separately approved Phase 1 Red contract for the pure
  transformation family; this issue does not claim consumer-wide AST removal.

Process review: no operating-contract deviation or operational problem found.
