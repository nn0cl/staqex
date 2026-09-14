# LISS-0555: Interfer node-shape contract reconciliation

## Metadata

- Local issue ID: LISS-0555
- GitHub issue: none
- Status: done
- Phase: done
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

## Phase 0 architecture review record

- Current evidence: the fixture produces one `InterferenceExpr` canonical node
  with `meaning_kind="interference"`, `state_role="interference_state"`, two
  `child_source_node_ids`, relative-phase metadata, a coherent branch
  relationship, and an interference relation.
- The two active-Red selectors are stale AST-shape expectations; they must
  select the canonical meaning node rather than require `kind == "Call"`.
- The fixture currently also reports `INTERFER_INDEPENDENT_STATE_ERROR` and
  finite-projection advisory diagnostics. These are semantic/capability
  evidence, not reasons to weaken the selector or fabricate a QPU artifact.
- Phase 1 Red will update only the selectors and add no new production
  behavior. The unsupported projection atomic-rejection test remains intact.
- Phase 2 Green is expected to be test-only if all canonical fields already
  exist; no semantic rewrite, classical-mixture conversion, or QPU support is
  authorized by this Issue.

## Dependencies

- Parent: WP-0161
- Depends on: none
- Blocks: none
- Related: LISS-0478 and current parser interference node

## Adjudicator Decision Points

- Approve syntax-shape supersession while retaining canonical meaning checks.
- Approve canonical `meaning_kind` selection as the replacement for the stale
  `Call` selector, with current diagnostic and no-artifact behavior preserved.

## Architecture approval request

Approve [ADR 0223](../architecture/adr/0223-interfer-canonical-meaning-selector.md)
and the bounded selector-reconciliation scope. This does not authorize a new
interference realization or Phase 2 implementation.

## Architecture approval result

- Adjudicator approval: `ADR 0223 Architecture / LISS-0555 Phase 0 acceptance
  承認`, received 2026-09-14.
- Canonical `meaning_kind="interference"` selection is accepted as the
  replacement for the obsolete `Call` selector.
- Existing meaning, provenance, diagnostics, and atomic no-artifact behavior
  remain mandatory.
- Next gate: `LISS-0555 Phase 1 Red 承認`.

## Phase 1 Red result

- Replaced the two obsolete `kind == "Call"` selectors with canonical
  `meaning_kind == "interference"` selectors.
- Preserved all meaning, operand identity, phase metadata, branch relationship,
  relation, and atomic unsupported-projection assertions.
- Direct verification: **3 passed**, with no collection errors.
- No production implementation changed.
- Next gate: `LISS-0555 Phase 2 Green / Implementation 承認`.

## Phase 1 Red review result

- Adjudicator approval: `LISS-0555 Phase 1 Red テストレビュー承認`,
  received 2026-09-14.
- The canonical selector correction and preserved meaning/rejection
  assertions are accepted.
- No production implementation is indicated by the current evidence.
- Next gate: `LISS-0555 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation result

- Adjudicator approval: `LISS-0555 Phase 2 Green / Implementation 承認`,
  received 2026-09-14.
- No production implementation was needed: canonical `InterferenceExpr`
  already satisfies the approved meaning, operand, phase, branch, relation,
  and unsupported-projection contracts.
- Verification: interfer, Coin/Mix, mixture-plan, and interference-prune
  suites **20 passed**; `py_compile`, lifecycle, coverage, and `git diff
  --check` passed.
- Phase 3 Refactor is limited to readability and final review.

## Phase 3 Refactor result

- Extracted the repeated canonical interfer selector into the test-local
  `_interfer_node()` helper.
- No production code, assertion semantics, diagnostic behavior, or QPU
  projection behavior changed.
- Verification: interfer/Coin/Mix/runtime/interference suites **20 passed**;
  `py_compile`, lifecycle, coverage, and `git diff --check` passed.
- Final Adjudicator review is required to close the Issue.

## Final review and completion

- Adjudicator approval: `LISS-0555 Phase 3 最終レビュー 承認`, received
  2026-09-14.
- The canonical selector reconciliation is complete; both active-Red nodes
  are removed from the manifest.
- No production semantic or QPU behavior was changed.

Process review: no operating-contract deviation or operational problem found.

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
