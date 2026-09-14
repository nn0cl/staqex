# LISS-0554: QASM canonical-input fail-closed regression

## Metadata

- Local issue ID: LISS-0554
- GitHub issue: none
- Status: done
- Phase: done
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

## Phase 0 architecture review record

- Current evidence: `QASM3Emitter.emit_unit()` accepts `semantic_ir=None` and
  currently rebuilds `ScientificSemanticIR` from the supplied AST before
  calling `build_qpu_ir()`. The exact active-Red test reproduces the resulting
  QASM artifact.
- Accepted design proposal: reject at the first emitter boundary when the
  canonical projection is absent, before source-shape inspection, routing,
  target metadata, or any allocation-capable path. Return one empty rejection
  envelope with `E_QPU_CANONICAL_PROVENANCE`.
- A supplied projection whose `source_unit_identity` does not match the unit
  remains rejected by the existing provenance guard.
- Public compile/source/path facades remain responsible for passing the
  compile-owned projection. Their accepted byte output is unchanged.
- Phase 1 Red will retain the exact missing-projection node and add only
  source-level/no-call and positive canonical-path evidence if not already
  covered by the existing LISS-0446/LISS-0477 suites.
- Phase 2 Green removes the fallback construction from this entry only;
  `lower_unit_to_circuit` remains available to explicitly approved legacy
  callers and dynamic/CH0 paths remain separate.

## Dependencies

- Parent: WP-0161
- Depends on: none
- Blocks: none
- Related: LISS-0477, LISS-0446, QASM public-entry specification

## Adjudicator Decision Points

- Approve the existing failing node as Phase 1 regression authority and the
  nearest accepted-QASM neighbor set.
- Approve rejection at the emitter boundary before AST inspection and
  allocation-capable work, with `E_QPU_CANONICAL_PROVENANCE` and an empty
  artifact envelope.

## Architecture approval request

Approve [ADR 0222](../architecture/adr/0222-qasm-canonical-input-fail-closed.md)
and the Phase 0 boundary above. This approval grants no Phase 1 test or Phase
2 implementation permission.

## Architecture approval result

- Adjudicator approval: `ADR 0222 Architecture / LISS-0554 Phase 0 acceptance
  承認`, received 2026-09-14.
- The emitter-boundary fail-closed contract and empty rejection envelope are
  accepted.
- Implementation permission: none. Next gate is `LISS-0554 Phase 1 Red
  承認`.

## Verification

One missing-projection rejection, caller-mismatch rejection, public QASM
positive paths, baseline QASM bytes, and allocation_started false.

## Phase 1 Red result

- Reused the existing LISS-0477 missing-projection node and added one
  no-rebuild negative test.
- Direct verification: **2 failed, 3 passed**, with no collection errors.
  The failures prove that raw input currently emits QASM and calls
  `build_scientific_semantic_ir`; the remaining authority/provenance tests
  pass.
- No production implementation was changed.
- Phase 1 Red test review is required before Phase 2 Green.

## Phase 1 Red review result

- Adjudicator approval: `LISS-0554 Phase 1 Red テストレビュー承認`,
  received 2026-09-14.
- The five-test contract is accepted: raw missing-projection rejection and
  no-rebuild are Red; mismatch and canonical provenance remain regression
  evidence.
- Next gate: `LISS-0554 Phase 2 Green / Implementation 承認`.

## Phase 2 implementation attempt — resolved boundary

- Phase 2 Green/Implementation approval was received on 2026-09-14.
- The initial guard exposed a conflict with the accepted LISS-0446 unit-only
  compatibility test.
- Resolution approved by the Adjudicator: the low-level emitter requires an
  explicit canonical projection, while the public unit-only facade may build
  one invocation-local projection and pass it explicitly.
- The LISS-0554 missing-projection test is narrowed to the direct emitter
  boundary; LISS-0446 continues to own facade compatibility.
- Phase 2 may continue under this separated boundary.

## Phase 2 Green / Implementation result

- Adjudicator approval: `LISS-0554 Phase 2 Green / Implementation 承認`,
  received 2026-09-14, with the layered boundary resolution subsequently
  approved.
- `QASM3Emitter.emit_unit()` now rejects missing canonical IR immediately with
  an empty `E_QPU_CANONICAL_PROVENANCE` envelope.
- `OpenQASM3Generator.generate_detailed()` owns the unit-only compatibility
  build, at most once per invocation, and passes the result explicitly.
- Updated the LISS-0446 build-count test to observe the new facade owner.
- Verification: LISS-0554/0477, LISS-0446, LISS-0501, and LISS-0503 **25
  passed**; `py_compile` passed. No provider or live-QPU test was run.
- Phase 3 Refactor and final review remain separately gated.

## Phase 3 Refactor result

- Extracted missing canonical-input rejection into the private
  `_missing_canonical_input_rejection()` helper.
- Simplified the identity check after the explicit `None` guard.
- No QASM output, rejection code, facade behavior, or canonical ownership
  behavior changed.
- Verification: QASM-related regression suite **25 passed**;
  `py_compile`, lifecycle, coverage, and `git diff --check` passed.
- Final Adjudicator review is required to close the Issue.

## Final review and completion

- Adjudicator approval: `LISS-0554 Phase 3 最終レビュー 承認`, received
  2026-09-14.
- The strict direct-emitter boundary and one-shot unit-only facade boundary
  are implemented and verified.
- The active-Red node is removed from the manifest.
- No provider, live-QPU, AWS, Rust, dynamic-QASM, CH0, or historical document
  was changed.

Process review: no operating-contract deviation or operational problem found.

## AI Planning Record — AIP-0554-001

- Status/date/size: proposed, 2026-09-11, M
- Route/scope: host; emitter canonical-input guard only
- Estimate: N/A; compatible metric unavailable
- Basis/confidence: direct code path at emitter fallback; high confidence

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none
