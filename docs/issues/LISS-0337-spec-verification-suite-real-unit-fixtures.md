# LISS-0337: migrate 5 stale spec_verification suite fixtures to real units (CI green-up)

## Metadata

- Local issue ID: LISS-0337
- Status/phase: **complete** (2026-08-05) — bundled into and merged with
  PR [#390](https://github.com/nn0cl/staqex/pull/390), commit `339ae99`,
  per Adjudicator direction (no separate branch/PR — landed together
  with the LISS-0336 post-merge-sync docs)
- Type: Feature Path (test fixture content only — 5 files under
  `tests/spec_verification/suites/`; no Kernel/grammar change)
- Priority: P1 (CI hygiene)
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: adjacent to WP-0095 (same ADR 0195 root cause) but not itself
  an example-migration work unit — these are Kernel spec_verification
  suite fixtures, not `.sqx` catalog examples
- Parent: [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
- Depends on: [LISS-0330](LISS-0330-real-hbar-kernel-primitive.md),
  [LISS-0336](LISS-0336-evolve-real-unit-canonicalization-bugs.md)
- Blocks: none
- Branch: `docs/liss-0336-post-merge-sync` (bundled into the open
  LISS-0336 post-merge-sync PR at the Adjudicator's explicit direction,
  since it was discovered while investigating that PR's CI failure)
- GitHub Issue / PR: [#390](https://github.com/nn0cl/staqex/pull/390)
  (merged, `339ae99`)

## Intent

`python3 tests/spec_verification/run_all.py`'s tracked "136/145" rate
(stable since LISS-0334) has never been broken down in
`open-work-register.md` beyond the aggregate number. Investigating PR
#390's CI failure found the 9 failing cases split into two categories:

1. 4 already-tracked WP-0095 unmigrated `.sqx` examples (`B04`, `B07`,
   `B08`, `A11` — expected, unchanged by this Issue).
2. **5 spec_verification suites whose own internal test fixtures were
   never updated for ADR 0195** and now crash outright (an uncaught
   `KernelDiagnosticError`/`ValueError`, not a graceful per-case `FAIL`,
   since these predate LISS-0330's fail-closed check and the suites'
   own `try/except AssertionFailure` blocks don't catch those exception
   types): `sv17_quantum_mechanics_syntax`, `sv19_arbitrary_hamiltonian`,
   `sv27_fock_quadrature`, `sv28_sparse_pauli`, `sv29_position_grid_ho`.

This Issue migrates category 2 only. Each suite's `evolve ... for
<bare-literal>` calls are given real, Time-typed durations; suites whose
Hamiltonian coefficients also flow through the ℏ-dividing sparse/dense
`expm` paths (`sv19`'s Ising unitarity check, `sv28`'s all three cases)
additionally get real `Energy`-typed coefficients so `|H*t/hbar|` stays
in a numerically safe range. Suites/cases that only exercise the
Fock/grid path with a Hamiltonian at its own eigenstate (`sv19`'s
`N+0.5`/`dirac(0)` case, `sv27`'s `P²+Q²`/`dirac(0)` case, `sv29`'s
symmetric wavepacket) are structurally invariant to the exact duration
chosen, so only their duration needs a Time-typed wrapper.

## Per-suite plan

- **sv17**: the `evolve psi0 under X for π/2` case uses the "legacy
  bare single-Pauli-letter" evolve form (`pauli_u`), which is **not**
  ℏ-divided (confirmed by reading `quantum_ops.py::pauli_u` — it treats
  `t` as a raw rotation angle, unchanged by ADR 0195). Fix: declare
  `Time dur = 1.5707963267948966.s` (canonical seconds, scale 1.0, so
  the raw π/2 value passes through unchanged) with a comment explaining
  this legacy path's angle-not-time semantics.
- **sv19**: `N+0.5`/`dirac(0)` Fock case and `H=Z`/`|0>` eigenstate case
  — wrap durations in `Time`-typed fs-scale variables (structurally
  invariant). Ising unitarity case (`J`, `h` coefficients) — give `J`/`h`
  real `Energy` (eV-scale) types and the duration a real `Time` (fs-scale)
  type. Direct `expm_ih(h, 0.37)` Python call — bypasses `.sqx` entirely;
  pass real SI-scale `t` directly in the Python float (fs-scale seconds)
  since the compiled `h` matrix already carries whatever coefficient
  magnitude `compile_hamiltonian` was given (unit ±1 Pauli products here,
  so `t` alone needs correcting to a small real-seconds value).
- **sv27**: `dirac(0)`/eigenstate case — Time-typed duration wrapper
  only.
- **sv28**: "sparse ≡ dense H" and "4-qubit evolve preserves norm" cases
  — give `J`/`h` real `Energy` types, duration a real `Time` type.
  "Taylor e^{-iHt}|ψ⟩ ≡ dense U|ψ⟩" — direct Python `expm_ih`/
  `expm_ih_apply` calls; replace the raw `t = 1.1` with a real
  fs-scale seconds value passed to both functions identically (the
  sparse≡dense equivalence assertion is scale-invariant as long as both
  calls use the same real `t`).
- **sv29**: symmetric Gaussian wavepacket case — Time-typed duration
  wrapper only (⟨x⟩≈0 by symmetry, invariant to the exact real duration).

## Explicitly out of scope

- Any change to the 4 already-tracked WP-0095 `.sqx` examples (B04/B07/
  B08/A11) — those remain scheduled as their own future WP-0095 work
  units.
- Any Kernel/grammar change — this Issue only touches test fixture
  content.
- A broader audit of every other spec_verification suite beyond these 5
  confirmed-crashing ones.

## Verification plan

Each of the 5 suites re-run individually (`python3 -m
tests.spec_verification.suites.svNN_...` or via `run_all.py`) to confirm
no suite-level crash and that each sub-case's original assertion still
holds under real-unit values. Full `pytest tests/ -q` and
`spec_verification/run_all.py` re-run to confirm the aggregate rate
improves from 136/145 to 141/145 (only the 4 already-tracked WP-0095
examples remaining) with no new failures elsewhere.

## Reviewer empathy summary

**何を目的として何を変更したか**: PR #390のCI失敗を調査した結果、
`spec_verification`の136/145という長期安定していた数字の内訳が、
WP-0095で追跡済みの未移行例4件と、一度もADR 0195向けに更新されていない
spec_verificationスイート自身のフィクスチャ5件に分かれていることが
判明した。後者5件（sv17/19/27/28/29、および共有フィクスチャ4ファイル）
を実物理単位へ移行し、CIをできる限り緑に近づけた。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 各テストケースの「意図された物理」を壊さないよう、(a)固有値不変性
  など構造的性質のみを検証するケースは実時間・実エネルギーへの変換で
  十分、(b)`sv17`の裸Pauli文字evolve（`pauli_u`）はADR 0195のℏ除算を
  受けないレガシー経路だと判明したため、`.s`サフィックスで元のπ/2の
  値をそのまま通す、(c)`sv19`/`sv28`のPythonレベル直接`expm_ih`呼び出し
  はhbarスケールの`t`を選んで数値破綻を回避、という3種類の対応方針を
  ケースごとに使い分けた。
- 検証中に3つの無関係な既存バグを発見した:
  `grid_oscillator.sqx`の`measure`対象ミス、`quantum_ising_4.sqx`の
  既存LINEAR問題（今回は無害と確認し未修正）、そして
  `lower.py`のQASM Trotterバックエンドが`Energy`/`Time`型のローカル変数
  を一度も認識していなかったという、より重大な既存ギャップ
  （`test_trotter_rejects_fock_hamiltonian`の回帰として発覚）。
  最後のものは実際にpytestの新規回帰を引き起こしたため、スコープを
  最小限に絞って修正した。

**人間がコードレビューで重点的に見るべきポイント**:
- `lower.py`の新しい`Attr`/`UnitConvert`認識ロジックが、他のQASM
  lowering経路（`second_quantized_env`等）と整合しているか。
- `quantum_ising_4.sqx`の既存LINEAR問題を今回あえて修正しなかった
  判断が妥当か（この場では「無害と確認済み・別スコープ」とした）。

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-05
- Size: `S` — five test fixture files, mechanical `Time`/`Energy`-typing
  changes plus, for two direct-Python-call cases, adjusted literal
  values; no Kernel/grammar changes.
- Route: direct implementation by this session, bundled into the open
  PR #390 at the Adjudicator's explicit direction.
- Confidence: high (root cause and per-case fix pattern directly
  confirmed by reading each suite's source and the relevant Kernel code
  paths).

## Exit criteria

- [x] All 5 suites re-run individually without a suite-level crash.
- [x] `python3 tests/spec_verification/run_all.py` reports **156/161**
      (96.89%) — higher than the originally estimated 141/145, because
      each formerly-crashing suite now reports its *full* set of
      individual cases (16 more total cases became visible/gradeable)
      instead of a single "suite-crash" placeholder. Only 5 failures
      remain, all attributable to the 4 already-tracked WP-0095
      unmigrated examples (`B04`/`B07`/`B08`/`A11`; `B08` is referenced
      twice, once directly and once via `sv19-example-files`).
- [x] `pytest tests/ -q` shows no new failures vs. the LISS-0336 baseline
      (60 failed / 1205 passed, unchanged) — after fixing one transient
      regression found and corrected during this Issue (see "Drive-by
      fixes" below).
- [x] `git diff --check` clean.

## Drive-by fixes (found during this Issue, small and directly blocking)

Three small, unrelated-to-ADR-0195 pre-existing issues were found while
verifying this Issue's own changes, each fixed inline since each was
either trivial or directly blocked confirming this Issue's own fix:

1. **`tests/fixtures/staqex/grid_oscillator.sqx`**: `measure psi` reused
   `psi`'s already-consumed linear resource (`inspect(psi)` on the
   preceding line moves it into `viewed`) — a pre-existing
   `LINEAR_DUPLICATE_USE` bug, confirmed present before this Issue's
   changes too (via `git stash`). One-line fix: `measure viewed`.
2. **`tests/fixtures/staqex/quantum_ising_4.sqx`**: has its own
   pre-existing, unrelated `LINEAR_DUPLICATE_USE`/`LINEAR_IMPLICIT_DISCARD`
   diagnostics (confirmed present before this Issue's changes too, via
   `git stash`) that make `compile_path(...).ok == False`. **Not fixed**
   — out of scope (a different bug class) — but confirmed harmless to
   this Issue's own goal, since `tests/spec_verification/suites/sv28_sparse_pauli.py`'s
   own `_eval` helper doesn't treat those specific diagnostic codes as
   hard failures, so `sv28-example` still passes despite them.
3. **`compiler/staqex/backend/qasm/lower.py`**: the QASM3 Trotter
   backend's local `scalars` dict (used by `eval_time_expr` to resolve
   `evolve ... for <Var>`) only ever recognized `Float`/`Int`-typed
   locals, never the newer Type-First `Energy`/`Time` dimensioned types
   — a real, previously-latent gap (nothing had exercised a
   `Time`-typed evolve duration through this specific QASM lowering path
   before ADR 0195 made `Time`-typed durations the *only* valid form).
   Surfaced as a genuine pytest regression
   (`test_qasm3_codegen.py::test_trotter_rejects_fock_hamiltonian`,
   caught before this PR was pushed) once `quantum_oscillator.sqx`'s
   duration became `Time`-typed. Fixed with a small, targeted addition:
   `lower.py` now also recognizes `Attr`/`UnitConvert`-shaped
   single-binding declarations and canonicalizes them via
   `dimensions.to_canonical_magnitude`, mirroring how the runtime
   evaluator already treats these forms (LISS-0336's own fix). Confirmed
   the blast radius was exactly one test (grepped for all fixture
   references across `tests/*.py`) before fixing.
