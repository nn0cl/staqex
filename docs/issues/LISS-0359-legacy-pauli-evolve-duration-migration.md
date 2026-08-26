# LISS-0359: migrate legacy single-Pauli-letter `evolve` tests to real Time units (WP-0096 work unit 1)

## Metadata

- Local issue ID: LISS-0359
- Status/phase: **complete** (2026-08-08) — PR
  [#437](https://github.com/nn0cl/staqex/pull/437) merged, commit
  `9eacfc8`
- Type: test-fixture-only migration (`tests/test_evolve_until_runtime_red.py`,
  `tests/test_qudit_d3_sv_slice_b_red.py`); no Kernel source change, no
  example content
- Priority: P3
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: [WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
  work unit 1 (lowest-risk group)
- Parent: [WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0359-legacy-pauli-evolve-duration-migration`
- GitHub Issue / PR: [#437](https://github.com/nn0cl/staqex/pull/437)
  (merged, `9eacfc8`)

## Design decision

Migrates the 4 `EVOLVE_UNRESOLVED_UNIT_ERROR` failures in
`test_evolve_until_runtime_red.py` (3 cases) and
`test_qudit_d3_sv_slice_b_red.py` (1 case) — both use the legacy
single-Pauli-letter `evolve ψ under X for t` path
(`runtime/quantum_ops.py::pauli_u`), which uses the *canonical-seconds*
magnitude of `t` directly as the rotation angle, with no `ℏ` reference.

**Correction to WP-0096's own investigation, caught before any test was
edited**: the investigation document originally said `.s`/`.fs` were
interchangeable for this case. Live-verifying immediately before this
Issue's Red phase found this false: `.fs` canonicalizes to ×1e-15
before reaching `pauli_u`, silently producing a near-zero rotation.
`evolve psi under X for 1.5707963267948966.s` reproduces the original
`for pi / 2.0` measurement (`1`) exactly; the same numeral with `.fs`
instead produces a different measurement (`0`). The suffix must be
`.s` specifically (seconds, the canonical `Time` unit, scale factor 1)
— confirmed and corrected in `WP-0096` before this Issue's Plan
approval was requested.

**Conversion applied**:
- `test_qudit_d3_sv_slice_b_red.py`: `evolve s under I for 0.0` →
  `evolve s under I for 0.0.s` (Identity short-circuits before
  `pauli_u` is reached; magnitude is irrelevant here, but `.s` is used
  for consistency with the rest of this work unit).
- `test_evolve_until_runtime_red.py`: `for pi / 2.0` (3 occurrences)
  and `for 1` (1 occurrence) cannot take a unit suffix directly — the
  suffix grammar only attaches to a literal, not to an arbitrary
  expression. Pre-computed `math.pi / 2 == PRELUDE_CONSTANTS["pi"] /
  2` (bit-for-bit, confirmed `prelude.py` defines `pi = math.pi`) as
  the literal `1.5707963267948966.s`; `for 1` → `for 1.s`.

No Kernel source change. No example content change.

## Explicitly out of scope

- Any other WP-0096 work unit (general-Hamiltonian conversion, `.fs`
  scale-factor case).
- Any Kernel change to how unit suffixes attach to non-literal
  expressions (a real gap — the suffix grammar requiring a literal
  operand meant `pi / 2.0` couldn't carry a suffix directly — but
  fixing that is a Kernel-source change outside this test-fixture-only
  Issue's scope; noted for a future Issue if it recurs).

## Acceptance reference

```gherkin
Feature: legacy single-Pauli-letter evolve tests use real Time units

  Scenario: each migrated test passes with behavior unchanged
    Given the 4 cases in test_evolve_until_runtime_red.py and
      test_qudit_d3_sv_slice_b_red.py, migrated to `.s`-suffixed durations
    When run
    Then each produces the same status/assertions as originally intended
      pre-ADR-0195 (no EVOLVE_UNRESOLVED_UNIT_ERROR)
```

## Verification plan for this design intake (not shipped as a test)

These are existing tests, not new ones — Red is "already failing on
`main` for the documented `EVOLVE_UNRESOLVED_UNIT_ERROR` reason" (no
new Red test file needed). Green is the 4 duration edits. Full `pytest
tests/ -q` regression, diffed against the current baseline (52 failed,
1256 passed), confirming exactly these 4 cases move from FAIL to PASS
and nothing else changes. `spec_verification` expected unchanged
(161/161).

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `XS` — 4 duration-literal edits across 2 files, no Kernel
  change, behavior-preservation verified live per case before editing.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red: confirmed the 4 target cases already fail on `main`
      for the documented `EVOLVE_UNRESOLVED_UNIT_ERROR` reason (no new
      test file needed — these are pre-existing tests).
- [x] Phase 2 Green: 4 duration-literal edits applied
      (`test_qudit_d3_sv_slice_b_red.py`: `for 0.0` → `for 0.0.s`;
      `test_evolve_until_runtime_red.py`: 3× `for pi / 2.0` →
      `for 1.5707963267948966.s`, 1× `for 1` → `for 1.s`). All 8 tests
      in both files pass.
- [x] Phase 3 Refactor: WP-0096 work unit 1 marked complete; reviewer
      empathy summary below.
- [x] Full regression: `pytest tests/ -q` → 1260 passed, 48 failed
      (exactly -4 vs. the established baseline — the 4 target cases
      moved from FAIL to PASS, confirmed via full failure-list
      comparison that nothing else changed); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: WP-0096作業単位1として、レガシー
単一Pauli文字`evolve`経路（`pauli_u`、ℏを参照しない）を使う4件の
テストケースを、ADR 0195準拠の実`Time`単位へ移行した。Kernel本体は
一切変更していない。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- WP-0096の調査ドラフトが当初「`.s`/`.fs`どちらでも良い」と誤って
  記載していたが、本Issueの実装直前にライブ検証で誤りを発見した
  （`.fs`はカノニカル秒への変換係数1e-15が掛かり、意図した回転角と
  異なる結果になる）。コードを一切変更せずにテストを編集する前に
  この誤りに気づけたのは、既存の値を実際に流して確認する
  （`for pi / 2.0`の元の測定結果と、`.s`版・`.fs`版それぞれの測定
  結果を比較する）という、このセッション全体で一貫している検証習慣
  のおかげ。WP-0096自体も本Issueの前に訂正済み。
- `pi / 2.0`のような非リテラル式は単位接尾辞を直接付与できない
  （文法上リテラルにしか付与できない）ため、Python側で
  `PRELUDE_CONSTANTS["pi"]`と完全に同じ値（`math.pi`）を事前計算し、
  リテラルとして埋め込んだ。

**人間がコードレビューで重点的に見るべきポイント**:
- 事前計算したリテラル値（`1.5707963267948966`）が、実行結果
  （`test_hamiltonian_evolve_until_stops_when_predicate_holds`が
  succeededになること）で間接的に検証されているが、桁落ちなどの
  懸念がないか。

## Non-goals

- Kernel source changes.
- Other WP-0096 work units.
