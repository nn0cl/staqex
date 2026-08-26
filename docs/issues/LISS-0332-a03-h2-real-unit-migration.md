# LISS-0332: migrate `A03_h2_vqe` to real physical units (WP-0095 work unit 2)

## Metadata

- Local issue ID: LISS-0332
- Status/phase: **complete** (2026-08-05) — PR
  [#381](https://github.com/nn0cl/staqex/pull/381) merged, commit
  `510e860`
- Type: Feature Path (Kernel — `compiler/staqex/dimensions.py` new `Ha`
  unit; example content — `examples/applied/A03_h2_vqe/main_h2_vqe.sqx`,
  `README.md`; no grammar/parser change beyond what LISS-0331 already
  shipped)
- Priority: P1
- Initial planning size: `M`
- Owner / agent: Claude Code
- Program: [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md)
  work unit 2 (first example migration)
- Parent: [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md);
  physics derivation grounded in
  [docs/research/2026-08-05-h2-two-orbital-jordan-wigner-cross-validation.md](../research/2026-08-05-h2-two-orbital-jordan-wigner-cross-validation.md)
  (merged)
- Depends on: [LISS-0330](LISS-0330-real-hbar-kernel-primitive.md) (real
  ℏ, merged); [LISS-0331](LISS-0331-second-quantized-leading-coefficient.md)
  (leading-coefficient parse fix, merged)
- Blocks: WP-0095 work unit 3+ (remaining 13 example migrations)
- Branch: `feature/liss-0332-a03-h2-real-unit-migration`
- GitHub Issue / PR: [#381](https://github.com/nn0cl/staqex/pull/381)
  (merged, `510e860`)

## Intent

`examples/applied/A03_h2_vqe/main_h2_vqe.sqx` currently uses a bare
fermionic hopping+interaction Hamiltonian with implicit (dimensionless)
coefficient 1 on each term, and `evolve ... for 0.5` (bare, dimensionless
duration) — both now rejected at runtime by LISS-0330's fail-closed
`EVOLVE_UNRESOLVED_UNIT_ERROR`. This Issue gives it real, dimensioned
values:

1. Add `Ha` (Hartree) to `dimensions.py`'s `Energy` unit tables —
   CODATA 2018 value `1 Ha = 4.3597447222071e-18 J` (a measured
   constant, not exact-by-definition the way `eV` is; comment this
   distinction, matching the existing `u`/`oz_t` precedent for
   CODATA-sourced, non-exact constants).
2. Extend the fermionic Hamiltonian with the two on-site energy terms it
   previously lacked (`create[0]*annihilate[0]`, `create[1]*annihilate[1]`),
   parameterized with the values derived in the research note:
   `ε0 = -1.8302 Ha` (as a positive `Energy` magnitude, negated via a
   parenthesized OpDSL coefficient per LISS-0331's documented
   parenthesized-form support — a bare unary-minus-prefixed named
   coefficient is not covered by that fix and was confirmed still
   broken during this Issue's design intake), `ε1 = -0.2738 Ha`,
   `t = 0.182 Ha`, `U = 2.2864 Ha`.
3. Add the nuclear-repulsion constant `E_nn = 0.705570 Ha` as a separate
   `Operator H = H_elec + Enn * I` term after the Jordan-Wigner mapping
   (confirmed working syntax during design intake).
4. Replace `evolve ... for 0.5` with a real `Time` duration
   (`1.0 fs`) — explicitly documented as an illustrative choice (no
   specific published Trotter-step protocol is being reproduced), unlike
   the Hamiltonian coefficients, which are literature-traced.
5. Rewrite the README's Honesty table: what is now literature-traced
   (ε0/ε1/t/U, cross-checked in the research note) vs. illustrative
   (the evolution duration) vs. still not claimed (production molecular
   integrals/basis-set computation, VQE optimizer loop — unchanged from
   today's honest "No").

## Explicitly out of scope

- Running the "Follow-up" live numerical cross-check from the research
  note (dumping Staqex's own compiled `QubitOperator` coefficients and
  diffing against the ENCCS fixture) — confirmed with the Adjudicator as
  separate, optional follow-up work, not required for this migration.
  This Issue's own manual verification (below) is a lighter, one-time
  sanity check during design intake, not a shipped automated test.
- Any other example's migration (work unit 3+).
- A general fix for bare unary-minus-prefixed leading coefficients in
  second-quantized expressions (`-e0mag * create[0]...` without
  parentheses) — confirmed still broken during this Issue's design
  intake, worked around with parentheses per LISS-0331's own documented
  boundary; not re-opening that Issue's scope here.
- Any VQE optimizer loop, parameter-shift gradients, or production
  molecular integrals — the README's existing honest "No" claims for
  these are unchanged.

## Acceptance reference

New Phase 1 scenarios (no existing spec section covers this specific
example's content — the acceptance evidence is that the migrated example
compiles, runs, and produces the intended real-unit physics):

```gherkin
Feature: A03_h2_vqe uses real physical units

  Scenario: the migrated example compiles and runs to a real terminal measurement
    Given the migrated main_h2_vqe.sqx
    When it is compiled and run with a fixed seed
    Then it compiles without EVOLVE_UNRESOLVED_UNIT_ERROR or any hard diagnostic
    And it reaches a non-vacuum terminal measurement

  Scenario: hbar is used, not the retired natural-units convention
    Given the same program
    When it runs
    Then the evolution reflects the real hbar division (confirmed by the
      Hamiltonian/duration magnitudes being real Joules/seconds, not bare
      floats)
```

## Verification plan for this design intake (not shipped as a test)

Before writing the final source, the following were confirmed live in
this session, informing the exit criteria above:

- `Energy e = 1.0.eV to J` and `Time dur = 1.0.fs` both compile and carry
  a resolvable unit (`self.scalar_units`), satisfying LISS-0330's
  fail-closed check.
- `Operator H = H_elec + enn * I` (adding a constant after JW mapping)
  compiles and runs.
- `Energy e0mag = 1.8302.eV to J` (positive magnitude) as a leading
  `FermionOperator` coefficient compiles, per LISS-0331.
- A bare `-e0mag * create[0]*...` (unary minus, no parens) still fails
  with the same class of `PARSE_ERROR` LISS-0331 fixed for other forms —
  confirmed out of that fix's documented scope. `(-e0mag) * create[0]*...`
  (parenthesized) compiles correctly.

## AI planning record (size M)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-05
- Size: `M` — one small dimension-table addition (`Ha`), one example's
  `.sqx` rewrite, one README rewrite. No new grammar/parser/evaluator
  code beyond what LISS-0330/0331 already shipped.
- Route: direct implementation by this session.
- Assumptions: the derived ε0/ε1/t/U/E_nn values (research note) are
  correct as derived; per the Adjudicator's explicit direction, no
  live numerical cross-check against Staqex's own compiled coefficients
  is required before shipping this migration (tracked as separate,
  optional follow-up work in the research note).
- Confidence: high for the syntax (directly verified live); medium for
  the specific numeric values (symbolic derivation only, per the research
  note's own stated limitations — secondary-sourced literature
  coefficients, not independently re-verified against the primary PDF).
- Revision links: none yet.

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0332_a03_h2_real_unit_migration_red.py`
      added. Commit `d68505a`: failed for the documented reason
      (`EVOLVE_UNRESOLVED_UNIT_ERROR` on the bare `for 0.5` duration).
- [x] Phase 2 Green: `Ha` unit added to `dimensions.py`; `main_h2_vqe.sqx`
      rewritten with real coefficients/duration. Commit `6e0ee86`: 1/1
      passed. **Two unanticipated bugs found and fixed during Green**
      (both real, both directly blocking this migration, not scope
      creep): (1) a genuine gap in `second_quantization.py`'s
      Jordan-Wigner `_expand()` — it only ever handled unweighted
      fermionic products, never a scalar coefficient on a term, because
      no example had ever attached one before; fixed with
      `_scalar_value()` and a `scalars` parameter threaded through
      `jordan_wigner_map`/`resolve_mapping_expr` and both call sites.
      (2) a naming collision, not a bug: the coefficient name `hop`
      collides with the reserved OpDSL atom `hop(i,j)`; worked around by
      naming it `coupling` in the source, documented so it is not
      mistaken for a language defect during future example authoring.
      Confirmed via `test_applied_catalog_health_red.py`: A03 no longer
      appears in that test's failure list (only A05/A06/A10/A11 remain,
      as designed).
- [x] Phase 3 Refactor: no further change; reviewed via `python3 -W
      error -c "import ..."`, clean. README honesty table rewritten
      (own commit `6ebbea1`). Reviewer empathy summary below.
- [x] Full regression: `pytest tests/ -q` → 1194 passed, 66 failed
      (same 66 as LISS-0330/0331's baseline — `test_applied_catalog_a01_a11_compile_and_run_green`
      remains in the count, now failing only for A05/A06/A10/A11, not
      A03; +1 vs. baseline is this Issue's own new test); `python3
      tests/spec_verification/run_all.py` → 133/145 (91.72%, +1 case
      vs. LISS-0330/0331's 132/145 — the A03 SV case); `git diff
      --check` → clean.
- [x] WP-0095 work unit 2 row updated.

## Reviewer empathy summary

**何を目的として何を変更したか**: `A03_h2_vqe`を、無次元・裸のリテラル
係数と時間から、実物理単位(Hartree・フェムト秒)を持つ本物の値に移行
した。係数は`docs/research/`の導出文書に基づき文献値から逆算した
ε0/ε1/coupling/interaction、核間反発定数、そして例示的な(文献由来では
ない)実時間durationで構成される。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- Green中に、`second_quantization.py`のJordan-Wigner `_expand()`が
  **スカラー係数付きフェルミオン項を一度も扱ったことがなかった**という、
  真に未発見だった実装ギャップを発見・修正した。これはA03固有の問題
  ではなく、今後スカラー係数を使うどの例でも起こりうる一般的なバグ
  だったため、`jordan_wigner_map`/`resolve_mapping_expr`のシグネチャ
  変更を含む修正とした。
- `hop`という変数名が予約済みOpDSLアトム名`hop(i,j)`と衝突するという
  発見は、当初「言語のバグ」に見えたが、実際には自分の命名選択の問題
  だった — 誤診断を避けるため、この経緯をコメント・reviewer summaryに
  明記した。
- 文献値の出典は研究文書自体に既に明記された限界(二次資料経由、一次
  PDF未確認)がそのまま適用される。

**人間がコードレビューで重点的に見るべきポイント**:
- `_scalar_value`が対応する範囲(リテラル・名前付き変数・それらの積・
  単項マイナス)で、実際にA03以外の将来の例で必要になる範囲を十分
  カバーしているか。
- `hop`という予約語との衝突は今回`coupling`で回避したが、将来的に
  OpDSL予約語一覧をドキュメント化すべきか。

## Non-goals

- The live numerical cross-check (research note Follow-up).
- Remaining example migrations (work unit 3+).
- General unary-minus-leading-coefficient parser support.

## Addendum (2026-08-05, LISS-0336)

Re-verification during [LISS-0336](LISS-0336-evolve-real-unit-canonicalization-bugs.md)
found and fixed two independent Kernel bugs that affected this example's
`evolve` (a coalescing epsilon that could zero real-unit coefficients;
the duration not being canonicalized from `fs` to seconds). This
example's numeric coefficients/durations were not changed by that fix.
Separately, that re-verification found this example is affected by a
**third, unrelated, pre-existing bug**: `hamiltonian.py::op_n_qubits`
undercounts the qubit register for `Operator H = H_electronic +
nuclear_repulsion * I` (the Jordan-Wigner-mapped `H_electronic`'s
2-qubit structure is invisible to `op_n_qubits`'s AST walker), causing
`evolve (a, b) under H for dur` to silently drop qubit `b`. This is
**not fixed by LISS-0336** and is tracked as a new, separate Issue —
this example's physical correctness remains open pending that fix.
