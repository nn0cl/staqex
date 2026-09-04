# LISS-0494: Evaluator pure-transformation runtime-plan family

| Field | Value |
|---|---|
| Status | **phase-3-refactor-complete** |
| Phase | phase-3-refactor-complete |
| Parent | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| Predecessor | [LISS-0493](LISS-0493-evaluator-ast-mechanics-retirement.md) |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0493-evaluator-ast-mechanics-retirement) |
| Scope approval | User approved continuation on 2026-09-01 |
| Architecture approval | Existing LISS-0493 runtime-plan boundary; no new boundary decision |
| Phase 1 Red approval | User approved 2026-09-01 |
| Implementation permission | Phase 3 refactor approved and completed |
| Next approval | Phase 1 Red approval for the next semantic family |

## [DESIGN CHECK]

- **Scope and expected behavior:** define the next runtime-plan family for
  non-destructive State transformations, including direct pushforward and a
  pure unary transformation chain ending in terminal `Measure`.
- **Specifications and files inspected:** LISS-0493, WP-0107, the scientific
  semantic consumer-migration Spec, runtime execution model, evaluator Joint
  primitives, testing strategy, implementation readiness, and process lessons.
- **Component boundaries:** `ScientificSemanticIR` remains the sole semantic
  authority; `RuntimeExecutionPlan` is an internal projection; the evaluator
  consumes a pure-transformation plan and existing Joint pushforward
  primitives. No new port or adapter is needed.
- **Applicable constraints:** Phase 1 Red only; no production implementation,
  AST-mechanics deletion, collapse before terminal Measure, finiteization,
  provider/QPU/AWS, Rust, solver, or public serialization.
- **Decisions and ambiguities:** this issue covers State-preserving transforms
  and unary chains only. `when`, `evolve`, operator/binder lowering,
  function/class runtime migration, and dynamic lanes remain separate. The
  exact plan node payload and lowering mechanics are intentionally left for
  Phase 2 after Red review.
- **Included and omitted context:** included canonical plan identity,
  provenance, evaluator state/pushforward semantics, and terminal measurement;
  omitted provider execution, QASM lowering, continuous systems, and broad
  evaluator rewrite.
- **Verification plan:** the new root acceptance test must fail without the
  pure-transformation plan contract, with no collection errors; existing
  LISS-0493 and evaluator regressions remain unchanged.

## Acceptance scenarios for Phase 1 Red

1. Given a compiled source containing a pure unary State transformation, when
   a runtime plan is built, then it is classified as the
   `pure_transformation` family.
2. Given that plan, when its transformation node is inspected, then input and
   output source node IDs, canonical authority, and provenance are present and
   conserved from the compile-owned semantic IR.
3. Given a pure transformation followed by terminal `Measure`, when canonical
   execution runs, then the plan executor is used and the legacy AST body is
   not entered.
4. Given a pure transformation, when it executes before terminal `Measure`,
   then State remains non-collapsed and the existing terminal measurement
   boundary is preserved.

## Phase boundary

Phase 1 creates only the failing acceptance contract. Phase 2 will add the
minimum plan classification and executor. Phase 3 may extract shared
pushforward mechanics only after unchanged-neighbor evidence.

## Phase 1 Red result

- Added `tests/test_liss_0494_pure_transformation_plan_red.py`.
- Red verification: **3 failed, 1 passed**, with no collection errors. The
  failures expose missing family classification, transformation identity
  fields, and the dedicated executor.
- No production implementation was changed for this issue.

## Phase 2 Green result

- Added explicit `pure_transformation` family classification to the internal
  runtime plan.
- Added transformation input/output source-node identity, authority, and
  provenance fields.
- Added `_execute_pure_transformation_plan`; canonical pure transformations no
  longer use the legacy AST body directly.
- Reviewed Red tests were unchanged.
- Verification: LISS-0494 **4 passed**; related runtime/API regressions
  **22 passed**; `py_compile` and `git diff --check` passed.
- Next step: Phase 3 refactor review. The implementation still shares the
  existing deferred pushforward mechanics with the first family.

## Phase 3 result

- Extracted the shared deferred State/Measure execution into a clearly named
  internal plan executor used by both the first family and pure transformations.
- Preserved the dedicated pure-transformation entry and the explicit legacy
  fallback for unsupported families.
- Reviewed assertions and runtime behavior were unchanged.
- Verification: LISS-0494 plus related runtime/API/port regressions **51
  passed**; `py_compile` and `git diff --check` passed.

### 変更の要約 (PR Summary)

- **何を目的として何を変更したか**: pure-transformation plan executionと
  State/Measure共通実行の責務を分離し、将来のfamily追加時に旧AST経路を
  誤って再利用しにくい命名と構造へ整理した。

### 残存リスク・検証の溝 (Verification Gap)

- **AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
  変換ノードのAST syntax payloadは次family移行まで残るため、意味判定を
  semantic IR以外へ広げないこと。
- **人間がコードレビューで重点的に見るべきポイント**: unsupported family
  が明示的legacy fallbackに限定され、pure transformationがterminal
  Measure前にcollapseしないこと。

Process review: no operating-contract deviation or operational problem found.
