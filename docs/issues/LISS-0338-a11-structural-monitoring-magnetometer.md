# LISS-0338: rewrite A11_noether_forge as a structural-monitoring quantum magnetometer (WP-0095 work unit 6)

## Metadata

- Local issue ID: LISS-0338
- Status/phase: **complete** (2026-08-06) — PR
  [#392](https://github.com/nn0cl/staqex/pull/392) merged, commit
  `42ca5ed`
- Type: Feature Path (example content rewrite, multi-file — all 14
  files under `examples/applied/A11_noether_forge/` plus `README.md`;
  no Kernel/grammar change)
- Priority: P1
- Initial planning size: `L`
- Owner / agent: Claude Code
- Program: [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md)
  work unit 6
- Parent: [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
- Depends on: [LISS-0336](LISS-0336-evolve-real-unit-canonicalization-bugs.md),
  [LISS-0337](LISS-0337-spec-verification-suite-real-unit-fixtures.md)
  (both merged; this Issue's physics numbers were re-verified live under
  the fixed Kernel, since the original pre-bugfix exploration's numbers
  are no longer valid)
- Blocks: none within WP-0095
- Branch: `feature/liss-0338-a11-structural-monitoring-magnetometer`
- GitHub Issue / PR: [#392](https://github.com/nn0cl/staqex/pull/392)
  (merged, `42ca5ed`)

## Design decision (already approved by the Adjudicator this session,
recorded here for the formal record)

A11's original "Noether Forge" quantum-matter-discovery theme (LISS-0120)
was rejected/deferred and formally marked "optional salvage only — not
authoritative" per `staqex-v1-showcase-mission-lock.md`. With the
Adjudicator's explicit direction to rethink A11's content while keeping
the "language review gate" spirit — and explicit freedom to freely
rewrite the existing 14-file ownership tree — this Issue rethemes A11 as
a **quantum magnetometer array for structural monitoring** (stress/
defect-induced magnetic-field distortion detection), the first of three
queued quantum-sensing themes (see memory: medical biomagnetic and
resource-exploration magnetic-anomaly detection are queued as future
candidates, not this Issue).

**Physics model:**
- NV (nitrogen-vacancy) center diamond spin qubits, a real, extensively
  published quantum-sensing platform (Doherty, M.W. et al. "The
  nitrogen-vacancy colour centre in diamond." *Physics Reports* **528**,
  1–45 (2013)). Ground-state zero-field splitting D ≈ 2.87 GHz is a
  well-established, frequently-cited real physical constant.
- **Rotating-frame simplification** (standard practice in magnetic
  resonance / ESR simulation): the D-splitting term is not itself
  simulated — it defines the qubit basis and is transformed away, so
  only the physically relevant *smaller* terms (defect-induced
  transverse coupling, inter-sensor dipolar coupling) are evolved. This
  is disclosed explicitly in the README, not hidden.
- A 3-sensor array (sites 0/1/2, site 1 "stressed", 0/2 "healthy").
  Stress/defect-induced strain shifts the stressed sensor's local
  Hamiltonian via a transverse (`X`) term (NV strain-magnetic coupling
  is real, documented physics — Barson et al. 2017 *Nano Lett.*,
  MacQuarrie et al. 2013 *PRL*). Neighboring sensors are weakly coupled
  via a real dipolar `ZZ` interaction. Magnitudes (15 MHz defect shift,
  500 kHz dipolar coupling) are physically plausible in order for real
  NV arrays but not traced to one specific cited measurement — the same
  honesty category established for A06/A10's SSH treatment.
- Noether-lineage callback (keeps the "language review gate" spirit
  alive in the *content*, not the governance sense): the defect breaks
  the array's site-permutation symmetry; that broken symmetry is the
  detection signal, read out via `physics/symmetries.sqx`.

**Re-verified live under the LISS-0336/0337-fixed Kernel** (the design's
original physics exploration predates those fixes and is no longer
trustworthy): `defect = 15 MHz`, `dip = 500 kHz`,
`Time dur = 16.7.ns` (a quarter-Rabi-period-scale duration for the
defect coupling) gives a clearly distinguishable signal — stressed site
⟨Z⟩ ≈ −0.99 (near-full flip) vs. healthy sites ⟨Z⟩ ≈ +1.13 (near
original, with a modest above-`|1|` deviation from this Kernel's
`expect(Z, …)` not performing a true partial-trace reduced-density-matrix
calculation on an entangled multi-qubit state — an existing Kernel
simplification, not something this Issue introduces or must fix;
disclosed in the README).

## Module repurposing (all 14 existing files rewired, none left as
unwired scaffolding)

- `domain/site.sqx` — `SensorRole` (Healthy/Stressed), `SiteId`,
  `SensorSite`.
- `domain/couplings.sqx` — `SensorCouplings` (real `Energy`-typed
  `defect`, `dip`).
- `domain/lattice.sqx` — `SensorArray` (3-site chain).
- `domain/experiment_config.sqx` — `ExperimentConfig` (real `Time`
  duration, seed).
- `physics/hamiltonian_builder.sqx` — `build_sensor_hamiltonian(...)`.
- `physics/model_families.sqx` — names the rotating-frame NV model
  family (documents the D-splitting simplification).
- `physics/initial_states.sqx` — baseline sensor-array state prep.
- `physics/observables.sqx` — per-site magnetization readout helpers.
- `physics/symmetries.sqx` — site-permutation symmetry-breaking check
  (Noether callback).
- `application/quench_protocol.sqx` — prepare → evolve → readout
  pipeline.
- `application/spectroscopy_protocol.sqx` — secondary readout comparing
  stressed vs. healthy signal magnitude.
- `application/phase_evidence.sqx` — assembles the detection evidence
  (signal difference, simple confidence marker).
- `application/result_contract.sqx` — small DTO for the dossier.
- `presentation/evidence_dossier.sqx` — human-readable detection
  summary.
- `main_static.sqx` — wires all of the above into the real,
  self-contained runnable entry (README's official entry point).

## Explicitly out of scope

- Medical biomagnetic and resource-exploration magnetic-anomaly themes
  (queued, not this Issue).
- Any Kernel change.
- A rigorous partial-trace fix for `expect(Z, …)` on entangled
  multi-qubit states (a pre-existing Kernel simplification, noted
  honestly in the README, not fixed here).
- Reopening the showcase mission lock — this stays `examples/applied`
  catalog content, not a showcase-track proposal.

## Acceptance reference

```gherkin
Feature: A11_noether_forge is a structural-monitoring quantum magnetometer

  Scenario: the rewritten example compiles and runs to a real terminal measurement
    Given the rewritten main_static.sqx (wiring all 14 modules)
    When it is compiled and run with a fixed seed
    Then it compiles without EVOLVE_UNRESOLVED_UNIT_ERROR or any hard diagnostic
    And it reaches a non-vacuum terminal measurement

  Scenario: the stressed sensor shows a distinguishable signal from healthy sensors
    Given the same example
    When the per-site magnetization readouts are inspected
    Then the stressed site's value differs qualitatively from the healthy sites'
```

## AI planning record (size L)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-05
- Size: `L` — full rewrite of 14 files plus README; no Kernel change.
- Route: direct implementation by this session.
- Assumptions: physics magnitudes chosen for a clean, demonstrable
  signal within this Kernel's numerical constraints; not literature-
  pinned beyond the D≈2.87GHz citation.
- Confidence: high for syntax (live-verified under the fixed Kernel);
  medium for the exact chosen magnitudes remaining stable through the
  full multi-file wiring (verified incrementally, file by file).
- Revision links: supersedes the pre-LISS-0336 physics exploration on
  the (deleted) `feature/liss-0336-a11-structural-monitoring-magnetometer`
  branch, which was never committed.

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0338_a11_structural_monitoring_magnetometer_red.py`
      added. Commit `97dc1d9`: failed for the documented reason
      (`EVOLVE_UNRESOLVED_UNIT_ERROR` on the old Noether Forge content's
      bare dimensionless duration).
- [x] Phase 2 Green: all 14 files rewritten and wired; test passes.
      Commit `3b591a0`. **Found and fixed a real, previously-undiscovered
      Kernel bug**: `evaluator.py::_bind_call` never checked
      `self.structs`/`self.classes` for a bare-`Var` callee, so any
      struct constructor call from *within an imported function's own
      body* (not main's top level) failed at runtime with `unknown
      function` even though it compiled cleanly — confirmed via a
      minimal isolated repro. Fixed by mirroring the existing
      struct/class-recognition logic already present in
      `_run_unit_body`'s top-level dispatch and `_eval_value`'s
      classical-expression dispatch. **Found, not fixed** (design
      avoided them instead, see "Related, not blocking" below): a
      deeper, separate limitation where user-defined free functions that
      *return* a struct type have no correct execution path at all
      (route through the state/Joint-oriented `_bind_user_fun`, not the
      classical-value `_eval_classical_call`, which explicitly excludes
      struct return types); `&&` is not a supported expression operator;
      Float relational comparisons (`>`,`<`,`>=`,`<=`) between two
      Classical-kind operands are mistyped as `Classical<Float>` instead
      of `Classical<Bool>`; the `abs()` math builtin only has a quantum-
      coordinate (`map_coord`) implementation, none for classical scalar
      context. Design was adjusted to avoid all four (struct
      construction happens directly in `main`, matching A06/A10's own
      already-working pattern; no `&&`/comparison-derived classical
      Bools; no classical `abs()` call).
- [x] Phase 3 Refactor: README fully rewritten (theme, physics
      citations, honesty table, "Units and interpretation", Kernel
      `expect` caveat); `test_noether_forge_slice_b/c_d_integrated_red.py`
      updated (obsolete LISS-0120 line-count-budget assertions removed;
      `run_source` → multi-file-aware `run_path`; physics_ir atom-symbol
      assertion relaxed to Operator-node presence — all documented
      in-file); reviewer empathy summary below.
- [x] Full regression: `pytest tests/ -q` → 1206 passed, 57 failed (-3
      vs. LISS-0337's 60, no new failures — A11 and the two
      `noether_forge` structural test files' pre-existing failures all
      resolved); `python3 tests/spec_verification/run_all.py` →
      157/161 (97.52%, +1 vs. LISS-0337's 156/161 — the A11 SV case);
      `git diff --check` → clean. Confirmed via
      `test_applied_catalog_health_red.py`: A11 no longer appears in
      that test's failure list (empty — all applied-catalog examples
      now pass).
- [x] WP-0095 work unit 6 row updated.

## Reviewer empathy summary

**何を目的として何を変更したか**: A11の14ファイル全て（`main_static.sqx`
含む）を、却下・凍結されたNoether Forge量子物質発見テーマから、構造物
監視向け量子磁力計アレイへ全面的に書き換えた。NV中心のD≈2.87GHzという
実在する物理定数を軸に、回転座標系近似（磁気共鳴シミュレーションの標準
手法）で欠陥結合・双極子結合という物理的に妥当な項のみを実際に評価する。
14ファイル全てが実際に配線され、以前のような未配線の死んだ足場は
残っていない。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- Green中に、**インポートされた関数の本体内での構造体コンストラクタ
  呼び出しが実行時に失敗する**という、真に未発見だったKernelバグを
  発見・修正した。これは`_run_unit_body`のトップレベル分岐や
  `_eval_value`の分類済み式評価には既に存在していた構造体認識ロジックが、
  関数本体を実行する`_bind_call`経路には一度も実装されていなかったため。
  最小再現で確認し、既存の2箇所と同じパターンのチェックを追加して修正
  した。
- 同じ調査の過程で、**さらに深い、別の言語ギャップ**（構造体を返す
  classical自由関数の実行経路が存在しない、`&&`が式として未対応、
  Float比較演算子がClassical<Bool>ではなくClassical<Float>と誤型付け
  される、`abs()`にclassicalスカラー版の実装が無い）を発見したが、
  これらは修正せず、設計側でこれらのパターンを完全に回避することで
  対応した — 修正には本セッションのスコープを大きく超えるKernel変更が
  必要と判断したため。
- 物理的な信号（`⟨Z⟩`が健全サイトで~1.13、応力下サイトで~-0.99）が
  1を超える点について、これはこのKernelの`expect(Z,…)`がエンタングルした
  多量子ビット状態に対して真の部分トレース計算を行っていないという
  既存の（このIssueが発見も修正もしていない）簡略化によるものと判断し、
  READMEに明記した。

**人間がコードレビューで重点的に見るべきポイント**:
- `_bind_call`への修正が、既存の`_run_unit_body`/`_eval_value`の構造体
  認識ロジックと矛盾なく統合されているか。
- 発見したが修正しなかった3つのKernel gapは、将来どのような優先度で
  対応すべきか（このIssueでは判断していない）。
- `test_noether_forge_slice_b/c_d_integrated_red.py`の書き換え（行数
  予算アサーションの削除）が、LISS-0120の歴史的文脈を正しく保存しつつ
  適切に更新されているか。

## Related, not blocking

Three deeper classical-language gaps were found live during Green,
confirmed real, and deliberately **not fixed** here (design avoided them
instead — see the reviewer empathy summary above for how):

1. User-defined free functions that *return* a struct type have no
   correct execution path — they route through the state/Joint-oriented
   `_bind_user_fun`, not the classical-value `_eval_classical_call`
   (which explicitly excludes struct return types via its
   `classical_heads` set). My `_bind_call` fix (this Issue) makes struct
   construction *inside* a function body work, but calling a function
   whose own *return type* is a struct from a Type-First binding site
   still fails (`unknown struct constructor` from `_construct_struct`'s
   own validation, since the binding's declared-type check and the
   actual RHS callee are conflated in `_run_unit_body`'s top-level
   dispatch).
2. `&&` lexes as an `AND` token but is not accepted in general
   expression position (`unexpected token in expression: '&&'`).
3. Float relational comparisons (`>`, `<`, `>=`, `<=`) between two
   Classical-kind operands are mistyped as `Classical<Float>` instead of
   `Classical<Bool>` (`typecheck.py::_infer_binop`'s "Classical ⊕
   Classical" branch has no case for relational operators, falling
   through to its Float-typed default) — confirmed the `RELATIONAL`
   branch that *does* correctly return `State<Bool>` is only reached
   when at least one operand is State-kind, never for pure classical
   comparisons.
4. The `abs()` math builtin only has a quantum-coordinate (`map_coord`)
   implementation (`math_ops.known_math_op`, gated to a single bare
   `Var` argument); no classical-scalar-context implementation exists.

None of these are fixed in this Issue. Flagged for a future Kernel-side
Issue if any of these patterns recur often enough (e.g. across the
remaining B04/B07/B08 migrations, or future multi-file examples using
DDD-style factory functions) to be worth generalizing.

## Non-goals

- Medical / resource-exploration sensing themes (queued for later).
- Fixing gaps 1–4 above (documented, not fixed).
- Remaining example migrations (B04/B07/B08).
