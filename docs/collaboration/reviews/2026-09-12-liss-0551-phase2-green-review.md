# LISS-0551 Phase 2 Green review packet

## Review Target

- Artifact: current-syntax fixture conformance for eight exact active-Red nodes
- Current phase: Phase 2 Green
- Requested approval: accept Green and authorize Phase 3 Refactor
- Approval type: phase
- Approved scope: five test fixtures only; assertions and production code are
  excluded
- Implementation allowed: yes, only for the approved fixture correction
- Post-review required: yes; Phase 3 final review remains separate
- Execution batch ID: not applicable

## Canonical Evidence Re-read

- `docs/specs/staqex-active-red-remediation.md`
- `docs/issues/LISS-0551-current-source-fixture-conformance.md`
- `docs/issues/LISS-0552-local-compile-projection-diagnostic-isolation.md`
- the five approved test files and their git history
- `docs/testing/active-red-tests.toml`

## What Changed

- Removed nine unused, same-scope duplicate `State` declarations from five
  test source strings.
- Preserved every Python assertion and all production source.
- The bounded evolve-until and pipeline associativity nodes now pass and were
  removed from the active-Red manifest.
- Transferred the six remaining exact nodes to LISS-0552 Phase 0. They no
  longer report `DUPLICATE_DECLARATION`; their local/linear/QSEM diagnostics
  remain visible for architecture review.

## Findings and Dispositions

- Apply: git history establishes `Dirac(0)` as the original pipeline input;
  the later ket declaration was migration residue and was removed.
- Apply: helper-only declarations added after already-complete measured values
  were removed instead of creating artificial nested scopes.
- Apply: the six residual failures stay Red under LISS-0552 rather than
  broadening LISS-0551 into compiler or semantic implementation.
- Already closed with evidence: no same-scope duplicate remains in the eight
  source fixtures, and no expected diagnostic/value assertion changed.
- Out of scope: deciding local compile `.ok`, linear ownership consumption,
  retired Evolve syntax, finite evidence, or approximation-obligation policy.

## Residual Diagnostic Inventory

- All six: `QSEM_FINITE_EVIDENCE_MISSING` and
  `QSEM_APPROXIMATION_OBLIGATION_MISSING`.
- Empty Sigma/Pi and explicit-register identity:
  `EVOLVE_HAMILTONIAN_SHORTCUT_RETIRED` and `LINEAR_IMPLICIT_DISCARD` also
  remain.
- Paper inner/outer and operator inner/outer:
  `LINEAR_IMPLICIT_DISCARD` also remains.

## Failure Scenarios Reviewed

- Permitting same-scope redeclaration instead of correcting stale setup.
- Removing or relaxing an assertion together with a duplicate declaration.
- Replacing the historical `Dirac(0)` pipeline input with migration residue.
- Hiding residual diagnostics or leaving them owned by the completed fixture
  scope.

## Verification

- Exact eight-node run after correction: 2 passed, 6 failed as inventoried.
- `DUPLICATE_DECLARATION`: absent from all eight corrected nodes.
- Assertion diff: unchanged; test edits remove source-string declarations only.
- Nearest lexical-scope and the two recovered nodes: 11 passed.
- Full blocking pytest: 2,045 passed, 17 exact nodes deselected.
- Spec Verification: 161/161 passed.
- Active-Red lifecycle: 17 valid entries as of 2026-09-12.
- Document lifecycle and coverage-ledger consistency: passed.
- Changed-test `compileall` and `git diff --check`: passed.

## Isolation

- Review isolation: `same_context`, weaker than `separate_context`.
- Planning size is M, so a same-context packet is permitted but does not replace
  human Adjudicator approval.

## Applied Process Lessons

- Existing active-Red nodes remain the test authority; no duplicate Red tests
  were introduced.
- Residual failures were re-owned with complete diagnostic evidence rather
  than absorbed through scope expansion.
- Issue, work-plan, trace, and lifecycle metadata were synchronized before the
  next gate.

## Next Approval Required

`LISS-0551 Phase 3 Refactor 承認`
