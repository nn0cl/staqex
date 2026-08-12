# LISS-0422: `Sigma` ket-sum must be literal/unnormalized, not self-normalizing

## Metadata

- Local issue ID: LISS-0422
- Status: complete
- Type: Feature Path (`compiler/staqex/runtime/evaluator.py`,
  `examples/showcase/S02_drug_discovery/main_selection.sqx`,
  `examples/showcase/S02_drug_discovery/README.md`,
  `tests/test_liss_0420_sigma_pi_unification_red.py`)
- Priority: P1 (corrects a shipped keyword's core semantics against the
  project's own binding physicist-first principle)
- Planning size: S (one evaluator function's weight formula, plus
  updating the one caller and its own test file)
- Owner / agent: Claude Code
- Parent: corrects LISS-0420 (WP-0098,
  `case-sensitive-keywords-and-sigma-binder`); direct follow-on to
  LISS-0421
- Branch: `feature/liss-0421-s02-sigma-ket-sum-rewrite` (folded into the
  still-open PR #548, since it directly affects the same file and the
  same `Sigma` construct that PR introduces to `main_selection.sqx`)
- GitHub Issue / PR: #548

## Intent

Adjudicator review of LISS-0421's rewrite ("黒板上のシグマとSigmaを同じもの
にして。係数を包含することは許さない。" — "make Sigma the same as the
blackboard sigma; do not allow it to include a coefficient") identified
that LISS-0420's shipped `KetSumBinder` semantics were wrong against this
project's own binding language-design priority
(`docs/architecture/adjudicator-language-vision.md` §2.2, "source must
denote the same physics as the blackboard").

## The gap (confirmed, not assumed)

The blackboard equation
$\lvert\psi_0\rangle = \dfrac{1}{\sqrt{2^n}}\sum_{x\in\{0,1\}^n}\lvert x\rangle$
has two separate parts: a **literal, unnormalized sum** $\sum_x|x\rangle$
(norm $\sqrt{2^n}$ on its own) and a **separate, explicit normalization
coefficient** $1/\sqrt{2^n}$.

LISS-0420's shipped `_bind_ket_sum_binder` did not implement this — it
assigned each basis ket an equal *probability* weight `1/len(patterns)`
(`joint.bind_split` turns a probability `p` into amplitude
`parent_amp * sqrt(p)`), making `Sigma (x In {0,1}^n) { |x> }` **already
normalized** on its own, with no way to reach the literal unnormalized
sum the bare `Sigma` symbol denotes. LISS-0420's own Hard Stop 2 explored
what an *external* coefficient does on top of that (found: it
double-applies, producing an honest but non-blackboard-matching
unnormalized result) but never questioned whether `Sigma`'s own bare
behavior was the right primitive in the first place. That was the actual
defect: `Sigma` the keyword stood in for a blackboard symbol, but did not
compute the same thing that symbol denotes.

## Fix

`_bind_ket_sum_binder` (`runtime/evaluator.py`) now binds each pattern
with probability weight `1.0` instead of `1.0 / len(patterns)`. Since
`bind_split` computes `amp = parent_amp * sqrt(p)`, `p = 1.0` yields
amplitude `1` per branch — literal, unnormalized addition, exactly
$\sum_x|x\rangle$. Total probability of a bare `Sigma (x In {0,1}^n) {
|x> }` is now `2^n`, not `1`; a normalized state requires the caller to
supply the same explicit coefficient the blackboard equation does
(`(1.0/sqrt(2.0^n)) * Sigma (x In {0,1}^n) { |x> }`), using the
amplitude-scaling bind path LISS-0420 already built for exactly this
purpose (`_bind_scaled_state` — unchanged, it was already doing literal
linear amplitude scaling; only `Sigma`'s own base case was wrong).

`_bind_prepare_selection` (the separate, pre-existing native primitive)
is **unchanged** — it is not a blackboard-symbol keyword and was never in
scope for this correction; it stays its own equal-weight/normalized
construction.

## Consequence for already-shipped consumers

- `main_selection.sqx` (LISS-0421, same PR): step 1 restored to include
  the explicit `(1.0 / sqrt(2.0 ^ n)) *` coefficient — now a genuinely
  literal, term-for-term transcription of the blackboard equation, not an
  approximation of it. Verified byte-identical seeded terminal output to
  the original `prepare_selection(n)` baseline (unchanged from LISS-0421's
  own verification, since the coefficient-scaled form is mathematically
  identical to the old bare-Sigma form — only the internal construction
  path changed).
- `tests/test_liss_0420_sigma_pi_unification_red.py`: the three tests that
  asserted or relied on bare-`Sigma` self-normalization were rewritten,
  not just patched — `test_ket_sum_over_bit_domain_is_equal_superposition`
  became `test_bare_ket_sum_is_literal_and_unnormalized` (now asserts
  total probability `2^n`); `test_ket_sum_matches_prepare_selection_exactly`
  became `test_coefficient_scaled_ket_sum_matches_prepare_selection_exactly`
  (compares the coefficient-scaled form, not bare `Sigma`, to
  `prepare_selection`); `test_external_coefficient_applies_literally_and_can_unnormalize`
  became `test_external_coefficient_applies_literally_as_amplitude_scale`
  (the coefficient is now the *required* normalization step, not a
  redundant double-application — docstrings rewritten to state this
  plainly, not left describing the old, incorrect framing).

## Design verification performed

1. Confirmed the exact mechanism: `bind_split(name, {pattern: 1.0 for
   pattern in patterns})` yields amplitude 1 per branch (since
   `sqrt(1.0) == 1.0`), i.e. literal unnormalized ket addition — not
   guessed, traced through `Joint.bind_split`'s own implementation
   (`runtime/joint.py:196-217`).
2. Confirmed `_bind_scaled_state`'s existing amplitude-scaling mechanism
   (`amp = w.amp * scale`, linear, not squared at this layer) needed no
   change — it was already the correct mechanism; only `Sigma`'s own
   unscaled base case was wrong.
3. Re-verified `main_selection.sqx`'s corrected form produces byte-
   identical seeded output (`selection pattern: (0, 1, 1, 1, 1, 1, 0, 0)`,
   `Vacuum: False`) to the pre-LISS-0421 `prepare_selection(n)` baseline.
4. Full regression sweep: 1511 passed (same count as before this
   correction — no test surface added beyond LISS-0420's own file being
   rewritten to test the corrected behavior). Spec verification: 100.00%
   (161/161).
5. Confirmed no other `.sqx` file in the corpus uses the `Sigma (... In
   {0,1}^n)` ket-sum construct besides `main_selection.sqx` (`grep -rl
   "In {0,1}" examples --include="*.sqx"`), so this correction has no
   other blast radius in shipped examples.

## Exit criteria

- [x] `Sigma (x In {0,1}^n) { |x> }` alone is the literal, unnormalized
  sum (total probability `2^n`), matching the bare blackboard `Sigma`
  symbol with no implicit normalization.
- [x] `main_selection.sqx` restored to the fully-literal transcription
  (explicit coefficient present), byte-identical terminal output
  preserved.
- [x] LISS-0420's own test file rewritten to assert and document the
  corrected semantics, not left asserting the superseded behavior.
- [x] Full regression sweep passes (1511); spec verification 100.00%.
