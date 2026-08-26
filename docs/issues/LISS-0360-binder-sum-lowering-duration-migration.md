# LISS-0360: migrate binder/sum-lowering evolve tests to real Time units (WP-0096 work unit 2)

## Metadata

- Local issue ID: LISS-0360
- Status/phase: **complete** (2026-08-08) — PR
  [#439](https://github.com/nn0cl/staqex/pull/439) merged, commit
  `80c0353`
- Type: test-fixture migration (6 files under `tests/`) plus one
  small Kernel bug fix found and fixed during Green (see below); no
  example content
- Priority: P3
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: [WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
  work unit 2
- Parent: [WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0360-binder-sum-lowering-duration-migration`
- GitHub Issue / PR: [#439](https://github.com/nn0cl/staqex/pull/439)
  (merged, `80c0353`)

## Design decision

Migrates the 14 `EVOLVE_UNRESOLVED_UNIT_ERROR` failures (WP-0096's own
investigation undercounted this group as 13; corrected here after
Red confirmed the actual count) in 6 files that
all compose their Hamiltonian via the Operator-DSL `sum`/`product`
binder machinery (`Z[i]*Z[next(i)]`-style sums, second-quantized
ladder operators, Fock quadrature `P`/`Q`): `test_binder_composition_
and_honest_deferral_red.py`, `test_binder_lowering_execution_wiring_
red.py`, `test_liss0055_execution_acceptance.py`, `test_liss_0224_
method_returned_binder_evolve_red.py`, `test_liss_0226_nested_empty_
sum_identity_red.py`, `test_liss_0227_operator_pqn_shadow_red.py`.

Applies WP-0096's case-2 conversion: `K = 1.0545718e-19` (= `ℏ / 1fs`)
scales the whole Hamiltonian, duration numerals are kept unchanged with
`.fs` appended — preserving `H·t/ℏ` exactly, hence every existing
numeric/marginal-equality assertion.

**Two edit shapes needed, both live-verified per pattern before any
file was touched** (mirroring this session's established rigor):
1. **Existing literal coefficient**: multiply the literal's value by
   `K` in place (e.g. `1.0 * Z[i] * Z[next(i)]` →
   `1.0545718e-19 * Z[i] * Z[next(i)]`; `-1.0 * (...)` →
   `-1.0545718e-19 * (...)`; `0.5 * (P * P + Q * Q)` →
   `5.272859e-20 * (P * P + Q * Q)`) — no restructuring, since these
   already sit in a valid `<literal> * <expr>` position.
2. **Bare tensor product / bare `sum`/`product` with no coefficient**
   (e.g. `Z[0] * Z[1]`, `sum (...) { Z[i] }`, `product (...) { Z[i] }`):
   wrap the whole expression as `1.0545718e-19 * (<expr>)` — the
   Operator-DSL's existing `TENSOR_GROUPING_ERROR` rule already requires
   explicit parentheses when a scalar multiplies a tensor product, so
   this wrapping is syntactically required regardless of the ADR 0195
   migration.

**Two currently-passing tests in this file set do not call `evolve`
and are otherwise unaffected, but share a `_source()`/expression helper
with failing tests in the same file** — live-verified before finalizing
this Issue's scope: `test_liss0055_execution_acceptance.py::test_
product_preserves_ascending_factor_order` (site-order check on
`lower_finite_binder_operators`'s output — confirmed `[0, 1, 2]`
unchanged) and `test_liss_0226_nested_empty_sum_identity_red.py::test_
lowered_where_sum_omits_undetermined_identity` (confirmed the
undetermined-identity walk still returns `False` unchanged).

**One pre-existing asymmetry, not introduced or resolved by this
Issue**: `test_binder_composition_and_honest_deferral_red.py::test_
named_scalar_coefficient_in_binder_matches_literal_coefficient`
compares a `Float J = 1.0` coefficient against a hardcoded `-1.0`
literal in the comparison target — an existing sign difference in the
test's own logic, predating this migration. Scaling both sides
uniformly by the same `K` preserves whatever relationship already made
this assertion pass (this Issue does not investigate or alter that
relationship, only preserves it).

**Correction found during Green, not anticipated in the design
decision above**: `test_liss0055_execution_acceptance.py`'s originally
planned central-template wrap (`Operator H = K * ({operator})` inside
`_source()`) breaks `test_where_filters_index_tuples_before_execution`,
which inspects `compiled.qpu_ir["binder_lowering"]["H"]["provenance"]`
— that provenance metadata is only recorded when `H`'s top-level RHS
*is* the `sum(...)`/`product(...)` binder expression directly, not when
it is embedded inside an enclosing `BinOp`. Reverted the central wrap;
instead injected the `K` scale **inside** each `operator` string's
binder body (e.g. `where i < j { Z[i] * Z[j] }` → `where i < j {
1.0545718e-19 * (Z[i] * Z[j]) }`), which is mathematically identical
(scalar multiplication distributes over the sum) but keeps the
top-level RHS as the binder expression itself, preserving provenance
tracking. Applied the same body-injection approach to
`test_liss_0226_nested_empty_sum_identity_red.py`'s `_where_sum_program`
too, for consistency, even though that file's own currently-passing
test only walks `lowered["H"]` (already confirmed tolerant of either
shape) rather than checking `qpu_ir["binder_lowering"]` provenance.

**Hard Stop, presented and confirmed with the Adjudicator before
proceeding**: migrating `test_binder_composition_and_honest_deferral_
red.py`'s duration to `.fs` broke a previously-passing test,
`test_composed_sums_emit_qasm` (`QASM_TROTTER_BAD_TIME: evolve duration
is not a closed classical float`) — a genuine, previously-undiscovered
Kernel bug, not a test-authoring mistake. Root cause:
`compiler/staqex/backend/qasm/trotter.py::_eval_float`'s `Attr`
(unit-suffix) handling used its own independent, hardcoded
`unit_scale` dict (`{"s": 1.0, "ms": ..., "us": ..., "ns": ...}`) that
predates ADR 0195's `ps`/`fs` additions to `dimensions.py`'s canonical
`UNIT_SCALE_TO_CANONICAL` table and was never updated to match — the
same "hardcoded shortlist goes stale relative to the canonical source
of truth" category found repeatedly elsewhere this session. Confirmed
narrow blast radius: `spec_verification`'s QASM suite
(`sv11_qasm_transpilation.py`) does not exercise `evolve` at all, and
no shipped example currently combines QASM emission with a
`.fs`/`.ps`-suffixed duration, so this had never been triggered before
this migration. **Confirmed with the Adjudicator to include the fix in
this Issue's scope** rather than split into a separate Issue, given its
size (~10 lines). Fixed by replacing the local hardcoded dict with a
lookup against `dimensions.py`'s own `UNIT_SCALE_TO_CANONICAL`
(filtered to Time-canonical entries, i.e. `canon == "s"`, plus an
explicit `"s" → 1.0` base case), eliminating the independent duplicate
entirely rather than just adding `fs`/`ps` to it.

**Self-caught editing mistake, corrected before Green completed**: an
early `replace_all` edit on `test_binder_lowering_execution_wiring_
red.py` matched `Operator H = Z[0] * Z[1]` as a *prefix* substring
inside `_HAND_WRITTEN_CHAIN`'s longer line (`Operator H = Z[0] * Z[1] +
Z[1] * Z[2] + Z[2] * Z[3]`), producing a syntactically-valid but
wrongly-scoped result (`K * (Z[0] * Z[1]) + Z[1] * Z[2] + Z[2] * Z[3]`
— only the first term scaled). Caught by re-grepping the file's actual
post-edit state before running tests, not by a test failure; corrected
to scale the whole three-term sum.

## Per-file edits (as actually applied)

- **`test_binder_composition_and_honest_deferral_red.py`**:
  `_COMPOSED_SUMS`/`_HAND_WRITTEN_TFIM`: each `-1.0` coefficient →
  `-1.0545718e-19`; `_NAMED_COEFFICIENT`: `Float J = 1.0` →
  `Float J = 1.0545718e-19`; all three `for 0.1` → `for 0.1.fs`.
- **`test_binder_lowering_execution_wiring_red.py`**:
  `_INDEXED_PAULI_OUTSIDE_BINDER`/`_HAND_WRITTEN_ZZ`: `Z[0] * Z[1]` →
  `1.0545718e-19 * (Z[0] * Z[1])`; `_BINDER_CHAIN`: `1.0 * Z[i] *
  Z[next(i)]` → `1.0545718e-19 * Z[i] * Z[next(i)]`;
  `_HAND_WRITTEN_CHAIN`: `Z[0]*Z[1] + Z[1]*Z[2] + Z[2]*Z[3]` →
  `1.0545718e-19 * (Z[0]*Z[1] + Z[1]*Z[2] + Z[2]*Z[3])`; all four
  `for 0.1` → `for 0.1.fs`.
- **`test_liss0055_execution_acceptance.py`**: `_source()`'s template
  duration only: `for 0.1` → `for 0.1.fs` (the template's `Operator H =
  {operator}` line is unchanged — see the provenance-tracking
  correction above). Each of the 3 `operator` argument strings that
  reach `evolve` has the `K` scale injected inside its binder body
  instead: `where i < j { Z[i] * Z[j] }` → `where i < j { 1.0545718e-19
  * (Z[i] * Z[j]) }`; the nested-sum case → `{ 1.0545718e-19 * (Z[i] *
  Z[j]) }` at the innermost body; the second-quantized case → `{
  1.0545718e-19 * (create[i] * annihilate[i]) }`. The 4th test
  (`test_product_preserves_ascending_factor_order`) never calls
  `evolve` and its `operator` argument is left untouched.
- **`test_liss_0224_method_returned_binder_evolve_red.py`**: both
  `_method_returned_binder_source`/`_top_level_binder_source`:
  `sum (i in Index<0..2>) { Z[i] }` → `sum (i in Index<0..2>) {
  1.0545718e-19 * Z[i] }` (body injection, no outer parens needed since
  `Z[i]` alone is not itself a tensor product); both `for 0.1` →
  `for 0.1.fs`.
- **`test_liss_0226_nested_empty_sum_identity_red.py`**:
  `_where_sum_program`: `Z[i] * Z[j]` (inside the `where i < j { ... }`
  body) → `1.0545718e-19 * (Z[i] * Z[j])` (body injection, matching the
  liss0055 correction above); `for 0.1` → `for 0.1.fs`.
- **`test_liss_0227_operator_pqn_shadow_red.py`**:
  `_method_return_named`: `product (i in Index<0..1>) { Z[i] }` →
  `product (i in Index<0..1>) { 1.0545718e-19 * Z[i] }` (body
  injection); `for 0.1` → `for 0.1.fs`; `_unbound_xp`: `0.5 * (P * P +
  Q * Q)` → `5.272859e-20 * (P * P + Q * Q)` (coefficient swap, already
  parenthesized); `for 0.5` → `for 0.5.fs`.
- **`compiler/staqex/backend/qasm/trotter.py`** (Kernel fix, see the
  Hard Stop above): `_eval_float`'s `Attr` branch now looks up
  `dimensions.py::UNIT_SCALE_TO_CANONICAL` (filtered to `canon == "s"`)
  instead of a local hardcoded dict, plus an explicit `"s" → 1.0` base
  case.

No example content change.

## Explicitly out of scope

- Any other WP-0096 work unit.
- Investigating or "fixing" the pre-existing `J`-vs-`-1.0` sign
  asymmetry noted above.
- Any Kernel change to the Operator-DSL's `TENSOR_GROUPING_ERROR`
  parenthesization requirement (unrelated, pre-existing, unaffected).

## Acceptance reference

```gherkin
Feature: binder/sum-lowering evolve tests use real Time units

  Scenario: each migrated test passes with behavior unchanged
    Given the 14 cases across the 6 files listed above, migrated with
      the K-scale/`.fs`-duration conversion
    When run
    Then each produces the same status/marginal-equality/assertion
      result as originally intended pre-ADR-0195 (no
      EVOLVE_UNRESOLVED_UNIT_ERROR)

  Scenario: the two currently-passing, non-evolve tests sharing a helper
    with failing tests are unaffected
    Given test_product_preserves_ascending_factor_order and
      test_lowered_where_sum_omits_undetermined_identity
    When run against the modified shared source template
    Then both still pass with identical assertions
```

## Verification plan for this design intake (not shipped as a test)

Every edit pattern (existing-coefficient swap, bare-expression wrap,
central-template wrap) live-verified in isolation before any file was
edited, including the two currently-passing tests sharing a helper
with failing tests. Full `pytest tests/ -q` regression, diffed against
the current baseline (48 failed, 1260 passed), confirming exactly these
14 cases move from FAIL to PASS and nothing else changes.
`spec_verification` expected unchanged (161/161).

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `S` — 6 files, ~20 individual literal/wrap edits, each pattern
  independently live-verified before editing; two shared-helper edge
  cases specifically checked for no regression.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red: confirmed 14 cases (not WP-0096's originally
      estimated 13) already fail on `main` for the documented
      `EVOLVE_UNRESOLVED_UNIT_ERROR` reason (pre-existing tests, no new
      test file needed).
- [x] Phase 2 Green: all per-file edits above applied, including the
      provenance-tracking correction (body injection instead of a
      central template wrap) and the `trotter.py` Kernel fix. All 22
      tests across the 6 files pass (14 fixed + 8 already-passing,
      confirmed unaffected).
- [x] Phase 3 Refactor: this design decision section corrected in place
      (13→14 count, actual final edit shapes, the two Hard Stop
      findings) rather than left describing the originally-planned
      approach; WP-0096 work unit 2 marked complete; reviewer empathy
      summary below.
- [x] Full regression: `pytest tests/ -q` → 1274 passed, 34 failed
      (exactly -14 vs. the established 48-failure baseline, confirmed
      via full failure-list comparison — none of this Issue's 6 files
      remain in the failure list); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: WP-0096作業単位2として、binder/sum-
lowering機構でHamiltonianを構成する6ファイル・14件の
`EVOLVE_UNRESOLVED_UNIT_ERROR`失敗を、`K = ℏ/1fs`によるHamiltonian
全体のスケーリングとduration数値維持+`.fs`付与という、`H·t/ℏ`保存の
変換で実`Time`単位へ移行した。加えて、作業中に発見した`trotter.py`の
Kernelバグ（`fs`/`ps`単位のローカルな重複テーブルがADR 0195更新に
追従していなかった）も同一Issue内で修正した（Adjudicator確認済み）。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- WP-0096の当初調査で「このグループは13件」と見積もっていたが、
  Red確認で実際は14件と判明し、本Issue内で訂正した。
- 当初計画していた`test_liss0055_execution_acceptance.py`の
  `_source()`テンプレート全体をラップする方式が、
  `qpu_ir["binder_lowering"]`のprovenance追跡（トップレベルRHSが
  直接`sum(...)`であることを前提とする）を壊すことをGreen中に発見し、
  スコープを設計時点から変更した——テンプレート全体のラップではなく、
  各`sum`/`product`本体の内側にスケール係数を注入する方式に切り替えた
  （分配法則により数学的に同一だが、provenance追跡の前提を壊さない）。
- `test_composed_sums_emit_qasm`（元々成功）が本Issueの移行で新たに
  失敗するようになったことから、`trotter.py`の未発見Kernelバグを
  検出した。影響範囲（`spec_verification`のQASM系スイートは`evolve`
  を使わない、出荷済みexamplesはQASM出力と`.fs`/`.ps`durationを
  組み合わせていない）を確認した上で、Adjudicatorに本Issueへの
  スコープ拡大の可否を確認してから修正した。
- 編集中に`replace_all`が意図せず`_HAND_WRITTEN_CHAIN`の長い行の
  一部（プレフィックス部分）だけにマッチしてしまうミスを、テスト実行
  前の`grep`による事後確認で自己発見・修正した。

**人間がコードレビューで重点的に見るべきポイント**:
- `trotter.py`の修正が、`dimensions.py`の`UNIT_SCALE_TO_CANONICAL`を
  正しくTime系単位のみにフィルタしているか（`canon == "s"`チェック）。
- 本体注入方式とテンプレートラップ方式が混在している6ファイル間で、
  それぞれの選択理由（provenance追跡の有無）が一貫しているか。

## Non-goals

- Kernel source changes.
- Other WP-0096 work units.
- The pre-existing `J`/`-1.0` sign asymmetry (preserved, not resolved).
