# LISS-0365: migrate continuous/grid Hamiltonian bridge evolve tests to real Time units (WP-0096 work unit 7)

## Metadata

- Local issue ID: LISS-0365
- Status/phase: **complete** (2026-08-08) — PR
  [#449](https://github.com/nn0cl/staqex/pull/449) merged, commit
  `bbb5a18`
- Type: test-fixture-only migration (`test_continuous_lowering_red.py`);
  no Kernel source change, no example content
- Priority: P3
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: [WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
  work unit 7
- Parent: [WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0365-continuous-grid-duration-migration`
- GitHub Issue / PR: [#449](https://github.com/nn0cl/staqex/pull/449)
  (merged, `bbb5a18`)

## Design decision

Migrates the 2 `EVOLVE_UNRESOLVED_UNIT_ERROR` failures in
`test_continuous_lowering_red.py` — the position-grid/continuous
Hamiltonian discretization bridge (`theory`/`discretization`/`use ...
as` DSL, `wavepacket(...)` initial states, `X`/`P` as continuous
position/momentum quadrature operators on a finite grid, not Pauli or
Fock atoms).

**WP-0096's own investigation explicitly flagged this work unit's
`K`-scaling identity as unverified** (only the sparse-Pauli path had
been live-checked). Verified here before drafting this Issue: the grid
Hamiltonian path (`evaluator.py`'s `grid_hamiltonians` dispatch) uses
the same `expm_ih` primitive WP-0095 work unit 1 updated to `U =
exp(-iHt/ℏ)` — the identical real-ℏ formula as the sparse-Pauli and
Fock paths. Live-verified end-to-end with the same `K = 1.0545718e-19`
constant: both `_BRIDGE_PROGRAM` (compiled via the discretization DSL)
and `_DIRECT_GRID_PROGRAM` (direct `Operator H_grid = ...`) compile,
run, preserve Born-rule norm (confirmed `sum |amp|² ≈ 1.0` to machine
precision), and their marginals still match each other exactly as
before migration — resolving WP-0096's open question: the same
identity holds for this path too, no different constant needed.

## Per-fixture edits

- `_BRIDGE_PROGRAM`: the `theory HarmonicOscillator { Operator H = 0.5
  * (X * X + P * P) }` coefficient → `5.272859e-20 * (X * X + P * P)`
  (`0.5 * K`); `for 0.1` → `for 0.1.fs`.
- `_DIRECT_GRID_PROGRAM`: `Operator H_grid = 0.5 * (X * X + P * P)` →
  `5.272859e-20 * (X * X + P * P)`; `for 0.1` → `for 0.1.fs`.

Both fixtures receive the identical scale, since
`test_bridge_evolve_matches_direct_grid_hamiltonian` compares their
marginals directly.

No Kernel source change. No example content change.

## Explicitly out of scope

- Any other WP-0096 work unit.
- `test_bridge_lowering_produces_finite_grid_hamiltonian`,
  `test_non_mvp_discretization_contract_is_rejected_at_lowering`,
  `test_lowering_grid_matches_periodic_uniform_abscissae` — none call
  `evolve` to a successful execution (compile-time-only or
  expected-rejection assertions), so none are in the failing set and
  none need editing. Live-verified the coefficient scale does not
  disturb them (unaffected — they don't depend on the coefficient's
  magnitude).

## Acceptance reference

```gherkin
Feature: continuous/grid Hamiltonian bridge evolve tests use real Time units

  Scenario: each migrated test passes with behavior unchanged
    Given the 2 cases in test_continuous_lowering_red.py, migrated with
      the K-scale/`.fs`-duration conversion applied identically to both
      the discretization-bridge and direct-grid fixtures
    When run
    Then each produces the same norm-preservation / marginal-equality
      result as originally intended pre-ADR-0195 (no
      EVOLVE_UNRESOLVED_UNIT_ERROR)
```

## Verification plan for this design intake (not shipped as a test)

Both cases live-verified end-to-end before this Issue was drafted,
including Born-rule norm preservation and the bridge-vs-direct
marginal-equality comparison — resolving WP-0096's flagged open
question about whether the grid path's scaling identity matches the
sparse-Pauli path (confirmed: yes, same `expm_ih` primitive, same
constant). Full `pytest tests/ -q` regression, diffed against the
current baseline (4 failed, 1304 passed), confirming exactly these 2
cases move from FAIL to PASS and nothing else changes.
`spec_verification` expected unchanged (161/161).

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `XS` — 1 file, 2 cases, resolves a previously-open question
  about the grid path's scaling identity via direct verification.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red: confirmed the 2 target cases already fail on `main`
      for the documented `EVOLVE_UNRESOLVED_UNIT_ERROR` reason
      (pre-existing tests, no new test file needed); the other 3 tests
      in the file already passed unchanged.
- [x] Phase 2 Green: both edits applied exactly as planned. All 5
      tests in the file pass, including the norm-preservation and
      bridge-vs-direct marginal-equality checks.
- [x] Phase 3 Refactor: no further code change needed; WP-0096 work
      unit 7 marked complete, resolving its own previously-flagged open
      question about the grid path's scaling identity.
- [x] Full regression: `pytest tests/ -q` → 1306 passed, 2 failed
      (exactly -2 vs. the established 4-failure baseline, confirmed
      via full failure-list comparison — only work unit 8's 2 cases
      remain); `python3 tests/spec_verification/run_all.py` → 161/161
      (100%, Gate: PASS, unchanged); `git diff --check` → clean.

## Non-goals

- Kernel source changes.
- Other WP-0096 work units.
