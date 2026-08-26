# LISS-0364: migrate Jordan-Wigner mapping evolve tests to real Time units (WP-0096 work unit 6)

## Metadata

- Local issue ID: LISS-0364
- Status/phase: **complete** (2026-08-08) — PR
  [#447](https://github.com/nn0cl/staqex/pull/447) merged, commit
  `800584b`
- Type: test-fixture-only migration (`test_jordan_wigner_mapping_red.py`);
  no Kernel source change, no example content
- Priority: P3
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: [WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
  work unit 6
- Parent: [WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0364-jordan-wigner-duration-migration`
- GitHub Issue / PR: [#447](https://github.com/nn0cl/staqex/pull/447)
  (merged, `800584b`)

## Design decision

Migrates the 4 `EVOLVE_UNRESOLVED_UNIT_ERROR` failures in
`test_jordan_wigner_mapping_red.py`. Each failing test runs **two**
programs and compares their measured marginals: a `FermionOperator`
mapped via `map(H, JordanWigner)`, and a hand-written equivalent
`Operator` expressed directly in Pauli terms. Both sides must receive
the identical `K = 1.0545718e-19` (= `ℏ / 1fs`) scale and `.fs`-suffixed
duration for the comparison to remain meaningful post-migration — a
concern WP-0096's own investigation flagged in advance for this work
unit specifically.

**New syntax constraint found and resolved during design intake**: the
Fermionic side has no existing scalar coefficient to swap (`create[0] *
annihilate[0]`, implicit coefficient 1), and two natural-looking ways
to scale it both fail:
- Wrapping the whole `FermionOperator` RHS in parens
  (`K * (create[0] * annihilate[0])`) hits `PARSE_ERROR: function
  result expression must be the final item in a block` —
  `FermionOperator`-typed binds route through a different grammar path
  than plain `Operator` binds (`_type_first_bind`'s
  `_second_quantized_rhs_is_op_dsl` heuristic), and a leading scalar
  literal is not recognized as starting a second-quantized expression.
- Scaling the already-mapped `QubitOperator` result
  (`K * map(H, JordanWigner)`) hits `SECOND_QUANTIZATION_TYPE_ERROR:
  second-quantized algebra cannot mix Operator and State values`.

**Working form, live-verified end-to-end for all 4 cases (including
the marginal-equality comparison itself)**: prefix the scale directly
onto each term, exactly as the general Pauli-sum case already required
(`K = 1.0545718e-19 * create[0] * annihilate[0]`, no enclosing parens —
mirrors the already-established `K * Z[i] * Z[next(i)]` pattern from
work units 2–5, just applied to the Fermionic ladder-operator grammar
instead of Pauli). For multi-term Hamiltonians, each `+`-separated term
gets its own `K *` prefix (matching how the hand-written side already
distributes its own coefficient across terms).

Also live-verified this does not disturb the 4 currently-passing tests
sharing these same fixture strings: the 4
`test_*_emits_qasm`/`test_*_provenance_*` tests (QASM emission and
`symbolic_ir` provenance are both compile-time-only, unaffected by
runtime duration semantics — confirmed the scaled fixture still
compiles, emits QASM, and records identical provenance).

## Per-fixture edits

- `_NUMBER_OPERATOR_JW`: `create[0] * annihilate[0]` → `1.0545718e-19 *
  create[0] * annihilate[0]`; `_NUMBER_OPERATOR_HAND_WRITTEN`: `0.5 *
  I - 0.5 * Z[0]` → `5.272859e-20 * I - 5.272859e-20 * Z[0]`; both
  `for 1.0` → `for 1.0.fs`.
- `_HOPPING_ADJACENT_JW`: each of `create[0] * annihilate[1]` /
  `create[1] * annihilate[0]` gets a `1.0545718e-19 *` prefix;
  `_HOPPING_ADJACENT_HAND_WRITTEN`: `0.5 * (X[0] * X[1])` / `0.5 *
  (Y[0] * Y[1])` → `5.272859e-20 * (...)`; both `for 1.0` →
  `for 1.0.fs`.
- `_HOPPING_WITH_PARITY_JW`/`_HOPPING_WITH_PARITY_HAND_WRITTEN`: same
  pattern as adjacent hopping, applied to the non-adjacent (`create[0]
  * annihilate[2]`) / Z-string (`X[0] * Z[1] * X[2]`) terms.
- `_TWO_BODY_DENSITY_JW`: `create[0] * create[1] * annihilate[1] *
  annihilate[0]` → `1.0545718e-19 * create[0] * create[1] *
  annihilate[1] * annihilate[0]`; `_TWO_BODY_DENSITY_HAND_WRITTEN`:
  each of the four `0.25 * ...` terms → `2.6364295e-20 * ...`; both
  `for 1.0` → `for 1.0.fs`.

No Kernel source change. No example content change.

## Explicitly out of scope

- Any other WP-0096 work unit.
- The `FermionOperator`/`_type_first_bind` grammar gap that makes
  `K * (create[0] * annihilate[0])` fail to parse — a real, narrow
  parser limitation, but this work unit's established `K *
  <term>`-prefix form works correctly and requires no Kernel change;
  flagged here for a future Issue if it recurs, not fixed now (mirrors
  the "found but not blocking" pattern used elsewhere this session).
- `test_boson_mapping_is_explicitly_diagnosed_not_silently_accepted`
  and the 2 provenance tests — none call `evolve` to a successful
  execution, so none are in the failing set.

## Acceptance reference

```gherkin
Feature: Jordan-Wigner mapping evolve tests use real Time units

  Scenario: each migrated test passes with behavior unchanged
    Given the 4 cases in test_jordan_wigner_mapping_red.py, migrated
      with the K-scale/`.fs`-duration conversion applied identically to
      both the JW-mapped and hand-written sides of each comparison
    When run
    Then each produces the same marginal-equality result as originally
      intended pre-ADR-0195 (no EVOLVE_UNRESOLVED_UNIT_ERROR)

  Scenario: currently-passing QASM/provenance tests sharing the same
    fixtures are unaffected
    Given the 4 emits-qasm/provenance tests
    When run against the modified fixtures
    Then all still pass with identical assertions
```

## Verification plan for this design intake (not shipped as a test)

All 4 cases live-verified end-to-end before this Issue was drafted,
including the marginal-equality comparison itself (not just "did it
run") and the shared QASM/provenance fixtures. Full `pytest tests/ -q`
regression, diffed against the current baseline (8 failed, 1300
passed), confirming exactly these 4 cases move from FAIL to PASS and
nothing else changes. `spec_verification` expected unchanged
(161/161).

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `S` — 1 file, 4 cases, but each requiring careful two-sided
  (JW + hand-written) scaling; a real syntax constraint was found and
  resolved during design intake before Red.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red: confirmed the 4 target cases already fail on `main`
      for the documented `EVOLVE_UNRESOLVED_UNIT_ERROR` reason
      (pre-existing tests, no new test file needed); the other 7 tests
      in the file already passed unchanged.
- [x] Phase 2 Green: all edits above applied exactly as planned
      (the `K * <term>`-prefix form, resolved during design intake,
      worked correctly on the first attempt). All 11 tests in the file
      pass, including the marginal-equality comparisons.
- [x] Phase 3 Refactor: no further code change needed; WP-0096 work
      unit 6 marked complete.
- [x] Full regression: `pytest tests/ -q` → 1304 passed, 4 failed
      (exactly -4 vs. the established 8-failure baseline, confirmed
      via full failure-list comparison — nothing else changed);
      `python3 tests/spec_verification/run_all.py` → 161/161 (100%,
      Gate: PASS, unchanged); `git diff --check` → clean.

## Non-goals

- Kernel source changes.
- Other WP-0096 work units.
