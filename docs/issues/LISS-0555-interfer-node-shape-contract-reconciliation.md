# LISS-0555: Interfer node-shape contract reconciliation

## Metadata

- Local issue ID: LISS-0555
- GitHub issue: none
- Status: proposed
- Phase: phase-0-design
- Type: semantic-IR test-contract supersession
- Priority: P1
- Initial/current planning size: M / M
- Owner/agent: host implementation; same-context review
- Related branch: `codex/liss-0555-interfer-contract`

## Summary

Update two tests that search for AST-era `kind == "Call"` after the parser
introduced `InterferenceExpr`, while retaining all canonical interference
meaning, operand, phase, branch, and relation evidence.

## Acceptance Notes

- Select by canonical `meaning_kind == "interference"`, not an obsolete syntax
  class, if the accepted parser contract confirms `InterferenceExpr`.
- Preserve `interference_state`, two operand IDs, relative-phase metadata,
  coherent branch relationship, and atomic unsupported QPU rejection.
- Do not convert coherent meaning into classical probability or a generic call.

## Dependencies

- Parent: WP-0161
- Depends on: none
- Blocks: none
- Related: LISS-0478 and current parser interference node

## Adjudicator Decision Points

- Approve syntax-shape supersession while retaining canonical meaning checks.

## Verification

Two active nodes, unsupported projection node, semantic fingerprint, and
neighboring Coin/Mix distinction tests.

## AI Planning Record — AIP-0555-001

- Status/date/size: proposed, 2026-09-11, M
- Route/scope: host; two selectors only unless meaning evidence also fails
- Estimate: N/A; compatible metric unavailable
- Basis/confidence: runtime inspection shows one correct `InterferenceExpr`
  semantic node with preserved metadata; high confidence

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none

