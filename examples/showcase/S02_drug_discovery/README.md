# S02 — indication-agnostic drug-discovery selection benchmark

Language expressiveness benchmark, **not** a chemistry, clinical, or
quantum-advantage claim. See
[S02 acceptance specification](../../../docs/specs/staqex-v1-s02-drug-discovery-benchmark.md)
and the [expressiveness review](../../../docs/specs/staqex-v1-s02-expressiveness-review.md)
(Ideal vs Today, 2026-08-10) for the full design record.

## What this program does

`main_selection.sqx` expresses a finite candidate-selection experiment
(8 candidates, select exactly 3) on a **single** quantum coordinate,
`psi_sel`:

1. **Hard-constraint selection subspace** — `(1.0/sqrt(2.0^n)) * Sigma (x
   In {0,1}^n) { |x> }` (LISS-0421/0422: `Sigma` is the literal,
   unnormalized ket sum, matching the bare blackboard `Sigma` symbol
   exactly; the explicit coefficient is what normalizes it, mirroring the
   blackboard equation's own separate `1/sqrt(2^n)` prefactor — same
   terminal distribution as the earlier `prepare_selection(n)` primitive
   it replaces). The source then builds the set `F`, the literal projector
   `P_F = Sigma (x In F) { |x><x| }`, and writes the projection plus its
   explicit norm division.
2. **Soft-objective evolution** — `psi_sel` itself evolved under a
   Hamiltonian built from named weighted terms (`activity`/`selectivity`/
   `diversity`), reusing S01's own energy-scale idiom
   (`Energy scale = 1.0.eV to J`).

Earlier designs (LISS-0402/0403) used two disconnected coordinates,
because `prepare_selection`'s tuple-valued state could not yet be
evolved under an ordinary Pauli-term `Operator`. LISS-0404/ADR 0205
shipped Pauli-term Hamiltonian evolution on tuple-valued coordinates, so
LISS-0405 collapsed this back down to `psi_sel` alone — see the Honesty
notes below for the measured effect of that change.

`pairwise_compatible`/`diversity_at_least` are `N×N` Host-computed
matrices (ADR 0194 `HostInputPort`) — the Kernel never sees candidate
identity, only the finite width `n` and the terminal selection pattern.

## Physics ↔ program

Each stage below pairs the actual physics with the exact `main_selection.sqx`
lines that realize it — nothing here is a separate re-derivation, it is the
same program read twice.

### 1. Equal superposition over selection patterns

$\lvert\psi_0\rangle = \dfrac{1}{\sqrt{2^n}}\sum_{x\in\{0,1\}^n}\lvert x\rangle$

```staqex
Int n = 8
State psi_sel = (1.0 / sqrt(2.0 ^ n)) * Sigma (x In {0,1}^n) { |x> }
```

### 2. Project onto the feasible subspace (hard constraint)

$\lvert\psi_{sel}\rangle = \dfrac{P_F\lvert\psi_0\rangle}{\lVert P_F\lvert\psi_0\rangle\rVert}$,
where $P_F=\sum_{x\in F}\lvert x\rangle\langle x\rvert$ projects onto the
feasible set $F$ (exactly 3 selected, pairwise-compatible,
diversity-separated — see `host/finite_boundary.py`/`host/scoring.py` for
how $F$ is defined Host-side).

```staqex
Set F = { ... }
Operator P_F = Sigma (x In F) { |x><x| }
State psi_sel = (project psi_0 onto P_F) / ||project psi_0 onto P_F||
```

### 3. Objective Hamiltonian (soft objective, per-candidate weighted)

$H_{obj} = \mathrm{scale}\cdot\left[w_a\displaystyle\sum_i a_i Z_i \;+\;
w_s\sum_i s_i X_i \;+\; w_d\sum_{i<j} Z_iZ_j\right]$

where $a_i$/$s_i$ are the Host-supplied per-candidate `activity_w`/
`selectivity_w` arrays (ADR 0119 coefficient tensor,
`host/run_selection.py`), and $w_a$/$w_s$/$w_d$ are the named
`ObjectiveWeights` struct fields.

```staqex
fn objective_hamiltonian(w: ObjectiveWeights, n: Int, activity_w: Float[8], selectivity_w: Float[8]) -> Operator {
    Operator z_field = Sigma (i In 0..n-1) { w.activity * activity_w[i] * Z[i] }
    Operator x_field = Sigma (i In 0..n-1) { w.selectivity * selectivity_w[i] * X[i] }
    Operator coupling = Sigma (i In 0..n-1, j In 0..n-1) where i < j {
        w.diversity * Z[i] * Z[j]
    }
    return z_field + x_field + coupling
}
```

### 4. Time evolution under $H_{obj}$

$\lvert\psi_{sel}(t)\rangle = U(t)\lvert\psi_{sel}(0)\rangle,\quad
U(t)=e^{-iH_{obj}t/\hbar}$

`Evolve() { U_t * psi_sel }.run()` *is* this operator-on-ket application.
The generator, duration, and exponential are written explicitly in the
source; `Evolve` is only the execution boundary.

```staqex
Operator H_obj = scale * objective_hamiltonian(weights, n, activity_w, selectivity_w)
Time dur = 0.6.fs
Operator U_t = exp(-i * H_obj * dur / hbar)
State psi_final = Evolve() { U_t * psi_sel }.run()
```

### 5. Terminal measurement (Born rule)

$P(x) = \lvert\langle x\rvert\psi_{sel}(t)\rangle\rvert^2$

```staqex
Measure psi_final
```

For a finite target, the formal blackboard construction and conversion are a
separate target lane; they do not replace the exact local `U_t` lane:

```staqex
Operator U_formal = Limit N -> Infinity {
    (I - i * H_obj * dur / (N * hbar)) ^ N
}
Operator U_qpu = Realize(
    source = U_formal, method = "suzuki", order = 2,
    steps = 8, error_budget = 1e-6
)
```

Note: step 4's $H_{obj}$ contains `X[i]` terms, which do not commute with
step 2's projector $P_F$ — so the terminal distribution is **not**
guaranteed to stay inside $F$. This is a real, disclosed effect (see
"Feasibility-leakage finding" below), not a simplification made for this
side-by-side.

## Run it

```bash
# Local Kernel-only compile check (no Host input -- project ... onto
# Host-supplied predicate matrices are required for full execution, so this
# only checks compilation:
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
- **Per-candidate weight channel shipped (LISS-0406):** `main_selection.sqx`'s
  `H_obj` field terms (`activity_w[i] * Z[i]`, `selectivity_w[i] * X[i]`)
  now carry genuine per-candidate weight, sourced from the exact same
  `scoring.build_candidate_scores` values the classical baseline scores
  against, via a Host-computed `Float[8]` coefficient tensor
  (`host("activity_weights")`/`host("selectivity_weights")`) — LISS-0406
  wired `HostInputPort` into the already-Accepted ADR 0119
  coefficient-tensor path (`Float[N]… = host("key")`), which existed but
  was unreachable from any real `Evaluator` run before this Issue.
  `top_k_overlap` is now **0.33** (up from LISS-0405's `0.0`), confirmed
  reproducible across an independent weight/duration sweep — a real,
  partial improvement, not a strong one: real-time unitary evolution
  under a fixed-duration Hamiltonian is not a scoring/ranking algorithm
  (no QAOA-style tuned cost/mixer alternation is shipped), so no
  particular overlap value was ever guaranteed.
- **Feasibility-leakage finding (LISS-0406), fixed, not just disclosed:**
  `H_obj`'s `X[i]` field terms do not commute with `project onto
  `P_F` projector — `X` flips a candidate's selected bit,
  changing Hamming weight, so real unitary evolution under a Hamiltonian
  containing `X` terms can leak probability mass outside the 25-pattern
  feasible subspace (a `Z`/`ZZ`-only Hamiltonian leaks nothing, being
  diagonal, but also provably cannot change the measurement distribution
  at all — diagonal evolution only adds phases). A non-vacuum terminal
  measurement is therefore **not** unconditionally feasible; the earlier
  assumption that it was held only for LISS-0402/0403's original
  disconnected-objective-qubit-pair design. This is exactly the case the
  S02 acceptance spec's own Constraint and objective contract anticipates
  ("If a penalty Hamiltonian is used, the report must identify it as a
  penalty profile and must not claim that a low penalty guarantees
  feasibility"). `benchmark_report.py` now verifies every non-vacuum shot
  against the real predicates (`scoring.is_feasible`) instead of assuming
  feasibility, reports a real `feasibility_rate`/`infeasible_shots`, and
  excludes infeasible shots from objective/top-k scoring. At the shipped
  weights, 6/20 seeds (0-19) leak.
