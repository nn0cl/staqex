# AI Work Trace: WP-0127 test failure recovery

## Request

- Date: 2026-09-04
- User request: Establish a work plan for the failing tests, split the work into issues, and begin correction.
- Current phase: Phase 3 review for LISS-0504; Phase 1/2 preparation for LISS-0505.
- Canonical issue or work plan: `docs/work-plans/WP-0127-test-failure-recovery.md`.
- AI planning record: AIP-0127-0504-001 through AIP-0127-0509-001.

## Context Ledger

- Included: the 13 failures observed in the full pytest run, current specifications, affected tests and runtime/IR code.
- Omitted: AWS real-device execution, Rust work, unrelated historical failures outside this WP.
- Assumptions: current accepted Scientific Semantic IR migration contracts take precedence over retired AST/symbolic authority expectations.
- Open decisions: whether each remaining failure is an implementation regression or a stale test contract will be decided per Issue before changing assertions.

## Routing

- Model/assistant/tool: host agent and deterministic pytest/source inspection.
- Reason: local runtime and test-contract recovery; no AI-generated runtime output.
- Privacy constraints: no secrets or external provider data.

## Execution

- LISS-0504 Red reproduced: stale assertion expected discretization provenance in legacy `symbolic_ir`.
- Disposition: update the test to assert the authoritative `compiled.discretization_bridges` already checked by the same test; do not restore a parallel symbolic authority.
- Result: targeted LISS-0504 tests pass (4/4); Issue moved to review, next Issue is LISS-0505.

## Verification

- `pytest -q tests/test_continuous_discretization_red.py`: 4 passed.
- Earlier WP baseline: spec verification 161/161; full pytest exposed 13 unrelated-to-Braket failures before interruption.
- `git diff --check`: passed.

## Changed Files

- `docs/work-plans/WP-0127-test-failure-recovery.md`
- `docs/issues/LISS-0504-continuous-discretization-provenance.md`
- `docs/issues/LISS-0505-inspect-deferred-pushforward.md`
- `docs/issues/LISS-0506-jordan-wigner-provenance.md`
- `docs/issues/LISS-0507-linked-operator-factory-runtime.md`
- `docs/issues/LISS-0508-free-function-struct-argument-binding.md`
- `docs/issues/LISS-0509-measurement-mixed-dispatch.md`
- `tests/test_continuous_discretization_red.py`

## Next Safe Action

Review and resolve LISS-0505 by comparing its deferred/eager expectations with the current observation contract before modifying runtime behavior.
