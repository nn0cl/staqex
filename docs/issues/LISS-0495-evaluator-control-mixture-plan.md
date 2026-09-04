# LISS-0495: Evaluator control-mixture runtime-plan family

| Field | Value |
|---|---|
| Status | **phase-3-refactor-complete** |
| Phase | phase-3-refactor-complete |
| Parent | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| Predecessor | [LISS-0494](LISS-0494-evaluator-pure-transformation-plan.md) |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0493-evaluator-ast-mechanics-retirement) |
| Scope approval | User approved continuation on 2026-09-01 |
| Architecture approval | Existing LISS-0493 runtime-plan boundary; no new boundary decision |
| Phase 1 Red approval | User approved 2026-09-01 |
| Implementation permission | Phase 3 refactor approved and completed |
| Next approval | Phase 1 Red approval for the next semantic family |

## [DESIGN CHECK]

- **Scope and expected behavior:** define a canonical runtime-plan family for
  single-level `Mix`/`when` control over an unmeasured State, preserving every
  positively weighted arm until terminal `Measure`.
- **Specifications and files inspected:** LISS-0493/0494, WP-0107, the
  consumer-migration Spec, language axioms and control syntax, Scientific
  Semantic IR control fields, evaluator mixture mechanics, testing strategy,
  implementation readiness, and process lessons.
- **Component boundaries:** `ScientificSemanticIR` owns control meaning,
  source identity, and branch rules; the internal Runtime Plan projects those
  fields; the evaluator will later consume a dedicated control executor. No
  new port or adapter is needed.
- **Applicable constraints:** Phase 1 Red only; single-level control only;
  no early measurement, classical short-circuit, nested `Mix`, QASM/QPU/AWS,
  Rust, solver, or public plan serialization.
- **Decisions and ambiguities:** `Mix` is the current surface spelling of the
  control family. Nested control and dynamic-lane control are separate. The
  exact branch execution payload remains a Phase 2 decision constrained by the
  existing canonical `control_source_node_id` and `branch_rules` fields.
- **Included and omitted context:** included canonical control provenance,
  mixture/state-preservation semantics, and terminal measurement; omitted
  provider execution, finite target lowering, and unrelated evaluator family
  migrations.
- **Verification plan:** add only the root Red acceptance test; it must expose
  missing plan classification, control/branch identity projection, and a
  dedicated executor without collection errors.

## Acceptance scenarios for Phase 1 Red

1. Given a compiled single-level `Mix` program, when a runtime plan is built,
   then it is classified as `control_mixture`.
2. Given that plan, when its control node is inspected, then the canonical
   control source node ID, branch rules, authority, and provenance are present.
3. Given a control mixture followed by terminal `Measure`, when canonical
   execution runs, then a dedicated control executor is used and the legacy
   AST body is not entered.
4. Given an unmeasured control State, when `Mix` executes, then all eligible
   branches remain in the joint until terminal measurement.

## Phase boundary

Phase 1 creates only this failing acceptance contract. Phase 2 will add the
minimum control-plan projection and executor. Nested control, dynamic lanes,
and target-specific control lowering remain separate issues.

## Phase 1 Red result

- Added `tests/test_liss_0495_evaluator_control_mixture_plan_red.py`.
- Red verification: **3 failed, 1 passed**, with no collection errors. The
  failures expose missing control-family classification, control/branch
  provenance projection, and the dedicated executor.
- No production implementation was changed for this issue.

Human review of the Red contract is required before Phase 2 Green.

## Phase 2 Green result

- Added `RuntimeControlNode` with canonical control source ID, branch rules,
  authority, and provenance.
- Runtime plans containing canonical `WhenExpr` nodes are classified as
  `control_mixture`.
- Added `_execute_control_mixture_plan`; canonical control mixtures use the
  dedicated entry while retaining existing joint-mixture and terminal-measure
  mechanics.
- Reviewed Red tests were unchanged.
- Verification: LISS-0495 **4 passed**; related runtime/API regressions
  **26 passed**; `py_compile` and `git diff --check` passed.
- Next step: Phase 3 refactor review. Nested and dynamic control remain out of
  scope.

## Phase 3 result

- Shared Runtime Plan type/family/payload validation is now centralized for
  pure transformation and control-mixture executors.
- Existing State/Measure execution mechanics and the explicit unsupported-family
  fallback are unchanged.
- Reviewed assertions and runtime behavior were unchanged.
- Verification: LISS-0495 plus related runtime/API/port regressions **55
  passed**; `py_compile` and `git diff --check` passed.

### 変更の要約 (PR Summary)

- **何を目的として何を変更したか**: plan executorごとの重複検証を共通化し、
  canonical familyの検証責務を一箇所に集約した。

### 残存リスク・検証の溝 (Verification Gap)

- **AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
  nested/dynamic controlはまだこのexecutorの対象ではない。
- **人間がコードレビューで重点的に見るべきポイント**: control-mixtureが
  Stateをterminal Measure前にcollapseせず、unsupported familyが明示的に
  legacy fallbackへ留まっていること。

Process review: no operating-contract deviation or operational problem found.
