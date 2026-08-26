# LISS-0377: `measure <Call>()` skips mixed/POVM path (narrow Var-only dispatch)

## Metadata

- Local issue ID: LISS-0377
- Status/phase: **complete** (2026-08-08) — PR
  [#473](https://github.com/nn0cl/staqex/pull/473) merged, commit
  `3b2d3ad`
- Type: Kernel bug fix (`compiler/staqex/measurement.py`,
  `compiler/staqex/runtime/evaluator.py`); no example content
- Priority: P2 (genuinely silent wrong output with `status=succeeded`:
  empty marginal / missing `POVM_DOMAIN_MISMATCH`)
- Initial planning size: `S`
- Owner / agent: Cursor (Claude process handoff, sixth architectural
  audit)
- Program: standalone Kernel fix, first candidate from the sixth
  architectural audit round (narrow AST-shape dispatch)
- Parent: none
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0377-measure-call-mixed-dispatch`
- GitHub Issue / PR: [#473](https://github.com/nn0cl/staqex/pull/473)
  (merged, `3b2d3ad`)

## Design decision

Live-verified (`compiled.ok`-first / `run_source`):

| Case | status | `POVM_DOMAIN_MISMATCH` | marginal / `state_type` |
|------|--------|------------------------|-------------------------|
| `measure rho with z` (Var, match) | succeeded | absent | `{0:0.25,1:0.75}` / DensityState |
| `measure make() with z` (Call, match) | succeeded | absent | **`{}` / None** (before fix) |
| `measure rho with p` (Var, mismatch) | failed | present | — |
| `measure make() with p` (Call, mismatch) | **succeeded** | **absent** (before fix) | **`{}` / None** |

Root cause (same narrow-AST-shape-dispatch category as LISS-0357–0376):

1. `measurement.py` — `POVM_DOMAIN_MISMATCH` only when
   `isinstance(statement.expr, Var)` (domain looked up in the local
   `states` map). A zero-arg user `Call` whose declared return type is
   `DensityState<T>` / `State<T>` is never checked.
2. `runtime/evaluator.py` — mixed terminal measure only when
   `isinstance(expr, Var) and name in mixed_states`. A Call falls
   through to `_measure` on the Joint, which yields vacuum / empty
   marginal while still reporting success.

**Adopted fix**:

1. Static: `_measure_source_domain` resolves a zero-arg `Call` callee
   to a `FunDecl` return type `State<T>` / `DensityState<T>` and feeds
   the existing POVM domain comparison.
2. Runtime: `_mixed_state_for_measure` evaluates a zero-arg
   DensityState-returning function’s `return DensityState(...)` via
   `density_from_call` and routes through `_measure_mixed`.

## Explicitly out of scope

- Attr / method-call measure targets (`box.rho`)
- Non-zero-arg user Calls as measure targets
- `DensityState rho = make()` bind construction (still unsupported)
- Candidates 2–4 from the sixth audit round (separate Issues)

## Acceptance reference

```gherkin
Feature: measure of a DensityState-returning Call matches the Var path

  Scenario: domain-matched Call measures like a named DensityState
    Given `fn make() -> DensityState<Qubit> { return DensityState(RawMatrix(...)) }`
      and `POVM<Qubit> z = ComputationalBasis()`
    When `measure make() with z` runs
    Then status is succeeded and the marginal matches the equivalent
      `measure rho with z` named-bind case

  Scenario: domain-mismatched Call is rejected like a named DensityState
    Given the same `make()` and `POVM<Position> p = ComputationalBasis()`
    When `measure make() with p` is compiled/run
    Then status is failed and diagnostics include POVM_DOMAIN_MISMATCH
```

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0377_measure_call_mixed_dispatch_red.py`
      (4 cases). Call match failed with empty `{}` marginal; Call
      mismatch failed asserting `failed` / `POVM_DOMAIN_MISMATCH`
      (status was `succeeded`). Named regression guards already passed.
- [x] Phase 2 Green: `measurement.py` domain resolution for zero-arg
      Call return types; `evaluator.py` `_mixed_state_for_measure` +
      both measure sites. All 4 Issue tests pass.
- [x] Phase 3 Refactor: Issue + open-work-register + reviewer summary.
- [x] Full regression: `pytest tests/ -q` → **1338 passed, 0 failed**;
      `spec_verification` → **161/161** (100%, Gate: PASS);
      `git diff --check` → clean.

### 変更の要約 (PR Summary)

**何を目的として何を変更したか**: 第6回アーキテクチャ監査の第1候補。
`measure make()`（`DensityState` を返すゼロ引数 Call）が、名前付き
`measure rho` と異なり、POVM ドメイン検査をすり抜け、Joint 真空測定で
空 marginal のまま `succeeded` になるサイレント不具合を修正した。
静的側は FunDecl の戻り型ドメインを既存の `POVM_DOMAIN_MISMATCH` に
接続し、実行側は `density_from_call` → `_measure_mixed` に載せた。

### 残存リスク・検証の溝 (Verification Gap)

- **AIが推測で補った部分**: ゼロ引数・`return DensityState(...)` 形に
  限定。`Ensemble(...)` 直返し、非ゼロ引数、Attr 測定対象、
  `DensityState rho = make()` バインドは未対応（スコープ外として記録）。
- **人間がコードレビューで重点的に見るべきポイント**:
  `_measure_source_domain` / `_mixed_state_for_measure` の形限定が
  受け入れシナリオと一致しているか；deferred-measure 経路の両方の
  Call サイトが同じヘルパーを通っているか。
