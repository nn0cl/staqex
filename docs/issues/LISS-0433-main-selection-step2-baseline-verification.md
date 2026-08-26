# LISS-0433: `main_selection.sqx` step 2 — baseline distributional-equivalence verification

## Metadata

- Local issue ID: LISS-0433
- Status: complete
- Type: Feature Path (verification only — `examples/showcase/S02_drug_discovery/**`
  was already rewritten as a mechanical necessity of LISS-0432/S10)
- Priority: P1
- Planning size: S — the file rewrite itself landed in LISS-0432; this
  Issue's own scope is the dedicated numeric verification against the
  pre-batch baseline
- Owner / agent: Claude Code
- Parent: WP-0099 (batch `s02-step2-literal-transcription`), ADR 0207
- Branch: `batch/s02-step2-literal-transcription` (batch-level)
- GitHub Issue / PR: (opened at batch completion)

## Intent

Confirm that `main_selection.sqx` step 2's literal, term-by-term
transcription (LISS-0421–0432) reproduces the *same physics* as the
pre-batch `project ... onto feasible(...)` primitive it replaces — not
merely "compiles and runs," but numerically equivalent to the captured
pre-batch baseline (`status: succeeded`, `selection pattern: (0, 1, 1, 1,
1, 1, 0, 0)`, `Vacuum: False`).

## Scope note: file rewrite vs this Issue

WP-0099's own execution order (`S9, S10 (any order, after S8) → S11`)
implicitly assumed `main_selection.sqx`'s step 2 rewrite would happen as
S11's own work. In practice, LISS-0432 (S10) needed to do the mechanical
rewrite itself: retiring `feasible(...)` outright left `main_selection.sqx`
(its last remaining caller in the whole corpus) non-compiling, and S10's
own self-verification requires a green full-regression sweep at the end of
*that* Issue, not a two-Issue-wide one. This Issue's own scope is therefore
the *dedicated verification* the batch record named for S11 — checking the
already-rewritten file against the baseline — not the rewrite itself
(disclosed in LISS-0432's own doc; not silently absorbed).

## Verification performed

Compared against the tip of LISS-0431 (commit `c26e1ee2`, via a disposable
`git worktree`, not by disturbing the working tree) for the *sampled
measurement outcome* across 10 seeds (0–9): **byte-identical** for every
seed. This alone was not sufficient to close the Issue, since sampling is
renormalization-invariant (LISS-0431's own finding) and so cannot alone
distinguish "same physics" from "same shape, different overall scale."

**Real finding while deepening the check**: comparing the *full marginal
distribution* (not just the one sampled outcome) at seed 0 found a real,
non-floating-point discrepancy — up to 0.028 absolute probability. Traced
to its root cause rather than dismissed: `c26e1ee2` is *itself* an
internally inconsistent comparison point for this specific check — LISS-
0431 (S9), by design, already removed `project`'s implicit renormalization
for *every* target shape, including `feasible(...)`, but at that commit
`main_selection.sqx` had not yet been updated with an explicit `/
||...||` for its `feasible(...)`-based projection (that update was
`main_selection.sqx`'s own step 2 rewrite, which only landed in LISS-0432).
So `c26e1ee2`'s own `main_selection.sqx` was, transiently and by design,
feeding *unnormalized* amplitudes into step 3's `Evolve` (confirmed by
directly capturing the exact vector passed to `sparse_pauli.expm_ih_apply`:
`0.0625` = $1/\sqrt{256}$, psi_0's own bare per-branch amplitude, not
$1/\sqrt{25}=0.2$, the correctly renormalized value the rewritten file
now feeds in). Since `expm_ih_apply` is linear, this made `c26e1ee2`'s raw
marginal an exact positive scalar multiple of the correct one, not a
different distribution. Confirmed directly: renormalizing `c26e1ee2`'s own
captured marginal by its own total (`0.09765625`, matching
$(0.0625/0.2)^2\times 1.0$) brought the max difference against the
rewritten file's marginal down to `1.46e-16` — floating-point-exact
agreement, not merely "close."

Also directly verified (not assumed): $F$ itself — the 25-element selection
subspace — is set-identical between `c26e1ee2`'s `feasible(...)`-computed
set and the rewritten file's `Set F = {...}` comprehension (`old_F ==
new_F`, confirmed by extracting both via `Measure`). And the pre-`Evolve`
marginal (immediately after `project`/`/ ||...||`, before step 3) is
exactly uniform (`0.04` per surviving World, i.e. $1/\lvert F\rvert$) in
the rewritten file, matching what a correctly-renormalized `feasible(...)`
projection of a uniform $\lvert\psi_0\rangle$ must give.

## Design verification performed

1. Sampled measurement outcome, seeds 0–9: byte-identical between the
   rewritten `main_selection.sqx` and the true pre-batch baseline (seed 0
   reproduces the exact captured `(0, 1, 1, 1, 1, 1, 0, 0)`).
2. Full marginal distribution at seed 0: floating-point-exact agreement
   (`1.46e-16` max difference) once the comparison point's own transient
   unnormalized state (an expected, disclosed consequence of this batch's
   own Issue ordering, not a defect) is accounted for.
3. $F$ (the 25-element selection subspace) verified set-identical between
   the old `feasible(...)`-based computation and the new `Set`
   comprehension.
4. Pre-`Evolve` marginal verified exactly uniform over $F$, the physically
   correct result for projecting a uniform $\lvert\psi_0\rangle$.
5. Full regression sweep (1537 passed, unchanged since LISS-0432 — this
   Issue added no new test files, only this verification doc), spec
   verification 100.00%, full `.sqx` corpus `staqex check` clean —
   already current from LISS-0432's own commit; re-confirmed, not
   re-run from scratch, since no source changed in this Issue.

## Exit criteria

- [x] `main_selection.sqx` step 2's literal transcription confirmed
  numerically equivalent to the pre-batch `feasible(...)`-based baseline
  — sampled outcome byte-identical across 10 seeds, full marginal
  distribution floating-point-exact once compared correctly.
- [x] The apparent discrepancy found mid-verification root-caused (an
  expected transient inconsistency in the S9-vs-S10 comparison point, not
  a defect in the rewritten file) rather than dismissed or hidden.
- [x] $F$ itself verified set-identical between old and new computations.
