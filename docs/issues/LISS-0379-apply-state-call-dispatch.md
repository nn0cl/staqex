# LISS-0379: `apply(ch, State)` type check only sees bare Var

## Metadata

- Local issue ID: LISS-0379
- Status/phase: **complete** (2026-08-08) — PR
  [#476](https://github.com/nn0cl/staqex/pull/476) merged, commit
  `56357b5`
- Type: Kernel bug fix (`compiler/staqex/mixed_state.py`)
- Priority: P3
- Initial planning size: `S`
- Owner / agent: Cursor (sixth audit candidate 3)
- Branch: `feature/liss-0379-apply-state-call-dispatch`
- GitHub Issue / PR: [#476](https://github.com/nn0cl/staqex/pull/476)
  (merged, `56357b5`)

## Design decision

`apply(ch, psi)` raises `MIXED_STATE_TYPE_ERROR`; `apply(ch, id(psi))`
compiled clean. Fix: `_apply_arg_is_state` also resolves FunDecl return
type `State` for Call args.

## Exit criteria

- [x] Red/Green; Issue suite 2 passed

### 変更の要約 (PR Summary)

**何を目的として何を変更したか**: Channel `apply` の State 拒否が Var
だけを見ていたため Call 戻り値の State がすり抜けていたのを修正。
