# LISS-0499: Evaluator dynamic-lane runtime-plan family

| Field | Value |
|---|---|
| Status | **phase-3-refactor-complete** |
| Phase | phase-3-refactor-complete |
| Parent | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| Predecessor | [LISS-0498](LISS-0498-evaluator-callable-plan.md) |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0499-dynamic-lane-runtime-plan-family) |
| Scope approval | User approved continuation on 2026-09-01 |
| Architecture approval | Existing LISS-0493 runtime-plan boundary; no new boundary decision |
| Phase 1 Red approval | User approved continuation on 2026-09-01 |
| Implementation permission | Phase 2 Green and Phase 3 refactor approved by user |
| Next approval | Next semantic-family Phase 1 Red |

## [DESIGN CHECK]

- **Scope and expected behavior:** define a canonical runtime-plan family for
  dynamic regions, mid-circuit controller measurement, branch feed-forward,
  wire lifecycle, and physical-outcome confirmation.
- **Specifications and files inspected:** WP-0107, LISS-0493–0498, the
  consumer-migration and dynamic-lane Specs, `DynamicQpuStmt`/`MatchStmt`/
  `Measure` canonical nodes, evaluator dynamic helpers, readiness, and process
  lessons.
- **Component boundaries:** canonical Semantic IR owns dynamic structure and
  provenance; Runtime Plan projects it; a later executor consumes the plan.
  Capability negotiation, QASM, and real-QPU adapters remain outside.
- **Applicable constraints:** Phase 1 Red only; no provider/QPU/AWS, Rust,
  target allocation, implicit `Realize`, or production implementation.
- **Decisions and ambiguities:** this slice covers one local dynamic region with
  one controller and match branches. Nested regions, reuse/reset policy,
  capability profiles, QASM, and real-provider execution remain separate.
- **Verification plan:** add root Red tests for family classification,
  region/controller/branch provenance, dedicated executor routing, and absence
  of implicit target realization.

## Acceptance scenarios for Phase 1 Red

1. Given a dynamic region with mid-circuit controller measurement and match,
   when a runtime plan is built, then its family is `dynamic_lane`.
2. Given that plan, when its lane node is inspected, then region, controller,
   branch, authority, provenance, and execution status are conserved.
3. Given canonical execution of the dynamic program, when execution runs, then
   a dedicated dynamic-lane executor is selected and the legacy AST body is not
   entered.
4. Given a dynamic program without source-visible `Realize`, when its plan is
   built, then no implicit target finite artifact is created.

## Phase boundary

Phase 1 creates only the failing acceptance contract. Phase 2 will add the
minimum dynamic-lane projection and bounded local executor. Capability
negotiation, QASM emission, nested/reuse semantics, and real-QPU execution
remain separate work.

## Phase 1 Red result

- Added `tests/test_liss_0499_evaluator_dynamic_lane_plan_red.py`.
- Red verification: **3 failed, 1 passed**, with no collection errors. The
  failures expose missing dynamic-lane classification, region/controller/
  branch fields, and the dedicated executor. No production implementation is
  authorized in this phase.

Human review of the Red contract is required before Phase 2 Green.

## Phase 2 Green result

- Added `RuntimeDynamicLaneNode` and `RuntimeExecutionPlan.dynamic_lanes` with
  region, controller, branch, wire, authority, provenance, and execution
  status evidence.
- Canonical plans containing `DynamicQpuStmt` are classified as
  `dynamic_lane` with precedence over static plan families.
- Added `_execute_dynamic_lane_plan` as the dedicated capability-gated entry;
  the existing dynamic helper remains the compatibility payload until its
  provider-neutral mechanics are separately migrated.
- LISS-0499 **4 passed**; related runtime-plan tests **25 passed**; existing
  dynamic execution regressions **9 passed**; `py_compile` and
  `git diff --check` passed.
- Capability negotiation, nested/reuse semantics, QASM, and real-provider
  execution remain out of scope.

## Phase 3 result

- Simplified dynamic-region projection by materializing the region child set
  once and filtering controller, branch, and wire records from that view.
- Preserved canonical source IDs, provenance, family precedence, capability
  gating, and the existing compatibility execution path.
- Same-context review found no blocking finding.
- Verification: LISS-0499 plus callable/evolution/control/binder runtime-plan
  tests and existing dynamic regressions **34 passed**; `py_compile` and
  `git diff --check` passed.

Process review: no operating-contract deviation or operational problem found.

Issue complete. The next safe action is a new semantic-family Phase 1 Red
contract.
