# LISS-0552: Local compile and finite-projection diagnostic isolation

## Metadata

- Local issue ID: LISS-0552
- GitHub issue: none
- Status: proposed
- Phase: phase-0-design
- Type: architecture / compiler diagnostics
- Priority: P0
- Initial/current planning size: L / L
- Owner/agent: host implementation; same-context review
- Related branch: `codex/liss-0552-projection-diagnostics`

## Summary

Decide whether local source acceptance may fail solely because optional finite
QPU projections lack carrier or approximation evidence. This Issue receives
only residual failures proven after LISS-0551 fixture correction.

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

## Acceptance Notes

- Preserve fail-closed QPU artifact emission and explicit
  `QSEM_FINITE_EVIDENCE_MISSING` / `QSEM_APPROXIMATION_OBLIGATION_MISSING`.
- Separate source/runtime validity from target-projection validity if the
  accepted compile-mode contract requires it; never erase the diagnostics.
- `evolve … until` remains local-runtime capable and static-QPU unsupported.
- Empty identity requires explicit acting-space evidence before execution.

## Dependencies

- Parent: WP-0161
- Depends on: LISS-0551
- Blocks: none
- Related: quantum-semantic-ir contract, ADR 0079, LISS-0056

## Adjudicator Decision Points

- Architecture decision: one compile result with lane-tagged diagnostics versus
  separate compile/projection requests.
- No Phase 1 starts until these six residual nodes and expected `.ok` semantics
  are reviewed and named in an accepted specification.

## Context and Verification

- Included: pipeline hard-code classification and QSEM diagnostic provenance.
- Omitted: provider, SDK, deployment, and automatic finiteization.
- Verify positive local execution, explicit QPU rejection, no partial artifact,
  and unchanged diagnostic evidence.

## AI Planning Record — AIP-0552-001

- Status/date/size: proposed, 2026-09-11, L
- Route/scope: host architecture review; residual nodes only
- Estimate: N/A; compatible metric unavailable
- Basis/assumption/confidence: diagnostics appear across multiple source
  families and may encode a contract conflict; medium confidence

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none
