# LISS-0372: `apply(rx(theta), q)` with a named-variable angle silently drops the gate

## Metadata

- Local issue ID: LISS-0372
- Status/phase: **complete** (2026-08-08) — PR
  [#463](https://github.com/nn0cl/staqex/pull/463) merged, commit
  `fe73ced`
- Type: Kernel bug fix (`compiler/staqex/backend/qasm/lower.py`); no
  example content
- Priority: P2 (confirmed silent wrong-circuit output — `compiled.ok`
  and `emitted.ok` both report success while a gate is missing from the
  emitted QASM; distinct from LISS-0371, which was mis-verified as
  silent and turned out to be a hard rejection)
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: standalone Kernel fix, second candidate from the third
  architectural audit round (LISS-0371 covered the first)
- Parent: none
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0372-rx-angle-silent-gate-drop`
- GitHub Issue / PR: [#463](https://github.com/nn0cl/staqex/pull/463)
  (merged, `fe73ced`)

## Design decision

Live-verified (checking `compiled.ok` and `emitted.ok` *before*
inspecting the emitted QASM, applying the lesson from LISS-0371's
verification-methodology self-correction):

```
Float theta = 1.57
state q = apply(rx(theta), q)
```

compiles (`compiled.ok = True` — typecheck has no angle-resolvability
check at all) and emits (`emitted.ok = True`) — but the `rx` gate is
**completely absent** from the emitted QASM text. The only trace is a
soft note (`'apply(rx(…)) angle not a closed literal/pi'`) that
nothing asserts on by default. The literal form
(`apply(rx(1.57), q)`) emits the gate correctly. This is a genuine
silent-wrong-circuit bug, unlike LISS-0371 (which reported the same
"silent" framing but was actually a hard typecheck-time rejection on
re-verification) — here both `compiled.ok` and `emitted.ok` are `True`
while the physics is silently wrong.

Root cause: `lower.py::_rotation_angle` (the same narrow-AST-shape-
dispatch category as every other finding this session) only recognizes
`LitFloat`/`LitInt`/a `Var` matching a name in `PRELUDE_CONSTANTS`/a
`pi/N` `BinOp` — not a named local `Float`/`Int` classical bind. Its
caller (`_from_ast_patterns`'s `apply(...)` lowering, around line 335)
treats an unresolved angle as a **soft** case: append a note and
`continue`, leaving `reject_code` unset — so the circuit silently loses
the gate instead of being marked unresolvable.

**Adopted fix (two parts, both required)**:
1. **Widen recognition** (same principle as LISS-0371): `_rotation_angle`
   gains a `scalars: dict[str, float]` parameter and resolves a `Var`
   through it instead of through a separate `PRELUDE_CONSTANTS`-only
   lookup. `_from_ast_patterns` already builds and populates a
   `scalars` dict (seeded from `PRELUDE_CONSTANTS`, then updated with
   every local `Float`/`Int` literal bind) *before* the `apply(...)`
   lowering loop runs — the exact dict LISS-0371 established the
   `static_scalars`/`scalars` naming convention for. The `pi/N` `BinOp`
   case is widened the same way (its `arg.lhs.name in PRELUDE_CONSTANTS`
   check becomes `arg.lhs.name in scalars`, a strict superset since
   `scalars` is seeded from `PRELUDE_CONSTANTS`).
2. **Convert the remaining fallback from silent-skip to explicit
   rejection** (Adjudicator direction, since a dropped gate is a more
   severe failure mode than LISS-0371's fallback-to-a-different-but-
   still-valid-order-2): when the angle is still unresolvable after
   widening, set `reject_code = "QASM_ROTATION_ANGLE_UNRESOLVED"` (a
   new module-level constant, mirroring the existing
   `QASM_TROTTER_STEPS_REQUIRED`/`QASM_FUNCTION_CALL_UNSUPPORTED`
   naming convention already in this file) instead of only appending a
   note and silently continuing. `reject_code` already flows through
   this function's existing plain-variable-assignment pattern (mirrors
   the already-correct `STATIC_HILBERT_RESOURCE_ERROR` sibling case a
   few dozen lines earlier in the same loop) to the final `Circuit(...)`
   return, and `emitter.py` already turns any non-empty `reject_code`
   into `EmitResult(qasm="", ok=False, ...)` — no new plumbing needed
   beyond setting the one field.

## Explicitly out of scope

- `ry`/`rz` share `_rotation_angle` and get the same fix "for free" —
  not separately re-verified per-gate-kind, since the function is
  identical for all three (`gate_nm in {"rx", "ry", "rz"}` at the call
  site already treats them uniformly).
- Arithmetic expressions (`theta * 2`) in the angle position — out of
  scope, same minimal-fix rationale as LISS-0371's
  `_static_scalar_value` (the acceptance scenario only requires a named
  scalar bind, matching the live-verified finding).
- Any further audit candidates — round three's list is now exhausted
  (LISS-0371 + LISS-0372 were the two confirmed real findings; no
  further candidates from that round remain to investigate).

## Acceptance reference

```gherkin
Feature: apply(rx(theta), q) resolves a named classical scalar angle, not just a literal

  Scenario: a named Float constant angle is honored, not silently dropped
    Given `Float theta = 1.57; state q = apply(rx(theta), q)`
    When compiled and QASM-emitted
    Then the emitted QASM contains the same `rx(1.57)` gate as the
      equivalent literal `apply(rx(1.57), q)` form

  Scenario: a genuinely unresolvable angle is now explicitly rejected, not silently dropped
    Given an angle expression referencing an unbound name
    When QASM-emitted
    Then `emitted.ok` is `False` with `QASM_ROTATION_ANGLE_UNRESOLVED`
      (regression guard against reverting to the silent-drop fallback)
```

## Verification plan for this design intake (not shipped as a test)

The silent-drop finding confirmed live before drafting this Issue by
checking `compiled.ok`/`emitted.ok` first (applying the LISS-0371
lesson), then inspecting the emitted QASM text directly for gate
presence/absence. Full `pytest tests/ -q` sweep after the fix, diffed
against the current baseline (0 failed, 1324 passed — `main` is fully
green), confirming no regression. `spec_verification` expected
unchanged (161/161).

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `S` — one function signature widened (mirrors an
  already-correct sibling `scalars` dict already built in the same
  function) plus one fallback-severity change at a single call site
  (mirrors an already-correct sibling `reject_code` pattern a few dozen
  lines away in the same function).
- Route: direct implementation by this session.
- Confidence: high — both the finding and the fix's two source patterns
  (the `scalars` dict, the `reject_code` plain-assignment convention)
  were directly confirmed by reading the surrounding code before
  planning the change.

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0372_rx_angle_silent_gate_drop_red.py`
      added (2 cases). Confirmed both failing for the documented reason
      before the fix: the named-variable-angle case emitted QASM with
      no `rx(...)` gate at all (`emitted.ok == True`, silent drop); the
      unresolvable-angle regression guard found `emitted.ok == True`
      with `reject_code is None` (the pre-fix silent-continue fallback).
- [x] Phase 2 Green: `_rotation_angle` gained a `scalars` parameter and
      now resolves a named `Var` (and the `Var` half of a `pi/N`
      `BinOp`) through the same `scalars` dict `_from_ast_patterns`
      already builds and populates before the `apply(...)` lowering
      loop runs (the exact dict LISS-0371 established the naming
      convention for) instead of a separate `PRELUDE_CONSTANTS`-only
      lookup. The call site's fallback for a still-unresolved angle now
      sets `reject_code = QASM_ROTATION_ANGLE_UNRESOLVED` (mirroring
      the already-correct `STATIC_HILBERT_RESOURCE_ERROR` sibling
      pattern a few dozen lines earlier in the same function) instead
      of only appending a note and silently continuing. Both tests
      pass; no other call site of `_rotation_angle` exists.
- [x] Phase 3 Refactor: design decision section already recorded the
      full rationale at Plan time (no new findings surfaced during
      Green); reviewer empathy summary below.
- [x] Full regression: `pytest tests/ -q` → **1326 passed, 0 failed**
      (+2 this Issue's own new tests) — `main` stays fully green;
      `python3 tests/spec_verification/run_all.py` → **161/161** (100%,
      Gate: PASS, unchanged); `git diff --check` → clean.

### 変更の要約 (PR Summary)

**何を目的として何を変更したか**: 第3回アーキテクチャ監査の第2候補
`apply(rx(theta), q)`(名前付き`Float`変数の角度)がゲートを
サイレントに欠落させる問題を修正した。LISS-0371の教訓
(`compiled.ok`を先に確認する検証手順)を適用して再検証した結果、
今回は`compiled.ok`・`emitted.ok`共に`True`のままゲートが消失する、
本当にサイレントなバグであることを確認した。修正は2段階:
(1) `_rotation_angle`が`_from_ast_patterns`内に既に構築済みの
`scalars`辞書(LISS-0371が命名規則を確立したものと同じパターン)
経由で名前付き変数を解決できるよう認識範囲を拡張、
(2) 解決不能な場合のフォールバックを、単なるnote追加+silent
continueから、既存の`reject_code`機構(同一関数内の
`STATIC_HILBERT_RESOURCE_ERROR`という既に正しい兄弟パターンを
そのまま踏襲)を使った明示的拒否に変更した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- フォールバック動作を「サイレントスキップ」から「明示的拒否」に
  変更するという判断は、LISS-0371(既存フォールバック動作は不変の
  まま認識範囲のみ拡張)とは異なる、より大きなセマンティクス変更
  であるため、実装前にAdjudicatorに選択肢を提示して承認を得た。
- `reject_code`をプレーンな変数代入で設定するだけで
  `EmitResult.ok=False`に正しく伝播することを、`emitter.py`の
  既存コード(`if logical.reject_code: ... ok=False`)を読んで
  実装前に確認した。

**人間がコードレビューで重点的に見るべきポイント**:
- `QASM_ROTATION_ANGLE_UNRESOLVED`という新しい拒否コードが、
  既存の`QASM_TROTTER_STEPS_REQUIRED`等の命名規則と整合しているか。
- `ry`/`rz`も`_rotation_angle`を共有するため同じ修正の恩恵を
  受けるが、個別のテストケースは追加していない(関数が3ゲート種別で
  完全に同一であるため)——この判断が妥当か。

## Non-goals

- Arithmetic angle expressions (`theta * 2`).
- Any further round-three audit candidates (list exhausted).
