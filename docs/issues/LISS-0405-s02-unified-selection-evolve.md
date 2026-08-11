# LISS-0405: S02 selection example — unified single-coordinate evolve

## Metadata

- Local issue ID: LISS-0405
- Status: complete
- Type: Feature Path (examples/showcase + Host Python only — no
  compiler/evaluator/hir.py change; LISS-0404 already shipped what this
  Issue needs)
- Priority: P1
- Planning size: `S`
- Owner / agent: Claude Code
- Parent: [WP-0093](../work-plans/WP-0093-s02-language-expressiveness-and-selection.md);
  follow-on to [LISS-0402](LISS-0402-s02-selection-example.md)/
  [LISS-0403](LISS-0403-s02-benchmark-report.md)/
  [LISS-0404](LISS-0404-tuple-coordinate-hamiltonian-evolve.md)
- Depends on: LISS-0404 (complete)
- Branch: `feature/liss-0405-s02-unified-selection-evolve`
- GitHub Issue / PR: (opened at Completion)

## Intent

Rewrite `main_selection.sqx` to use LISS-0404's tuple-coordinate evolve
directly on `psi_sel` — the disconnected `obj0`/`obj1` qubit pair is no
longer needed. Also fixes the disclosed `Z*Z` same-site bug (ADR 0205
Context point 1) as part of the same rewrite, using already-shipped
`Z[i]` indexed syntax.

## Design verification performed before writing

1. **Confirmed the unified design runs end to end and genuinely biases
   sampling.** `objective_hamiltonian` rebuilt using `sum (i in
   Index<0..7>) { Z[i] }` / `{ X[i] }` (field terms, one per candidate
   position) plus `sum (i in Index<0..7>, j in Index<0..7>) where i < j {
   Z[i] * Z[j] }` (all-pairs coupling, 28 terms for `n=8` — genuinely
   distinct site pairs this time, not the old bug's same-site
   collision). `sum`/`Index` binder syntax already shipped (S01's
   `grid/block_costs.sqx`, LISS-0230/0232) — reused unchanged, not
   invented.
2. **Re-tuned weights for the larger 44-term Hamiltonian** (8 `Z[i]` + 8
   `X[i]` + 28 `Z[i]*Z[j]`, vs the old design's 2-3 terms on 2 qubits):
   `activity=0.02, selectivity=0.01, diversity=0.01` keeps `|H*t/hbar|`
   inside the sparse evolution step budget (ADR 0195) — confirmed by
   direct execution; the old design's larger weights (`0.45/0.30/0.20`)
   would overflow at this larger acting space.
3. **Confirmed the terminal distribution is now genuinely non-uniform
   across the 25 feasible patterns** (direct execution: probabilities
   ranging from `~1.4e-11` to `~0.0399`, not the old design's implicit
   uniform-over-feasible sampling) — the objective Hamiltonian now
   demonstrably influences which feasible selection is more likely to be
   measured. This closes the *architectural* half of the
   `top_k_overlap≈0` finding LISS-0403 disclosed (the evolution no longer
   acts on a disconnected qubit pair that cannot influence `psi_sel` at
   all).
4. **`obj0`/`obj1` and the separate `expect(ZZ, obj0, obj1)` diagnostic
   are removed** — no longer meaningful once the objective acts on
   `psi_sel` directly; `expect` on `psi_sel` itself is not substituted in
   this Issue (out of scope, see below) since `expect(Z[i], psi_sel)`-
   shaped diagnostics on a tuple-valued coordinate were not verified
   here.
5. **`top_k_overlap` re-measured after the fix and found unchanged
   (still 0.0), for a different and now-understood reason.** Re-running
   `benchmark_report.py` after the rewrite showed the bias is real (point
   3) but does not raise `top_k_overlap` against `scoring.py`'s
   `baseline_top_k`. Root cause, confirmed by inspecting
   `objective_hamiltonian` itself: `z_field`/`x_field`/`coupling` give the
   *same* scalar weight (`activity`/`selectivity`/`diversity`) to every
   one of the 8 candidate positions — the Hamiltonian has no per-candidate
   term, only a per-position-uniform one. `scoring.py`'s
   `build_candidate_scores` assigns each candidate a distinct
   `(activity, selectivity)` pair that never crosses into the `.sqx`
   source at all (Host-only, by the Explicitly-out-of-scope note below).
   A uniform-weight Hamiltonian has no mechanism to prefer the specific
   candidates `scoring.py` considers strong, so the two rankings have no
   reason to correlate — `top_k_overlap≈0` is the honestly expected
   result of comparing an architecturally-connected but per-candidate-blind
   evolution against a per-candidate-aware classical proxy, not evidence
   the LISS-0404 fix is ineffective. Closing this gap for real would
   require a *further* mechanism for Host-computed per-position weights
   (not candidate identity — ADR 0194's constraint is unaffected) to enter
   an `Operator`'s field terms, e.g. a per-position `Float[]` bound via
   `HostInputPort` and indexed into `sum (i in Index<0..7>) { w[i] * Z[i]
   }`. That is new surface, not exercised or shipped anywhere today —
   out of scope for this Issue; left as a disclosed follow-on question,
   not filed as a new Issue without further direction.

## Scope

1. Rewrite `main_selection.sqx`: `objective_hamiltonian` uses
   `sum`/`Index`/`Z[i]`/`X[i]` over all `n=8` positions; `evolve` acts on
   `psi_sel` directly (`state psi_sel = evolve psi_sel under H_obj for
   dur`); `obj0`/`obj1`/`expect` removed; `measure psi_sel` (no
   `tracing_out` needed — no other linear leftovers remain).
2. Update `host/run_selection.py`/`host/benchmark_report.py`'s resource
   metadata (`objective_qubits` → removed, replaced by
   `objective_acting_space: 8`; Suzuki fields removed since default
   single-step evolution is used, matching the verified working
   configuration).
3. Update regression tests (LISS-0402/0403's own tests) for the new
   source shape where their assertions depended on the old two-coordinate
   design.
4. Re-run the benchmark report and record the new `top_k_overlap` value
   in the Issue/README, honestly, whatever it turns out to be.

## Explicitly out of scope

- Any further compiler/evaluator change — LISS-0404 already shipped
  everything this rewrite needs.
- Re-adding an `expect`-based diagnostic on `psi_sel` — not verified in
  this Issue's design pass; a future Issue if wanted.
- Re-tuning the classical baseline's own scoring weights
  (`scoring.py`'s `build_candidate_scores`) — unrelated to this rewrite,
  left unchanged; the baseline continues to use its own independent
  per-candidate proxy score, not the Kernel Hamiltonian's field/coupling
  weights (the two were never meant to be numerically identical, only to
  agree on the feasible-set definition, per LISS-0403's own design).

## Exit criteria

- [x] `main_selection.sqx` compiles with no hard diagnostics and runs
  end to end producing a non-uniform distribution over the feasible
  subspace (verified: probabilities range `~1.4e-11`–`~0.0399` across
  the 25 feasible patterns, not uniform `1/25`).
- [x] `host/run_selection.py`/`host/benchmark_report.py` updated for the
  new resource metadata shape (`hamiltonian_term_count` replaces
  `suzuki_steps`/`objective_qubits`); full regression passes (1450
  passed).
- [x] `top_k_overlap` re-measured and recorded honestly: **still 0.0**,
  not improved. The evolution genuinely biases `psi_sel` now (previous
  bullet), but `objective_hamiltonian`'s field terms weight every
  candidate position identically, so that bias has no per-candidate
  structure to correlate against `scoring.py`'s independent
  per-candidate `baseline_top_k`. See Design verification point 5 for
  the full root-cause account and the disclosed follow-on question
  (per-position Host-computed weights entering `Operator` field terms —
  not attempted here). The stale `benchmark_report.py` warning text
  (which blamed the old disconnected-qubit-pair design) has been
  corrected to state this actual cause.
- [x] Full regression sweep unaffected outside targeted updates (1450
  passed, `.venv/bin/python -m pytest -q`).
