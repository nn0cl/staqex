# LISS-0370: Jordan-Wigner mapping expands `adjoint(...)` of a fermionic sub-expression

## Metadata

- Local issue ID: LISS-0370
- Status/phase: **complete** (2026-08-08) — PR
  [#459](https://github.com/nn0cl/staqex/pull/459) merged, commit
  `de176cf`
- Type: Kernel bug fix (`compiler/staqex/second_quantization.py`,
  `compiler/staqex/finite_binder.py`); no example content
- Priority: P3
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: standalone Kernel fix, closes the fourth candidate from the
  second architectural audit (LISS-0368/0369 covered the other three),
  re-verified with corrected repro syntax after the first repro attempt
  failed for unrelated reasons
- Parent: none
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0370-jw-mapping-adjoint-support`
- GitHub Issue / PR: [#459](https://github.com/nn0cl/staqex/pull/459)
  (merged, `de176cf`)

## Design decision

Re-verifying the fourth audit candidate with the correct combining
syntax (`Operator H = sum (...) { ... }`, not `FermionOperator<Orbitals>
H = sum (...) { ... }` — the earlier repro attempt used the wrong bind
type and failed identically for both the control and candidate case,
masking the real finding) confirmed a genuine bug:
`annihilate[i]` succeeds inside a binder body; the physically-equivalent
`adjoint(create[i])` fails. Each of three tested contexts fails with a
*different* error, tracing to the same root cause at different depths:

- Inside a `sum` binder body: `RUNTIME_ERROR: cannot compile sparse
  Pauli for OpBinder` (`finite_binder.py::_contains_second_quantized`
  never recognizes an `OpCall`, so the binder-lowering path never
  routes the term through the Jordan-Wigner mapping at all).
- As a bare `Operator` expression outside a binder: `RUNTIME_ERROR:
  indexed sparse Pauli requires a literal site` (a different pipeline
  entirely, also with no `adjoint`-of-ladder-operator support).
- Through the explicit `FermionOperator` + `map(H, JordanWigner)` path:
  `RUNTIME_ERROR: SECOND_QUANTIZATION_MAPPING_UNSUPPORTED: \`OpCall\`
  is not covered by the Jordan-Wigner mapping slice` — the precise
  root cause: `second_quantization.py::_expand` has **no case at all**
  for `OpCall` (which `adjoint(x)`/postfix `†` always parses to,
  confirmed via direct code reading of `parser.py`'s `adjoint`
  handling) — not a narrow-recognition gap like LISS-0368/0369, but a
  genuinely missing semantic rule.

**Unlike LISS-0368/0369 (mirroring an already-correct sibling
recognition pattern), this requires implementing new mapping logic —
verified for physical correctness before implementation**, not just
widening an existing check. `_create(index)`/`_annihilate(index)` each
produce a list of `(complex coefficient, {site: Pauli letter})` terms
where every term's Pauli-tensor-product factor is Hermitian (each
single-qubit `X`/`Y`/`Z`/`I` is self-adjoint, and different-site
factors commute in this dict-keyed representation). For any Hermitian
operator `Op` and complex scalar `c`, `(c · Op)† = c̄ · Op`, and adjoint
distributes over sums — so the adjoint of *any* expandable
second-quantized (sub-)expression is simply its term list with each
coefficient complex-conjugated, the Pauli-operator part unchanged.
**Verified numerically before implementation**: conjugating every
coefficient of `_create(0)`'s two terms produces exactly
`_annihilate(0)`'s terms (`[(0.5+0j, {0:'X'}), (0.5j, {0:'Y'})]` in
both cases after conjugation) — confirming the general rule, not just
the single-atom case the original finding used.

**Adopted fix (three sites — the third found only while confirming
Green for the binder case, not anticipated at Plan time)**:
1. `second_quantization.py::_expand` gains an `OpCall` case: for
   `adjoint(x)` (`expr.name == "adjoint"`, one argument), recursively
   expand `x` and return each term with its coefficient conjugated.
   Any other `OpCall` name (e.g. `commutator`/`anticommutator`, out of
   ADR 0093's stated scope) still raises the existing
   `SECOND_QUANTIZATION_MAPPING_UNSUPPORTED` error, unchanged.
2. `finite_binder.py::_contains_second_quantized` gains an `OpCall`
   case, recursing into `expr.args` — generalizing the same way its
   existing `OpBin` case already recurses into `lhs`/`rhs`, so any
   call wrapping a second-quantized atom (not just `adjoint`
   specifically) is correctly detected and routed to the JW-mapping
   binder-lowering path instead of silently falling through.
3. **Found only after (1) and (2) still left the binder-body case
   failing** (`RUNTIME_ERROR: cannot compile sparse Pauli for
   OpBinder`, unchanged): `finite_binder.py::_substitute_indices` —
   which resolves a binder's bound index variable (`i` in `sum (i in
   Index<0..1>) {...}`) into a concrete literal before JW mapping runs
   — also had no `OpCall` case, so `adjoint(create[i])`'s `i` was
   never substituted and reached `_orbital_index` still symbolic.
   Added the same recursive `OpCall` case, mirroring its existing
   `OpBin` case, rebuilding the call with each argument's indices
   substituted.

## Explicitly out of scope

- `adjoint` of a general (non-fermionic) Operator expression — already
  works via the existing, unrelated Operator-DSL `adjoint`/`†`
  mechanism; this Issue only adds the missing case inside the
  Jordan-Wigner `_expand` function specifically.
- `commutator`/`anticommutator` of fermionic terms — remain genuinely
  unsupported (ADR 0093 scope), still rejected with the existing
  diagnostic, unchanged by this fix.
- Any other audit candidate (LISS-0368/0369 already closed the other
  three).

## Acceptance reference

```gherkin
Feature: Jordan-Wigner mapping expands adjoint(...) of a fermionic sub-expression

  Scenario: adjoint(create[i]) is accepted as equivalent to annihilate[i], inside a binder
    Given `Operator H = sum (i in Index<0..1>) { K * (create[i] * adjoint(create[i])) }`
    When compiled and run
    Then it does not raise RUNTIME_ERROR
    And it produces the same measured outcome as the equivalent
      `create[i] * annihilate[i]` form

  Scenario: adjoint(create[i]) is accepted through the explicit FermionOperator + JordanWigner path
    Given `FermionOperator<Orbitals> H = K * create[0] * adjoint(create[0])`
    When compiled and run (via `map(H, JordanWigner)`)
    Then it does not raise SECOND_QUANTIZATION_MAPPING_UNSUPPORTED

  Scenario: a genuinely unsupported OpCall (e.g. commutator) is still rejected
    Given a fermionic expression using `commutator(...)`
    When compiled and run
    Then it still raises SECOND_QUANTIZATION_MAPPING_UNSUPPORTED (regression guard)
```

## Verification plan for this design intake (not shipped as a test)

The physical correctness of the adopted rule (conjugate-coefficient
adjoint) verified two ways before implementation: analytically (each
term's Pauli-tensor factor is Hermitian, so `(c·Op)† = c̄·Op`) and
numerically (`_create(0)`'s conjugated terms exactly equal
`_annihilate(0)`'s terms). The target failure confirmed live in all
three contexts with the corrected repro syntax before drafting this
Issue. Full `pytest tests/ -q` sweep after the fix, diffed against the
current baseline (0 failed, 1318 passed — `main` is fully green),
confirming no regression. `spec_verification` expected unchanged
(161/161).

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `S` — one new semantic case in `_expand` (verified correct
  both analytically and numerically before implementation) plus one
  additive recursion case in `_contains_second_quantized`.
- Route: direct implementation by this session.
- Confidence: high (physics verified two independent ways before
  writing any implementation code).

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0370_jw_mapping_adjoint_support_red.py` added (3
      cases). Confirmed 2 of 3 failing with the fix not yet applied
      (`RUNTIME_ERROR: cannot compile sparse Pauli for OpBinder` /
      `SECOND_QUANTIZATION_MAPPING_UNSUPPORTED: OpCall is not covered`,
      matching each documented finding exactly); the unit-level
      regression guard (a genuinely unsupported `OpCall` name must
      still be rejected) correctly already passed. The originally
      drafted commutator-based integration regression guard was
      dropped after discovering it hits an unrelated, pre-existing
      Operator-DSL leading-atom parser gap (`commutator(...)` alone is
      never recognized as a valid FermionOperator RHS start) — replaced
      with a direct unit-level test of `_expand` constructing the
      `OpCall` AST node manually, bypassing that unrelated gap.
- [x] Phase 2 Green: applied fixes (1) and (2) from the design section;
      re-ran Red and found the binder-body case still failing with the
      *same* error, unchanged — found and fixed site (3)
      (`_substitute_indices`) before Green was actually reached. All 3
      tests pass.
- [x] Phase 3 Refactor: design decision section updated in place to
      record the third fix found only during Green, not anticipated at
      Plan time; reviewer empathy summary below.
- [x] Full regression: `pytest tests/ -q` → 1321 passed, 0 failed
      (unchanged — `main` stays fully green; +3 this Issue's own new
      tests); `python3 tests/spec_verification/run_all.py` → 161/161
      (100%, Gate: PASS, unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: 2回目のアーキテクチャ監査で発見し、
当初は誤った構文検証により再現できなかった`adjoint(create[i])`が
`annihilate[i]`と等価に動作しないという問題を、正しい構文
（`Operator H = sum(...) {...}`）で再検証した上で修正した。単なる
既存チェックの認識範囲拡張ではなく、`_expand`にadjoint演算の新しい
写像規則（係数の複素共役を取る）を実装前に解析的・数値的に両方で
物理的正しさを検証してから追加した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- `adjoint(create[i]) == annihilate[i]`という物理的主張を、実装前に
  2通りで検証した：(1) 解析的に——各項のPauli演算子部分は全て
  自己随伴（Hermitian）であり異なるサイト間は可換なので、
  `(c・Op)† = c̄・Op`が成り立つこと、(2) 数値的に——`_create(0)`の
  各項の係数を複素共役した結果が`_annihilate(0)`の項と完全一致する
  ことをPythonで直接確認した。この2重検証により、単一atomのケース
  だけでなく、任意の複合的な二次量子化部分式に対しても一般的に
  正しい規則であることを確認した。
- 修正(1)(2)を適用した後もbinder内のケースだけが同じエラーで失敗
  し続けたため、`_substitute_indices`という3つ目の未修正箇所を
  Green段階で発見した——これはPlan承認時点では想定していなかった
  追加修正だが、同一Issueの同一根本テーマ（adjoint()をbinder+JW写像
  パイプライン全体で動作させる）の範囲内での発見だったため、
  別Issueに分割せず本Issue内で完結させた。
- 当初の`commutator(...)`を使った回帰ガードテストが、本Issueとは
  無関係な既存のパーサー制約（`commutator(...)`単体がFermionOperator
  RHSの開始として認識されない）に阻まれることを発見し、AST構築を
  直接行うユニットレベルのテストに差し替えた。

**人間がコードレビューで重点的に見るべきポイント**:
- `_expand`の`adjoint`規則の物理的正しさの根拠（Hermitianな
  Pauli演算子部分×複素係数の随伴 = 係数の複素共役）が、この
  設計セクションの説明で十分か。

## Non-goals

- `adjoint` outside the Jordan-Wigner `_expand` path (already works).
- `commutator`/`anticommutator` (out of ADR 0093 scope, unchanged).
- Other audit candidates (already closed).
