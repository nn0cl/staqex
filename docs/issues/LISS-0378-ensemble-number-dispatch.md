# LISS-0378: Ensemble/RawMatrix numeric weights reject BinOp and named scalars

## Metadata

- Local issue ID: LISS-0378
- Status/phase: **complete** (2026-08-08) — PR
  [#475](https://github.com/nn0cl/staqex/pull/475) merged, commit
  `b9f03d5`
- Type: Kernel bug fix (`compiler/staqex/mixed_state.py`,
  `compiler/staqex/runtime/mixed_state.py`, evaluator scalar threading)
- Priority: P3
- Initial planning size: `S`
- Owner / agent: Cursor (sixth architectural audit, candidate 2)
- Branch: `feature/liss-0378-ensemble-number-dispatch`
- GitHub Issue / PR: [#475](https://github.com/nn0cl/staqex/pull/475)
  (merged, `b9f03d5`)

## Design decision

Live-verified: literal `1.0` weight OK; `1.0 * 1.0` and named `Float w`
raised `MALFORMED_DENSITY_STATE`. Root cause: `_number` was Lit-only.

**Fix**: fold `BinOp` `+ - * /`; resolve `Var` against collected
`Float`/`Int` binds; thread scalars into runtime `density_from_call`.

## Exit criteria

- [x] Red: 2 failures for BinOp/named; 1 regression OK
- [x] Green: static + runtime `_number` widened; 3 passed
- [x] Regression: **1341 passed**; SV **161/161**

### 変更の要約 (PR Summary)

**何を目的として何を変更したか**: Ensemble/RawMatrix の数値葉がリテラル
以外を誤拒否していたのを、BinOp 畳み込みと名前付き Float/Int 解決で
修正した（第6回監査候補2、LISS-0371 同類）。

### 残存リスク・検証の溝

- Attr / Call 形の数値は未対応（スコープ外）。
- 実行時は `self.scalars` に載った名前のみ（Float バインド経路依存）。
