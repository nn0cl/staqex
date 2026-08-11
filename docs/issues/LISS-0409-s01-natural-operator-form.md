# LISS-0409: S01 objective Hamiltonians — natural physicist form

## Metadata

- Local issue ID: LISS-0409
- Status: complete
- Type: Feature Path (examples/showcase only — no compiler/evaluator
  change; LISS-0407 already shipped what this Issue needs)
- Priority: P2
- Planning size: `S`
- Owner / agent: Claude Code
- Parent: follow-on to [LISS-0407](LISS-0407-operator-resolution-unification.md)/
  [LISS-0408](LISS-0408-s02-natural-objective-form.md)
  (Adjudicator-requested: "他に気になるところはある？S01は更新されてい
  る？" → S01 has the same `H_raw`/`H` two-step pattern LISS-0408 removed
  from S02 → "最新の言語でブラッシュアップして")
- Branch: `feature/liss-0409-s01-natural-operator-form`
- GitHub Issue / PR: (opened at Completion)

## Intent

S01 was the file that originally established the `Operator H_raw =
f(...); Operator H = scale * H_raw` two-step idiom (LISS-0402 later
confirmed by direct execution that a bare `scale * f(...)` raised
`cannot compile sparse Pauli for OpCall`, and copied S01's own
established workaround rather than inventing a new one). LISS-0407
closed that gap. This Issue removes the now-unnecessary `*_raw`
intermediates across S01, the same way LISS-0408 did for S02.

## Scope

Eight occurrences across four files, collapsed to single-line scaled
Operator binds:

1. `main_day2_recovery.sqx`: `Operator H_raw = recovery_hamiltonian(coeffs);
   Operator H = scale * H_raw` → `Operator H = scale *
   recovery_hamiltonian(coeffs)`.
2. `main_disaster_response.sqx`: four pairs
   (`constraint_hamiltonian(coeffs)`, `damage_hamiltonian()`,
   `corridor_product()`, `flood_zone_sum()`) collapsed the same way.
3. `main_lattice_four.sqx`: two pairs (`damage_hamiltonian_four()`,
   `basis_zone_sum()`) collapsed the same way.
4. `main_morning_collect.sqx`: `Operator H_raw = Z; Operator H = scale *
   H_raw` → `Operator H = scale * Z`. Note this one was never actually
   blocked by the OpCall gap (`Z` is a bare Pauli literal, not a call) —
   simplified for consistency with the other three files, not because it
   was broken.

## Explicitly out of scope

- Any change to physics, coefficients, durations, or evolve policies —
  unrelated to this rewrite.
- Any further compiler change — none needed.
- Any other S01 file or example outside these four — not reviewed for
  further polish opportunities in this Issue.

## Design verification performed

1. **Captured exact `staqex run --seed 0` output for all four files
   before editing**, then diffed against the same command after each
   edit: all four are **byte-identical**, confirming the rewrite changes
   nothing about program behavior.
2. **All four files re-verified with `staqex check`**: no hard compile
   diagnostics.
3. Full regression sweep: 1459 passed (unchanged). Spec verification:
   100.00% (161/161). S01-specific tests (LISS-0344–0348 real-unit
   migration, linker runtime, CNOT multi-wire, tonight-ticket export):
   17 passed.

## Exit criteria

- [x] All eight `*_raw` intermediates removed across the four files.
- [x] Byte-identical `staqex run --seed 0` output confirmed for all four
  files before/after.
- [x] Full regression sweep passes (1459 passed); spec verification
  100.00% (161/161); all S01-specific tests pass (17 passed).
