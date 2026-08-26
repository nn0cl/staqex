# LISS-0345: migrate `S01_quantum_disaster_response/main_lattice_four` to real units (WP-0095 work unit 13)

## Metadata

- Local issue ID: LISS-0345
- Status/phase: **complete** (2026-08-06) — PR
  [#406](https://github.com/nn0cl/staqex/pull/406) merged, commit
  `1c1b2c6`
- Type: Feature Path (example content — new shared
  `physics/ops_energy_scale.sqx` +
  `examples/showcase/S01_quantum_disaster_response/main_lattice_four.sqx`;
  no Kernel change)
- Priority: P1
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md)
  work unit 13 — second of the 5 locked S01 files, chosen as the
  simplest file that needs the `ops_energy_scale()` design (2
  coefficient-1 Hamiltonians, both literal durations, no computed
  duration expressions)
- Parent: [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
- Depends on: [LISS-0344](LISS-0344-s01-fuel-search-real-unit-migration.md)
  (settled the `ops_energy_scale()` design this Issue implements)
- Blocks: none within WP-0095 (subsequent S01 files reuse
  `ops_energy_scale()` once it exists here, but are otherwise
  independent)
- Branch: `feature/liss-0345-s01-lattice-four-real-unit-migration`
- GitHub Issue / PR: [#406](https://github.com/nn0cl/staqex/pull/406)
  (merged, `1c1b2c6`)

## Design decision

Lock-boundary check already covered by LISS-0344's survey (value-
internal retype only, no scope/story/coverage change) — not repeated
per-file.

`main_lattice_four.sqx` imports `damage_hamiltonian_four()` and
`basis_zone_sum()` from `grid/block_costs.sqx` — both build an
`Operator` via `sum(...)` with an implicit coefficient of `1` (no
scalar multiplier). Confirmed live (LISS-0344's survey) that evolving
these under real ℏ with any human-scale duration fails closed:
`RUNTIME_ERROR: evolve magnitude |H*t/hbar| ~= ... exceeds the sparse
evolution step budget`.

**Adopted fix** (per LISS-0344's confirmed design): add
`examples/showcase/S01_quantum_disaster_response/physics/ops_energy_scale.sqx`,
a single new file exporting `pub fn ops_energy_scale() -> Energy {
return 1.0.eV to J }`, with a disclosure comment adapted from
A05_qaoa_portfolio's own honesty wording. `main_lattice_four.sqx`
imports it (parent-relative `..physics.ops_energy_scale`, matching the
file's existing `..grid.block_costs` import style — ADR 0183), binds
`Energy scale = ops_energy_scale()` once, and wraps both Hamiltonian
assignments as `scale * H_raw` (binding each factory call's result to
its own local `Operator` variable first — **found live during Green**:
`scale * damage_hamiltonian_four()` inline fails
`RUNTIME_ERROR: cannot compile sparse Pauli for OpCall`, since the
Operator-compiler's scalar-multiplication path only recognizes a `Var`
operand, not a direct function `Call`; the Issue's own original Intent
draft had this wrong, corrected during Green, not a new Kernel bug —
same constraint the LISS-0343/0344 probes already worked around by
pre-binding). No change to
`grid/block_costs.sqx` itself. Both evolve durations (`for 0.15`, `for
0.1`) are already literals, but **found live during Green**: an inline
unit-suffixed literal directly in the `for` clause (`for 0.15.fs`) does
not satisfy the fail-closed check either — `_hamiltonian_evolve_one_step`
only resolves `duration_unit` when `expr.duration` is a `Var`
(confirmed in `compiler/staqex/runtime/evaluator.py`), so the duration
must be a separately-declared `Time`-typed variable referenced by name,
matching every prior WP-0095 example's pattern: `Time dur_h = 0.15.fs`
/ `Time dur_basis = 0.1.fs`, then `evolve ... for dur_h` / `for
dur_basis`.

## Intent

1. New file `physics/ops_energy_scale.sqx`: `pub fn ops_energy_scale()
   -> Energy { return 1.0.eV to J }` + disclosure comment.
2. `main_lattice_four.sqx`:
   - Import `ops_energy_scale` (parent-relative).
   - `Energy scale = ops_energy_scale()`.
   - `Operator H = damage_hamiltonian_four()` → bind the factory result
     to `Operator H_raw` first, then `Operator H = scale * H_raw`
     (inline `scale * damage_hamiltonian_four()` fails — see design
     decision).
   - `Operator H_basis = basis_zone_sum()` → same pre-binding pattern
     (`H_basis_raw`, then `scale * H_basis_raw`).
   - `evolve (a, b, c, d) under H for 0.15` → declare `Time dur_h =
     0.15.fs`, then `... for dur_h`.
   - `evolve (a, b) under H_basis for 0.1` → declare `Time dur_basis =
     0.1.fs`, then `... for dur_basis`.

## Explicitly out of scope

- Any Kernel change.
- `grid/block_costs.sqx`'s own internals (untouched — confirmed live
  the `scale * <factory call>()` wrapper at the call site is
  sufficient).
- The remaining 3 S01 files (independent Issues, sequenced next:
  `main_morning_collect`, `main_day2_recovery`,
  `main_disaster_response`).

## Acceptance reference

```gherkin
Feature: S01 main_lattice_four uses real physical units

  Scenario: the migrated example compiles and runs to a real terminal measurement
    Given the migrated main_lattice_four.sqx and the new ops_energy_scale.sqx
    When it is compiled and run with a fixed seed
    Then it compiles without EVOLVE_UNRESOLVED_UNIT_ERROR, RUNTIME_ERROR, or any hard diagnostic
    And it reaches a non-vacuum terminal measurement
```

## Verification plan for this design intake (not shipped as a test)

Confirmed live during LISS-0344's survey: `scale * damage_hamiltonian_four()`
and the equivalent `scale * basis_zone_sum()` pattern compile and evolve
to a real, non-degenerate measurement (not a `RUNTIME_ERROR`, not a
trivial near-identity rotation) with `1eV`/`fs`-scale values.

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-06
- Size: `S` — one new small shared file + one example file with 2
  Hamiltonian call sites and 2 literal-duration retypes.
- Route: direct implementation by this session.
- Confidence: high — the exact pattern was live-verified during
  LISS-0344's design intake before this Issue was drafted.

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0345_s01_lattice_four_real_unit_migration_red.py`
      added. Failed for the documented reason
      (`EVOLVE_UNRESOLVED_UNIT_ERROR` at runtime on the bare `for 0.15`
      duration).
- [x] Phase 2 Green: `physics/ops_energy_scale.sqx` added;
      `main_lattice_four.sqx` rewritten. **Found and corrected two
      wrinkles in this Issue's own Intent draft during Green (not new
      Kernel bugs, both already flagged as open questions in the design
      decision and resolved by testing directly)**: (1) `scale *
      <factory call>()` inline fails `RUNTIME_ERROR: cannot compile
      sparse Pauli for OpCall` — the Operator-compiler's scalar
      multiplication only recognizes a `Var` operand, not a direct
      `Call`; fixed by pre-binding each factory's result to its own
      local `Operator` variable before multiplying by `scale`. (2) an
      inline unit-suffixed literal directly in the `for` clause (`for
      0.15.fs`) does not satisfy the fail-closed duration check either
      — `_hamiltonian_evolve_one_step` only resolves `duration_unit`
      when `expr.duration` is a `Var`; fixed by declaring `Time dur_h`/
      `Time dur_basis` variables and referencing them by name, matching
      every prior WP-0095 example's pattern. 1/1 passed after both
      corrections.
- [x] Phase 3 Refactor: no further change needed; reviewer empathy
      summary below.
- [x] Full regression: `pytest tests/ -q` → 1217 passed, 55 failed
      (unchanged failure count vs. LISS-0344's 55, no new failures — +1
      is this Issue's own new test); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged — this file isn't exercised by any SV suite);
      `git diff --check` → clean.
- [x] WP-0095 work unit 13 row updated.

## Reviewer empathy summary

**何を目的として何を変更したか**: S01の`main_lattice_four.sqx`の
2つの係数1 Hamiltonian（`damage_hamiltonian_four()`、
`basis_zone_sum()`）に、新規共有関数`ops_energy_scale()`
（1.0 eV相当、A05パターンのarbitrary units honesty category）を
乗算し、実ℏ下で物理的に意味のある回転角にした。`grid/block_costs.sqx`
自体は無変更。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 本Issueの設計段階（LISS-0344の調査中）で確認したライブプローブでは
  `scale * <関数呼び出し>`の直接記述が動作することを確認していたが、
  実際にIntentドラフトを書く際に誤って`Operator H = scale *
  damage_hamiltonian_four()`という「呼び出しを直接乗算」の形で
  記述してしまっていた。Green実装時に実際にコンパイル・実行して
  `RUNTIME_ERROR: cannot compile sparse Pauli for OpCall`を確認し、
  正しいパターン（工場関数の戻り値を一度ローカル変数に束縛してから
  乗算）に訂正した。
- 同様に、`evolve ... for 0.15.fs`という行内サフィックス記法が
  duration解決チェックを満たすと誤って想定していたが、実際には
  `expr.duration`が`Var`である場合のみ`duration_unit`が解決される
  実装であることを確認し、B04/B07と同じ「別名Time変数を宣言してから
  参照する」パターンに訂正した。いずれも新規Kernelバグではなく、
  設計ドラフト作成時の想定ミスをGreenフェーズでの実行確認により
  修正したもの。

**人間がコードレビューで重点的に見るべきポイント**:
- `H_raw`/`H_basis_raw`という中間変数名が、今後このパターンを再利用
  する残り3ファイル（morning_collect/day2_recovery/disaster_response）
  でも一貫して使われるか。

## Non-goals

- Kernel changes.
- The remaining 3 S01 files (separate Issues).
