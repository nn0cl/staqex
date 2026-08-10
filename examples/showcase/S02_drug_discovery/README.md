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
```

## Honesty notes

- SIM-only; no live QPU, no optimality claim.
- The classical baseline and the Kernel program are cross-checked to
  agree on the *feasible set* (same predicates, same manifest) — they are
  not required to pick the same terminal pattern, since the Kernel
  program samples uniformly over the feasible subspace at terminal
  `measure` rather than maximizing the objective before sampling.
- Candidate identity (descriptors, scores, tags) never crosses into the
  Kernel — only the finite width `n` and the Host-computed predicate
  matrices do, per the S02 acceptance spec's own boundary contract.
