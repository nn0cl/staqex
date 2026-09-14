# LISS-0553: Symbolic compatibility contract reconciliation

## Metadata

- Local issue ID: LISS-0553
- GitHub issue: none
- Status: done
- Phase: done
- Type: test-contract supersession review
- Priority: P1
- Initial/current planning size: M / M
- Owner/agent: host implementation; same-context review
- Related branch: `codex/liss-0553-symbolic-contract`

## Summary

Reconcile LISS-0476's old `compiled.symbolic_ir is None` assertion with the
later accepted LISS-0489 derived compatibility-view contract.

## Canonical design

- `ScientificSemanticIR` remains the sole authority.
- A non-`None` `symbolic_ir` dictionary is a derived inspection compatibility
  view. It is not a second IR, execution plan, finiteization record, or QPU
  authorization surface.
- The view must identify `ScientificSemanticIR` as its authority, preserve the
  compile-owned source identity/fingerprint, and expose no finite plan,
  allocation, gates, or collapse record.
- It must be constructed from the compile-owned canonical projection without
  calling `build_symbolic_ir(unit)` or walking the AST as a semantic source.
- The old absence assertion is replaced only by these positive authority and
  negative-artifact checks. A compatibility view remains temporary until all
  consumers migrate; its final removal is a separate architecture decision.

## Dependencies

- Parent: WP-0161
- Depends on: none
- Blocks: none
- Related: LISS-0476, LISS-0489, WP-0107

## Adjudicator Decision Points

- Confirm LISS-0489 supersedes only the absence assertion, not LISS-0476's
  authority prohibition.
- Confirm the compatibility view's explicit diagnostic-only role and its
  negative authorization contract.

## Phase 0 architecture review record

- Current evidence: the exact active-Red node fails only because ordinary
  compile currently returns a derived compatibility dictionary; the result
  already reports `scientific_semantic_ir` as `execution_authority`.
- Resolution proposed: supersede the `symbolic_ir is None` assertion narrowly;
  retain the compatibility surface with canonical authority, source identity,
  fingerprint, and no-artifact evidence.
- No production behavior, test assertion, or active-Red manifest entry is
  changed by Phase 0.
- Phase 1 Red candidate: update the existing LISS-0476 node and add focused
  negative checks only if the existing LISS-0489 suite does not already cover
  each field. The test must also monkeypatch the legacy builder and assert it
  is not called.
- Phase 2 Green candidate: no new semantic authority; only the smallest
  metadata/accessor wiring needed to make the role machine-checkable.
- Phase 3 candidate: remove redundant compatibility construction or migrate
  remaining consumers only after an inventory and unchanged-neighbor evidence.

## Architecture approval result

- Adjudicator approval: `ADR 0221 Architecture / LISS-0553 Phase 0 acceptance
  承認`, received 2026-09-14.
- The derived diagnostic-only compatibility-view boundary is accepted.
- The old absence assertion may be superseded narrowly; authority,
  provenance, source identity, fingerprint, no-allocation, and no-authorization
  evidence remain mandatory.
- Implementation permission: granted for the approved Phase 2 Green slice only.

## Verification

Run the one active node plus LISS-0489 canonical identity, fingerprint,
no-allocation, no-legacy-builder, and compatibility-role tests. Phase 2 must
also run the nearest symbolic expression, binder, mapping, discretization, and
second-quantized consumer suites. No provider or live-QPU test is required.

## Phase 1 Red result

- Updated the existing LISS-0476 acceptance node to assert the accepted
  derived-view boundary instead of requiring field absence.
- Added one focused negative authorization test requiring explicit false
  permissions for execution, `Realize`, allocation, and QPU projection.
- Direct verification: **1 failed, 4 passed**, with no collection errors.
  The failure is the missing machine-checkable authorization metadata; the
  canonical fingerprint assertion already passes.
- Production source was not changed. The active-Red manifest now points to
  the renamed representative test.
- Phase 1 Red review was approved before Phase 2 Green.

## Phase 1 Red review result

- Adjudicator approval: `LISS-0553 Phase 1 Red テストレビュー承認`,
  received 2026-09-14.
- The five-test contract is accepted: four existing authority/provenance and
  no-artifact checks remain green, and the explicit authorization metadata
  check is the intended Red gap.
- Phase 2 Green/Implementation is the next approval gate.

## AI Planning Record — AIP-0553-001

- Status/date/size: proposed, 2026-09-11, M
- Route/scope: host; one assertion and its replacement evidence
- Estimate: N/A; compatible metric unavailable
- Basis/confidence: direct accepted successor contract; high confidence

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none

## Phase 2 Green / Implementation result

- Adjudicator approval: `LISS-0553 Phase 2 Green / Implementation 承認`,
  received 2026-09-14.
- Added only explicit false authorization metadata to the derived view for
  `execute`, `realize`, `allocate`, and `qpu_projection`.
- Verification: target contracts and LISS-0489/LISS-0500 **15 passed**;
  nearest symbolic/binder/mapping/discretization consumers **35 passed**;
  `py_compile`, `git diff --check`, and lifecycle checks passed.
- Phase 3 Refactor and final review remain separately gated.

## Phase 3 Refactor result

- Extracted derived compatibility authority construction into the private
  `_derived_compatibility_authority()` helper.
- No assertion, public API, dictionary shape, authority value, or execution
  boundary changed.
- Verification: target and nearest consumer suites **35 passed**;
  `py_compile`, `git diff --check`, and lifecycle checks passed.
- Same-context final review is recorded separately; final Adjudicator approval
  is required to close LISS-0553.

## Final review and completion

- Adjudicator approval: `LISS-0553 Phase 3 最終レビュー 承認`, received
  2026-09-14.
- The approved compatibility-view authority boundary is implemented and
  verified. The active-Red node is removed from the manifest.
- No provider, live-QPU, AWS, Rust, S02, or historical document was changed.

Process review: no operating-contract deviation or operational problem found.
