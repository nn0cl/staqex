# LISS-0341: migrate `B08_operators_hamiltonians` to real units (WP-0095 work unit 9)

## Metadata

- Local issue ID: LISS-0341
- Status/phase: **complete** (2026-08-06) — PR
  [#398](https://github.com/nn0cl/staqex/pull/398) merged, commit
  `45fe41d`
- Type: Feature Path (example content only —
  `examples/basics/B08_operators_hamiltonians/operators_hamiltonians.sqx`;
  no Kernel change)
- Priority: P1
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md)
  work unit 9 — the last `examples/basics`/`examples/applied` entry;
  after this, only the 5 locked S01 files and `quantum_matter_discovery`
  remain
- Parent: [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
- Depends on: [LISS-0330](LISS-0330-real-hbar-kernel-primitive.md),
  [LISS-0336](LISS-0336-evolve-real-unit-canonicalization-bugs.md)
- Blocks: none within WP-0095
- Branch: `feature/liss-0341-b08-operators-hamiltonians-real-unit-migration`
- GitHub Issue / PR: [#398](https://github.com/nn0cl/staqex/pull/398)
  (merged, `45fe41d`)

## Design decision

`B08_operators_hamiltonians` teaches ADR 0176's **minimal dialect face**
(`// staqex-profile: experiment`-style, no `package`/`main`, no ritual
uncompute) with ADR 0180 Operator type-inference and ADR 0184 classical
multi-bind: `J, h = 1.0, 0.5` (untyped multi-bind), `H_chain = -J *
(Z[0]*Z[1]) - h*(X[0]+X[1])` (inferred `Operator`), `evolve ... for 0.7`
(bare duration). This is the same qubit-Pauli sparse-path pattern as
B07 (LISS-0340) — genuinely needs real, appropriately-scaled `Energy`/
`Time` values, not just a unit-satisfying wrapper.

**Adopted fix**: `J`/`h` become explicit `Energy`-typed declarations
(breaking pure type-inference for just these two, since a bare
multi-bind literal cannot carry unit information — confirmed no other
way to attach a unit to an inferred classical multi-bind); `H_chain`
stays inferred (no `Operator` keyword needed — confirmed live: ADR
0180's ty-fill still works with `Energy`-typed operands); the duration
becomes an explicit `Time dur = 0.7.fs`. This preserves the "minimal
dialect" teaching point (no `package`/`main`, `H_chain`/`s0,s1` stay
inferred) while satisfying ADR 0195's real-unit requirement for the two
values that must carry dimensions.

## Intent

1. `J, h = 1.0, 0.5` → `Energy J = 1.0.eV to J` / `Energy h = 0.5.eV to
   J` (ratio preserved).
2. `H_chain = ...` — unchanged (still inferred).
3. `evolve (s0, s1) under H_chain for 0.7` → `... for dur`, declaring
   `Time dur = 0.7.fs` (ratio/magnitude preserved from the original).

## Explicitly out of scope

- Any Kernel change.
- Changing `H_chain`/`s0, s1`'s inferred-type style (still demonstrates
  ADR 0180/0176).
- Remaining example migrations (the 5 locked S01 files,
  `quantum_matter_discovery`).

## Acceptance reference

```gherkin
Feature: B08_operators_hamiltonians uses real physical units

  Scenario: the migrated example compiles and runs to a real terminal measurement
    Given the migrated operators_hamiltonians.sqx
    When it is compiled and run with a fixed seed
    Then it compiles without EVOLVE_UNRESOLVED_UNIT_ERROR or any hard diagnostic
    And it reaches a non-vacuum terminal measurement
```

## Verification plan for this design intake (not shipped as a test)

Confirmed live: `Energy J = 1.0.eV to J`, `Energy h = 0.5.eV to J`,
`H_chain = -J * (Z[0]*Z[1]) - h*(X[0]+X[1])` (still inferred, no
`Operator` keyword), `Time dur = 0.7.fs`, `evolve (s0, s1) under
H_chain for dur` compiles and runs to a non-vacuum measurement.

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-06
- Size: `XS` — one example file, minimal targeted retyping.
- Route: direct implementation by this session.
- Confidence: high (identical pattern to B07/LISS-0340, plus a live
  confirmation that ADR 0180 inference still works with Energy operands).

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0341_b08_operators_hamiltonians_real_unit_migration_red.py`
      added. Commit `17c6e59`: failed for the documented reason
      (`EVOLVE_UNRESOLVED_UNIT_ERROR` on the bare `for 0.7` duration).
- [x] Phase 2 Green: `.sqx` rewritten. Commit `03dd23d`: 1/1 passed.
      **Found and fixed a real, previously-undiscovered Kernel bug**:
      `backend/qasm/trotter.py`'s Suzuki gate-angle computation
      (`theta = coeff * delta_t`) was never updated for ADR 0195's real-ℏ
      formula, and `_suzuki_term_gates` had its own absolute-coefficient
      epsilon (`1e-15`) predating the coalescing-epsilon bug LISS-0336
      fixed in `sparse_pauli.py` — together, both silently collapsed
      B08's real Joule-scale Hamiltonian's QASM3 Trotter emission into an
      "idle/global-phase" no-op circuit
      (`test_qasm3_codegen.py::test_trotter_ising_evolve_qasm` caught
      this). Confirmed this affects *any* future QASM3-emitted example
      whose evolve duration becomes real-`Time`-typed, not just B08 (B07
      wasn't caught only because no QASM3 test exercises it). Fixed by
      dividing by real ℏ (matching `expm_ih`/`expm_ih_apply`'s own
      formula) and removing the redundant/incorrect pre-division
      absolute-coefficient filter (the existing post-division
      dimensionless-`theta` check is the correct, unit-independent
      negligibility test).
- [x] Phase 3 Refactor: no further change needed; reviewer empathy
      summary below.
- [x] Full regression: `pytest tests/ -q` → 1209 passed, 57 failed
      (unchanged failure count vs. LISS-0340's 57, no new failures — +1
      is this Issue's own new test); `python3
      tests/spec_verification/run_all.py` → **161/161 (100%, Gate:
      PASS)** — every `.sqx` case `spec_verification`'s own 161-case
      suite exercises now passes. **Correction, checked directly**:
      this is not a complete repository-wide audit — `examples/basics/B16_effect_marking`
      is still unmigrated (confirmed live: `EVOLVE_UNRESOLVED_UNIT_ERROR`)
      and simply isn't referenced by any `spec_verification` suite, so
      it was never counted in the 161. WP-0095's own work-unit list
      already tracked B16 separately; not claiming it complete here.
      `git diff --check` → clean.
- [x] WP-0095 work unit 9 row updated.

## Reviewer empathy summary

**何を目的として何を変更したか**: `B08_operators_hamiltonians`の
`J`/`h`を明示的なEnergy型（`H_chain`自体は型推論のまま）に、durationを
明示的なTime型に変更した。この過程で、QASM3 Trotterバックエンドの
ゲート角度計算がADR 0195の実ℏ式に一度も対応していなかったという、
真に未発見だったKernelバグを発見・修正した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- `test_trotter_ising_evolve_qasm`が「idle/global-phase」という
  フォールバックコメント付きの出力を返していたことから、角度が
  事実上ゼロになっていると推測し、`theta = coeff * delta_t`という式が
  ℏ除算を欠いていることを直接コード読解で確認した。
- `_suzuki_term_gates`の絶対値1e-15の事前フィルタは、LISS-0336で
  `sparse_pauli.py`に見つけた`_coalesce`の絶対イプシロンバグと**全く
  同じ構造**だが、別の場所（QASMバックエンド）にある独立した実装
  だったため、LISS-0336の修正では対応できていなかった。この事前
  フィルタを削除し、ℏ除算後の無次元`theta`に対する既存のチェック
  （こちらは単位に依存しない正しい判定）のみを残した。
- この問題はB08固有ではなく、実Time型durationを使う将来のどのQASM3
  出力例でも起こりうることを確認し、WP-0095/open-work-registerに
  明記した。

**人間がコードレビューで重点的に見るべきポイント**:
- `trotter.py`の修正が、実際に`compiler/staqex/runtime/matrix.py`の
  `expm_ih`と数式として整合しているか（同じHBAR_SIを参照している）。
- 他にも同様の「Kernelのℏ変更が伝播していないコードパス」が残って
  いないか（このセッションで既に3箇所発見・修正済み: runtime evolve、
  spec_verificationフィクスチャ、QASMバックエンド）。

## Non-goals

- Kernel changes.
- Remaining example migrations (5 locked S01 files,
  `quantum_matter_discovery`).
