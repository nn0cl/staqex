# LISS-0348: migrate `S01_quantum_disaster_response/main_disaster_response` to real units (WP-0095 work unit 16)

## Metadata

- Local issue ID: LISS-0348
- Status/phase: **complete** (2026-08-06) — PR
  [#412](https://github.com/nn0cl/staqex/pull/412) merged, commit
  `f22d78a`
- Type: Feature Path (example content only —
  `examples/showcase/S01_quantum_disaster_response/main_disaster_response.sqx`;
  no Kernel change, no change to `physics/constraint_h.sqx` or
  `grid/block_costs.sqx`)
- Priority: P1
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md)
  work unit 16 — **final** S01 file, the flagship "tonight spine"
  (`CH-tonight-spine`), done last per work unit 12's sequencing so the
  `ops_energy_scale()` pattern is proven across every Hamiltonian shape
  this showcase uses before tackling the most complex file
- Parent: [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
- Depends on: [LISS-0345](LISS-0345-s01-lattice-four-real-unit-migration.md)
  (`ops_energy_scale.sqx` + the two call-site constraints),
  [LISS-0347](LISS-0347-s01-day2-recovery-real-unit-migration.md)
  (confirms the same pattern for `ConstraintCoeffs`-weighted
  Hamiltonians, which this file also uses)
- Blocks: WP-0095 completion (this is the last unmigrated example)
- Branch: `feature/liss-0348-s01-disaster-response-real-unit-migration`
- GitHub Issue / PR: [#412](https://github.com/nn0cl/staqex/pull/412)
  (merged, `f22d78a`)

## Design decision

Lock-boundary check already covered by LISS-0344's survey (value-
internal retype only, no scope/story/coverage change) — not repeated
per-file.

`main_disaster_response.sqx` builds **4 Hamiltonians**, each evolved
for a **different duration**:

| Hamiltonian | Source | Coefficient nature | Duration | Duration nature |
|---|---|---|---|---|
| `H_drive` | `constraint_hamiltonian(coeffs)` — `ConstraintCoeffs` (shared with LISS-0347's `main_day2_recovery`) | computed `Float` weights | `t_drive` | computed classical expression |
| `H_damage` | `damage_hamiltonian()` — `grid/block_costs.sqx` (shared with LISS-0345's `main_lattice_four`) | coefficient-1 | `t_damage` | computed classical expression |
| `H_flood` | `flood_zone_sum()` — `grid/block_costs.sqx` | coefficient-1 | `t_flood` | **literal** (`0.1`) |
| `H_corridor` | `corridor_product()` — `grid/block_costs.sqx` (a `product(...)` combinator, not `sum(...)`) | coefficient-1 | `t_corridor` | computed classical expression |

Every Hamiltonian gets the same `scale * <pre-bound factory result>`
wrap this program has already shipped twice (work units 13 and 15) —
confirmed live during LISS-0344's survey this holds uniformly
regardless of whether the source is `ConstraintCoeffs`-weighted or
coefficient-1, and regardless of whether the combinator is `sum(...)`
or `product(...)` (a scalar applied once to the whole assembled
Operator result, not distributed into individual factors — distributing
into a `product(...)`'s factors would multiply the scale in
`N` times, not once, which is not what any prior work unit did).

**The durations are the new complexity this file introduces.** 3 of
the 4 (`t_drive`, `t_damage`, `t_corridor`) are computed classical
`Float` expressions (e.g. `t_drive = duration + load * 0.05 +
request_load + roll_min * 0.001`), not literals. Confirmed live: a
computed dimensionless `Float` cannot be converted to `Time` via `to`
either (`DIMENSION_MISMATCH_ERROR: [1] vs [Time]` — the source must
already carry a matching dimension for `to` to apply) — so neither the
literal-suffix route nor the `to`-conversion route is available for a
genuinely computed value. This is the exact same constraint
`main_structure_visibility` (LISS-0340/B07) already hit and resolved:
declare an **independent** `Time`-typed literal for each of these 3
durations, replacing their role in the `evolve ... for` clause. The
original classical `Float t_drive`/`t_damage`/`t_corridor`
computations stay in the file unchanged (still demonstrating the
domain→Joint causal map this file's own header comment calls out), but
a fresh `Time` literal — not derived from that computation — takes over
the specific "what gets passed to evolve" role, matching B07's already-
Adjudicator-approved resolution for this exact problem shape. `t_flood`
(the one already-literal duration) becomes a `Time`-typed literal
directly, same as every other single-literal-duration migration this
program has done.

The specific `Time` literal magnitudes for `t_drive`/`t_damage`/
`t_corridor` are **arbitrary illustrative values** (matching B07's own
precedent of 0.5.fs, unrelated to the original expression's structure)
— the original computed expressions were never physically dimensioned
to begin with (pre-ADR-0195 natural units), so no real magnitude is
being "lost." Chosen: `0.6.fs` (`dur_drive`), `0.3.fs` (`dur_damage`),
`0.4.fs` (`dur_corridor`), `0.1.fs` (`dur_flood`, preserving the
original literal exactly).

## Intent

1. Import `ops_energy_scale` (same-package-level `.physics.ops_energy_scale`,
   matching this file's existing `.grid.block_costs`/`.physics.constraint_h`
   import style — no `..` prefix, since this file's own package **is**
   `examples.showcase.s01_disaster`).
2. `Energy scale = ops_energy_scale()`.
3. For each of `H_drive`/`H_damage`/`H_flood`/`H_corridor`: bind the
   factory call's result to its own `_raw` `Operator` variable first,
   then `Operator H_x = scale * H_x_raw`.
4. Declare 4 independent `Time` literals (`dur_drive = 0.6.fs`,
   `dur_damage = 0.3.fs`, `dur_flood = 0.1.fs`, `dur_corridor =
   0.4.fs`); reference each by name in its corresponding `evolve ...
   for` clause, replacing `t_drive`/`t_damage`/`t_flood`/`t_corridor`.
   The original `Float t_drive`/`t_damage`/`t_flood`/`t_corridor`
   classical computations stay in the file, unchanged, still
   demonstrating the causal map — just no longer literally fed into
   `evolve`.

## Explicitly out of scope

- Any Kernel change.
- `physics/constraint_h.sqx` / `grid/block_costs.sqx` themselves
  (untouched).
- `ops_energy_scale.sqx` itself (unchanged, reused as-is).
- Preserving the exact original numeric ratios between the 4 durations
  (not physically meaningful under the old natural-units convention to
  begin with — same reasoning B07 already established).

## Acceptance reference

```gherkin
Feature: S01 main_disaster_response uses real physical units

  Scenario: the migrated flagship example compiles and runs to a real terminal measurement
    Given the migrated main_disaster_response.sqx (4 Hamiltonians, 4 durations)
    When it is compiled and run with a fixed seed
    Then it compiles without EVOLVE_UNRESOLVED_UNIT_ERROR, RUNTIME_ERROR, or any hard diagnostic
    And it reaches a non-vacuum terminal measurement
```

## Verification plan for this design intake (not shipped as a test)

Confirmed live: a computed dimensionless `Float` cannot be `to`-
converted to `Time` (`DIMENSION_MISMATCH_ERROR`), confirming the
B07-style independent-literal workaround is required, not avoidable.
The `scale * <pre-bound factory result>` wrap pattern itself is already
shipped and verified end-to-end for both `ConstraintCoeffs`-weighted
(work unit 15) and coefficient-1 `sum(...)`-built (work unit 13)
Hamiltonians; this Issue additionally exercises a `product(...)`-built
Hamiltonian (`corridor_product()`) for the first time, applying the
scale once to the whole assembled result (not distributed into
factors) to preserve the mechanism this program has used uniformly.

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-06
- Size: `S` — one example file, but 4 Hamiltonian call sites and 4
  duration declarations (3 needing the independent-literal workaround).
  Every individual mechanism is already proven by prior work units;
  this Issue combines them in one file for the first time.
- Route: direct implementation by this session.
- Confidence: high — every constituent pattern (wrap-at-call-site,
  pre-bind before `scale *`, independent `Time` literal for computed
  durations) is already shipped and verified; this is a mechanical
  combination, not new design.

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0348_s01_disaster_response_real_unit_migration_red.py`
      added. Failed for the documented reason
      (`EVOLVE_UNRESOLVED_UNIT_ERROR` at runtime on the bare `for
      t_drive` duration, the first of the 4 evolve calls).
- [x] Phase 2 Green: `.sqx` rewritten — all 4 Hamiltonians wrapped with
      the pre-bind + `scale *` pattern (including the first-time use of
      the pattern on a `product(...)`-built Hamiltonian,
      `corridor_product()`, applied once to the whole assembled result);
      4 independent `Time` literals declared, replacing the computed/
      literal `Float` durations in each `evolve ... for` clause. 1/1
      passed on the first attempt — every constituent pattern was
      already proven by prior work units, this Issue combines them.
- [x] Phase 3 Refactor: no further change needed; reviewer empathy
      summary below.
- [x] Full regression: `pytest tests/ -q` → 1223 passed, 52 failed
      (**-3** vs. LISS-0347's 55, no new failures — **bonus fix**: all 3
      cases in `test_s01_tonight_ticket_export.py`
      (`test_spine_source_has_no_inspect_or_identity_evolve_times`,
      `test_build_tonight_ticket_happy_path_schema`,
      `test_export_tonight_ticket_cli_writes_json`) depend on
      `main_disaster_response.sqx` running end-to-end and were failing
      purely because the file was broken under real ℏ — confirmed these
      are structural/behavioral checks (schema shape, non-vacuum
      measurement, exit code), not tied to any specific duration
      magnitude, so the arbitrary illustrative `Time` literals chosen
      here don't affect them; +1 is this Issue's own new test); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged — this file isn't exercised by any SV suite);
      `git diff --check` → clean.
- [x] WP-0095 work unit 16 row updated; WP-0095 status header updated
      to reflect **all** examples migrated — WP-0095 itself marked
      complete.

## Reviewer empathy summary

**何を目的として何を変更したか**: S01の旗艦「tonight spine」
`main_disaster_response.sqx`の4つのHamiltonian
（`H_drive`/`H_damage`/`H_flood`/`H_corridor`）すべてに
`ops_energy_scale()`をラップし、4つのdurationのうち3つ（計算済み式）
をB07と同じ独立`Time`リテラル方式で対応した。これはWP-0095の
最後のexample migrationであり、これによりADR 0195の実単位移行が
リポジトリ全体で完了した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- `corridor_product()`は`product(...)`コンビネータ（`sum(...)`では
  ない）で構築されたHamiltonianであり、本Issueで初めて`scale *`
  ラップパターンを適用した。個々の因子に`scale`を分配せず、
  組み立て済みOperator全体に一度だけ`scale`を乗算する（他の
  work unitと同じ方式）ことを設計段階で確認した——`product`の
  各因子に分配すると`scale`が因子数だけ乗算されてしまい、
  意図と異なる結果になるため。
- `t_drive`/`t_damage`/`t_corridor`の具体的な仮値（0.6fs/0.3fs/0.4fs）
  は、B07の前例（0.5fs、元の式構造とは無関係）にならって選んだ
  恣意的な例示値。元の計算式は実ℏ移行前の自然単位系のもとでは
  そもそも物理的な次元を持たない数値だったため、「失われる」
  実際の物理的magnitudeは存在しない。
- テスト実行で`test_s01_tonight_ticket_export.py`の3ケースが
  ボーナスで合格に転じたことを発見した。これらは
  `main_disaster_response.sqx`が最後まで正常実行されることに
  依存するテストで、実ℏ下でファイルが壊れていたために失敗していた
  だけだったことをテスト内容の直接確認で検証した（スキーマ形状・
  非真空測定・終了コードのチェックであり、特定のduration数値には
  依存しない）。

**人間がコードレビューで重点的に見るべきポイント**:
- `dur_drive`/`dur_damage`/`dur_corridor`/`dur_flood`の4つの仮値が、
  4つのSuzuki分解（`steps = 4`/`4`/`2`/`2`）と組み合わさったときに
  数値的に不安定（`|H*t/hbar|`が過大）にならないか（今回のテスト
  実行では非真空測定に正常到達しているため問題ないことを確認済み）。
- 元の`Float t_drive`等の計算チェーン（congestion/fairness/hazard_
  pressure/open_scoreなど）が、コメントで明示した通り「もはや
  evolveには直接渡らないが、causal mapのデモとしてファイルに
  残されている」という位置づけが、将来の読者に伝わるか。

## Non-goals

- Kernel changes.
- `physics/constraint_h.sqx` / `grid/block_costs.sqx` changes.
- Preserving the original duration ratios exactly.
