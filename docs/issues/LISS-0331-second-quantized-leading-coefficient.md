# LISS-0331: `FermionOperator`/etc. RHS with a leading scalar coefficient fails to parse

## Metadata

- Local issue ID: LISS-0331
- Status/phase: **complete** (2026-08-05) — PR
  [#378](https://github.com/nn0cl/staqex/pull/378) merged, commit
  `4e0ae9a`
- Type: Feature Path (Kernel — `compiler/staqex/parser.py::_type_first_bind`
  only; no AST/typecheck/evaluator change)
- Priority: P2
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: found during
  [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md) work
  unit 2 design intake (`A03_h2_vqe` migration); this Issue fixes an
  unrelated, pre-existing parser bug the migration surfaced, not part of
  WP-0095's own scope
- Depends on: none
- Branch: `feature/liss-0331-second-quantized-leading-coefficient`
- GitHub Issue / PR: none yet

## Intent

`FermionOperator<Orbitals> H = 1.0 * create[0] * annihilate[0]` fails to
parse (`PARSE_ERROR: function result expression must be the final item in
a block`), while `create[0] * annihilate[0] * 1.0` and `create[0] * 1.0 *
annihilate[0]` (coefficient anywhere except first) both parse and compile
cleanly.

Root cause, confirmed by direct code reading:
`parser.py::_type_first_bind` (line ~1886) decides whether a
`FermionOperator`/`BosonOperator`/`SpinOperator`/`QubitOperator` binding's
RHS is parsed via the Operator-DSL grammar (`_op_expression()`, which
understands `create[i]`/`annihilate[i]` second-quantized atoms) or the
ordinary expression grammar (`_expression()`, which does not) based
**only** on whether the very first token is `IDENT` immediately followed
by `[`:

```python
if (
    self._peek().kind == TokenKind.IDENT
    and self._peek_at_kind(1) == TokenKind.LBRACKET
):
    expr = self._op_expression()
else:
    expr = self._expression()
```

A leading scalar coefficient (`1.0 * create[0] * ...`) makes the first
token a `FLOAT`, not `IDENT`, so this check silently routes the whole
fermionic expression through the wrong grammar, producing a confusing,
unrelated-looking parse error instead of a real second-quantized
expression.

## Fix

**Scope widened during design intake**: a named `Float`-variable leading
coefficient (`Float e0 = 1.0` then `FermionOperator<Orbitals> H = e0 *
create[0] * annihilate[0]`) was verified to fail identically
(`e0` is `IDENT` but followed by `STAR`, not `LBRACKET`, so the original
single-token check also misses it) — this is the more realistic pattern
for physically-real, named-scalar coefficients (WP-0095's own migration
need), so the fix generalizes to a small bounded forward scan rather than
only the literal-numeric case:

```python
def _second_quantized_rhs_is_op_dsl(self) -> bool:
    """FermionOperator/BosonOperator/SpinOperator/QubitOperator RHS:
    detect a second-quantized OpDSL expression (`create[i]`/`annihilate[i]`
    atoms) even behind a chain of leading scalar coefficients
    (`1.0 * create[0]...`, `e0 * create[0]...`, `2.0 * e0 * create[0]...`),
    not just when the atom is the very first token."""
    offset = 0
    while offset <= 8:  # bounded: a handful of chained coefficients at most
        kind = self._peek_at_kind(offset)
        next_kind = self._peek_at_kind(offset + 1)
        if kind == TokenKind.IDENT and next_kind == TokenKind.LBRACKET:
            return True
        if kind not in (TokenKind.INT, TokenKind.FLOAT, TokenKind.IDENT):
            return False
        if next_kind != TokenKind.STAR:
            return False
        offset += 2
    return False
```

Used in place of the inline condition at `_type_first_bind`'s
`FermionOperator`/etc. branch. Verified this does not regress the
`QubitOperator<Qubits> H = map(H_fermion, JordanWigner)` binding form
(the second token after `map` is `LPAREN`, not `STAR`/`LBRACKET`, so the
scan correctly falls through to `False` / ordinary `_expression()` on the
very first iteration).

## Explicitly out of scope

- Any change to `_op_expression`/`_op_primary`'s own internal handling of
  multiplication once dispatched correctly — only the FermionOperator/etc.
  binding's up-front grammar-selection heuristic changes.
- Unary-prefix coefficients with no parentheses (e.g. `-1.0 * create[0]`)
  — not raised as a concern; the scan treats a leading `-` as an
  unrecognized token and falls through. A parenthesized form
  (`(-1.0) * create[0]`) is covered, since it is skipped as a balanced
  group.

**Scope extended again during review**: a parenthesized compound
coefficient expression (`(e0 + e1) * create[0] * ...`) was flagged by the
Adjudicator as common enough to support, not deferred. The scan now skips
a balanced `(...)` group (depth-counted, so nested parens and any
operators inside are handled without needing to parse them) as one
coefficient term, in addition to a bare literal or name.

## Acceptance reference

```gherkin
Feature: FermionOperator RHS with a leading scalar coefficient

  Scenario: a leading numeric literal coefficient parses via the OpDSL grammar
    Given FermionOperator<Orbitals> H = 1.0 * create[0] * annihilate[0]
    When the program is compiled
    Then it compiles without a PARSE_ERROR

  Scenario: a leading named Float coefficient parses via the OpDSL grammar
    Given Float e0 = 1.0
      And FermionOperator<Orbitals> H = e0 * create[0] * annihilate[0]
    When the program is compiled
    Then it compiles without a PARSE_ERROR

  Scenario: existing non-leading-coefficient forms are unaffected
    Given FermionOperator<Orbitals> H = create[0] * annihilate[0] * 1.0
    When the program is compiled
    Then it compiles without a PARSE_ERROR (regression, already passing)

  Scenario: the QubitOperator map(...) binding form is unaffected
    Given QubitOperator<Qubits> H = map(H_fermion, JordanWigner)
    When the program is compiled
    Then it compiles without a PARSE_ERROR (regression, already passing)
```

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-05
- Size: `S` — one lookahead condition in one function, one file.
- Route: direct implementation by this session.
- Confidence: high — root cause directly confirmed by reading the exact
  dispatch condition and reproducing the failure/success pattern across
  three coefficient-position variants before drafting this Issue.

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0331_second_quantized_leading_coefficient_red.py`
      added (4 scenarios). Commit `826be6a`: 2/4 failed for the documented
      reason (both leading-coefficient forms); the two already-working
      forms (trailing coefficient, `map(...)` binding) passed unchanged.
- [x] Phase 2 Green: `_second_quantized_rhs_is_op_dsl` added, replacing
      the single-token check. Commit `390c32b`: 4/4 passed.
- [x] Phase 3 Refactor: no further change; reviewed via `python3 -W
      error -c "import ..."`, clean. Reviewer empathy summary below.
- [x] Full regression (after both rounds — leading token coefficient, then
      the parenthesized-expression extension): `pytest tests/ -q` → 1193
      passed, 66 failed (same 66 as before this fix — all the
      pre-existing, unrelated ADR 0195/LISS-0330
      `EVOLVE_UNRESOLVED_UNIT_ERROR` family; +5 vs. the pre-LISS-0331
      baseline are this Issue's own new tests; no new failures
      introduced); `python3 tests/spec_verification/run_all.py` →
      132/145 (91.03%), unchanged from before this fix; `git diff
      --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: `FermionOperator`等の右辺式で、
先頭にスカラー係数(`1.0 * create[0]*...`または`e0 * create[0]*...`)が
来ると、パーサが誤った文法(OpDSLではなく通常式)を選択し、無関係に
見えるパースエラーを出す問題を修正した。`_second_quantized_rhs_is_op_dsl`
という有界の先読みスキャンで、係数の連鎖の後に`atom[`が現れるかを
正しく検出するようにした。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 元のIssue設計では数値リテラル係数のみを対象にしていたが、設計調査中に
  名前付き`Float`変数係数(`e0 * create[0]*...`、WP-0095の実移行で実際に
  必要な形)も同様に壊れていることを発見し、スコープを拡張した。
- 先読みの上限(8トークン、係数4個分)は経験的な選択で、正式な要件から
  導出したものではない。

**人間がコードレビューで重点的に見るべきポイント**:
- 有界スキャン(係数項6個分)が実用上十分か。
- レビュー中にAdjudicatorから「`(e0 + e1) * create[0]*...`のような複合式
  係数はよく見る形」との指摘を受け、括弧でまとまった係数式(深さ管理付き
  スキャンで内部の`+`/`-`等は解析せずスキップ)にも対応するようスコープを
  拡張した。単項マイナス無括弧形式(`-1.0 * create[0]`)は依然非対応
  (Non-goals記載)だが、括弧で囲めば(`(-1.0) * create[0]`)動作する。

## Non-goals

- General multi-term/named-variable coefficient forward-scanning beyond
  the single-leading-numeric-literal case.
