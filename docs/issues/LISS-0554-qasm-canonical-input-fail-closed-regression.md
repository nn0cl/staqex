# LISS-0554: QASM canonical-input fail-closed regression

## Metadata

- Local issue ID: LISS-0554
- GitHub issue: none
- Status: proposed
- Phase: phase-0-design
- Type: compiler/backend regression
- Priority: P0
- Initial/current planning size: M / M
- Owner/agent: host implementation; same-context review
- Related branch: `codex/liss-0554-qasm-canonical-input`

## Summary

Restore the accepted rule that a raw parsed unit without its compile-owned
canonical projection cannot emit QASM. Current emitter code rebuilds
Scientific Semantic IR from the AST and emits an artifact.

## Acceptance Notes

- Preserve the existing failing assertion and rejection code
  `E_QPU_CANONICAL_PROVENANCE`.
- Reject before allocation, gates, QASM text, routing, or target metadata.
- Public compile-to-QASM paths must still pass their canonical projection and
  continue producing byte-identical accepted output.
- No AST fallback or synthetic canonical object is permitted.

## Dependencies

- Parent: WP-0161
- Depends on: none
- Blocks: none
- Related: LISS-0477, LISS-0446, QASM public-entry specification

## Adjudicator Decision Points

- Approve the existing failing node as Phase 1 regression authority and the
  nearest accepted-QASM neighbor set.

## Verification

One missing-projection rejection, caller-mismatch rejection, public QASM
positive paths, baseline QASM bytes, and allocation_started false.

## AI Planning Record — AIP-0554-001

- Status/date/size: proposed, 2026-09-11, M
- Route/scope: host; emitter canonical-input guard only
- Estimate: N/A; compatible metric unavailable
- Basis/confidence: direct code path at emitter fallback; high confidence

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none

