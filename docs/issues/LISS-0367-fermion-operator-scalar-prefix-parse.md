# LISS-0367: `FermionOperator`/`BosonOperator`/`SpinOperator`/`QubitOperator` RHS recognizes a parenthesized second-quantized atom behind a scalar prefix

## Metadata

- Local issue ID: LISS-0367
- Status/phase: **complete** (2026-08-08) — PR
  [#453](https://github.com/nn0cl/staqex/pull/453) merged, commit
  `92c6a56`
- Type: Kernel bug fix (`compiler/staqex/parser.py`); no example
  content
- Priority: P3
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: standalone Kernel fix, closes a narrow parser gap found and
  deliberately deferred during LISS-0364 (WP-0096 work unit 6, Jordan-
  Wigner duration migration)
- Parent: none
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0367-fermion-operator-scalar-prefix-parse`
- GitHub Issue / PR: [#453](https://github.com/nn0cl/staqex/pull/453)
  (merged, `92c6a56`)

## Design decision

During LISS-0364, migrating a `FermionOperator` fixture to a real-Time
duration required scaling its coefficient. The natural spelling —
wrapping the whole ladder-operator expression in parens after a
leading scalar, `K * (create[0] * annihilate[0])` — failed to parse
(`PARSE_ERROR: function result expression must be the final item in a
block`), forcing a workaround (`K * create[0] * annihilate[0]`, no
enclosing parens) that LISS-0364 adopted without a Kernel change,
flagging the parse gap for a future Issue. This Issue is that future
Issue.

**Root cause**: `parser.py::_second_quantized_rhs_is_op_dsl` — the
heuristic `_type_first_bind` uses to decide whether a
`FermionOperator`/`BosonOperator`/`SpinOperator`/`QubitOperator`-typed
bind's RHS should parse via the Operator-DSL (`_op_expression`) or the
general expression grammar (`_expression`) — scans a bounded chain of
leading scalar-coefficient terms looking for an indexed atom
(`IDENT[`, e.g. `create[0]`). Its parenthesized-group case
(`(e0 + e1) * create[0]...`) exists to skip over a compound *scalar
coefficient* written in parens before a further `* create[...]`
continuation — but it skips the group's contents opaquely, without
checking whether the atom itself is *inside* the parens. For `K *
(create[0] * annihilate[0])`, the group being skipped **is** the
second-quantized expression, not a coefficient wrapper — the heuristic
consumes it blindly, finds no trailing `*` afterward, and returns
`False`, routing the RHS to `_expression()` instead of
`_op_expression()`, which cannot parse `create[0]`/`annihilate[0]`
atoms and produces the confusing downstream `PARSE_ERROR`.

**Adopted fix**: when `_second_quantized_rhs_is_op_dsl` skips a
parenthesized group, additionally scan the tokens *inside* that group
for an `IDENT[` pattern before continuing — if found, the group
contains (not just precedes) the second-quantized atom, so return
`True` immediately. This is additive: the existing compound-coefficient
case (no atom inside the parens) falls through unchanged, still
requiring a trailing `*` to continue the scan exactly as before.

**Live-verified** before drafting this Issue:
- `FermionOperator<Orbitals> H = 1.0545718e-19 * (create[0] *
  annihilate[0])` — previously `PARSE_ERROR`, confirmed to be the
  target this fix resolves.
- The already-working LISS-0364 workaround form (`K * create[0] *
  annihilate[0]`, no parens) and the pre-existing single-atom form
  (`create[0] * annihilate[0]`, no scalar prefix) must remain
  unaffected — both already pass through the unmodified top-level
  `IDENT[` check or the unmodified bare-chain case.

## Explicitly out of scope

- Reverting LISS-0364's workaround in `test_jordan_wigner_mapping_red.py`
  back to the parenthesized form — the workaround remains valid and
  is not required to change; this Issue only removes the *need* for
  it going forward.
- Any other parser heuristic or grammar path.

## Acceptance reference

```gherkin
Feature: second-quantized RHS recognizes a parenthesized atom behind a scalar prefix

  Scenario: scalar-prefixed, parenthesized ladder-operator expression parses
    Given `FermionOperator<Orbitals> H = 1.0545718e-19 * (create[0] * annihilate[0])`
    When compiled
    Then it does not raise PARSE_ERROR

  Scenario: the existing no-parens scalar-prefix form is unaffected
    Given `FermionOperator<Orbitals> H = 1.0545718e-19 * create[0] * annihilate[0]`
    When compiled
    Then it does not raise PARSE_ERROR (regression guard)

  Scenario: the existing bare atom form is unaffected
    Given `FermionOperator<Orbitals> H = create[0] * annihilate[0]`
    When compiled
    Then it does not raise PARSE_ERROR (regression guard)

  Scenario: a genuine compound-coefficient-then-atom form is unaffected
    Given `FermionOperator<Orbitals> H = (a + b) * create[0] * annihilate[0]`
      (a, b classical Float locals)
    When compiled
    Then it does not raise PARSE_ERROR (regression guard for the
      heuristic's original intended case)
```

## Verification plan for this design intake (not shipped as a test)

The target case confirmed failing pre-fix with the documented
`PARSE_ERROR`; root cause confirmed by direct code reading of
`_second_quantized_rhs_is_op_dsl`'s token-scan logic. Full `pytest
tests/ -q` regression after the fix, diffed against the current
baseline (0 failed, 1308 passed — `main` is fully green), confirming
no regression. `spec_verification` expected unchanged (161/161).

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `XS` — one additive inner-scan loop in one existing function,
  root cause already isolated by direct code reading.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0367_fermion_operator_scalar_prefix_parse_red.py`
      added (4 cases). Confirmed 1 of 4 failing with the fix not yet
      applied (`PARSE_ERROR: function result expression must be the
      final item in a block`, matching the documented finding); the
      other 3 (regression guards for the no-parens workaround, the
      bare-atom form, and the genuine compound-coefficient case)
      correctly already passed.
- [x] Phase 2 Green: `parser.py::_second_quantized_rhs_is_op_dsl`'s
      parenthesized-group case now scans inside the skipped group for
      an `IDENT[` atom before falling through to the compound-
      coefficient assumption. All 4 tests pass.
- [x] Phase 3 Refactor: no further code change needed; reviewer
      empathy summary below.
- [x] Full regression: `pytest tests/ -q` → 1312 passed, 0 failed
      (unchanged — `main` stays fully green; +4 this Issue's own new
      tests); `python3 tests/spec_verification/run_all.py` → 161/161
      (100%, Gate: PASS, unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: LISS-0364（WP-0096作業単位6）で
発見し、ワークアラウンドで回避したまま将来のIssueとして記録して
いたパーサーギャップを修正した。`FermionOperator`等の型付きbindの
RHSがOpDSL文法（`_op_expression`）か一般式文法（`_expression`）の
どちらでパースされるべきかを判定する`_second_quantized_rhs_is_op_dsl`
ヒューリスティックが、括弧グループをスキップする際にその中身を
チェックしていなかったため、`K * (create[0] * annihilate[0])`の
ようにスカラー接頭辞の後の括弧内に二次量子化atomがある形を認識
できず、一般式文法に誤って振り分けられ`create[0]`をパースできずに
`PARSE_ERROR`となっていた。括弧グループをスキップする際に、その
内部トークンも`IDENT[`パターンでスキャンし、見つかればOpDSL式と
即座に判定するよう追加した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- ヒューリスティック本来の意図（`(e0 + e1) * create[0]...`のような、
  括弧が真に複合係数を表すケース）を壊さないことを、専用の回帰
  テストケース（`test_compound_coefficient_then_atom_still_parses`）
  で明示的に確認した。
- LISS-0364が採用したワークアラウンド形式（括弧なし）と、既存の
  裸atom形式の両方が引き続き正しくパースされることも回帰テストで
  確認した。

**人間がコードレビューで重点的に見るべきポイント**:
- 特になし（既存ヒューリスティックへの局所的・加算的な拡張、副作用
  なしを回帰テストで確認済み）。

## Non-goals

- Changing LISS-0364's existing test fixtures.
- Any other parser heuristic.
