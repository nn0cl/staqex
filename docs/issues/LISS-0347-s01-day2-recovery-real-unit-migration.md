# LISS-0347: migrate `S01_quantum_disaster_response/main_day2_recovery` to real units (WP-0095 work unit 15)

## Metadata

- Local issue ID: LISS-0347
- Status/phase: **complete** (2026-08-06) — PR
  [#410](https://github.com/nn0cl/staqex/pull/410) merged, commit
  `cde5191`
- Type: Feature Path (example content only —
  `examples/showcase/S01_quantum_disaster_response/main_day2_recovery.sqx`;
  no Kernel change, no change to the shared `physics/constraint_h.sqx`)
- Priority: P1
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md)
  work unit 15 — fourth of the 5 locked S01 files; the first of the two
  files that build their Hamiltonian from `ConstraintCoeffs` (shared
  with `main_disaster_response`, done last)
- Parent: [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
- Depends on: [LISS-0345](LISS-0345-s01-lattice-four-real-unit-migration.md)
  (introduces `ops_energy_scale.sqx` and confirms the two call-site
  constraints this Issue reuses)
- Blocks: none within WP-0095 (informs
  [main_disaster_response](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md)'s
  own Issue, the final S01 file, since it shares `ConstraintCoeffs`
  with this file, but does not block it — each Issue wraps its own
  Hamiltonian call sites independently, no shared-file edit needed)
- Branch: `feature/liss-0347-s01-day2-recovery-real-unit-migration`
- GitHub Issue / PR: [#410](https://github.com/nn0cl/staqex/pull/410)
  (merged, `cde5191`)

## Design decision

Lock-boundary check already covered by LISS-0344's survey (value-
internal retype only, no scope/story/coverage change) — not repeated
per-file.

`main_day2_recovery.sqx` builds `Operator H = recovery_hamiltonian(coeffs)`
from a classical `ConstraintCoeffs(0.6, 0.5, 0.0)` (`congestion`/
`fairness`, both `Float`, weighted Pauli terms — **not** an implicit
coefficient of `1`, unlike the 3 Hamiltonians work units 13–14 already
fixed). Per WP-0095 work unit 12's confirmed design, `ConstraintCoeffs`
itself stays `Float` — no struct/field retyping, preserving this file's
existing classical desk computations untouched. The same
`ops_energy_scale()` wrap-at-call-site pattern applies uniformly
regardless of whether the wrapped Hamiltonian's own coefficients are
`1` or a computed `Float` weight: `scale * H_raw`, with the two
confirmed constraints (work unit 13) — pre-bind the factory's result to
its own `Operator` variable before multiplying by `scale`; the evolve
duration must be its own `Time`-typed variable, not an inline literal
suffix.

`main_day2_recovery.sqx`'s evolve duration (`for 0.9`) is already a
literal (unlike `main_disaster_response`'s 3 of 4 computed duration
expressions) — becomes `Time dur = 0.9.fs` directly, no B07-style
independent-literal workaround needed.

`named_coeff_sum(coeffs) -> Float` (a classical desk/log value, not fed
into the Hamiltonian) is untouched — it already type-checks and runs
correctly as `Float`, no relation to the `evolve` real-unit gate.

## Intent

1. Import `ops_energy_scale` (parent-relative
   `..physics.ops_energy_scale`, matching `main_lattice_four.sqx`'s
   import style).
2. `Energy scale = ops_energy_scale()`.
3. `Operator H = recovery_hamiltonian(coeffs)` → bind to `Operator
   H_raw = recovery_hamiltonian(coeffs)` first, then `Operator H =
   scale * H_raw`.
4. `evolve (plan0, plan1) under H for 0.9` → declare `Time dur =
   0.9.fs`, then `... for dur`.

## Explicitly out of scope

- Any Kernel change.
- `physics/constraint_h.sqx` itself (untouched — `ConstraintCoeffs`
  stays `Float`, confirmed sufficient in work unit 12's design).
- `ops_energy_scale.sqx` itself (unchanged, reused as-is).
- `named_coeff_sum`'s `Float` return (classical desk value, unrelated
  to the Hamiltonian).
- The final S01 file (`main_disaster_response`, separate Issue, done
  last).

## Acceptance reference

```gherkin
Feature: S01 main_day2_recovery uses real physical units

  Scenario: the migrated example compiles and runs to a real terminal measurement
    Given the migrated main_day2_recovery.sqx
    When it is compiled and run with a fixed seed
    Then it compiles without EVOLVE_UNRESOLVED_UNIT_ERROR, RUNTIME_ERROR, or any hard diagnostic
    And it reaches a non-vacuum terminal measurement
```

## Verification plan for this design intake (not shipped as a test)

Confirmed live during LISS-0344's survey: `scale * <ConstraintCoeffs-
based Hamiltonian factory result>` (pre-bound to a local `Operator`
variable) compiles and evolves to a real, non-degenerate measurement
with `1eV`/`fs`-scale values, the same pattern LISS-0345/0346 already
shipped for coefficient-1 Hamiltonians.

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-06
- Size: `XS` — one example file, one Hamiltonian call site, one literal
  duration, direct reuse of LISS-0345/0346's already-shipped pattern.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0347_s01_day2_recovery_real_unit_migration_red.py`
      added. Failed for the documented reason
      (`EVOLVE_UNRESOLVED_UNIT_ERROR` at runtime on the bare `for 0.9`
      duration).
- [x] Phase 2 Green: `.sqx` rewritten. 1/1 passed on the first attempt
      — LISS-0345's confirmed pattern applied directly with no new
      findings, confirming it holds equally for a `ConstraintCoeffs`-
      weighted Hamiltonian, not just the coefficient-1 case.
- [x] Phase 3 Refactor: no further change needed; reviewer empathy
      summary below.
- [x] Full regression: `pytest tests/ -q` → 1219 passed, 55 failed
      (unchanged failure count vs. LISS-0346's 55, no new failures — +1
      is this Issue's own new test); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged — this file isn't exercised by any SV suite);
      `git diff --check` → clean.
- [x] WP-0095 work unit 15 row updated.

## Reviewer empathy summary

**何を目的として何を変更したか**: S01の`main_day2_recovery.sqx`の
`ConstraintCoeffs`ベースHamiltonian（`recovery_hamiltonian(coeffs)`）に
`ops_energy_scale()`を乗算し、実ℏ下で物理的に意味のある回転角にした。
`ConstraintCoeffs`自体（congestion/fairness）はFloatのまま無変更、
`physics/constraint_h.sqx`も無変更。durationも`Time`型変数として
明示化。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 特になし。LISS-0345/0346で確立・検証済みのパターンをそのまま適用し、
  1回でGreenに到達した。係数1のHamiltonianだけでなく、計算済みFloat
  係数（congestion/fairness）を使うHamiltonianにも同じラップ方式が
  問題なく通用することを確認した。

**人間がコードレビューで重点的に見るべきポイント**:
- 特になし（LISS-0345/0346と同一パターンの単純な再適用）。
- 残るmain_disaster_responseは同じ`ConstraintCoeffs`を共有しつつ、
  4つのHamiltonian（うち3つは計算済みduration式）を持つため、
  このIssueで確認した「ConstraintCoeffsパターンが計算済み係数でも
  そのまま通用する」という結果が特に重要になる。

## Non-goals

- Kernel changes.
- `physics/constraint_h.sqx` changes.
- The final S01 file, `main_disaster_response` (separate Issue).
