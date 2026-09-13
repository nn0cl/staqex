# LISS-0552: Local compile and finite-projection diagnostic isolation

## Metadata

- Local issue ID: LISS-0552
- GitHub issue: none
- Status: done
- Phase: done
- Type: architecture / compiler diagnostics
- Priority: P0
- Initial/current planning size: L / L
- Owner/agent: host implementation; same-context review
- Related branch: `codex/liss-0552-projection-diagnostics`

## Summary

Decide whether local source acceptance may fail solely because optional finite
QPU projections lack carrier or approximation evidence. This Issue receives
only residual failures proven after LISS-0551 fixture correction.

Canonical proposal:
[local compile and finite-projection diagnostic isolation](../specs/staqex-local-compile-finite-projection-diagnostic-isolation.md).
Architecture proposal:
[ADR 0220](../architecture/adr/0220-local-compile-and-finite-projection-diagnostic-isolation.md).

## Residual Node Intake from LISS-0551

Six exact nodes were received after the approved fixture-only correction:

- empty Sigma warning, empty Pi warning, and explicit-register identity;
- paper-notation inner and outer;
- operator-algebra inner/outer boundary.

All six no longer report `DUPLICATE_DECLARATION`. Every node reports
`QSEM_FINITE_EVIDENCE_MISSING` and
`QSEM_APPROXIMATION_OBLIGATION_MISSING`. The three empty-domain nodes also
report `EVOLVE_HAMILTONIAN_SHORTCUT_RETIRED` and `LINEAR_IMPLICIT_DISCARD`;
the remaining nodes report `LINEAR_IMPLICIT_DISCARD`. Phase 0 must decide the
local-acceptance, linear-use, and target-projection lanes before any expected
`.ok` behavior or implementation is changed.

## Phase 0 Architecture Review Record

- Direct inspection established that the QSEM codes alone are already
  non-hard; all six nodes are currently blocked by linear-use diagnostics.
- Current-source candidates prove that explicit propagator evolution and
  terminal `tracing_out` reconcile the fixtures without softening linearity.
- A neighboring QPU check found that canonical `inner`/`outer` source can emit
  measure-only QASM despite unresolved projection evidence. ADR 0220 assigns
  operation-conservation policy to QPU IR and keeps QASM as a consumer.
- LISS-0554 remains the missing/mismatched canonical-input guard; LISS-0552
  owns present-but-unprojected canonical operations.
- No test or production source changed in Phase 0.

## Acceptance Notes

- Preserve fail-closed QPU artifact emission and explicit
  `QSEM_FINITE_EVIDENCE_MISSING` / `QSEM_APPROXIMATION_OBLIGATION_MISSING`.
- Separate source/runtime validity from target-projection validity if the
  accepted compile-mode contract requires it; never erase the diagnostics.
- Empty-domain fixtures must move from the retired Hamiltonian shortcut to the
  accepted explicit propagator without changing identity assertions.
- Empty identity requires explicit acting-space evidence before execution.

## Dependencies

- Parent: WP-0161
- Depends on: LISS-0551
- Blocks: none
- Related: quantum-semantic-ir contract, ADR 0079, ADR 0212, ADR 0220,
  LISS-0056, LISS-0554

## Adjudicator Decision Points

- Architecture decision: one compile result with lane-tagged diagnostics versus
  separate compile/projection requests.
- No Phase 1 starts until these six residual nodes and expected `.ok` semantics
  are reviewed and named in an accepted specification.

Accepted resolution: one local `CompileResult` with explicit `local_ok` and
tagged advisory evidence, plus a separate authoritative target-projection
request. ADR 0220 Architecture and Phase 0 acceptance were approved on
2026-09-13. `LISS-0552 Phase 1 Red 承認` was received on 2026-09-13.

## Phase 1 Red Record

- The six transferred active-Red fixtures now use the accepted explicit
  propagator and terminal `tracing_out` forms; their assertions were retained
  verbatim and all six now pass.
- The six entries were removed from `active-red-tests.toml`; LISS-0552 no
  longer owns an active-Red exclusion.
- Five focused contracts were added as Red in
  `tests/test_liss0552_projection_diagnostic_isolation_red.py`: `local_ok`,
  QSEM advisory metadata, linear hard behavior through `local_ok`, QPU IR
  operation-conservation rejection, and atomic QASM rejection.
- No production source changed. The Phase 1 test review was approved on
  2026-09-13. `LISS-0552 Phase 2 Green / Implementation 承` was received on
  2026-09-13.

## Phase 2 Green Record

- `CompileResult.local_ok` is the explicit local acceptance signal and `ok`
  remains its compatibility alias.
- The two QSEM obligations are copied to the local diagnostic surface with
  advisory severity, quantum-semantic phase, and finite-projection scope;
  pure lowering diagnostics remain unmutated.
- Canonical `inner`/`outer` operations without an approved finite projection
  now reject in QPU IR with source-node provenance; QASM consumes the
  rejection and emits no artifact or allocation.
- Existing linear hard diagnostics and supported neighboring QPU/QASM behavior
  remain intact.
- Verification passed: direct 22 tests, neighboring 63 tests, and full
  blocking suite 2,056 passed with 11 lifecycle exclusions.
- No provider, live-QPU, or deployment test was performed. Phase 3 remains
  separately gated. `LISS-0552 Phase 3 Refactor 承認` was received on
  2026-09-14.

## Phase 3 Refactor Record

- Consolidated the repeated canonical-projection rejection result construction
  in the QASM adapter into `_projection_rejection`.
- Kept QPU IR as the semantic projection authority; the adapter remains a
  consumer and does not inspect source meaning.
- Preserved diagnostic code, reason, source-node provenance, empty QASM,
  allocation state, and partial-program behavior.
- No test assertion or production behavior was intentionally changed.
- Final review was approved on 2026-09-14.

## Final Review Record

- Approval: `LISS-0552 Phase 3 最終レビュー 承認`, received 2026-09-14.
- Disposition: approved with no remaining blocker for this Issue.
- Completion: LISS-0552 is done; it owns no active-Red manifest entry.

## Context and Verification

- Included: pipeline hard-code classification and QSEM diagnostic provenance.
- Omitted: provider, SDK, deployment, and automatic finiteization.
- Verify positive local execution, explicit QPU rejection, no partial artifact,
  and unchanged diagnostic evidence.

## AI Planning Record — AIP-0552-001

- Status/date/size: phase-3-refactor, 2026-09-14, L
- Route/scope: host architecture review; residual nodes only
- Estimate: N/A; compatible metric unavailable
- Basis/assumption/confidence: diagnostics appear across multiple source
  families and may encode a contract conflict; medium confidence

## Process Review

- Outcome: Phase 3 Refactor and final review complete
- Lesson written: diagnostic scope versus target readiness recorded
- Template-feedback path: none

Process review: no operating-contract deviation or operational problem found.
