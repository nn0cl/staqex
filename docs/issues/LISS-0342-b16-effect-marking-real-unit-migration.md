# LISS-0342: migrate `B16_effect_marking` to real units (WP-0095 work unit 10)

## Metadata

- Local issue ID: LISS-0342
- Status/phase: **complete** (2026-08-06) — PR
  [#400](https://github.com/nn0cl/staqex/pull/400) merged, commit
  `adf63b4`
- Type: Feature Path (example content only —
  `examples/basics/B16_effect_marking/effect_marking.sqx`; no Kernel
  change)
- Priority: P1
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md)
  work unit 10 — found unmigrated during LISS-0341's honest correction
  (not exercised by any `spec_verification` suite, so absent from the
  161/161 figure)
- Parent: [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
- Depends on: [LISS-0330](LISS-0330-real-hbar-kernel-primitive.md),
  [LISS-0336](LISS-0336-evolve-real-unit-canonicalization-bugs.md)
- Blocks: none within WP-0095
- Branch: `feature/liss-0342-b16-effect-marking-real-unit-migration`
- GitHub Issue / PR: [#400](https://github.com/nn0cl/staqex/pull/400)
  (merged, `adf63b4`)

## Design decision

`B16_effect_marking` teaches ADR 0081 explicit effect marking (a
library `fn peek_zz(...) -> State<Float> effects { Inspect } {...}`)
using the same untyped multi-bind qubit-Pauli Hamiltonian pattern as
B08 (LISS-0341): `J, h = 1.0, 0.5`, `H = -J*(Z[0]*Z[1]) -
h*(X[0]+X[1])` (inferred), `evolve ... for 0.5` (bare duration). Same
fix as B08: `J`/`h` become explicit `Energy`-typed (ratio preserved);
`H` stays inferred; duration becomes explicit `Time`. The `peek_zz`
effect-marking teaching point is untouched.

## Intent

1. `J, h = 1.0, 0.5` → `Energy J = 1.0.eV to J` / `Energy h = 0.5.eV to
   J`.
2. `evolve (s0, s1) under H for 0.5` → `... for dur`, declaring `Time
   dur = 0.5.fs`.

## Explicitly out of scope

- Any Kernel change.
- The `peek_zz` effect-marking mechanism itself.
- Remaining example migrations (5 locked S01 files,
  `quantum_matter_discovery`).

## Acceptance reference

```gherkin
Feature: B16_effect_marking uses real physical units

  Scenario: the migrated example compiles and runs to a real terminal measurement
    Given the migrated effect_marking.sqx
    When it is compiled and run with a fixed seed
    Then it compiles without EVOLVE_UNRESOLVED_UNIT_ERROR or any hard diagnostic
    And it reaches a non-vacuum terminal measurement
```

## Verification plan for this design intake (not shipped as a test)

Confirmed live: identical structure to B08 (`Energy J`/`h`, inferred
`H`, `Time dur`) plus the unchanged `peek_zz` effect-marked helper
compiles and runs to a non-vacuum measurement.

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-06
- Size: `XS` — identical pattern to LISS-0341/B08.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0342_b16_effect_marking_real_unit_migration_red.py`
      added. Commit `af8d2bc`: failed for the documented reason
      (`EVOLVE_UNRESOLVED_UNIT_ERROR` on the bare `for 0.5` duration).
- [x] Phase 2 Green: `.sqx` rewritten. Commit `6bd3993`: 1/1 passed.
      **Bonus**: `test_liss_0306_nested_opattr_and_effects_red.py::test_b16_effect_marking_sample`
      (a pre-existing test also referencing B16) flipped from failing to
      passing — same root cause.
- [x] Phase 3 Refactor: no further change needed; reviewer empathy
      summary below.
- [x] Full regression: `pytest tests/ -q` → 1211 passed, 56 failed (-1
      vs. LISS-0341's 57, no new failures — the bonus fix above); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged — B16 isn't exercised by any SV suite); `git diff --check`
      → clean.
- [x] WP-0095 work unit 10 row updated.

## Reviewer empathy summary

**何を目的として何を変更したか**: `B16_effect_marking`の`J`/`h`を
明示的なEnergy型に、durationを明示的なTime型に変更した。B08
（LISS-0341）と全く同じ構造だったため、追加調査なしに同じパターンを
適用した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 特になし。LISS-0341で確立したパターンをそのまま再利用した。

**人間がコードレビューで重点的に見るべきポイント**:
- `peek_zz`のeffect marking教育目的（ADR 0081）が変更by影響を受けて
  いないか（コード上は無変更のはず）。

## Non-goals

- Kernel changes.
- Remaining example migrations (5 locked S01 files,
  `quantum_matter_discovery`).
