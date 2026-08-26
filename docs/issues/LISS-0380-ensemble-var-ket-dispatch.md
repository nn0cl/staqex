# LISS-0380: Ensemble accepts Var states statically but runtime requires KetLit

## Metadata

- Local issue ID: LISS-0380
- Status/phase: **complete** (2026-08-08) — PR
  [#477](https://github.com/nn0cl/staqex/pull/477) merged, commit
  `deab864`
- Type: Kernel bug fix (`compiler/staqex/runtime/mixed_state.py`,
  `compiler/staqex/runtime/evaluator.py`)
- Priority: P3
- Initial planning size: `S`
- Owner / agent: Cursor (sixth audit candidate 4 — final)
- Branch: `feature/liss-0380-ensemble-var-ket-dispatch`
- GitHub Issue / PR: [#477](https://github.com/nn0cl/staqex/pull/477)
  (merged, `deab864`)

## Design decision

Static allowed Ensemble Var states; runtime only KetLit. Fix: track
`ket_labels` for `State`/`state` binds to `|0>`/`|1>` and resolve Vars
in `_matrix_from_ensemble`.

## Exit criteria

- [x] Red/Green; **1345 passed**; SV **161/161**

### 変更の要約 (PR Summary)

**何を目的として何を変更したか**: Ensemble の静的契約が許す名前付き
ket を実行時も解決し、第6回監査候補リストを閉じた。
