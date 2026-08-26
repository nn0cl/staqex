# LISS-0325: real `NON_HERMITIAN_OPERATOR_ERROR` check for H1 operators

## Metadata

- Local issue ID: LISS-0325
- Status/phase: **complete** (2026-08-05) — PR
  [#359](https://github.com/nn0cl/staqex/pull/359) merged, commit
  `765ed17`
- Type: Feature Path (Kernel — `compiler/staqex/h1_authoring.py`; no
  grammar/parser/AST change)
- Priority: P2 (test-suite-only blast radius; no shipped example uses
  `theory`/`experiment`)
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: [WP-0092](../work-plans/WP-0092-quantum-mental-model-follow-up.md)
  work unit 6
- Related: [LISS-0326](LISS-0326-h1-basis-target-capability-diagnostics.md)
  (the other two H1 diagnostic-honesty gaps found in the same investigation;
  deliberately split out — see that Issue's scope note for why)
- Depends on: none
- Branch: `feature/liss-0325-h1-non-hermitian-operator-diagnostic`
- GitHub Issue / PR: none yet

## Intent

`compiler/staqex/h1_authoring.py::_operator_diagnostics` (line 370) currently
fires `NON_HERMITIAN_OPERATOR_ERROR` on:

```python
if "i" in referenced_names and "sum" not in operator.source_tokens:
```

This is a naming-convention heuristic (does an identifier literally spell
`i`?), not a type-aware check. Verified false positive (documented in the
[kernel stub and placeholder registry](../architecture/kernel-stub-and-placeholder-registry.md#h1-authoring-layer-h1_authoringpy--multiple-substringname-heuristics-behind-real-looking-diagnostic-codes)):

```staqex
theory Valid {
  parameter i: Real
  operator H = i * Z
}
```

still raises `NON_HERMITIAN_OPERATOR_ERROR`, even though `i` is declared as
an ordinary `Real` scalar parameter (mathematically producing a Hermitian
operator), because the checker never consults `operator.parameter_types`.

Fix: only treat `i` as the imaginary unit when it is **not** a declared
operator parameter —

```python
if (
    "i" in referenced_names
    and "i" not in operator.parameter_types
    and "sum" not in operator.source_tokens
):
```

`operator.parameter_types: dict[str, str]` is already real, structured data
(built by `Parser._parse_h1_theory_members`, `parser.py:553`) — this fix
adds no new AST surface, just consults a field that already exists.

## Verified: does not regress the existing positive test

`tests/test_h1_3_operator_ast_red.py::test_h1_3_non_hermitian_hamiltonian_is_rejected`
uses `theory Invalid { operator H = i * X }` with **no** `parameter i: ...`
declaration — `operator.parameter_types` is `{}` there, so
`"i" not in operator.parameter_types` stays `True` and the diagnostic still
fires. Confirmed by reading the test source directly
(`tests/test_h1_3_operator_ast_red.py:74-84`) before drafting this Issue.

## Explicitly out of scope

- `BASIS_MISMATCH_ERROR` / `TARGET_CAPABILITY_REJECT` — see LISS-0326; these
  require a grammar/AST extension, unlike this fix.
- Any change to `theory`/`experiment` grammar, `TheoryDecl`, or
  `H1OperatorDecl`'s fields.
- A general symbolic/type-aware Hermiticity checker (e.g. verifying operator
  algebra actually satisfies $H = H^\dagger$). This Issue only removes one
  false-positive path in the existing name-based heuristic; it does not
  replace the heuristic with full symbolic verification, which is out of
  scope for the H1 authoring layer's current "structured metadata, not
  numerical execution" boundary (module docstring).

## Acceptance reference

New Phase 1 scenario (no existing spec has a normative H1 Hermiticity
section yet; this Issue's Red test is the acceptance evidence, matching the
established pattern for H1-layer Issues found directly in prior sessions,
e.g. LISS-0320's `test_liss_0320_superpose_formal_grammar_red.py`):

```gherkin
Feature: H1 operator Hermiticity diagnostic honesty

  Scenario: a declared real parameter literally named i is not flagged
    Given theory Valid { parameter i: Real; operator H = i * Z }
    When the program is compiled
    Then NON_HERMITIAN_OPERATOR_ERROR does not fire

  Scenario: an undeclared imaginary-unit spelling is still flagged
    Given theory Invalid { operator H = i * X }
    When the program is compiled
    Then NON_HERMITIAN_OPERATOR_ERROR fires
```

The second scenario is the existing, unchanged
`test_h1_3_non_hermitian_hamiltonian_is_rejected` regression — restated here
only to make the acceptance contract explicit, not duplicated as a new test.

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-05
- Size: `S` — one boolean condition in one function, one file; no new AST,
  no new diagnostic code, no parser change.
- Route: direct implementation by this session.
- Assumptions: `parameter_types` correctly reflects every `parameter <name>:
  <type>` declared directly in the theory body (verified by reading
  `parser.py:553` — `parameter_types` is built from the same `parameters`
  list right before each operator is constructed, so ordering within the
  theory body does not create a staleness risk for a `parameter` declared
  before the `operator` line, which is the only order the grammar allows
  since `parameter` and `operator` are scanned in one forward pass).
- Confidence: high — false-positive and non-regression behavior both
  verified by direct source reading before drafting this Issue.

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0325_h1_non_hermitian_operator_diagnostic_red.py`
      added. Commit `27c60b5`: failed for the documented reason
      (`NON_HERMITIAN_OPERATOR_ERROR` fired on a declared `parameter i:
      Real`).
- [x] Phase 2 Green: `"i" not in operator.parameter_types"` added to the
      condition. Commit `0fb1ba2`: new test passes; existing H1 test suite
      (`test_h1_3_operator_ast_red.py` 5/5, `test_h1_2_parser_ast_red.py`
      4/4) unchanged and passing, including the undeclared-`i` regression.
- [x] Phase 3 Refactor: no further change — the fix is already a single,
      minimal condition; nothing to simplify without losing clarity.
      Reviewer empathy summary below.
- [x] Full regression: `pytest tests/ -q` → 1229 passed; `python3
      tests/spec_verification/run_all.py` → 161/161; `git diff --check` →
      clean.
- [x] WP-0092 work unit 6 row and the kernel stub registry's
      `NON_HERMITIAN_OPERATOR_ERROR` entry updated to reflect the real fix.

## Reviewer empathy summary

**何を目的として何を変更したか**: `h1_authoring.py::_operator_diagnostics`の
`NON_HERMITIAN_OPERATOR_ERROR`判定に`"i" not in operator.parameter_types`
条件を追加した。これにより、`parameter i: Real`のように`i`が通常の実数
パラメータとして明示的に宣言されている場合は誤検出しなくなる。既存の
(未宣言の`i`が虚数単位とみなされ検出される)回帰は変更なし。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- `operator.parameter_types`が理論本文で宣言された`parameter`のみを反映し、
  `operator`宣言の引数リスト(`operator H(J, h) = ...`の`J`,`h`)とは別物
  であることを`parser.py`の実装を直接確認した上で前提としている。両者が
  将来ズレる設計変更が入った場合、この修正の前提が崩れる可能性がある。
- この修正は依然として名前ベースのヒューリスティックの一部(識別子`i`の
  綴りチェック)であり、真の記号的/型的エルミート性検証ではない。将来
  `i`以外の綴り(`imag`, `𝑖`等)や複素数型導入時の扱いは対象外。

**人間がコードレビューで重点的に見るべきポイント**:
- `parameter_types`を「宣言済みパラメータの型」以外の意味(例:演算子の
  引数リスト)と混同していないか。
- この修正がH1認証層全体の「文字列ヒューリスティック」という性質を変え
  ない、限定的な訂正であることに同意できるか(BASIS_MISMATCH_ERROR/
  TARGET_CAPABILITY_REJECTはLISS-0326で別途、より大きな設計変更として
  扱う)。

## Non-goals

- Full symbolic Hermiticity verification.
- Any change touching `BASIS_MISMATCH_ERROR` or `TARGET_CAPABILITY_REJECT`.
