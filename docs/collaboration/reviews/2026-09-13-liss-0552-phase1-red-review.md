# LISS-0552 Phase 1 Red review packet

## Review Target

- Artifact: six reconciled source fixtures and five focused Phase 1 Red tests
- Current phase: Phase 1 Red, awaiting human test review
- Requested approval: accept the failing-test contract and authorize the next
  distinct Phase 2 Green / Implementation decision
- Approval type: phase
- Approved scope: only LISS-0552's accepted local-compile/finite-projection
  boundary; no provider, deployment, or physical-algorithm scope
- Implementation allowed: no
- Post-review required: yes — Phase 2 requires separate explicit
  implementation approval
- Execution batch ID: none

## Canonical Documents and Files Re-read

- [LISS-0552 specification](../../specs/staqex-local-compile-finite-projection-diagnostic-isolation.md)
- [ADR 0220](../../architecture/adr/0220-local-compile-and-finite-projection-diagnostic-isolation.md)
- [LISS-0552 issue](../../issues/LISS-0552-local-compile-projection-diagnostic-isolation.md)
- [WP-0161](../../work-plans/WP-0161-active-red-remediation.md)
- `tests/test_liss0056_empty_domain_identity_red.py`
- `tests/test_liss0234_dirac_paper_var_sugar_red.py`
- `tests/test_operator_algebra_red.py`
- `tests/test_liss0552_projection_diagnostic_isolation_red.py`
- `docs/testing/active-red-tests.toml`

## What Changed

- Replaced the retired empty-domain Evolve fixture with the accepted explicit,
  dimensioned propagator form; existing warning and identity assertions are
  unchanged.
- Added terminal `tracing_out` only for named residual state carriers in the
  paper-notation and operator-algebra fixtures; AST and runtime assertions are
  unchanged.
- Removed the six formerly failing, now-passing LISS-0552 entries from the
  active-Red exclusion manifest.
- Added five focused contracts: `local_ok`; QSEM advisory diagnostic scope;
  retained linear hard failure; QPU IR semantic-operation conservation; and
  an empty, provenance-bearing QASM rejection envelope.
- Changed no production, adapter, provider, runtime, or deployment file.

## Findings and Dispositions

- Apply: the fixture corrections pass all six original assertions without
  suppressing diagnostics or restoring retired syntax.
- Apply: QSEM diagnostic metadata is independently Red (`KeyError` for the
  absent `severity` field), so Phase 2 cannot hide the missing classification
  behind a new boolean.
- Apply: the QPU IR contract is independently Red (`projection_error` is
  currently `None`), proving operation conservation is not yet enforced at
  the correct boundary.
- Apply: QASM currently emits a successful program for locally valid `inner`
  input. The atomic-rejection test is therefore Red and prevents silent loss
  of the algebraic operation.
- Already closed with evidence: `LINEAR_IMPLICIT_DISCARD` is still observed
  when `tracing_out` is omitted; the new `local_ok` assertion is Red only
  because the name does not yet exist.
- Out of scope: defining a finite inner/outer algorithm, auto-finiteization,
  QASM adapter AST inspection, AWS/provider work, or broad diagnostic type
  migration.

## Deterministic Verification

- Direct affected suite: **17 passed, 5 failed**.
- The 17 passing tests include every one of the six removed active-Red nodes.
- The five failures are exactly the intended unimplemented contracts:
  missing `CompileResult.local_ok` (two assertions), missing QSEM metadata,
  absent QPU IR projection rejection, and non-atomic QASM success.
- Active-Red lifecycle: passed with **11** remaining entries; none belongs to
  LISS-0552.
- Document lifecycle, coverage-ledger consistency, and `git diff --check`:
  passed.

## Isolation and Blocker

- Configured review isolation: `same_context`, which is weaker than a
  separate-context review.
- LISS-0552 is size L; this author/reviewer cannot claim independent approval.
  This packet is evidence for the human Adjudicator.
- Blocker: Phase 2 must not begin until the Adjudicator accepts these Red tests
  and separately grants Green / Implementation permission.

## Adjudicator Checklist

- [ ] The phase is correct.
- [ ] Existing fixture assertions remain authoritative.
- [ ] The five new tests exactly map to ADR 0220 and the accepted spec.
- [ ] The six manifest removals correspond to passing exact nodes.
- [ ] Implementation permission is not inferred.

## Next Approval Required

`LISS-0552 Phase 1 Red テストレビュー承認`
