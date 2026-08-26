# LISS-0361: migrate periodic-boundary and acting-space-typing evolve tests to real Time units (WP-0096 work unit 3)

## Metadata

- Local issue ID: LISS-0361
- Status/phase: **complete** (2026-08-08) — PR
  [#441](https://github.com/nn0cl/staqex/pull/441) merged, commit
  `8e44252`
- Type: test-fixture-only migration (2 files under `tests/`); no Kernel
  source change, no example content
- Priority: P3
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: [WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
  work unit 3
- Parent: [WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0361-periodic-boundary-acting-space-duration-migration`
- GitHub Issue / PR: [#441](https://github.com/nn0cl/staqex/pull/441)
  (merged, `8e44252`)

## Design decision

Migrates the 4 `EVOLVE_UNRESOLVED_UNIT_ERROR` failures in
`test_liss0057_periodic_boundary_red.py` (1 case) and
`test_liss0058_acting_space_typing_red.py` (3 cases) — both concern how
`evolve` infers/retains the acting Hilbert-space shape, a related
structural concern per WP-0096's grouping.

Applies the same `K = 1.0545718e-19` (= `ℏ / 1fs`) scale / `.fs`-suffix
(numeral unchanged) conversion as work unit 2, live-verified per
pattern before editing:

- `test_liss0057_periodic_boundary_red.py`: `_ring_source()`'s existing
  coefficient `-1.0 * Z[i] * Z[wrap(i)]` → `-1.0545718e-19 * Z[i] *
  Z[wrap(i)]` (coefficient swap, no restructuring). Live-verified this
  does not disturb `qpu_ir["binder_lowering"]["H"]`'s `expanded_terms`/
  `provenance.accessors` (both currently-passing, non-`evolve`-execution
  tests sharing `_ring_source()` with the one failing test).
- `test_liss0058_acting_space_typing_red.py`: `_program()`'s shared
  duration line only (`for 0.1` → `for 0.1.fs`) — the `operator`
  argument is scaled per call site, not centrally, since one
  currently-passing call (`test_site_free_identity_uses_declared_
  register_shape`, `sum (i in Index<3..1>) { Z[i] }`) never reaches
  `evolve` execution (`compile_source`-only assertion) and is left
  untouched. The 3 failing calls: `_program("I")` →
  `_program("1.0545718e-19 * I")`; `_program("Z[0]")` →
  `_program("1.0545718e-19 * Z[0]")`; the separate inline
  `make_h() -> Operator<QubitRegister<4>> { return Z[0] }` source →
  `return 1.0545718e-19 * Z[0]` (plus its own `for 0.1` → `for 0.1.fs`).
  Live-verified all three still report `{4}` logical qubits (the
  assertion these tests check), confirming the acting-space-shape
  inference these tests exist to guard is unaffected by the
  coefficient's specific value.

None of the 4 target cases' assertions depend on the Hamiltonian's
exact numeric phase (they check structural properties: term count,
accessor provenance, site pairs, or acting-space qubit count) — the
`K`-scale convention is still applied uniformly for consistency with
every other WP-0096 work unit, not because these specific assertions
require it.

## Explicitly out of scope

- Any other WP-0096 work unit.
- `test_liss0058_acting_space_typing_red.py`'s other 3 tests
  (`test_site_free_identity_uses_declared_register_shape`,
  `test_context_free_operator_execution_has_no_one_qubit_fallback`,
  `test_multi_register_operator_is_rejected_explicitly`) — none call
  `evolve` to a successful execution (the latter two assert
  compilation/execution *failure* for unrelated reasons), so none are
  in the failing set and none need editing.

## Acceptance reference

```gherkin
Feature: periodic-boundary and acting-space-typing evolve tests use real Time units

  Scenario: each migrated test passes with behavior unchanged
    Given the 4 cases across the 2 files listed above, migrated with
      the K-scale/`.fs`-duration conversion
    When run
    Then each produces the same status/structural-assertion result as
      originally intended pre-ADR-0195 (no EVOLVE_UNRESOLVED_UNIT_ERROR)

  Scenario: currently-passing, non-evolve-execution tests sharing a
    helper with failing tests are unaffected
    Given test_wrap_is_accepted_as_periodic_index_accessor,
      test_wrap_keeps_the_closing_bond,
      test_wrap_does_not_silently_leave_the_static_register,
      test_next_remains_an_open_boundary_accessor, and
      test_site_free_identity_uses_declared_register_shape
    When run against the modified shared source helpers
    Then all still pass with identical assertions
```

## Verification plan for this design intake (not shipped as a test)

Both edit patterns (coefficient swap, per-call-site operator scaling)
live-verified in isolation before any file was edited, including
confirming the currently-passing, non-evolve-execution tests sharing a
helper remain unaffected. Full `pytest tests/ -q` regression, diffed
against the current baseline (34 failed, 1274 passed), confirming
exactly these 4 cases move from FAIL to PASS and nothing else changes.
`spec_verification` expected unchanged (161/161).

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `XS` — 2 files, ~6 individual edits, each pattern independently
  live-verified before editing.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red: confirmed the 4 target cases already fail on `main`
      for the documented `EVOLVE_UNRESOLVED_UNIT_ERROR` reason
      (pre-existing tests, no new test file needed); the other 7 tests
      in both files already passed unchanged.
- [x] Phase 2 Green: all edits above applied exactly as planned (no
      surprises this time). All 11 tests across the 2 files pass.
- [x] Phase 3 Refactor: no further code change needed; reviewer
      empathy summary below; WP-0096 work unit 3 marked complete.
- [x] Full regression: `pytest tests/ -q` → 1278 passed, 30 failed
      (exactly -4 vs. the established 34-failure baseline, confirmed
      via full failure-list comparison — nothing else changed);
      `python3 tests/spec_verification/run_all.py` → 161/161 (100%,
      Gate: PASS, unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: WP-0096作業単位3として、periodic
boundary（`wrap()`アクセサ）とacting-space型付け（宣言済みレジスタ
形状の保持）に関する2ファイル・4件の`EVOLVE_UNRESOLVED_UNIT_ERROR`
失敗を、確立済みの`K`スケール変換で実`Time`単位へ移行した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 対象4件のアサーションは、Hamiltonianの正確な数値位相ではなく構造的
  性質（項数、accessor provenance、サイト対、acting-spaceの量子ビット
  数）のみを検証していることを確認した。そのため`K`スケーリングは
  正確性のために必須ではなかったが、他の作業単位との一貫性のために
  同じ規約を適用した。
- `test_liss0058_acting_space_typing_red.py`の`_program()`ヘルパーは
  6テストで共有されているが、1テスト（`test_site_free_identity_uses_
  declared_register_shape`）は`compile_source`のみで`evolve`を実行
  しないため、失敗セットに含まれず、そのoperator引数文字列は無変更の
  ままにした。

**人間がコードレビューで重点的に見るべきポイント**:
- 特になし（作業単位2で確立したパターンをそのまま適用した、低リスク
  な変更）。

## Non-goals

- Kernel source changes.
- Other WP-0096 work units.
- The 3 already-passing tests in `test_liss0058_acting_space_typing_red.py`
  noted above.
