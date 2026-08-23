# CI test-failure recovery design intake

## Scope

- Branch: `codex/ci-test-failure-recovery`
- Trigger: PR #558 CI run #1178 failed with 16 failures and 1,691 passes.
- Goal: repair the failing test contracts or the production behavior they
  expose, then rerun the full root suite and the spec-verification gate.
- Merge target: none in this batch; the branch is intentionally separate from
  the LISS-0448 completion branch.

## Failure inventory

The failures cross multiple existing contracts:

- explicit Trotter-step policy (`tests/test_explicit_trotter_steps_red.py`);
- LISS-0396 live-QPU CLI fail-closed behavior;
- LISS-0437 explicit-evolution target rejection;
- LISS-0438 and LISS-0443 S02 finite-lane rejection evidence;
- LISS-0444 finite canonical instruction projection;
- function-call, qudit, multi-register, and simulator-resource regression
  contracts.

The first pass must classify each failure as one of:

1. production behavior contradicts an accepted contract;
2. an acceptance test still names a superseded contract and must be migrated
   with its authoritative Issue/Spec; or
3. the failure is outside this recovery batch and must remain a blocker rather
   than being suppressed.

## Design check

- Scope and expected behavior: restore a green, truthful root CI suite while
  preserving the physicist-first canonical semantic boundary and fail-closed
  QPU behavior.
- Specifications and files inspected: `AGENTS.md`, the AT-TDD process,
  independent-review perspectives, LISS-0437/0438/0443/0444/0448 artifacts,
  LISS-0064 resource contract, the failing tests, and the CI job log.
- Component boundaries, ports/adapters, and VO/DTO candidates: no new
  boundary or dependency is proposed. Existing canonical semantic IR, QASM
  emitter/lowerer, CLI delivery path, and resource enforcement boundary remain
  authoritative.
- Applicable constraints: no QPU provider integration, credential use,
  network submission, silent source rewrite, generic `Mix`/`Coin` fallback,
  or CI-test exclusion.
- Decisions, assumptions, and unresolved ambiguities: exact disposition of
  each `_red` test requires the linked Issue/Spec to be checked. A changed
  diagnostic code is not sufficient evidence by itself to rewrite an
  acceptance test.
- Included and omitted AI context: include only the failing test, its direct
  production path, and its authoritative contract; omit unrelated repository
  history and provider integrations.
- Task routing: deterministic local inspection and test execution; no external
  model or provider is required.
- Input/output evidence contract: input is the CI failure and linked contract;
  output is a minimal patch plus test evidence naming the exact failure and
  preserved boundary. No hidden reasoning is recorded.
- Independent review lenses selected: contract completeness, architecture and
  boundary integrity, realization/fail-closed behavior, migration/regression
  safety, canonical authority, projection conservation, and executable
  projection integrity.
- Verification plan: focused test groups first, then `python3 -m pytest
  tests/ -q` in CI-equivalent Python, full spec verification, diff checks, and
  an independent review before any merge decision.

## Phase boundary

This intake does not authorize changing an accepted architecture or hiding
failures from CI. Production fixes or acceptance-contract migrations will be
made only after each failure is mapped to its authoritative Issue/Spec and the
allowed phase is recorded in the subsequent work trace.

## First correction batch

- Restored `SIMULATOR_RESOURCE_ERROR` for QASM resource-budget rejection,
  matching the accepted capability-rejection matrix.
- Made ordinary Measure-only canonical projections executable again and kept
  canonical function calls and plain Hamiltonian Evolve fail-closed with their
  actionable diagnostics.
- Restored static multi-register Hilbert shape precedence over the generic
  semantic projection shape.
- Allowed explicit finite Suzuki policy to reach the existing finite
  exponential lowerer while retaining rejection when no explicit policy is
  supplied.
- Updated LISS-0437/0438/0443 assertions to the accepted current rejection or
  explicit-realization alternatives; no CI test was excluded.

## Deterministic verification

- Focused failure files: passed.
- LISS-0448 focused suite: passed.
- Spec verification: **161/161 (100%)**.
- `py_compile`: passed for touched production modules.
- `git diff --check`: passed.

The full pytest root suite remains the remote CI gate because pytest is not
installed in the local runtime. The branch must be pushed for a CI-equivalent
retry before any merge decision.

## Follow-up correction: dynamic evolve-until boundary

- `.venv` was used to run the CI-equivalent command. The first full run
  reproduced one failure in `tests/test_evolve_until_red.py`: dynamic
  `Evolve ... until converged(...) max N` reached QASM emission as if it were
  a static projection.
- The failure was corrected in `compiler/staqex/backend/qasm/emitter.py` by
  rejecting `until_predicate` before canonical instruction emission with the
  existing `E_QPU_UNSUPPORTED_CAPABILITY` contract.
- Focused verification: `tests/test_evolve_until_red.py` **5 passed**.
- A subsequent `.venv` full-suite run reached **851 passed** with no further
  failure, then was interrupted at the long-running S02 numerical case
  `test_feasibility_leak_is_detected_and_excluded_from_scoring`; this is a
  runtime-duration blocker, not a new assertion failure.

## CI failure follow-up and local closure

- CI run for `d568116e` reported six failures after 1701 passes. The failure
  log showed that the emitter guard had been placed too broadly and that
  Measure-only and finite-target compatibility paths were unintentionally
  changed.
- Corrections were narrowed as follows: user-function rejection is applied
  only when no canonical executable instruction exists; plain non-Fock
  Hamiltonian Evolve requires an explicit Suzuki policy; Fock Hamiltonians
  retain canonical projection rejection; ordinary untyped qubit Measure-only
  programs retain the legacy QASM path; finite target profiles retain their
  accepted realization behavior; canonical gate instructions receive a
  deterministic fallback comment when source provenance has none.
- `.venv/bin/python -m pytest tests/ -q`: **1707 passed**.
- `.venv/bin/python tests/spec_verification/run_all.py`: **161/161 (100%)**.
- `.venv` `py_compile` and `git diff --check`: passed.
