# LISS-0553: Symbolic compatibility contract reconciliation

## Metadata

- Local issue ID: LISS-0553
- GitHub issue: none
- Status: proposed
- Phase: phase-0-design
- Type: test-contract supersession review
- Priority: P1
- Initial/current planning size: M / M
- Owner/agent: host implementation; same-context review
- Related branch: `codex/liss-0553-symbolic-contract`

## Summary

Reconcile LISS-0476's old `compiled.symbolic_ir is None` assertion with the
later accepted LISS-0489 derived compatibility-view contract.

## Acceptance Notes

- `ScientificSemanticIR` remains the sole authority.
- A non-`None` compatibility dictionary is allowed only when it is generated
  from the compile-owned canonical projection and carries authority/source-ID
  evidence with no finite artifact.
- Replace the old absence assertion only if the LISS-0489 no-bypass suite proves
  the stronger boundary; do not revive direct AST semantic construction.

## Dependencies

- Parent: WP-0161
- Depends on: none
- Blocks: none
- Related: LISS-0476, LISS-0489, WP-0107

## Adjudicator Decision Points

- Confirm LISS-0489 supersedes only the absence assertion, not LISS-0476's
  authority prohibition.

## Verification

Run the one active node plus LISS-0489 canonical identity, fingerprint,
no-allocation, and no-legacy-builder tests.

## AI Planning Record — AIP-0553-001

- Status/date/size: proposed, 2026-09-11, M
- Route/scope: host; one assertion and its replacement evidence
- Estimate: N/A; compatible metric unavailable
- Basis/confidence: direct accepted successor contract; high confidence

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none

