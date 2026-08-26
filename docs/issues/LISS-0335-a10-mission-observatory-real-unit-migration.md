# LISS-0335: migrate `A10_mission_observatory` to real physical units (WP-0095 work unit 5)

## Metadata

- Local issue ID: LISS-0335
- Status/phase: **complete** (2026-08-05) — PR
  [#387](https://github.com/nn0cl/staqex/pull/387) merged, commit
  `556d459`
- Type: Feature Path (example content only, multi-file —
  `examples/applied/A10_mission_observatory/main_mission_observatory.sqx`,
  `domain/observatory_config.sqx`, `operators/ssh_hamiltonian.sqx`,
  `README.md`; no Kernel/grammar change)
- Priority: P1
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md)
  work unit 5
- Parent: [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
- Depends on: [LISS-0330](LISS-0330-real-hbar-kernel-primitive.md) (real
  ℏ, merged); [LISS-0334](LISS-0334-a06-ssh-real-unit-migration.md) (SSH
  honesty-category precedent, merged)
- Blocks: none within WP-0095 (each remaining migration is independent)
- Branch: `feature/liss-0335-a10-mission-observatory-real-unit-migration`
- GitHub Issue / PR: [#387](https://github.com/nn0cl/staqex/pull/387)
  (merged, `556d459`)

## Design decision carried into this Issue (resolved before Plan approval)

`A10_mission_observatory` builds the same class of SSH tight-binding
Hamiltonian as `A06_topological_edge_memory` (`operators/ssh_hamiltonian.sqx`,
hop coefficients `0.5`/`1.5`, ratio 1:3), and its README neither cites a
specific paper's numeric parameters nor claims real mission data
("Real spacecraft operations / spectrum mission data" is already
disclaimed as **No**). This Issue reuses LISS-0334's established third
honesty category (real `eV`-scale `Energy` magnitudes, ratio preserved,
documented as physically plausible for a tight-binding hopping
amplitude but not literature-traced) without re-litigating that choice.

A distinct, newly-discovered Kernel limitation was found live during
this Issue's design intake: `evolve site under Hssh for config.duration`
(a struct-field access, even when the field is declared `Time`-typed and
constructed from a dimensioned literal) is **not** recognized by
LISS-0330's fail-closed check (`_hamiltonian_evolve_one_step` in
`compiler/staqex/runtime/evaluator.py`), which only inspects
`isinstance(expr.duration, Var)` — a struct-field `Attr` expression is
rejected with `EVOLVE_UNRESOLVED_UNIT_ERROR` even though the underlying
value genuinely does carry a resolvable `Time` unit (confirmed live via
`_attr_field_unit`/ADR 0174 struct field-unit tracking). Confirmed
workaround: assigning `Time dur = config.duration` to a plain local
variable immediately before `evolve` resolves correctly (the local
variable's `scalar_units` entry is populated from the struct field's
tracked unit). This is a real, narrow Kernel gap — **not fixed in this
Issue** (out of scope: WP-0095 migrates examples, not the fail-closed
check's expression coverage) — noted here so a future Issue does not
mistake it for a fresh discovery, and recorded in "Related, not
blocking" below.

## Intent

1. In `domain/observatory_config.sqx`, change `Config.duration`'s
   declared type from `Float` to `Time`.
2. In `main_mission_observatory.sqx`:
   - `Config config = Config(3, 0.25, 0)` → `Config config = Config(3,
     0.25.fs, 0)`.
   - Insert `Time dur = config.duration` immediately before the `evolve`
     call (working around the field-access limitation above), and change
     `evolve site under Hssh for config.duration` to `evolve site under
     Hssh for dur`.
3. In `operators/ssh_hamiltonian.sqx`, apply LISS-0334's established
   pattern: `Energy v = 0.5.eV to J`, `Energy w = 1.5.eV to J`,
   multiplying the `hop(i, j)` terms (ratio unchanged).
4. Add a short comment in `ssh_hamiltonian.sqx` (matching A06's wording)
   and a new "Units and interpretation" README section.

## Explicitly out of scope

- Fixing the Kernel's fail-closed check to recognize dimensioned
  struct-field-access durations directly (noted above, not fixed here).
- A literature-grounded derivation of real SSH parameters (same
  rejection rationale as LISS-0334).
- Any other example's migration (A11/B04/B07/B08/B16/S01×5/
  quantum_matter_discovery).

## Acceptance reference

```gherkin
Feature: A10_mission_observatory uses real physical units

  Scenario: the migrated example compiles and runs to a real terminal measurement
    Given the migrated main_mission_observatory.sqx, observatory_config.sqx,
      and ssh_hamiltonian.sqx
    When it is compiled and run with a fixed seed
    Then it compiles without EVOLVE_UNRESOLVED_UNIT_ERROR or any hard diagnostic
    And it reaches a non-vacuum terminal measurement
```

## Verification plan for this design intake (not shipped as a test)

Confirmed live in this session before finalizing the source:

- `Observatory.Config` with a `Time`-typed `duration` field, constructed
  as `Config(3, 0.25.fs, 0)`, compiles.
- `evolve site under Hssh for config.duration` (direct field access)
  still fails with `EVOLVE_UNRESOLVED_UNIT_ERROR` — confirming the
  limitation above.
- `Time dur = config.duration` followed by `evolve site under Hssh for
  dur` compiles and runs (`status: succeeded`, non-vacuum measurement).

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-05
- Size: `S` — no Kernel change; three `.sqx` files' small edits, one
  README section addition.
- Route: direct implementation by this session.
- Assumptions: same as LISS-0334 (eV-scale magnitude, ratio preserved,
  no physical-measurement claim).
- Confidence: high (syntax and the struct-field workaround directly
  verified live).
- Revision links: none yet.

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0335_a10_mission_observatory_real_unit_migration_red.py`
      added. Commit `264696b`: failed for the documented reason
      (`EVOLVE_UNRESOLVED_UNIT_ERROR` on the bare `for config.duration`
      dimensionless `Float`).
- [x] Phase 2 Green: `.sqx` files rewritten with explicit `Energy`/`Time`
      values and the local-variable field-access workaround. Commit
      `c67ba85`: 1/1 passed. Confirmed via
      `test_applied_catalog_health_red.py`: A10 no longer appears in
      that test's failure list (only A11 remains). **Bonus, unanticipated
      fix**: three more tests exercising A10's legacy multi-file/capstone
      source (`test_liss0051_operator_factory_runtime_red.py`,
      `test_liss0107_examples_linker_runtime_red.py`,
      `test_quantum_observatory_capstone.py`) also flipped from failing
      to passing — same root cause, not scope creep.
- [x] Phase 3 Refactor: README "Units and interpretation" section and two
      new Honesty-table rows added; reviewer empathy summary below.
- [x] Full regression: `pytest tests/ -q` → 1203 passed, 60 failed (-3
      vs. LISS-0334's 63, from the bonus fixes above); `python3
      tests/spec_verification/run_all.py` → 136/145 (93.79%, +1 vs.
      LISS-0334's 135/145 — the A10 SV case); `git diff --check` →
      clean.
- [x] WP-0095 work unit 5 row updated.

## Reviewer empathy summary

**何を目的として何を変更したか**: `A10_mission_observatory`のSSH
Hamiltonianと evolve durationを、A06と同じ第三の誠実さの型（物理的に
妥当だが文献未追跡）で実物理単位へ移行した。加えて、`Config.duration`
構造体フィールドを`Float`から`Time`型に変更した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 設計調査中に、`evolve ... for config.duration`のような構造体フィールド
  アクセス経由のdurationが、たとえフィールド自体が`Time`型で正しく単位を
  持っていても、fail-closedチェック（`Var`型しか見ない）に引っかかる
  という、真に未発見だったKernelの制約を発見した。このIssueでは
  Kernel本体を修正せず、evolve直前にローカル`Time`変数へ束縛する
  ワークアラウンドを採用し、その経緯をLISS-0335とコード内コメントに
  明記した。
- Green中に、A10のレガシーマルチファイル/capstoneソースを経由する
  3つの無関係に見えたテストが同一根本原因で副次的に修正されたことを
  確認した。

**人間がコードレビューで重点的に見るべきポイント**:
- `evolve`のfail-closedチェックが構造体フィールドアクセスを認識しない
  という制約は、将来的にKernel側で一般化すべきか（このIssueでは判断
  せず記録のみ）。
- README「Units and interpretation」がA06との一貫性を保っているか。

## Related, not blocking

The fail-closed `evolve` duration check
(`_hamiltonian_evolve_one_step`) only recognizes a bare `Var` duration,
not a dimensioned struct-field `Attr` expression, even when the field
genuinely carries a resolvable unit via ADR 0174's field-unit tracking.
Not fixed here (out of WP-0095's example-migration scope); flagged for a
future Kernel-side Issue if this pattern recurs often enough to be worth
generalizing.

**Fixed (2026-08-07)**: see
[LISS-0357](LISS-0357-evolve-duration-attr-and-literal-unit-recognition.md)
(PR [#432](https://github.com/nn0cl/staqex/pull/432), merged `8f25c61`)
— `_hamiltonian_evolve_one_step` now resolves the duration unit via
`_eval_value_with_unit`, recognizing struct-field `Attr` access (this
Issue's original finding) and inline unit-suffixed literals (LISS-0345's
finding) alongside the bare-`Var` case. The local-variable workaround
this Issue adopted (`Time dur = config.duration`) remains valid but is
no longer required.

## Non-goals

- Kernel fail-closed check field-access support.
- Literature-grounded SSH parameter derivation.
- Remaining example migrations (A11/B04/B07/B08/B16/S01×5/
  quantum_matter_discovery).

## Addendum (2026-08-05, LISS-0336)

Re-verification during [LISS-0336](LISS-0336-evolve-real-unit-canonicalization-bugs.md)
found this example was affected by the evolve-duration-canonicalization
bug (not the `_coalesce` epsilon bug, since this example's Hamiltonian
is built via the Fock/`hop()` path, not `compile_sparse_pauli`). Both
Kernel bugs are now fixed; this example was re-run under the fix and
confirmed to reach a non-vacuum measurement. No numeric coefficient/
duration values in this example were changed.
