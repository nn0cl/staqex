# LISS-0363: migrate Suzuki/Trotter policy evolve tests to real Time units (WP-0096 work unit 5)

## Metadata

- Local issue ID: LISS-0363
- Status/phase: **complete** (2026-08-08) — PR
  [#445](https://github.com/nn0cl/staqex/pull/445) merged, commit
  `77c177f`
- Type: test-fixture-only migration (3 files under `tests/`); no
  Kernel source change, no example content
- Priority: P3
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: [WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
  work unit 5
- Parent: [WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0363-suzuki-trotter-duration-migration`
- GitHub Issue / PR: [#445](https://github.com/nn0cl/staqex/pull/445)
  (merged, `77c177f`)

## Design decision

Migrates the 3 `EVOLVE_UNRESOLVED_UNIT_ERROR` failures in
`test_explicit_trotter_steps_red.py` (1 case),
`test_liss_0270_experiment_surface_profile_red.py` (1 case), and
`test_liss_0280_0288_sugar_red.py` (1 case) — all concern explicit
`using Suzuki(order=..., steps=...)` policy handling, unrelated to the
duration/coefficient migration itself.

Applies the same `K = 1.0545718e-19` (= `ℏ / 1fs`) scale / `.fs`-suffix
conversion as prior work units, live-verified per pattern before
editing:

- `test_explicit_trotter_steps_red.py::test_plain_evolve_still_runs_on_
  the_sv_simulator`: `_PLAIN_EVOLVE`'s `0.5 * I - 0.5 * Z[0]` →
  coefficient swap; `for 100.0` → `for 100.0.fs` (verified the larger
  duration numeral does not overflow the sparse-evolution step-budget
  check, since the `H·t/ℏ` product is identical to the original
  ~50-magnitude value). `_PLAIN_EVOLVE` is shared with two
  currently-passing QASM-emission tests
  (`test_plain_evolve_qasm_emission_is_rejected_not_silently_clamped`,
  `test_plain_evolve_rejection_names_the_fix`) that check for
  `QASM_TROTTER_STEPS_REQUIRED` rejection due to the *absence* of a
  `using Suzuki(...)` clause — QASM emission is a compile-time-only
  lowering pass that never reaches the runtime fail-closed duration
  check, so these are unaffected by the duration format (already
  confirmed as a general pattern in WP-0096's own investigation).
- `test_liss_0270_experiment_surface_profile_red.py::test_experiment_
  profile_omits_package_and_main_wrapper`: `Float J = 1.0`/`Float h =
  0.5` → scaled; `for 0.7` → `for 0.7.fs`.
- `test_liss_0280_0288_sugar_red.py::test_0180_inferred_classical_and_
  operator`: `J = 1.0`/`h = 0.5` (ADR 0180 inferred bind, no explicit
  `Float` annotation) → scaled; `for 0.3` → `for 0.3.fs`.

## Explicitly out of scope

- Any other WP-0096 work unit.
- Any other test in these 3 files (none call `evolve` to a successful
  execution besides the 3 cases above).

## Acceptance reference

```gherkin
Feature: Suzuki/Trotter policy evolve tests use real Time units

  Scenario: each migrated test passes with behavior unchanged
    Given the 3 cases across the 3 files listed above, migrated with
      the K-scale/`.fs`-duration conversion
    When run
    Then each produces the same status result as originally intended
      pre-ADR-0195 (no EVOLVE_UNRESOLVED_UNIT_ERROR)

  Scenario: currently-passing QASM-emission tests sharing a fixture
    with the failing test are unaffected
    Given test_plain_evolve_qasm_emission_is_rejected_not_silently_clamped
      and test_plain_evolve_rejection_names_the_fix
    When run against the modified _PLAIN_EVOLVE fixture
    Then both still pass with identical assertions
```

## Verification plan for this design intake (not shipped as a test)

All 3 edits live-verified in isolation before this Issue was drafted,
including confirming the larger duration numeral (100.0) does not
overflow the step-budget check. Full `pytest tests/ -q` regression,
diffed against the current baseline (11 failed, 1297 passed),
confirming exactly these 3 cases move from FAIL to PASS and nothing
else changes. `spec_verification` expected unchanged (161/161).

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `XS` — 3 files, 3 cases, each pattern independently
  live-verified before editing.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red: confirmed the 3 target cases already fail on `main`
      for the documented `EVOLVE_UNRESOLVED_UNIT_ERROR` reason
      (pre-existing tests, no new test file needed); the other 11
      tests in these 3 files already passed unchanged.
- [x] Phase 2 Green: all edits above applied exactly as planned. All
      19 tests across the 3 files pass.
- [x] Phase 3 Refactor: no further code change needed; WP-0096 work
      unit 5 marked complete.
- [x] Full regression: `pytest tests/ -q` → 1300 passed, 8 failed
      (exactly -3 vs. the established 11-failure baseline, confirmed
      via full failure-list comparison — nothing else changed);
      `python3 tests/spec_verification/run_all.py` → 161/161 (100%,
      Gate: PASS, unchanged); `git diff --check` → clean.

## Non-goals

- Kernel source changes.
- Other WP-0096 work units.
