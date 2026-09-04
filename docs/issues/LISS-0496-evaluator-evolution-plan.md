# LISS-0496: Evaluator evolution runtime-plan family

| Field | Value |
|---|---|
| Status | **phase-3-refactor-complete** |
| Phase | phase-3-refactor-complete |
| Parent | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| Predecessor | [LISS-0495](LISS-0495-evaluator-control-mixture-plan.md) |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0493-evaluator-ast-mechanics-retirement) |
| Scope approval | User approved continuation on 2026-09-01 |
| Architecture approval | Existing LISS-0493 runtime-plan boundary; no new boundary decision |
| Phase 1 Red approval | User approved 2026-09-01 |
| Implementation permission | Phase 3 refactor approved and completed |
| Next approval | Phase 1 Red approval for the next semantic family |

## [DESIGN CHECK]

- **Scope and expected behavior:** define a canonical runtime-plan family for
  explicit local `Evolve` state evolution, retaining Hamiltonian, duration,
  source identity, and realization/approximation status.
- **Specifications and files inspected:** LISS-0493–0495, WP-0107, the
  consumer-migration and language Specs, Scientific Semantic IR evolution
  projections, evaluator evolution mechanics, implementation readiness, and
  process lessons.
- **Component boundaries:** canonical semantic IR owns evolution meaning and
  provenance; Runtime Plan projects it; the evaluator will later execute the
  plan through existing local evolution primitives. QASM/target realization
  remains a separate consumer boundary.
- **Applicable constraints:** Phase 1 Red only; no provider/QPU/AWS, Rust,
  solver, hidden discretization, implicit `Realize`, or public serialization.
- **Decisions and ambiguities:** this slice covers explicit local evolution
  only. Target-specific Suzuki/QASM realization, continuous/open-system
  evolution, binders, and dynamic lanes remain separate. Unsupported or
  unresolved realization must fail closed without partial plan output.
- **Included and omitted context:** included `EvolveExpr`, explicit evolution
  metadata, terminal measurement, and local evaluator behavior; omitted target
  providers and unrelated plan families.
- **Verification plan:** add only root Red tests for classification,
  source/provenance and realization evidence, dedicated executor routing, and
  non-collapse until terminal Measure.

## Acceptance scenarios for Phase 1 Red

1. Given a compiled explicit local `Evolve` program, when a runtime plan is
   built, then it is classified as `evolution`.
2. Given that plan, when its evolution node is inspected, then input/output
   source node IDs, Hamiltonian/duration evidence, authority, provenance, and
   realization status are conserved.
3. Given local evolution followed by terminal `Measure`, when canonical
   execution runs, then a dedicated evolution executor is used and the legacy
   AST body is not entered.
4. Given exact local evolution, when it executes before terminal `Measure`, then
   State remains non-collapsed and no implicit target finiteization occurs.

## Phase boundary

Phase 1 creates only the failing acceptance contract. Phase 2 will add the
minimum evolution-plan projection and local executor. Target/QASM realization,
continuous evolution, and solver policy remain separate.

## Phase 1 Red result

- Added `tests/test_liss_0496_evaluator_evolution_plan_red.py`.
- Red verification: **3 failed, 1 passed**, with no collection errors. The
  failures expose missing evolution-family classification, evolution source
  and realization fields, and the dedicated executor.
- The initial fixture used an invalid `Evolve()` body and was corrected to the
  accepted `Operator * State` form before recording the Red result.
- No production implementation was changed for this issue.

Human review of the Red contract is required before Phase 2 Green.

## Phase 2 Green result

- Added `RuntimeEvolutionNode` with evolved State input/output identity,
  Hamiltonian/duration source evidence, authority, provenance, and realization
  status.
- Runtime plans containing canonical `EvolveExpr` nodes are classified as
  `evolution`.
- Added `_execute_evolution_plan` for the bounded local block-evolution slice;
  complex Hamiltonian/propagator and target-specific forms remain an explicit
  legacy fallback until their own mechanics are migrated.
- Reviewed Red tests were unchanged after the valid fixture was selected.
- Verification: LISS-0496 **4 passed**; related evolution/runtime/API
  regressions **36 passed**; `py_compile` and `git diff --check` passed.
- Next step: Phase 3 refactor review. Target realization and broader evolution
  forms remain out of scope.

## Phase 3 result

- Extracted the local-evolution runtime-unit shaping into
  `_evolution_runtime_unit`, keeping compile-time Operator declarations out of
  deferred runtime bind steps.
- Preserved the local evolution executor, target-specific legacy fallback, and
  terminal measurement behavior.
- Reviewed assertions and runtime behavior were unchanged.
- Verification: LISS-0496 plus related evolution/runtime/API regressions **40
  passed**; `py_compile` and `git diff --check` passed.

### 変更の要約 (PR Summary)

- **何を目的として何を変更したか**: local evolution executorの入力整形責務を
  独立ヘルパーへ抽出し、compile-time Operatorとruntime State処理の境界を
  明確化した。

### 残存リスク・検証の溝 (Verification Gap)

- **AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
  複雑なHamiltonian/propagator、Suzuki/QASM、continuous evolutionはまだ
  専用Planの対象ではない。
- **人間がコードレビューで重点的に見るべきポイント**: local exact evolution
  が暗黙のtarget realizationや早期collapseを起こさず、未移行形式だけが
  legacy fallbackへ進むこと。

Process review: no operating-contract deviation or operational problem found.
