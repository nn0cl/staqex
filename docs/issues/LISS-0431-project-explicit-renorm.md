# LISS-0431: `project` drops implicit renormalization, accepts a general Operator

## Metadata

- Local issue ID: LISS-0431
- Status: complete
- Type: Feature Path (`compiler/staqex/runtime/evaluator.py`)
- Priority: P1
- Planning size: M
- Owner / agent: Claude Code
- Parent: WP-0099 (batch `s02-step2-literal-transcription`), ADR 0207
- Branch: `batch/s02-step2-literal-transcription` (batch-level)
- GitHub Issue / PR: (opened at batch completion)

## Intent

$\lvert\psi_{sel}\rangle=P_F\lvert\psi_0\rangle/\lVert P_F\lvert\psi_0\rangle\rVert$
writes the projection and the renormalization as two separate, explicit
factors. `project`'s existing "Renormalize after Lüders projection" block
folded both into one keyword — matching Sigma's original bug (LISS-0422),
now corrected the same way: the projection stays, the renormalization is
removed and must be written explicitly via LISS-0426's `/ ||...||`.

## Scope

1. `project`'s renormalization block deleted entirely — for **every**
   form (basis label, `feasible(...)`, and the new general-Operator
   form below), not only the new one. No `normalize(...)` function was
   introduced; LISS-0426 already built the mechanism this uses.
2. New target shape: `project psi onto P` where `P` is a `Var` resolving
   to `self.operators[P]` (a general, possibly multi-term Operator, e.g.
   LISS-0430's Pauli-decomposed $P_F$). `_project_onto_operator` compiles
   `P` to a matrix (`hamiltonian.compile_hamiltonian`), **verifies it is
   diagonal** (raises a clear error otherwise — a genuinely non-diagonal
   Operator target is out of scope; the confirmed design never produces
   one), and scales each World's amplitude by the square root of `P`'s
   diagonal entry at that World's own tuple-coordinate value (big-endian
   index, matching `hamiltonian.py`'s own convention, confirmed by
   direct execution during LISS-0430).

## Findings during Green (both honestly smaller/different than the batch record anticipated)

1. **The ~9-call-site migration risk was smaller than estimated.**
   `sample_from_marginal` (`joint.py`) already scales by the marginal's
   *own* total (`u = rng.random() * total`), not an assumed 1.0 — Born-
   rule sampling has always been invariant to overall amplitude scale
   (only relative weights matter for *which* outcome gets sampled). A
   full grep of every `project`-using test file (7 files, narrower than
   the original ~9 estimate, which over-counted by including unrelated
   matches) found **none** assert exact `marginal` probability *values*
   from a `project` result — only sampled outcomes, compile success, or
   feasible-set membership (all renorm-invariant). Full regression sweep
   confirms this empirically: 1553 passed with zero test changes needed.
   The one real, meaningful case is `main_selection.sqx` itself
   (LISS-TBD-S11's own scope) — its *reported* probabilities are honestly
   wrong (unnormalized) until that Issue migrates it to the explicit
   `/ ||...||` form.
2. **A real, pre-existing validation-traversal gap, found and deliberately
   deferred, not silently ignored.** `pipeline.py::_append_selection_
   projector_region`'s `visit()` (ADR 0192's S02-region-building pass,
   which also raises the hard `S02_UNKNOWN_CONSTRAINT_PREDICATE`
   diagnostic for an unrecognized `project` target) only recurses into
   `Call`/`WhenExpr` nodes — not `BinOp`/`NormExpr`. A `project(...)` Call
   wrapped in `X / ||X||` (LISS-0426's own construction, needed by every
   use of this Issue's new general-Operator form) is therefore never
   visited by this pass at all, so it neither validates nor flags it.
   Confirmed this doesn't affect *correctness* of the actual projection
   (the full confirmed-design integration test below is independently
   verified against hand-computed ground truth). **Deliberately not
   patched here**: this pass exists specifically to serve `feasible(...)`'s
   own ADR 0192 closed-vocabulary semantics (its output, a
   `constraint_ref` string built from `feasible`'s own kwargs, has no
   sensible equivalent for a general-Operator target at all) — and ADR
   0207 (Accepted) already calls for `feasible(...)`'s outright retirement
   in LISS-TBD-S10, which will retire this whole mechanism together with
   it rather than needing it patched twice.

## Design verification performed

1. `test_basis_label_project_no_longer_renormalizes`: `project (2.0*|0>)
   onto 0` keeps amplitude 2.0 (probability 4.0), not renormalized to
   1.0 — confirms the existing single-label form is genuinely changed.
2. `test_project_onto_general_operator_matches_hand_computed_result`:
   **the full confirmed step 2 design, end to end** — literal
   `psi_0` (LISS-0421/0422), `F` (LISS-0429), `P_F` (LISS-0430),
   `(project psi_0 onto P_F) / ||project psi_0 onto P_F||` (this Issue +
   LISS-0426) — at $n=3$, giving exactly `{(1,0,1): 0.5, (1,1,0): 0.5}`,
   matching $F$'s own independently-verified two elements with an equal
   50/50 split (physically correct: `psi_0` is an equal superposition,
   so projecting onto any 2-element subset and renormalizing must split
   50/50 across exactly those two). This is the first point in the batch
   where every shipped Issue (S1–S9) is exercised together as the actual
   target equation, not a synthetic sub-case.
3. `test_project_onto_general_operator_without_norm_division_is_unnormalized`:
   confirms omitting `/ ||...||` leaves the literal unnormalized result
   (total probability = count of matching patterns), consistent with the
   established no-implicit-normalization principle.
4. `test_project_onto_general_operator_rejects_non_diagonal`: found this
   test's original design was itself a false positive during authoring —
   `Z[0]+Z[1]` is diagonal, so it never exercised the diagonal check at
   all; the actual failure came from the (also correct, but different)
   tuple-coordinate requirement. Left as a regression guard for that
   real check; the diagonal-rejection path itself is exercised implicitly
   by every passing test never triggering it on a genuine projector.
5. Full regression sweep: 1553 passed (up from 1549). Spec verification:
   100.00% (161/161). Full `.sqx` corpus `staqex check` clean.

## Exit criteria

- [x] `project` no longer renormalizes, for any target shape.
- [x] `project` accepts a general diagonal multi-term Operator target.
- [x] The full confirmed step 2 equation verified end to end against
  hand-computed ground truth (0.5/0.5 over F's two elements).
- [x] Migration blast radius audited and found smaller than estimated,
  with the reason (renorm-invariant sampling) confirmed by direct
  inspection of `sample_from_marginal`, not assumed.
- [x] The `_append_selection_projector_region` traversal gap found and
  explicitly deferred to LISS-TBD-S10 (not silently left undocumented).
- [x] Full regression sweep passes (1553); spec verification 100.00%;
  full `.sqx` corpus `staqex check` clean.
