# LISS-0208: 10 test files are unrunnable by the documented invocation

## Metadata

- Local issue ID: LISS-0208
- Status: **proposed** (investigation intake — no Red authorized)
- Phase: phase-0-design
- Type: bug
- Priority: P0
- Planning size: S
- Program: [WP-0069](../work-plans/WP-0069-operations-review-intake.md)
- Related: [`testing-strategy.md`](../architecture/testing-strategy.md)
- Blocks: [LISS-0209](LISS-0209-ci-runs-test-suite.md)

## Intent

[`testing-strategy.md`](../architecture/testing-strategy.md) states that suites
run as plain scripts and that "the repository has no pytest configuration; do
not assume a pytest-only invocation". Ten suites contradict that: five import
`pytest`, five omit the `sys.path` bootstrap every other suite carries. All ten
fail before executing a single assertion.

## Evidence (reproduced 2026-08-01)

**`ModuleNotFoundError: No module named 'pytest'`** (5):

```
tests/test_host_qpu_submit_orchestration_red.py
tests/test_liss0058_acting_space_typing_red.py
tests/test_multi_register_acting_space_red.py
tests/test_qpu_observation_result_integration_red.py
tests/test_simulator_resource_execution_wiring_red.py
```

**`ModuleNotFoundError: No module named 'compiler'`** — missing the
`sys.path.insert(0, _REPO)` prologue used by the other 216 suites (5):

```
tests/test_higher_order_suzuki_green.py
tests/test_liss_0125_hir_binop_expr_children_red.py
tests/test_qft_basic_gate_lowering_red.py
tests/test_qpu_ir_lowering_green.py
tests/test_qpu_ir_lowering_red.py
```

These ten are part of the 50 failing files in the 2026-08-01 sweep, but unlike
the regression clusters they prove nothing about the Kernel — they never ran.

Separate numbering gap found in the same pass: `tests/spec_verification/suites/`
runs `sv01`–`sv11`, `sv13`–`sv31`. **`sv12` does not exist** and no record
explains its absence. Either it was retired without a note or it was dropped.

## Adjudicator decision points

1. Is `pytest` being adopted as a dependency, or must those five suites be
   rewritten as plain scripts to match the stated strategy? The dependency
   choice is a technology selection and needs its own approval
   ([`dependency-policy.md`](../architecture/dependency-policy.md),
   [`external-resource-adoption-contract.md`](../architecture/external-resource-adoption-contract.md)).
2. `sv12`: restore, or record the retirement and renumber nothing?
3. Should the bootstrap prologue be factored into a shared helper rather than
   copied into 220+ files?

## Exit

- [ ] All ten suites execute under the documented invocation
- [ ] pytest question answered explicitly, not by drift
- [ ] `sv12` restored or its retirement recorded
- [ ] Whatever the ten suites then assert is triaged (they may join a
      regression cluster once they actually run)

## Non-goals

Fixing the assertions those suites make once runnable — that is triage output,
tracked against the regression Issues; enabling CI (LISS-0209).
