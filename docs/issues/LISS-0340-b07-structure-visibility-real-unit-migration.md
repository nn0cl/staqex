# LISS-0340: migrate `B07_structure_visibility` to real units (WP-0095 work unit 8)

## Metadata

- Local issue ID: LISS-0340
- Status/phase: **complete** (2026-08-06) — PR
  [#396](https://github.com/nn0cl/staqex/pull/396) merged, commit
  `f385df8`
- Type: Feature Path (example content only —
  `examples/basics/B07_structure_visibility/structure_visibility.sqx`;
  no Kernel change)
- Priority: P1
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md)
  work unit 8
- Parent: [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
- Depends on: [LISS-0330](LISS-0330-real-hbar-kernel-primitive.md),
  [LISS-0336](LISS-0336-evolve-real-unit-canonicalization-bugs.md)
- Blocks: none within WP-0095
- Branch: `feature/liss-0340-b07-structure-visibility-real-unit-migration`
- GitHub Issue / PR: [#396](https://github.com/nn0cl/staqex/pull/396)
  (merged, `f385df8`)

## Design decision

`B07_structure_visibility` teaches `namespace`/`enum`/`struct`/`pub`/
module-private fields, using `Model.IsingParams { J, h, _pad }` (bare
`Float` fields) to build a qubit-Pauli Hamiltonian
(`ising_hamiltonian(p) -> Operator`, `Z[0]*Z[1]`/`X[0]+X[1]` terms) and
`evolve (s0, s1) under H for scale * 0.25` (`scale = seg.length`, a
struct-field-derived bare duration). This example's Hamiltonian goes
through the qubit-Pauli sparse path (`compile_sparse_pauli`), the same
path LISS-0336 fixed a coalescing-epsilon bug for — so, unlike B04's
non-ℏ-divided legacy path, this one genuinely needs real, appropriately-
scaled `Energy`/`Time` values (matching A05/A06's precedent), not just a
unit-satisfying wrapper.

**Adopted fix**:
- `IsingParams.J`/`.h` become `Energy`-typed (was `Float`); constructed
  with `1.0.eV to J` / `0.5.eV to J` (ratio preserved).
- `ising_hamiltonian(p: Model.IsingParams) -> Operator` — unchanged in
  shape; confirmed live this is the already-proven-safe "struct
  parameter, `Operator` return" pattern (same as A11's
  `build_sensor_hamiltonian`, LISS-0338).
- The duration's struct-field-derived computation (`scale * 0.25`) can
  no longer directly become a `Time`-typed value (the unit-suffix
  grammar only attaches to a literal, not an arbitrary expression,
  confirmed during LISS-0337/0338/0339) — replaced with an independent
  `Time dur = 0.5.fs` (matching the original numeric ratio's rough
  scale). `Float scale = seg.length` is kept as its own line (still
  demonstrates reading a `pub` struct field into a classical value, this
  example's actual teaching point), just no longer wired into the
  evolve duration.

## Intent

1. Change `Model.IsingParams.J`/`.h` from `Float` to `Energy`.
2. Construct `params` with `J: 1.0.eV to J, h: 0.5.eV to J` (ratio
   preserved from the original `1.0`/`0.5`).
3. Replace `evolve (s0, s1) under H for scale * 0.25` with `... for
   dur`, declaring `Time dur = 0.5.fs` (keep `Float scale = seg.length`
   as its own, still-meaningful demonstration line).

## Explicitly out of scope

- Any Kernel change.
- Any other example's migration (B08/B16/S01×5/quantum_matter_discovery).
- Reconnecting the geometry (`seg.length`) to the evolve duration — no
  longer directly expressible now that durations must be real
  `Time`-typed literals or variables, not derived expressions; this
  example's teaching point (namespace/enum/struct/visibility) doesn't
  depend on that connection.

## Acceptance reference

```gherkin
Feature: B07_structure_visibility uses real physical units

  Scenario: the migrated example compiles and runs to a real terminal measurement
    Given the migrated structure_visibility.sqx
    When it is compiled and run with a fixed seed
    Then it compiles without EVOLVE_UNRESOLVED_UNIT_ERROR or any hard diagnostic
    And it reaches a non-vacuum terminal measurement
```

## Verification plan for this design intake (not shipped as a test)

Confirmed live: `Model.IsingParams` with `Energy`-typed `J`/`h` fields,
constructed via named kwargs (`J: 1.0.eV to J, h: 0.5.eV to J`), passed
to `ising_hamiltonian(params) -> Operator`, evolved with `Time dur =
0.5.fs`, compiles and runs to a non-vacuum measurement.

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-06
- Size: `S` — one example file, struct field retyping plus duration fix.
- Route: direct implementation by this session.
- Confidence: high (all patterns directly verified live, each already
  established by a prior WP-0095 Issue).

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0340_b07_structure_visibility_real_unit_migration_red.py`
      added. Commit `d86c984`: failed for the documented reason
      (`EVOLVE_UNRESOLVED_UNIT_ERROR` on the bare `for scale * 0.25`
      duration).
- [x] Phase 2 Green: `.sqx` rewritten. Commit `f787115`: 1/1 passed.
- [x] Phase 3 Refactor: no further change needed; reviewer empathy
      summary below.
- [x] Full regression: `pytest tests/ -q` → 1208 passed, 57 failed
      (unchanged failure count vs. LISS-0339's 57, no new failures — +1
      is this Issue's own new test); `python3
      tests/spec_verification/run_all.py` → 159/161 (98.76%, +1 vs.
      LISS-0339's 158/161 — the B07 SV case); `git diff --check` →
      clean.
- [x] WP-0095 work unit 8 row updated.

## Reviewer empathy summary

**何を目的として何を変更したか**: `B07_structure_visibility`の
`IsingParams.J`/`.h`をFloatからEnergy型に変更（比率維持）し、
`evolve`のdurationを`scale * 0.25`という構造体フィールド由来の式から、
独立した実Time値に置き換えた。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- `scale = seg.length`という構造体フィールド読み出しは、単位サフィックス
  がリテラルにしか付与できない制約により、もはやdurationへ直接接続
  できない。この例の本来の教育目的（namespace/enum/struct/visibility）
  には影響しないため、`scale`を単独の実演行として残し、durationとは
  切り離した。

**人間がコードレビューで重点的に見るべきポイント**:
- `scale`が今後も使われないまま残ることが、読者に混乱を与えないか
  （コメントで明示的に理由を説明済み）。

## Non-goals

- Kernel changes.
- Remaining example migrations (B08/B16/S01×5/quantum_matter_discovery).
