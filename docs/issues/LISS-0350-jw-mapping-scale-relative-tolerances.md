# LISS-0350: fix Jordan-Wigner mapping's absolute zero/Hermitian tolerances (fixes A03_h2_vqe's silently-zeroed Hamiltonian)

## Metadata

- Local issue ID: LISS-0350
- Status/phase: **complete** (2026-08-07) — PR
  [#416](https://github.com/nn0cl/staqex/pull/416) merged, commit
  `add8447`
- Type: Kernel bug fix (`compiler/staqex/second_quantization.py`); no
  example content changed (`examples/applied/A03_h2_vqe/main_h2_vqe.sqx`
  itself is unchanged — the bug is entirely in the Kernel's JW-mapping
  pipeline, not in the example source)
- Priority: P1 (silently produces physically wrong output for A03's
  own literature-cross-validated claim)
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: standalone Kernel fix, root-caused while investigating the
  deferred `op_n_qubits` Jordan-Wigner qubit-undercount bug (flagged
  during WP-0095 work unit LISS-0336, never independently filed)
- Parent: none (not itself part of WP-0095 — WP-0095 is complete;
  this is a standalone Kernel correctness fix discovered afterward)
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0350-jw-mapping-scale-relative-tolerances`
- GitHub Issue / PR: [#416](https://github.com/nn0cl/staqex/pull/416)
  (merged, `add8447`)

## Design decision

### What was asked vs. what was found

Investigating `hamiltonian.py::op_n_qubits`'s deferred Jordan-Wigner
qubit-undercount (LISS-0336: "op_n_qubits undercounts the qubit
register for Operators containing a Jordan-Wigner-mapped runtime
value") found the undercount is a **symptom**, not the root cause.
Live trace on `examples/applied/A03_h2_vqe/main_h2_vqe.sqx` (the only
`.sqx` example using Jordan-Wigner mapping) showed
`self.operators["H_electronic"]` — the JW-mapped `QubitOperator` —
resolves to a bare `OpLit(0.0)`: **the entire 2-orbital H2 electronic
Hamiltonian collapses to zero**, not merely one dropped qubit site.

### Root cause

`second_quantization.py::jordan_wigner_map` filters grouped Pauli-term
coefficients with two **fixed absolute** thresholds:

```python
_REAL_TOL = 1e-9
_ZERO_TOL = 1e-12
...
if abs(coeff) < _ZERO_TOL:
    continue
if abs(coeff.imag) > _REAL_TOL:
    raise SecondQuantizationMappingError(...)
```

This is the same systemic bug category already found and fixed 3 times
this session in different files (`sparse_pauli.py::_coalesce` /
LISS-0336, `backend/qasm/trotter.py`'s Suzuki-angle filter / LISS-0341,
and `typecheck.py`'s payload-collapse bugs are a related-but-distinct
category) — a numeric-noise-floor epsilon calibrated for the old
natural-units convention (coefficients O(1)) silently breaks under
ADR 0195's real SI-unit coefficients. Traced live: A03's grouped JW
coefficients are all **~1e-18 to 1e-19** (real Joule-scale, per ADR
0195's `Ha to J` conversion) — six orders of magnitude below
`_ZERO_TOL`, so every term in `H_electronic` was dropped as
"numerically zero," and `result` fell through to the function's own
`if result is None: result = OpLit(value=0.0, ...)` fallback.

Effect: `H = H_electronic + nuclear_repulsion * I` reduces to a pure
global-phase operator (`nuclear_repulsion * I` alone). **A03's `evolve`
has produced no real H2 electronic-structure dynamics since its
real-unit migration (LISS-0332)** — its existing test only asserts
"compiles, runs, non-vacuum measurement" (the loose pattern used
throughout WP-0095), which a global-phase evolution of the initial
`|+>⊗|0>` superposition still satisfies, so the bug was never caught.

`_REAL_TOL = 1e-9` (the non-Hermitian-residual check, same function)
is the same bug's mirror-image, unconfirmed-but-latent form: at
Joule-scale coefficients, an imaginary residual up to `1e-9` — nine
orders of magnitude *larger* than the coefficients themselves — would
still silently pass as "real" (Hermitian), meaning this guard would
not currently catch a genuinely broken (non-Hermitian) JW-mapped
result at real-unit scale. Not observed causing wrong output yet
(no example currently produces such a residual), but the same
mechanism, fixed together per Adjudicator direction.

### Blast-radius audit (before deciding the fix)

Confirmed via a full sweep of every absolute numeric threshold in
`compiler/staqex/`:

- **Same bug category, in scope for this fix**: `second_quantization.py`'s
  `_ZERO_TOL`/`_REAL_TOL` only (this Issue).
- **Already fixed this session**: `sparse_pauli.py::_coalesce` (scale-
  relative since LISS-0336), `backend/qasm/trotter.py`'s Suzuki-angle
  filter (unit-independent post-ℏ-division check since LISS-0341).
- **Confirmed unrelated** (operate on dimensionless, normalized
  quantities — Born-rule probability, quantum-amplitude, or an
  already-ℏ-divided dimensionless matrix exponent — never exposed to
  raw physical coefficients): `mixed_state.py` (density-matrix trace),
  `quantum_ops.py` (`⟨Z⊗Z⟩` probability weights), `matrix.py`'s
  `expm_ih` Taylor-series convergence check (confirmed: its input
  matrix is already divided by `HBAR_SI` before this check runs, so
  the check operates on a properly-normalized dimensionless exponent,
  standard scaling-and-squaring practice) and grid-spacing check,
  `numeric_policy.py`/`uncompute.py` (Born-rule residual mass, bounded
  `[0,1]`), `joint.py` (amplitude/probability pruning),
  `evaluator.py`'s classical polynomial pipe-fusion (Float function
  composition, not currently exercised with Energy-typed values by any
  shipped example) and state-overlap check (bounded `[-1,1]` inner
  product).
- **Blast radius of the fix itself**: only
  `examples/applied/A03_h2_vqe/main_h2_vqe.sqx` uses Jordan-Wigner
  mapping among shipped `.sqx` examples; no `spec_verification` suite
  fixture does. The three existing JW-related test files
  (`test_jordan_wigner_mapping_red.py`,
  `test_second_quantized_operators_red.py`,
  `test_liss_0331_second_quantized_leading_coefficient_red.py`) all use
  small illustrative `Float` coefficients (e.g. `1.0`), well above
  either threshold — confirmed unaffected by the fix.

### Adopted fix

Mirror `sparse_pauli.py::_coalesce`'s already-shipped, already-proven
scale-relative pattern (LISS-0336) for **both** thresholds: derive
`scale = max(abs(c) for c in grouped.values())` once, then use
`scale * _ZERO_TOL` / `scale * _REAL_TOL` in place of the fixed
constants, so the same relative fractions (`1e-12`, `1e-9`) now apply
*relative to the largest coefficient present*, not to an absolute,
unit-convention-specific floor.

## Intent

1. `second_quantization.py::jordan_wigner_map`: compute `scale =
   max((abs(c) for c in grouped.values()), default=0.0)` once, before
   the filtering loop.
2. Replace `if abs(coeff) < _ZERO_TOL` with `if abs(coeff) <= scale *
   _ZERO_TOL`.
3. Replace `if abs(coeff.imag) > _REAL_TOL` with `if abs(coeff.imag) >
   scale * _REAL_TOL`.
4. Update `_ZERO_TOL`/`_REAL_TOL`'s doc comment to state they are now
   relative fractions, not absolute thresholds.

## Explicitly out of scope

- `examples/applied/A03_h2_vqe/main_h2_vqe.sqx` itself — unchanged;
  the bug and fix are entirely in the Kernel's JW-mapping pipeline.
- `hamiltonian.py::op_n_qubits` itself — unchanged; confirmed it
  already correctly counts sites once `H_electronic` is a real
  (non-degenerate) Pauli-sum `OpExpr`, so no separate fix is needed
  there once the root cause is addressed.
- The `evaluator.py` classical polynomial pipe-fusion epsilons —
  audited and confirmed not currently exposed to Energy-typed values
  by any shipped example; flagged for a future Issue only if a later
  example chains Energy-valued function pipes.
- Any other absolute-threshold location audited and confirmed
  unrelated (see the blast-radius audit above).

## Acceptance reference

```gherkin
Feature: Jordan-Wigner mapping preserves real-unit-scale coefficients

  Scenario: A03_h2_vqe's electronic Hamiltonian is not silently zeroed
    Given the unmodified main_h2_vqe.sqx (real Joule-scale coefficients, ~1e-18)
    When it is compiled and run with a fixed seed
    Then the resolved H_electronic Operator is a real, non-degenerate Pauli sum
    And it is not collapsed to a bare zero literal
    And hamiltonian.py::op_n_qubits correctly reports 2 qubits for the combined H
```

## Verification plan for this design intake (not shipped as a test)

Confirmed live: before the fix, `self.operators["H_electronic"]`
resolves to `OpLit(0.0)` and `op_n_qubits(H, ...)` returns `1`. After
the fix, `H_electronic` is a real 6-term Pauli sum (`I`, `Z0`, `Z1`,
`Y0Y1`, `X0X1`, `Z0Z1`) with coefficients at the expected `~1e-18` to
`1e-19` Joule scale, and `op_n_qubits(H, ...)` correctly returns `2`.
Full `pytest tests/ -q` sweep confirmed no new failures at the exact
post-WP-0095 baseline (52 failed, 1225 passed);
`spec_verification` unchanged (161/161).

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-06/07
- Size: `S` — a two-line fix (scale-relative thresholds mirroring an
  already-shipped pattern) plus a systematic blast-radius audit across
  the whole runtime module, both already completed and verified before
  this Issue was drafted.
- Route: direct implementation by this session.
- Confidence: high — the fix mirrors an already-proven pattern; live
  repro and fix confirmed before drafting; blast radius confirmed
  narrow (one example, no SV suite, no other test exposure).

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0350_jw_mapping_scale_relative_tolerances_red.py`
      added (2 cases). Confirmed both failing with the fix temporarily
      reverted: `test_h2_electronic_hamiltonian_is_not_silently_zeroed`
      → `H_electronic` resolved to a bare `OpLit(0.0)`;
      `test_op_n_qubits_reports_two_qubits_for_the_combined_hamiltonian`
      → `op_n_qubits` reported `1` instead of `2`.
- [x] Phase 2 Green: `second_quantization.py`'s `jordan_wigner_map`
      fixed (scale-relative `_ZERO_TOL`/`_REAL_TOL`, mirroring
      `sparse_pauli.py::_coalesce`'s already-shipped pattern). Both
      tests pass.
- [x] Phase 3 Refactor: no further change needed; reviewer empathy
      summary below.
- [x] Full regression: `pytest tests/ -q` → 1227 passed, 52 failed
      (unchanged failure count vs. the post-WP-0095 baseline, no new
      failures — +2 is this Issue's own new tests); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: 当初依頼された「`op_n_qubits`の
Jordan-Wigner qubitカウント不足バグ」を調査した結果、これが症状に
過ぎず、真の原因は`second_quantization.py::jordan_wigner_map`の
絶対しきい値（`_ZERO_TOL=1e-12`、`_REAL_TOL=1e-9`）が実Joule単位
スケール（~1e-18〜1e-19）の係数を全て「数値的にゼロ」として
除外してしまい、A03_h2_vqeの電子Hamiltonian全体が単一のゼロ
リテラルに潰れていたことにあると判明した。これにより、A03の
`evolve`は実単位移行（LISS-0332）以降、H2分子の電子構造由来の
物理を一切反映せず、単なるグローバル位相演算子（核反発項のみ）を
適用していたに過ぎなかった。`sparse_pauli.py::_coalesce`
（LISS-0336）で既に確立・検証済みのスケール相対パターンを、同じ
関数内の隣接する`_REAL_TOL`（非エルミート残差チェック、未発症だが
同じ機制の潜在リスク）と合わせて適用した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 修正前に、Kernel全体の絶対数値しきい値を体系的に監査し
  （`mixed_state.py`、`quantum_ops.py`、`matrix.py`、
  `numeric_policy.py`/`uncompute.py`、`joint.py`、
  `evaluator.py`の各箇所）、どれが「無次元・正規化された量
  （確率・振幅・ℏ除算済み無次元行列指数）」を扱っていて対象外か、
  どれが「生の物理係数」を扱っていて同じバグの危険があるか
  を1つずつ確認した。特に`matrix.py`の`expm_ih`のTaylor級数
  収束チェックは、入力行列が既に`HBAR_SI`で除算済み（無次元化済み）
  であることをコードを直接読んで確認し、対象外と判断した。
- A03の既存テスト（LISS-0332）が「コンパイル・実行・非真空測定」
  のみをチェックする緩いパターンだったため、このバグを一度も
  検出できていなかったことを、テスト内容の直接確認で検証した
  （初期状態`|+>⊗|0>`自体が既に重ね合わせなので、グローバル位相
  のみの発展でも非真空の測定結果が得られてしまうため）。

**人間がコードレビューで重点的に見るべきポイント**:
- `docs/research/2026-08-05-h2-two-orbital-jordan-wigner-cross-validation.md`
  （A03の物理由来を記した文献照合ドキュメント）が、今回修正後の
  実際の測定結果とどう整合するか、改めて確認が必要（本Issueの
  スコープ外だが、A03自体の物理的妥当性の再検証が望ましい）。
- `_REAL_TOL`側は今回「未発症の潜在リスク」として一緒に修正した
  ものであり、実際に非エルミート残差を検出するテストケースは
  追加していない（現状どの既存exampleもこの経路を踏まないため）。

## Non-goals

- `main_h2_vqe.sqx` example content changes.
- `op_n_qubits` changes.
- `evaluator.py`'s classical polynomial pipe-fusion epsilons.
