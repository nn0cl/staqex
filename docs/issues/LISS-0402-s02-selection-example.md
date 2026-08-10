# LISS-0402: S02 end-to-end `.sqx` selection example + classical baseline

## Metadata

- Local issue ID: LISS-0402
- Status: complete
- Type: Feature Path (examples/showcase — no compiler/evaluator change;
  Host baseline is Python)
- Priority: P1
- Planning size: `M`
- Owner / agent: Claude Code
- Parent: [WP-0093](../work-plans/WP-0093-s02-language-expressiveness-and-selection.md)
  Work Unit E (remaining scope: "classical baselines and an end-to-end
  runnable `.sqx` S02 example")
- Related: [S02 expressiveness review](../specs/staqex-v1-s02-expressiveness-review.md)
  (2026-08-10, identified this as the P0 finding — no `.sqx` existed for
  S02 at all)
- Branch: `feature/liss-0402-s02-selection-example`
- GitHub Issue / PR: (opened at Completion)

## Intent

Write the first runnable S02 `.sqx` example, using existing shipped
Kernel surface at maximum density (Adjudicator directive: "S01のように極限
まで言語仕様を利用する形で書いて" — write it using the language
specification to its fullest extent, like S01), plus the classical
baseline Work Unit E also names.

## Design verification performed before writing (grounding, not assumption)

1. **Confirmed `prepare_selection(n)` produces a single tuple-valued Joint
   coordinate**, not `n` separate qubit coordinates (`evaluator.py::_bind_prepare_selection`
   — `joint.bind_split(name, {pattern: weight for pattern in
   itertools.product((0,1), repeat=n)})`). Verified directly: `state psi0
   = prepare_selection(4)` binds one coordinate whose values are 4-tuples.
2. **Confirmed `project psi0 onto feasible(...)` correctly filters that
   tuple-valued coordinate** by re-deriving `n` from a sampled world
   (`evaluator.py:4187-4199`) — ran `prepare_selection(4)` →
   `project ... onto feasible(exactly_selected=2)` end to end; got exactly
   the 6 = C(4,2) equal-weight patterns expected.
3. **Discovered a real, load-bearing incompatibility**: the Ideal
   sketch's `evolve ψ0 |> project onto P |> evolve under H` cannot evolve
   the *same* tuple-valued selection coordinate under an ordinary
   Pauli-term `Operator` — confirmed by direct execution:
   `evolve psi1 under Z` (where `psi1` came from `prepare_selection`)
   raises `KernelError: hamiltonian \`Z\` expects qubit support {0,1}, got
   [(0, 1), (1, 0)]`. Pauli-term Hamiltonians act on ordinary 0/1 qubit
   coordinates, not tuple-valued ones.
4. **Resolved by mirroring S01's own actual pattern, not the Ideal
   sketch's literal single-state-thread reading.** S01's `plan0`/`plan1`
   are ordinary `|0>`/`|+>` qubits evolved under a Hamiltonian *built from*
   classical domain coefficients (`ConstraintCoeffs`) — the domain data
   feeds the Hamiltonian's coefficients, it never becomes the evolved
   state itself. Applying the same split here: the **hard-constraint**
   selection lives in its own tuple-valued coordinate
   (`prepare_selection` → `project onto feasible(...)`); the
   **soft-objective** evolution acts on a *separate*, ordinary qubit pair
   under a Hamiltonian built from named weighted Float terms
   (`activity`/`selectivity`/`diversity`) — exactly the P1 "named
   weighted objective terms" gap the expressiveness review flagged,
   closed here using existing Operator algebra, not new syntax. This is
   arguably a *more* honest reading of the spec's own "hard-constraint
   Projector" vs "soft-objective evolution" distinction than a single
   forced state thread would have been.
5. **Confirmed the energy-scale requirement** (ADR 0195): a raw weighted
   Operator without an explicit energy scale overflows the sparse
   evolution step budget (`|H*t/hbar| ~= 2**63`). Fixed by reusing S01's
   own `Energy scale = 1.0.eV to J; Operator H = scale * H_raw` idiom
   verbatim — not inventing a new scaling convention.
6. **Confirmed a free-fn `Operator`-returning Call cannot be used inline**
   inside a further Operator expression (`scale * objective_hamiltonian(weights)`
   directly raised `cannot compile sparse Pauli for OpCall`) — must bind
   the Call's result to its own named `Operator` variable first, then
   scale it as a separate statement. Matches S01's own two-step
   `H_drive_raw` → `H_drive` pattern exactly; not a new discovery about
   the language, a confirmation that S01's idiom is load-bearing, not
   stylistic.
7. **`pairwise_compatible`/`diversity_at_least` require `HostInputPort`
   data** (ADR 0194) — an `N×N` bool matrix and an `N×N` float matrix,
   keyed `"pairwise_compatible"`/`"diversity_at_least"` in Host settings.
   The `.sqx` file alone cannot supply this; the runnable command and
   README must pass it via `submit_source`/CLI settings, matching the
   `.py` companion. `finite_boundary.py`'s `FiniteManifestWitness` is a
   separate Host input-hygiene check upstream of this (validates the
   candidate manifest before any of these matrices are even constructed);
   this Issue treats it as already-shipped Host code the runner reuses,
   not something this Issue re-implements.
8. **End-to-end run confirmed** (seed 0, `n=6` during design verification;
   final file uses `n=8` per the spec's fixture minimum) — produces a
   real, non-vacuum terminal measurement respecting `exactly_selected`,
   `pairwise_compatible`, and `diversity_at_least` simultaneously.

## Scope

1. `examples/showcase/S02_drug_discovery/main_selection.sqx` — the example
   program described above (`prepare_selection` → `project onto
   feasible(...)` for hard constraints; separate qubit pair evolved under
   a named-weighted-term Hamiltonian for the soft objective; `expect` for
   a non-destructive diagnostic; terminal `measure ... tracing_out ...`).
2. A small Host runner script
   (`examples/showcase/S02_drug_discovery/host/run_selection.py`) that
   supplies the `pairwise_compatible`/`diversity_at_least` `HostInputPort`
   data and runs the program via `submit_source`, matching the shape of
   S01's own `host/*.py` runner scripts.
3. A classical baseline
   (`examples/showcase/S02_drug_discovery/host/classical_baseline.py`):
   brute-force exact search over all `2^n` patterns for the same
   feasibility predicates + objective, per the design doc §7 "Baseline
   discipline" requirement (greedy + exact small-instance baseline) —
   exact search is tractable at `n=8` (256 patterns) and doubles as a
   correctness cross-check for the Kernel program's own feasible-set
   filtering.
4. A short `examples/showcase/S02_drug_discovery/README.md` documenting
   the runnable commands, mirroring S01's showcase README convention.

## Explicitly out of scope

- Any compiler, evaluator, or `hir.py` change — confirmed unnecessary by
  the design-verification runs above; every primitive used is already
  Runtime-real.
- The Kernel-visible finite-witness surface gap (P1 in the expressiveness
  review) — this Issue works around it using the already-shipped bare-`Int`
  `prepare_selection` signature, per the review's own recommendation not
  to invent new Kernel surface ahead of demonstrated need.
- Multi-file package decomposition (S01-style `domain/`/`grid/`/`physics/`
  tree) — kept to one `.sqx` file plus one `struct`/one free-fn, matching
  the S02 spec's own "avoid enterprise ceremony" / "no general-purpose
  collection language" guidance; S02's problem is narrower than S01's,
  and forcing a multi-file split here would not exercise more language
  surface, only add ceremony.

## Exit criteria

- [x] `main_selection.sqx` compiles with no hard diagnostics.
- [x] Runs end to end at a fixed seed with `HostInputPort` data supplied,
  producing a real non-vacuum terminal measurement.
- [x] Terminal measurement respects `exactly_selected`, `pairwise_compatible`,
  and `diversity_at_least` simultaneously (spot-checked against the
  classical baseline's own feasible-set enumeration).
- [x] Classical baseline runs independently and agrees with the Kernel
  program's feasible-set definition (same predicates, same manifest).
- [x] Full regression sweep unaffected (no Kernel files touched).
