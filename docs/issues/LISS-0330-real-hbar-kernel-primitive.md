# LISS-0330: real ℏ Kernel primitive (WP-0095 work unit 1)

## Metadata

- Local issue ID: LISS-0330
- Status/phase: **complete** (2026-08-05) — PR
  [#376](https://github.com/nn0cl/staqex/pull/376) merged, commit
  `29f2ee8`
- Type: Feature Path (Kernel — `compiler/staqex/dimensions.py`,
  `compiler/staqex/runtime/matrix.py`, `compiler/staqex/runtime/sparse_pauli.py`,
  `compiler/staqex/stdlib/prelude.py`; no grammar/parser change)
- Priority: P1
- Initial planning size: `M`
- Owner / agent: Claude Code
- Program: [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md)
  work unit 1
- Parent: [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
  (Accepted)
- Depends on: none
- Blocks: WP-0095 work unit 2 (`A03_h2_vqe` migration) and every later
  example migration — and, by design, makes **every currently-passing
  `evolve`-using example fail closed** until it is individually migrated
  (per ADR 0195's explicit rejection of a silent natural-units fallback)
- Branch: `feature/liss-0330-real-hbar-kernel-primitive`
- GitHub Issue / PR: none yet

## Intent

Implement ADR 0195 Decisions 1, 2, and 4 (the Kernel primitive only — no
example migration, that is WP-0095 work unit 2+):

1. Add `HBAR_SI = 1.054571817e-34` (J·s, CODATA 2018 exact) to
   `compiler/staqex/dimensions.py` as the single source of truth.
2. Change `runtime/matrix.py::expm_ih`'s phase scaling from `-1j *
   float(t)` to `-1j * float(t) / HBAR_SI`, and `runtime/sparse_pauli.py::expm_ih_apply`'s
   `scale = (-1j * tt) / k` to `scale = (-1j * tt / HBAR_SI) / k` —
   confirmed these are the only two matrix-exponential primitives
   `evolve` reaches (all three `runtime/evaluator.py` call sites at
   lines 1614/1644/1752 route through `expm_ih`; the sparse-Pauli lane
   routes through `expm_ih_apply` separately).
3. Add a fail-closed diagnostic (name TBD during Red — candidate
   `EVOLVE_UNRESOLVED_UNIT_ERROR`) when `H`'s coefficients or `t` are not
   resolvable to real `Energy`/`Time` dimensions by the time they reach
   these primitives, per ADR 0195 Decision 4. This is the mechanism that
   makes an unmigrated example fail closed instead of silently running
   under a reintroduced ℏ = 1 path.
4. Add `"hbar": HBAR_SI` to `compiler/staqex/stdlib/prelude.py`'s
   `PRELUDE_CONSTANTS`, importing the same `HBAR_SI` value — never a
   second, separately-maintained number.
5. Add `ns` (`1e-9` s) and `fs` (`1e-15` s) to `dimensions.py`'s time-unit
   tables, filling the gap ADR 0195's design check found (only
   `s`/`ms`/`us`/`ps` exist today), needed for the reference test case
   below and anticipated by realistic molecular/atomic timescales in the
   first migration (WP-0095 work unit 2).
6. Add a reference test case verified against a hand-computed expected
   value, independent of the Kernel's own output: a single-qubit system
   with `H = (E/2) * Z` for a real, literature-plausible energy `E` in
   `eV`, evolved for a real duration `t` in `fs`, asserting the resulting
   phase matches `exp(-i * (E_joules / 2) * t_seconds / HBAR_SI)` computed
   independently in the test itself (not by re-deriving the Kernel's own
   formula).

## Explicitly out of scope

- Any example migration (`A03_h2_vqe` or any other `.sqx` file) — WP-0095
  work unit 2+.
- The unrelated `Operator G = adjoint(H)` / `hamiltonian.py` `Call`-node
  bug — tracked separately under WP-0092, not this Issue.
- Any change to `Operator`/Hamiltonian *construction* semantics (Pauli
  algebra, `sum`/`product` binders, dimension checking beyond what's
  needed for the fail-closed diagnostic) — only the time-evolution
  primitive's numeric formula and the new fail-closed guard change.
- Live QPU/pulse-level timing (ADR 0193, separate).

## Acceptance reference

New Phase 1 scenarios (no existing spec section covers real-ℏ dynamics
yet — this Issue's own Red test is the acceptance evidence):

```gherkin
Feature: real hbar time evolution

  Scenario: a real energy and real duration produce the physically correct phase
    Given H = (E/2) * Z for a real Energy E and evolve for a real Time t
    When the state reaches terminal measure (or an intermediate `inspect`)
    Then the resulting phase matches exp(-i * E_joules/2 * t_seconds / hbar),
      computed independently of the Kernel's own evolve formula

  Scenario: hbar is a usable prelude constant
    Given a program reads `hbar` directly
    When the program runs
    Then its value equals 1.054571817e-34 (CODATA 2018), the same value
      evolve's own formula uses

  Scenario: an unresolved-unit Hamiltonian or duration fails closed
    Given `evolve` is given a bare dimensionless Float H or t with no
      Energy/Time unit resolvable
    When the program runs
    Then it fails with an explicit diagnostic
    And no phase is silently computed under an implicit ℏ = 1 fallback

  Scenario: every existing evolve-using example now fails closed, by design
    Given an existing example written under the old ℏ = 1 convention
    When it is run unmodified after this Issue lands
    Then it fails with the same explicit diagnostic, not a silently wrong
      physical result
    And this is recorded as an accepted, temporary state until each
      example's own migration Issue lands (WP-0095 work unit 2+)
```

The fourth scenario is a documentation/acceptance statement, not a new
runtime behavior distinct from the third — it exists to make explicit
that this Issue's Green phase is expected to (temporarily) break every
currently-passing `evolve`-using test and example, and that this is the
intended, ADR-approved outcome, not a regression to walk back.

## AI planning record (size M)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-05
- Size: `M` — two small, well-localized primitive changes
  (`expm_ih`/`expm_ih_apply`), one new constant, one new diagnostic, two
  new unit-table entries, one hand-verified reference test. The larger
  cost is not code volume but consequence: this Issue's Green phase
  intentionally breaks every existing `evolve`-using test/example until
  each is separately migrated.
- Route: direct implementation by this session.
- Assumptions: `H`'s "resolvable to Energy" check can reuse
  `dimensions.py`'s existing dimension-inference machinery (already used
  elsewhere for `to`-conversion type-checking) rather than inventing new
  inference logic — to be confirmed during Red/Green, not assumed
  finished here.
- Confidence: medium — the primitive-formula change itself is
  low-risk and precisely located (both call sites read directly before
  drafting this Issue), but the fail-closed unit-resolution diagnostic's
  exact integration point (compile-time typecheck vs. runtime check) is
  not yet fully verified against `dimensions.py`'s existing machinery and
  may surface a smaller design question during Red, consistent with this
  session's established pattern.
- Revision links: none yet.

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0330_real_hbar_kernel_primitive_red.py`
      added. Commit `2585190`: failed as a compile failure
      (`ImportError: cannot import name 'HBAR_SI'`) — a documented,
      CLAUDE.md-allowed Red form.
- [x] Phase 2 Green: `HBAR_SI` added to `stdlib/prelude.py` (not
      `dimensions.py` as originally sketched — that module is
      compile-time-only per its own docstring, discovered during Green;
      an implementation-detail refinement within approved scope, not a
      new decision, matching this session's established pattern e.g.
      LISS-0321's directory-layout refinement); `expm_ih`/`expm_ih_apply`
      formulas changed; `EVOLVE_UNRESOLVED_UNIT_ERROR` added;
      `ns`/`fs` units added. Commit `1e6e044`: all 4 new tests pass.
      **Two unanticipated numerical-robustness bugs found and fixed
      during Green** (not scope creep — both are in the exact two
      primitives this Issue modifies, and both were exposed only by this
      Issue's own change): `expm_ih`'s old fixed 12-halving
      scaling-and-squaring silently left `||A||/2^12 >> 1` for the much
      larger magnitudes real ℏ division produces, overflowing the Taylor
      series -- fixed by computing the halving count directly from the
      operator norm. `expm_ih_apply` (sparse, no dense matrix) has no
      matrix-squaring trick available, so an unboundedly large step count
      is intractable, not just slow -- fixed with an explicit, generous
      cap (2**16) and a clean `ValueError`/`KernelError` beyond it,
      instead of an `OverflowError` crash or an infinite loop (confirmed
      one real test — `sv28_sparse_pauli` — previously hung/crashed until
      this second fix landed).
- [x] Phase 3 Refactor: no further change — reviewed for unused
      imports/dead branches via `python3 -W error -c "import ..."`, none
      found. Reviewer empathy summary below.
- [x] Full regression, honestly reported: `pytest tests/ -q` → **66
      failed, 1188 passed** (every failure is the `EVOLVE_UNRESOLVED_UNIT_ERROR`
      family, the intended fail-closed outcome, not a crash or hang —
      confirmed by full names in the commit message); `python3
      tests/spec_verification/run_all.py` → **132/145, 91.03%, Gate:
      FAIL** (also added a suite-level exception guard to `run_all.py`
      itself so it produces this honest count instead of crashing
      entirely on the first `KernelDiagnosticError`/`ValueError` it hits —
      needed to fulfill this Issue's own reporting requirement, not
      unrelated scope); `git diff --check` → clean.
- [x] WP-0095 work unit 1 row updated; work unit 2 (`A03_h2_vqe`
      migration) explicitly named as the next, separately-approved Issue.

## Reviewer empathy summary

**何を目的として何を変更したか**: ADR 0195のDecision 1・2・4を実装した。
`hbar`をSI実測値(CODATA 2018)として`stdlib/prelude.py`に追加し、
`evolve`の時間発展計算式を`exp(-iHt)`(旧・自然単位)から
`exp(-iHt/hbar)`(実際のℏ)に変更した。バレの無次元durationは
`EVOLVE_UNRESOLVED_UNIT_ERROR`でfail-closedになる。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- `HBAR_SI`の配置先をADR 0195の想定(`dimensions.py`)から
  `stdlib/prelude.py`に変更した。`dimensions.py`はdocstringで
  「compile-time only」と明記されており、実行時に使う数値定数を
  置く場所として不適切だったため。ADR自身が「TBD during
  implementation」と明記していた点なので、実装判断の範囲内と判断した。
- Green中に見つかった2つの数値的頑健性バグ(`expm_ih`のスケーリング
  上限、`expm_ih_apply`の無制限ステップ数)は、このIssueが直接変更する
  2つのプリミティブ内で、このIssue自身の変更によって初めて露呈した
  問題であり、スコープ拡大ではなく本Issueの範囲内の修正と判断した。
  `expm_ih_apply`の2^16ステップという上限値は経験的な選択で、正式な
  性能要件から導出したものではない。
- `evolve`のduration側のみユニット解決チェックを実装し、Hamiltonian
  係数側(H自体がEnergy次元を持つか)のチェックは実装していない
  (このIssueの元々のスコープ縮小判断 — H側の完全なチェックは
  各サンプル移行Issueでの実地検証を通じて必要性を判断する方が良いと
  考えた)。

**人間がコードレビューで重点的に見るべきポイント**:
- `expm_ih_apply`の2^16ステップという上限が、将来の実サンプル移行
  (A03_h2_vqe等)で本当に十分か、それとも実際の分子系ではもっと
  大きな上限が必要になるか。
- duration側のみのユニットチェックで十分か、H側のチェックも
  このIssueに含めるべきだったか。
- `HBAR_SI`の配置場所変更(`dimensions.py`→`stdlib/prelude.py`)が
  ADR 0195の意図と整合しているか。

## Non-goals

- Any example migration.
- The unrelated `adjoint(H)` bug.
- Live QPU timing.
