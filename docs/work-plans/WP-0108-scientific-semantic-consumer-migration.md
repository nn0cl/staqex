# WP-0108: Scientific Semantic Consumer-Wide Migration

| Field | Value |
|---|---|
| Status | **bounded binder canonical-projection slice complete; follow-up boundaries remain separately gated** |
| Issue | [LISS-0445](../issues/LISS-0445-scientific-semantic-consumer-migration.md) |
| Specification | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md) |
| Parent | [WP-0107](WP-0107-scientific-semantic-core.md) / [LISS-0444](../issues/LISS-0444-scientific-semantic-core.md) |
| ADR | [ADR 0211](../architecture/adr/0211-scientific-semantic-core-and-ir-authority.md) |
| Current approval | Design, Phase 1 Red, Phase 2 Green, and binder-slice implementation approved; LISS-0446 implementation not approved |

## Recommended execution order

1. **Design review:** independently review this Issue/Spec/WP against the
   current implementation and perspectives ledger.
2. **Phase 1 Red:** create only migration inventory assertions, canonical
   authority tests, fallback/no-bypass tests, and representative fixtures.
3. **Phase 2 Green:** migrate one consumer slice selected from Red evidence;
   stop if it requires a new architecture decision or changes explicit
   realization semantics.
4. **Phase 3 Refactor:** retire obsolete paths only after independent review,
   full regression, and rollback evidence.

## Allowed scope for the planned Red phase

- `tests/test_liss_0445_consumer_migration_red.py`;
- `tests/fixtures/semantic_consumer_migration/`;
- this WP, the LISS-0445 Issue/Spec, and review/trace records for this Issue;
- no production implementation, deletion, provider, network, S02, or solver.

## Allowed scope for the approved Phase 2 Green slice

- `compiler/staqex/scientific_semantic_ir.py`;
- `compiler/staqex/qpu_ir.py`;
- `compiler/staqex/pipeline.py`;
- `compiler/staqex/backend/qasm/emitter.py`;
- the existing LISS-0445 binder tests and Issue/Spec/WP/trace/review records;
- no Algorithm Plan, H1, ordinary QASM fallback, provider, network, S02, or
  solver migration in this slice.
- Public `emit_openqasm3()` and `codegen_qasm.generate_detailed()` facades are
  explicitly deferred; they require a separate QASM-entry migration Issue so
  their compile/result ownership can be designed without broadening this
  binder slice.

## Acceptance conditions

- every claimed consumer is reachable from real `.sqx` source;
- the inventory names owner, disposition, phase, and exit/deferral evidence
  for physics, equation, HIR, quantum, symbolic, evaluator, QASM, QPU,
  binder, H1, continuous, and host paths;
- canonical source identity/provenance and structural fields are observable;
- legacy AST/DTO bypass is negatively tested;
- exact/symbolic and finite realization boundaries remain distinct;
- invalid/unsupported paths are fail-closed and artifact-free;
- Red cases cover bare `Limit`, explicit `Realize`, `State<T>`, terminal
  `Measure`, and no-allocation/no-QASM rejection;
- independent review returns READY before Phase 2 Green closeout;
- approval records name paths, phase, exclusions, and next gate.

## Stop conditions

Stop and request Architecture/User judgment if migration requires changing
ADR-0211, source syntax, `Realize`/`Limit` semantics, provider technology,
S02 scope, or the meaning of `State<T>`/terminal `measure`.

## Verification plan

- `.venv/bin/pytest` targeted Red suite;
- canonical provenance and no-artifact assertions;
- unchanged-neighbor regression;
- `git diff --check`;
- independent context review with recorded dispositions;
- Phase 1 Red approval and Phase 2 Green implementation approval are recorded;
  no later slice is implied by this approval.

## Phase 1 Red test inventory

The fixed Red file must test inventory completeness; canonical authority and
negative AST/DTO bypass; diagnostic binder no-relowering; finite/non-finite/
ordinary/unsupported QASM fallback boundaries; bare `Limit` versus explicit
`Realize`; `State<T>` and terminal `Measure` provenance; no-artifact rejection;
and caller-injected/string-only DTO non-authority. Red may fail because these
guarantees are not implemented; that failure does not authorize production
edits.

## Phase 1 Red result

- Added `tests/test_liss_0445_consumer_migration_red.py` and the fixed fixture
  `tests/fixtures/semantic_consumer_migration/ordinary_gate.sqx`.
- `.venv/bin/pytest -q tests/test_liss_0445_consumer_migration_red.py`:
  **5 failed, 7 passed**, no collection errors.
- The failures are intentional migration gaps: the two Algorithm Plan
  representations are still simultaneously executable, diagnostic binder
  calls rebuild the canonical projection, compilation rebuilds the binder
  projection more than once, the H1 early-return bypasses the canonical
  result, and the ordinary QASM fixture still reaches
  `lower_unit_to_circuit()`.
- During Phase 1 Red, no production code, deletion, provider, network, S02,
  or solver change was made. Phase 2 Green implementation is recorded below;
  the historical Phase 1 closeout condition was an independent review.

## Phase 2 Green result — binder canonical projection slice

- `build_scientific_semantic_ir` now builds the finite binder projection once
  and reuses its diagnostics for projection errors.
- `qpu_ir_diagnostics` accepts the compile-owned canonical semantic IR;
  pipeline and QASM diagnostics pass that projection instead of rebuilding it.
- The focused LISS-0445 suite is **9 passed, 3 failed**; the remaining three
  failures are the explicitly excluded Algorithm Plan, H1, and ordinary QASM
  fallback slices.
- Related regression: **27 passed**.
- Full regression: **1659 passed, 3 failed**; the same three excluded Red
  contracts account for all failures.
- The reviewed Red test invocation was minimally updated to pass the
  compile-owned canonical IR into the diagnostic API; its assertions and
  failure contracts were not weakened.
- Direct `QASM3Emitter.emit_unit(..., semantic_ir=...)` canonical sharing is in
  scope. Public convenience facades that do not retain the compile-owned IR
  are a documented follow-up boundary, not a hidden completion claim.

## Phase 2 Green closeout

- Binder canonical projection slice: **complete** after independent review.
- LISS-0446 tracks the deferred public QASM facade ownership boundary; it is
  parked and has no implementation authorization.

## Phase 3 Refactor closeout

- The approved binder slice retains one compile-owned canonical
  `ScientificSemanticIR` projection for QPU/QASM diagnostics.
- No additional production refactor was required; Algorithm Plan, H1,
  ordinary QASM fallback, and public facade migration remain excluded or
  parked boundaries.
- Phase 3 is `final-review-ready` pending completion-record review.

## Completion synchronization

- LISS-0445 bounded binder slice: **done** after same-context completion review.
- Verification: the fixed consumer-migration suite is **12 passed**;
  `git diff --check` passed.
- Current Next Issue: LISS-0446 public QASM facade ownership remains parked
  until its separate phase is approved; LISS-0503 unsupported-evolution
  rejection is complete. No provider, live-QPU, S02, or solver work is opened.
