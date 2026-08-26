# LISS-0366: migrate remaining misc evolve tests to real Time units (WP-0096 work unit 8, final)

## Metadata

- Local issue ID: LISS-0366
- Status/phase: **complete** (2026-08-08) — PR
  [#451](https://github.com/nn0cl/staqex/pull/451) merged, commit
  `31a9bd5`
- Type: test-fixture-only migration (2 files under `tests/`); no
  Kernel source change, no example content
- Priority: P3
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: [WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
  work unit 8 (final)
- Parent: [WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0366-misc-duration-migration`
- GitHub Issue / PR: [#451](https://github.com/nn0cl/staqex/pull/451)
  (merged, `31a9bd5`)

## Design decision

Migrates the last 2 `EVOLVE_UNRESOLVED_UNIT_ERROR` failures in the
entire `tests/` suite — `test_operator_pauli_atom_call_parse_red.py`
(1 case) and `test_when_ket_prepare_arms_red.py` (1 case). Completing
this Issue closes [WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
entirely: every test failure tracked since the ADR 0195 real-ℏ
migration (WP-0095) will be resolved, restoring `main` to a fully
green `pytest tests/ -q` for the first time since 2026-08-05.

Applies the same `K = 1.0545718e-19` (= `ℏ / 1fs`) scale / `.fs`-suffix
conversion as every prior work unit, live-verified before drafting:

- `test_operator_pauli_atom_call_parse_red.py::test_bare_pauli_
  product_hamiltonian_runs_on_sv_simulator`: `_BARE_ZZ_PROGRAM`'s bare
  `Operator H = Z[0] * Z[1]` → `1.0545718e-19 * (Z[0] * Z[1])`
  (paren-wrap, same shape as LISS-0360's `_INDEXED_PAULI_OUTSIDE_
  BINDER`); `for 0.1` → `for 0.1.fs`. Live-verified the shared
  currently-passing `test_bare_pauli_product_hamiltonian_emits_qasm`
  (QASM emission, compile-time-only) is unaffected.
- `test_when_ket_prepare_arms_red.py::test_when_ket_prepare_zero_and_
  plus_runs`: `_PREPARE_PLUS`'s `Operator H = Z + 0.25 * X` (a sum of a
  bare atom and an already-scaled atom) → `1.0545718e-19 * Z +
  2.6364295e-20 * X` (both terms scaled, no restructuring needed since
  neither `Z` nor `X` alone is a tensor product); `for 0.35` →
  `for 0.35.fs`.

## Explicitly out of scope

- Nothing further — this is WP-0096's final work unit.

## Acceptance reference

```gherkin
Feature: the last remaining evolve tests use real Time units

  Scenario: each migrated test passes with behavior unchanged
    Given the 2 cases across the 2 files listed above, migrated with
      the K-scale/`.fs`-duration conversion
    When run
    Then each produces the same status result as originally intended
      pre-ADR-0195 (no EVOLVE_UNRESOLVED_UNIT_ERROR)

  Scenario: main returns to a fully green pytest suite
    Given every WP-0096 work unit 1-8 merged
    When `pytest tests/ -q` runs
    Then it reports 0 EVOLVE_UNRESOLVED_UNIT_ERROR failures (the
      52-failure ADR-0195 regression tracked since 2026-08-05 is fully
      closed)
```

## Verification plan for this design intake (not shipped as a test)

Both edits live-verified in isolation before this Issue was drafted.
Full `pytest tests/ -q` regression, diffed against the current baseline
(2 failed, 1306 passed), confirming these are the last 2 cases and the
suite returns to 0 known `EVOLVE_UNRESOLVED_UNIT_ERROR` failures.
`spec_verification` expected unchanged (161/161).

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `XS` — 2 files, 2 cases, both patterns already established in
  prior work units.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red: confirmed the final 2 cases already fail on `main`
      for the documented `EVOLVE_UNRESOLVED_UNIT_ERROR` reason
      (pre-existing tests, no new test file needed); the other 6 tests
      in these 2 files already passed unchanged.
- [x] Phase 2 Green: both edits applied exactly as planned. All 8
      tests across the 2 files pass.
- [x] Phase 3 Refactor: WP-0096 marked **complete** — all 8 work units
      merged; reviewer empathy summary below.
- [x] Full regression: `pytest tests/ -q` → **1308 passed, 0 failed** —
      `main` returns to a fully green suite for the first time since
      the ADR 0195 real-ℏ migration began (2026-08-05); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: WP-0096の最終作業単位として、残る
2件の`EVOLVE_UNRESOLVED_UNIT_ERROR`失敗を確立済みの`K`スケール変換で
実`Time`単位へ移行した。これにより、ADR 0195（実ℏ移行、2026-08-05
開始）以来`main`が抱えていた既知・追跡済みの52件の回帰失敗が全て
解消され、`pytest tests/ -q`が完全グリーン（1308 passed, 0 failed）
に戻った。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 特になし。両ケースとも既に確立されたパターン（裸のテンソル積の
  括弧ラップ、既存係数と裸atomが混在する和の各項スケーリング）を
  そのまま適用した、低リスクな変更。

**人間がコードレビューで重点的に見るべきポイント**:
- WP-0096全体を通して8つの作業単位に分割して段階的に進めたが、
  最終的な52件の移行が、それぞれの作業単位のIssueファイルに記録
  された設計判断（`H*t/ℏ`保存の恒等式、各ファイルの具体的な変換）
  で正しく裏付けられているか、必要であれば`docs/work-plans/
  WP-0096-tests-real-hbar-duration-migration.md`を通覧して確認
  いただきたい。

## Non-goals

- None — WP-0096's final work unit.
