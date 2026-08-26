# LISS-0351: automate A03_h2_vqe's Jordan-Wigner literature cross-check (research note follow-up)

## Metadata

- Local issue ID: LISS-0351
- Status/phase: **complete** (2026-08-07) — PR
  [#418](https://github.com/nn0cl/staqex/pull/418) merged, commit
  `4eb91ad`
- Type: Feature Path (test-only addition —
  `tests/test_liss_0351_a03_jw_literature_crosscheck_red.py`; no
  Kernel or example content change)
- Priority: P2
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: standalone, grounding the "Follow-up (not yet done)" item in
  `docs/research/2026-08-05-h2-two-orbital-jordan-wigner-cross-validation.md`,
  requested after [LISS-0350](LISS-0350-jw-mapping-scale-relative-tolerances.md)
  fixed A03's silently-zeroed Hamiltonian
- Parent: none
- Depends on: [LISS-0350](LISS-0350-jw-mapping-scale-relative-tolerances.md)
  (the fix this test would have caught a regression of, had it existed
  earlier)
- Blocks: none
- Branch: `feature/liss-0351-a03-jw-literature-crosscheck-test`
- GitHub Issue / PR: [#418](https://github.com/nn0cl/staqex/pull/418)
  (merged, `4eb91ad`)

## Design decision

The research note's own "Follow-up (not yet done)" section named exactly
this gap: its cross-check was symbolic (hand-derived, cross-checked
against `second_quantization.py`'s own multiplication table), not a
live run of Staqex's compiler. Now that LISS-0350 has fixed the bug
that was silently zeroing A03's Hamiltonian, this Issue performs that
live check and turns it into an automated regression test.

**Live result** (confirmed before drafting this Issue): extracting
A03's actual compiled `H_electronic` `QubitOperator` (via `run_path`
with `hamiltonian.op_n_qubits` traced to capture
`self.operators["H_electronic"]`, the same extraction point LISS-0350's
own test already uses) and converting each Pauli-term coefficient from
Joules back to Hartree (`coeff_J / (1 Ha in J)`):

| Term | Computed (post-LISS-0350) | Research note / literature |
|---|---|---|
| I (electronic only) | −0.4804 Ha | −0.4804 Ha (derived, §6) |
| Z0 | 0.3435 Ha | 0.3435 Ha (literature `g1`) |
| Z1 | −0.4347 Ha | −0.4347 Ha (literature `g2`) |
| Z0Z1 | 0.5716 Ha | 0.5716 Ha (literature `g3`) |
| X0X1 | 0.0910 Ha | 0.091 Ha (literature `g4`) |
| Y0Y1 | 0.0910 Ha | 0.091 Ha (literature `g5`) |

All six match to 4 decimal places (the literature source's own
precision). `g0_electronic + E_nn = −0.4804 + 0.70557 = 0.2252 Ha`,
matching the literature's full `g0 = 0.2252 Ha` to within `0.013%`
relative difference — consistent with the research note's own §7
symbolic result (`0.0043%`, computed with more decimal precision than
this test's 4-decimal literature inputs allow).

**This confirms two things at once**: (1) LISS-0350's fix produced not
merely *some* nonzero Hamiltonian, but the *numerically correct* one,
matching literature; (2) the research note's own symbolic derivation
(§2-§7) is independently confirmed against Staqex's actual compiled
output, closing its named gap.

## Intent

1. New test file
   `tests/test_liss_0351_a03_jw_literature_crosscheck_red.py`: run
   `main_h2_vqe.sqx`, extract `H_electronic`'s 6 grouped Pauli-term
   coefficients (same trace-`op_n_qubits` extraction pattern LISS-0350
   established), convert Joules to Hartree, and assert each matches
   the research note's derived/literature values to within a small
   absolute tolerance (`1e-3` Hartree, looser than the 4-decimal
   literature source's own precision to avoid brittleness). Also
   assert `g0_electronic + E_nn` matches the literature's full `g0`
   within the same tolerance.
2. Update the research note's "Follow-up (not yet done)" section to
   record this test now exists and the live numeric result, closing
   the named gap (without editing any of the note's earlier
   sections/claims, which remain the honest historical symbolic-only
   record).

## Explicitly out of scope

- `main_h2_vqe.sqx` itself (unchanged).
- `second_quantization.py` (unchanged — LISS-0350 already fixed it;
  this Issue only verifies the fix's output against literature).
- Re-deriving or re-verifying the literature source values themselves
  against the primary O'Malley et al. 2016 paper (the research note's
  own "Provenance caveat" in §4 already flags this as unresolved and
  out of scope for that note; this Issue inherits the same caveat,
  unchanged).
- Building the separate `A03_h2_jw_crosscheck` dedicated example the
  research note also suggested as an alternative — a test is
  sufficient and lower-overhead for this purpose.

## Acceptance reference

```gherkin
Feature: A03_h2_vqe's compiled Jordan-Wigner output matches literature

  Scenario: the six Pauli-term coefficients match the research note's derivation
    Given the compiled main_h2_vqe.sqx's H_electronic QubitOperator
    When each coefficient is converted from Joules to Hartree
    Then all six match the research note's derived/literature values within tolerance

  Scenario: the full identity coefficient matches literature once nuclear repulsion is added
    Given g0_electronic (from H_electronic) and E_nn (nuclear_repulsion, in Hartree)
    When summed
    Then the result matches the literature's full g0 = 0.2252 Ha within tolerance
```

## Verification plan for this design intake (not shipped as a test)

Already performed live (see table above) before drafting this Issue;
the test formalizes this exact check as an assertion-based regression.

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-07
- Size: `XS` — one test file, values and extraction pattern already
  live-verified before drafting.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0351_a03_jw_literature_crosscheck_red.py` added
      (2 cases). Confirmed both failing with LISS-0350's fix
      temporarily reverted (`git show <pre-fix-commit>^:...` swapped
      in, then restored): `H_electronic` collapsed to a bare
      `OpLit(0.0)`, so the coefficient-extraction helper's own
      structural assertion failed (`expected a scalar*Pauli term, got
      OpLit(value=0.0, ...)`).
- [x] Phase 2 Green: with LISS-0350's fix restored (unmodified), both
      tests pass — confirming the extracted `H_electronic` coefficients
      match the research note's derived/literature values.
- [x] Phase 3 Refactor: no further change needed; reviewer empathy
      summary below; research note's Follow-up section updated
      separately.
- [x] Full regression: `pytest tests/ -q` → 1229 passed, 52 failed
      (unchanged failure count vs. the post-LISS-0350 baseline, no new
      failures — +2 is this Issue's own new tests); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged); `git diff --check` → clean;
      `second_quantization.py` confirmed unmodified by this Issue
      (`git diff --stat` shows no changes to it — only new test/docs
      files).

## Reviewer empathy summary

**何を目的として何を変更したか**: `docs/research/2026-08-05-h2-two-orbital-jordan-wigner-cross-validation.md`
自身が「Follow-up (not yet done)」として明記していたギャップ
（記号的な手計算による照合のみで、Staqexコンパイラの実際の出力に
対するライブ検証が未実施）を埋めた。LISS-0350の修正により
`H_electronic`が実際に非ゼロになったことで、この照合が初めて
意味を持つようになったため、修正直後にこの検証を実施した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- テストの許容誤差（`1e-3` Hartree）は、文献ソース自体が4桁精度
  でしか与えられていないこと（`0.2252`等）を踏まえ、その精度より
  緩く設定した——文献値自体の丸め誤差でテストが壊れないようにする
  ため。実際の一致は4桁全てで完全一致していることを確認済み。
- Red確認時、LISS-0350修正前のコミット（`git show
  <commit>^:second_quantization.py`）を一時的に差し替えて検証した後、
  必ず修正後の内容に戻し、`git diff --stat`でファイルが実際に
  無変更の状態に戻っていることを確認した（誤って古いバージョンの
  まま残してしまわないように）。

**人間がコードレビューで重点的に見るべきポイント**:
- research note自体の§4「Provenance caveat」（文献値が一次資料PDFから
  直接再抽出されたものではなく、二次資料の再現値に基づく）は、本
  Issueでも未解決のまま引き継いでいる。将来一次資料での再検証が
  行われた場合、このテストの期待値も合わせて更新が必要になる。

## Non-goals

- Kernel or example content changes.
- Re-verifying the literature source against the primary paper.
