# LISS-0344: migrate `S01_quantum_disaster_response/main_fuel_search` to real units (WP-0095 work unit 12)

## Metadata

- Local issue ID: LISS-0344
- Status/phase: **complete** (2026-08-06) — PR
  [#404](https://github.com/nn0cl/staqex/pull/404) merged, commit
  `2c62100`
- Type: Feature Path (example content only —
  `examples/showcase/S01_quantum_disaster_response/main_fuel_search.sqx`;
  no Kernel change)
- Priority: P1
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md)
  work unit 12 — first of the 5 locked S01 files, chosen as the simplest
  (bare-Pauli-letter form, no Hamiltonian energy-scale question)
- Parent: [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
- Depends on: [LISS-0330](LISS-0330-real-hbar-kernel-primitive.md),
  [LISS-0339](LISS-0339-b04-evolve-not-loops-real-unit-migration.md)
  (identical fix pattern)
- Blocks: none within WP-0095 (the other 4 S01 files are independent —
  see design decision below)
- Branch: `feature/liss-0344-s01-fuel-search-real-unit-migration`
- GitHub Issue / PR: [#404](https://github.com/nn0cl/staqex/pull/404)
  (merged, `2c62100`)

## Design decision

### Lock-boundary check (per WP-0095's explicit flag for S01)

`main_fuel_search.sqx` is a "locked scenario seat" (SE-04/11) per
[`staqex-v1-showcase-mission-lock.md`](../specs/staqex-v1-showcase-mission-lock.md).
This migration changes only the internal representation of an existing
duration value (a unit-satisfying retype, not a value, scenario, or
theme change) — the locked mission's scope, story, and coverage are
untouched. No lock-boundary conflict.

### S01 real-unit migration survey (covers all 5 remaining WP-0095 examples)

Live investigation of all 5 unmigrated S01 files found this program is
more involved than any prior WP-0095 example: 3 of the 5
(`main_lattice_four`, `main_morning_collect`, and 3 of
`main_disaster_response`'s 4 Hamiltonians) reference Hamiltonians with
an *implicit* coefficient of exactly `1` (built via `sum(...)`/
`product(...)` combinators or a bare `Operator H = Z`, no scalar
multiplier) — evolving these under real ℏ with any human-scale duration
produces a numerically meaningless rotation angle. Confirmed live:
`RUNTIME_ERROR: evolve magnitude |H*t/hbar| ~= 2**61 exceeds the sparse
evolution step budget (2**16) -- H and/or t are not physically
plausible real-unit values`. This is presented in full, with the
Adjudicator-agreed resolution, under the design decision of
[LISS-0345](LISS-0345-s01-lattice-four-real-unit-migration.md) (the
first file that needs it) — not repeated per-file. `main_fuel_search`
does **not** need this: its bare-Pauli-letter evolve form (`under X`,
literally naming a Pauli letter at the evolve callsite) hits the
existing legacy fast path (`quantum_ops.py::pauli_u`), the exact same
code path LISS-0339 (B04) already fixed — no Hamiltonian energy-scale
question applies here.

### This Issue's fix

`main_fuel_search.sqx`: `evolve fuel under X for pi / 2.0 until
converged(fuel) max 64` — identical structure to B04
(`evolve psi under Z for pi / 2.0`), confirmed the `until ... max N`
loop wrapper does not change the duration-resolution code path (shared
`_hamiltonian_evolve_one_step`, called once per loop iteration). Same
fix as LISS-0339: declare `Time dur = 1.5707963267948966.s` (canonical
seconds; pre-computed literal since unit suffixes attach only to
literals, not the `pi / 2.0` expression) before the evolve, replacing
the inline `pi / 2.0`.

## Intent

1. `evolve fuel under X for pi / 2.0 until converged(fuel) max 64` →
   declare `Time dur = 1.5707963267948966.s`, then `evolve fuel under X
   for dur until converged(fuel) max 64`.

## Explicitly out of scope

- Any Kernel change.
- The `until ... max 64` convergence-loop mechanism itself.
- The other 4 S01 files (independent Issues:
  [LISS-0345](LISS-0345-s01-lattice-four-real-unit-migration.md)
  `main_lattice_four`, then `main_morning_collect`,
  `main_day2_recovery`, `main_disaster_response`).
- The new shared `ops_energy_scale()` function (introduced by
  LISS-0345, not needed here).

## Acceptance reference

```gherkin
Feature: S01 main_fuel_search uses real physical units

  Scenario: the migrated example compiles and runs to a real terminal measurement
    Given the migrated main_fuel_search.sqx
    When it is compiled and run with a fixed seed
    Then it compiles without EVOLVE_UNRESOLVED_UNIT_ERROR or any hard diagnostic
    And it reaches a non-vacuum terminal measurement
```

## Verification plan for this design intake (not shipped as a test)

Confirmed live: identical structure to B04's already-shipped fix
(`Time dur` literal, bare-Pauli-letter fast path, `until`/`max` loop
transparent to duration resolution).

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-06
- Size: `XS` — one example file, identical pattern to LISS-0339/B04.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0344_s01_fuel_search_real_unit_migration_red.py`
      added. Failed for the documented reason
      (`EVOLVE_UNRESOLVED_UNIT_ERROR` at runtime on the bare `for pi /
      2.0` duration). **Found one test-harness wrinkle, not a Kernel
      bug**: the file's own pre-existing, documented
      `E_QPU_UNSUPPORTED_CAPABILITY` diagnostic (static QPU IR cannot
      represent the dynamic `evolve ... until ... max` loop — unrelated
      to real units) needed adding to the test's soft-diagnostic filter
      alongside the existing `QSEM_*`/`MULTI_REGISTER_INDEX_AMBIGUOUS`
      exclusions.
- [x] Phase 2 Green: `.sqx` rewritten (`Time dur =
      1.5707963267948966.s` declared, replacing the inline `pi / 2.0`).
      1/1 passed.
- [x] Phase 3 Refactor: no further change needed; reviewer empathy
      summary below.
- [x] Full regression: `pytest tests/ -q` → 1216 passed, 55 failed
      (unchanged failure count vs. LISS-0343's 55, no new failures — +1
      is this Issue's own new test); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged — this file isn't exercised by any SV suite);
      `git diff --check` → clean.
- [x] WP-0095 work unit 12 row updated.

## Reviewer empathy summary

**何を目的として何を変更したか**: S01の`main_fuel_search.sqx`の`evolve
... for pi / 2.0 until ... max 64`を、LISS-0339（B04）と全く同じ
パターンで明示的な`Time dur`宣言に変更した。5つのS01ファイルの事前
調査（本Issueの設計判断セクション、詳細はLISS-0345側）により、
このファイルは係数1のHamiltonianエネルギースケール問題の対象外
（bare-Pauli-letterの高速パスを通るため）と確認済み。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- テスト作成時、このファイル固有の既存
  `E_QPU_UNSUPPORTED_CAPABILITY`診断（`until`ループが静的QPU IRで
  表現できないという、ファイル自身のヘッダーコメントに明記された
  既知の制約）をhard診断として誤検出してしまい、テストのフィルタを
  調整する必要があった。これは今回の実単位移行とは無関係な、
  既存の想定内の挙動であることをファイルのコメントで確認した。

**人間がコードレビューで重点的に見るべきポイント**:
- `Time dur = 1.5707963267948966.s`の数値がpi/2.0の正確な浮動小数点
  表現と一致しているか（LISS-0339と同じ値の取り方）。

## Non-goals

- Kernel changes.
- The remaining 4 S01 files (separate Issues).
