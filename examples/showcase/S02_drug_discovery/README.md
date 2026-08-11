# S02 — indication-agnostic drug-discovery selection benchmark

Language expressiveness benchmark, **not** a chemistry, clinical, or
quantum-advantage claim. See
[S02 acceptance specification](../../../docs/specs/staqex-v1-s02-drug-discovery-benchmark.md)
and the [expressiveness review](../../../docs/specs/staqex-v1-s02-expressiveness-review.md)
(Ideal vs Today, 2026-08-10) for the full design record.

## What this program does

`main_selection.sqx` expresses a finite candidate-selection experiment
(8 candidates, select exactly 3) with two deliberately separate quantum
coordinates:

1. **Hard-constraint selection subspace** — `prepare_selection(n)` (equal
   superposition over all `2^n` selection patterns) restricted by
   `project ... onto feasible(exactly_selected = 3, pairwise_compatible =
   true, diversity_at_least = 0.3)`.
2. **Soft-objective evolution** — a separate qubit pair evolved under a
   Hamiltonian built from named weighted terms (`activity`/`selectivity`/
   `diversity`), reusing S01's own energy-scale idiom
   (`Energy scale = 1.0.eV to J`).

These are two coordinates, not one, because `prepare_selection`'s
tuple-valued state cannot itself be evolved under an ordinary Pauli-term
`Operator` — confirmed by direct execution during design (see
[LISS-0402](../../../docs/issues/LISS-0402-s02-selection-example.md)
Design verification point 3). This mirrors S01's own pattern: classical
domain data feeds a Hamiltonian's *coefficients*, it never becomes the
evolved state itself.

`pairwise_compatible`/`diversity_at_least` are `N×N` Host-computed
matrices (ADR 0194 `HostInputPort`) — the Kernel never sees candidate
identity, only the finite width `n` and the terminal selection pattern.

## Run it

```bash
# Local Kernel-only compile check (no Host input -- project ... onto
# feasible(...) needs pairwise_compatible/diversity_at_least at runtime,
# so this only checks compilation, not full execution):
python3 -m compiler.staqex check examples/showcase/S02_drug_discovery/main_selection.sqx

# Full run, with the required HostInputPort data supplied:
python3 examples/showcase/S02_drug_discovery/host/run_selection.py

# Classical baseline (exact brute-force search over all 2^n patterns;
# design doc §7 "Baseline discipline"; cross-checks the same feasible-set
# definition the Kernel program uses):
python3 examples/showcase/S02_drug_discovery/host/classical_baseline.py

# Full multi-shot benchmark report (LISS-0403) -- real baseline/objective/
# reranked scores, resource metadata, and quality metrics (feasibility
# rate, objective gap to the exact baseline, top-k overlap,
# reproducibility), per the S02 acceptance spec's Result contract:
python3 examples/showcase/S02_drug_discovery/host/benchmark_report.py
```

## Honesty notes

- SIM-only; no live QPU, no optimality claim.
- The classical baseline and the Kernel program are cross-checked to
  agree on the *feasible set* (same predicates, same manifest) — they are
  not required to pick the same terminal pattern.
- Candidate identity (descriptors, scores, tags) never crosses into the
  Kernel — only the finite width `n` and the Host-computed predicate
  matrices do, per the S02 acceptance spec's own boundary contract.
- **Architecture fix shipped (LISS-0404/ADR 0205, applied here in
  LISS-0405):** `prepare_selection`'s tuple-valued coordinate can now be
  evolved directly under an ordinary Pauli-term `Operator` (`Z[i]`/`X[i]`
  indexed field terms). `main_selection.sqx`'s `H_obj` now acts on
  `psi_sel` itself — not a disconnected qubit pair — and measurably
  biases the terminal distribution away from uniform-over-feasible
  (verified: per-pattern probabilities range `~1.4e-11`–`~0.0399` across
  the 25 feasible patterns, not the old design's implicit uniform
  `1/25`).
- **Disclosed expressiveness finding (LISS-0405), superseding the old
  LISS-0403 note:** `benchmark_report.py`'s `top_k_overlap` metric still
  measures `0.0` even after the architecture fix above. This is real,
  not a bug, and not the same gap as before: `objective_hamiltonian`
  gives every one of the 8 candidate positions the *same* scalar weight
  (`activity`/`selectivity`/`diversity` are per-run constants, not
  per-candidate), so the bias it produces has no per-candidate structure
  to correlate against `scoring.py`'s independent per-candidate
  `build_candidate_scores` proxy used for `baseline_top_k`. Making the
  two agree would need a further, unshipped mechanism for Host-computed
  *per-position weights* (not candidate identity — the existing boundary
  contract above is unaffected) to enter an `Operator`'s field terms,
  e.g. a `Float[]` bound via `HostInputPort` and indexed into
  `sum (i in Index<0..7>) { w[i] * Z[i] }`. Left open pending direction,
  not worked around ahead of review.
