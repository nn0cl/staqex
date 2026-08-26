# LISS-0369: `Float[M…] row = expr[i]` RHS recognizes a struct/class-field array before the index, not just a bare variable

## Metadata

- Local issue ID: LISS-0369
- Status/phase: **complete** (2026-08-08) — PR
  [#457](https://github.com/nn0cl/staqex/pull/457) merged, commit
  `421edf6`
- Type: Kernel bug fix (`compiler/staqex/parser.py`); no example
  content
- Priority: P3
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: standalone Kernel fix, closes a narrow parser gap found
  during the same architectural audit as LISS-0368 (the fourth
  candidate from that audit, previously deferred to its own Issue
  since it is a different file/layer)
- Parent: none
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0369-typed-array-field-index-bind`
- GitHub Issue / PR: [#457](https://github.com/nn0cl/staqex/pull/457)
  (merged, `421edf6`)

## Design decision

`parser.py::_type_first_bind`'s ADR 0118 / LISS-0149 gate for
`Float[M…] row = h[i]` (an array-typed local bound to an indexed slice
of another classical array, so the RHS is parsed via the Operator-DSL
grammar, which is the only grammar with `[` postfix indexing support
for classical values) only recognizes a **bare variable name**
immediately followed by `[`: `self._peek().kind == TokenKind.IDENT and
self._peek_at_kind(1) == TokenKind.LBRACKET`. A struct- or class-field
array (`m.h[1]`, where `m.h` is itself the array) does not match —
`self._peek_at_kind(1)` is `DOT`, not `LBRACKET` — so the RHS falls
through to the general expression grammar (`_expression()`), which has
no `[` postfix indexing support at all for classical values, and the
parse fails downstream with a misleading `PARSE_ERROR: function result
expression must be the final item in a block`.

Live-verified: `Float[2][2] h = [...]; Float[2] row = h[1]` (bare
variable, the form the existing LISS-0149 test covers) compiles;
`D.Mat m = D.Mat([...]); Float[2] row = m.h[1]` (identical array value,
reached through a class field) fails with the documented error.

**Adopted fix**: generalize the gate the same way LISS-0358 generalized
the analogous `Operator H = recv.method()` dotted-call gate — replace
the single-hop `self._peek_at_kind(1) == TokenKind.LBRACKET` check with
a new `_dotted_index_lookahead` helper accepting any depth of
`.<ident>` hops (including zero, preserving the existing bare-variable
case) before the `[`.

**Hard Stop, presented and confirmed with the Adjudicator before
finalizing scope**: applying the parser fix alone surfaced a *second*,
larger gap one layer down — `typecheck.py::_check_float_partial_bind`
(ADR 0118's own type-checking for this construct) requires the indexed
expression's root to be an `OpVar` present in `self.float_arrays`, a
flat `name -> shape` dict that **only tracks top-level local
variables** — no struct/class field-array shape-tracking exists
anywhere in the codebase (unlike the unit-tracking case in LISS-0357,
where ADR 0174's `field_units` already existed and just needed to be
consulted). Making `m.h[1]` fully *execute* would require designing
and implementing new field-array-shape-tracking infrastructure, a
materially larger scope than this Issue's originally-approved "mirror
an existing lookahead helper" fix. **Confirmed with the Adjudicator to
keep this Issue's scope as originally approved**: the parser fix alone
is still a genuine, valuable improvement in isolation — `m.h[1]` now
correctly reaches the Operator-DSL grammar (no more misleading
`PARSE_ERROR: function result expression must be the final item in a
block`) and instead surfaces the accurate, narrowly-scoped ADR 0118
diagnostic (`TYPE_MISMATCH: partial Float index requires a known
Float[…] tensor root`) — a real diagnostic-quality fix, even though
full struct/class field-array indexing support remains a separate,
unimplemented future Issue.

## Explicitly out of scope

- Any other candidate from the same audit round (LISS-0368 covered the
  two `second_quantization.py` gaps; the `finite_binder.py`
  `adjoint(...)` candidate remains unverified and unpursued).
- Any change to `_op_expression()`'s own indexing/attribute grammar
  (already general — `OpVar → OpAttr* → OpIndexed*` — confirmed by
  direct call during investigation; only the *gate deciding whether to
  invoke it* was narrow).
- **Struct/class field-array shape-tracking in `typecheck.py`** — the
  second, larger gap found while applying this fix (see the Hard Stop
  above). `m.h[1]` still does not fully compile after this Issue;
  it now fails with an accurate `TYPE_MISMATCH` instead of a
  misleading `PARSE_ERROR`. Implementing full support is a separate,
  future Issue (would need a `field_shapes`-style tracking mechanism
  analogous to ADR 0174's `field_units`, plus updates to
  `_check_float_partial_bind` and its sibling shape-resolution check
  to accept an `OpAttr` root).

## Acceptance reference

```gherkin
Feature: typed array-index bind RHS recognizes a field array before the index

  Scenario: a struct/class-field array indexed on the RHS reaches the
    correct, accurate diagnostic instead of a misleading parse error
    Given `D.Mat m = D.Mat([...]); Float[2] row = m.h[1]` (m.h is a
      Float[2][2] class field)
    When compiled
    Then it does not raise PARSE_ERROR
    And it raises the ADR 0118 TYPE_MISMATCH ("partial Float index
      requires a known Float[…] tensor root") instead, since
      struct/class field-array shape tracking is not yet implemented

  Scenario: the existing bare-variable form is unaffected
    Given `Float[2][2] h = [...]; Float[2] row = h[1]`
    When compiled
    Then it does not raise PARSE_ERROR (regression guard, ADR 0118 / LISS-0149)
```

## Verification plan for this design intake (not shipped as a test)

The target case confirmed failing pre-fix with the documented
`PARSE_ERROR`; root cause confirmed by direct code reading of the
existing gate condition. Full `pytest tests/ -q` sweep after the fix,
diffed against the current baseline (0 failed, 1316 passed — `main` is
fully green), confirming no regression. `spec_verification` expected
unchanged (161/161).

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `XS` — one lookahead-helper generalization mirroring the
  already-shipped `_dotted_call_lookahead` pattern from LISS-0358.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0369_typed_array_field_index_bind_red.py` added
      (2 cases). Confirmed the target case failing pre-fix with the
      documented `PARSE_ERROR` (re-confirmed via `git stash` on
      `parser.py` alone after the scope-narrowing Hard Stop, to verify
      the *updated* assertion — no `PARSE_ERROR`, a `TYPE_MISMATCH`
      instead — genuinely fails against the unfixed parser); the
      bare-variable regression guard correctly already passed.
- [x] Phase 2 Green: `parser.py` gained `_dotted_index_lookahead`
      (mirroring `_dotted_call_lookahead`'s pattern from LISS-0358),
      replacing the single-hop check in the ADR 0118 / LISS-0149 gate.
      Both tests pass.
- [x] Phase 3 Refactor: this design decision section updated in place
      with the Hard Stop finding and the resulting scope narrowing,
      rather than left describing only the originally-planned full fix;
      reviewer empathy summary below.
- [x] Full regression: `pytest tests/ -q` → 1318 passed, 0 failed
      (unchanged — `main` stays fully green; +2 this Issue's own new
      tests); `python3 tests/spec_verification/run_all.py` → 161/161
      (100%, Gate: PASS, unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: 2回目のアーキテクチャ監査で発見した
`parser.py`の`Float[M…] row = h[i]`ゲートの狭さ（裸の変数名のみを
`IDENT[`として認識し、`m.h[1]`のようなstruct/classフィールド経由の
配列を認識しない）を、LISS-0358で確立した`_dotted_call_lookahead`と
同じパターンで一般化した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 当初はパーサー修正だけで`m.h[1]`が完全にコンパイル・実行できる
  ようになると想定していたが、修正適用後に`typecheck.py`側の
  `_check_float_partial_bind`が、配列形状追跡を「トップレベルの
  ローカル変数のみ」に限定した独立した別のギャップであることを
  発見した——これはADR 0174の単位追跡のように「既存の仕組みを
  呼び出し忘れていた」のではなく、struct/classフィールドの配列形状
  追跡という**未実装の新機能**が必要になるケースだった。作業を
  中断してAdjudicatorに報告し、元々承認されていたスコープ
  （パーサー修正のみ）を維持する方針を確認した上で、テストの
  アサーションを「完全コンパイル成功」から「PARSE_ERRORが消え、
  正確なTYPE_MISMATCHに置き換わること」へ訂正した。
- スコープ変更後のRedを、`git stash`で`parser.py`の変更のみを
  一時的に外し、更新後のアサーションが未修正コードに対して正しく
  失敗することを再確認してから、Greenへ進んだ。

**人間がコードレビューで重点的に見るべきポイント**:
- struct/classフィールド配列形状追跡（`field_shapes`スタイルの
  新機構）を将来実装する際、この記録（未実装であることの明示的な
  記録）が出発点として十分か。

## Non-goals

- Other audit candidates (tracked separately or unverified).
- `_op_expression()`'s own grammar (already general).
- Struct/class field-array shape tracking (a separate, larger future
  Issue — see the Hard Stop above).
