# LISS-0346: migrate `S01_quantum_disaster_response/main_morning_collect` to real units (WP-0095 work unit 14)

## Metadata

- Local issue ID: LISS-0346
- Status/phase: **complete** (2026-08-06) — PR
  [#408](https://github.com/nn0cl/staqex/pull/408) merged, commit
  `c1ab33f`
- Type: Feature Path (example content only —
  `examples/showcase/S01_quantum_disaster_response/main_morning_collect.sqx`;
  no Kernel change)
- Priority: P1
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md)
  work unit 14 — third of the 5 locked S01 files, reuses
  `ops_energy_scale()` (LISS-0345) for a single coefficient-1
  Hamiltonian, the simplest remaining case (one `evolve`, one literal
  duration, no struct-coefficient Hamiltonian)
- Parent: [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
- Depends on: [LISS-0345](LISS-0345-s01-lattice-four-real-unit-migration.md)
  (introduces `ops_energy_scale.sqx` and confirms the two call-site
  constraints this Issue reuses)
- Blocks: none within WP-0095
- Branch: `feature/liss-0346-s01-morning-collect-real-unit-migration`
- GitHub Issue / PR: [#408](https://github.com/nn0cl/staqex/pull/408)
  (merged, `c1ab33f`)

## Design decision

Lock-boundary check already covered by LISS-0344's survey (value-
internal retype only, no scope/story/coverage change) — not repeated
per-file.

`main_morning_collect.sqx` has `Operator H = Z` (a bare Pauli letter
assigned to an intermediate `Operator`-typed variable), then `evolve
status under H for 0.4`. Confirmed during LISS-0344's survey this does
**not** hit the legacy bare-Pauli-letter fast path (that path requires
the evolve clause to *literally* write `under Z`, not a `Var` that
happens to hold the value of `Z`) — it goes through the general
real-ℏ-divided matrix-exponential path with an implicit coefficient of
`1`, confirmed live to fail: `RUNTIME_ERROR: evolve magnitude
|H*t/hbar| ~= 2**62 exceeds the sparse evolution step budget`.

**Adopted fix**: reuse `ops_energy_scale()` (LISS-0345), applying the
two call-site constraints that Issue confirmed: bind the bare `Z` to
its own `Operator` variable first (`Operator H_raw = Z`), then `Operator
H = scale * H_raw` (an inline `scale * Z` was not tested and is not
assumed to work — pre-binding is the confirmed-working pattern); and
declare the duration as its own `Time` variable (`Time dur = 0.4.fs`),
not an inline unit-suffixed literal in the `for` clause.

## Intent

1. Import `ops_energy_scale` (parent-relative
   `..physics.ops_energy_scale`, matching `main_lattice_four.sqx`'s
   import style).
2. `Energy scale = ops_energy_scale()`.
3. `Operator H = Z` → `Operator H_raw = Z` then `Operator H = scale *
   H_raw`.
4. `evolve status under H for 0.4` → declare `Time dur = 0.4.fs`, then
   `... for dur`.

## Explicitly out of scope

- Any Kernel change.
- `ops_energy_scale.sqx` itself (unchanged, reused as-is).
- The remaining 2 S01 files (independent Issues, sequenced next:
  `main_day2_recovery`, `main_disaster_response`).

## Acceptance reference

```gherkin
Feature: S01 main_morning_collect uses real physical units

  Scenario: the migrated example compiles and runs to a real terminal measurement
    Given the migrated main_morning_collect.sqx
    When it is compiled and run with a fixed seed
    Then it compiles without EVOLVE_UNRESOLVED_UNIT_ERROR, RUNTIME_ERROR, or any hard diagnostic
    And it reaches a non-vacuum terminal measurement
```

## Verification plan for this design intake (not shipped as a test)

Confirmed live during LISS-0344's survey: `Operator H = Z` evolved
under real ℏ with a human-scale duration fails
`RUNTIME_ERROR: evolve magnitude |H*t/hbar| ~= 2**62 ...`. The
`ops_energy_scale()`-wrapped, pre-bound pattern is the same one
LISS-0345 already shipped and verified end-to-end for two other
coefficient-1 Hamiltonians.

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-06
- Size: `XS` — one example file, one Hamiltonian, one duration, direct
  reuse of LISS-0345's already-shipped pattern and constraints.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0346_s01_morning_collect_real_unit_migration_red.py`
      added. Failed for the documented reason
      (`EVOLVE_UNRESOLVED_UNIT_ERROR` at runtime on the bare `for 0.4`
      duration).
- [x] Phase 2 Green: `.sqx` rewritten. 1/1 passed on the first attempt
      — LISS-0345's confirmed pattern (pre-bind before `scale *`,
      duration as its own `Time` variable) applied directly with no
      new findings.
- [x] Phase 3 Refactor: no further change needed; reviewer empathy
      summary below.
- [x] Full regression: `pytest tests/ -q` → 1218 passed, 55 failed
      (unchanged failure count vs. LISS-0345's 55, no new failures — +1
      is this Issue's own new test); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged — this file isn't exercised by any SV suite);
      `git diff --check` → clean.
- [x] WP-0095 work unit 14 row updated.

## Reviewer empathy summary

**何を目的として何を変更したか**: S01の`main_morning_collect.sqx`の
`Operator H = Z`（係数1のbare Pauli Z）に、共有関数`ops_energy_scale()`
（LISS-0345で導入済み）を乗算し、実ℏ下で物理的に意味のある回転角に
した。durationも`Time`型変数として明示化。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 特になし。LISS-0345で確立・検証済みの「工場結果を一度ローカル変数に
  束縛してからscaleを乗算する」パターンと「durationを別名Time変数に
  する」パターンをそのまま適用し、1回でGreenに到達した。

**人間がコードレビューで重点的に見るべきポイント**:
- 特になし（LISS-0345と同一パターンの単純な再適用）。

## Non-goals

- Kernel changes.
- The remaining 2 S01 files (separate Issues).
