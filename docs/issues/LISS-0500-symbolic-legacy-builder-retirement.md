# LISS-0500: Symbolic legacy-builder retirement

| Field | Value |
|---|---|
| Status | **phase-3-refactor-complete** |
| Phase | phase-3-refactor-complete |
| Parent | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| Predecessor | [LISS-0499](LISS-0499-evaluator-dynamic-lane-plan.md) |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0500-symbolic-legacy-builder-retirement) |
| Scope approval | User approved continuation on 2026-09-02 |
| Architecture approval | Existing LISS-0489 canonical inspection boundary |
| Phase 1 Red approval | User approved continuation on 2026-09-02 |
| Implementation permission | Phase 2 Green and Phase 3 refactor approved by user |
| Next approval | Next consumer migration Phase 1 Red |

## [DESIGN CHECK]

- **Scope and expected behavior:** remove the direct legacy AST builder from
  the canonical symbolic compatibility-view path while preserving the explicit
  legacy API for separately controlled callers.
- **Specifications and files inspected:** WP-0107, LISS-0489, LISS-0499,
  migration Spec, `symbolic_ir.py`, pipeline wiring, canonical inspection,
  readiness, and process lessons.
- **Component boundaries:** Scientific Semantic IR owns meaning; symbolic
  compatibility is a derived view. The legacy dictionary cannot rebuild
  canonical meaning or authorize allocation/finiteization.
- **Applicable constraints:** Phase 1 Red only; no provider/QPU/AWS, Rust,
  finite target, solver, or public API deletion.
- **Decisions and ambiguities:** explicit direct callers of `build_symbolic_ir`
  are not removed in this slice. The canonical compatibility view must be
  rebuilt from canonical nodes; unresolved and finite consumers remain gated.
- **Verification plan:** test no legacy-builder bypass, canonical identity
  conservation, no finite artifact, and explicit legacy API isolation.

## Acceptance scenarios for Phase 1 Red

1. Given a compile-owned Semantic IR, when the symbolic compatibility view is
   built, then `_build_symbolic_ir_legacy` is not called.
2. Given that view, then canonical authority and all canonical source node IDs
   are conserved.
3. Given exact/symbolic inspection without `Realize`, then no finite plan or
   allocation artifact is created.
4. Given an explicit legacy API caller, then the compatibility API remains
   isolated and callable until a separate retirement decision.

## Phase boundary

Phase 1 adds only the failing acceptance contract. Phase 2 will derive the
compatibility view from canonical IR with the smallest stable dictionary shape.
Phase 3 may retire obsolete direct-builder paths only after no-bypass and
unchanged-neighbor evidence.

## Phase 1 Red result

- Added `tests/test_liss_0500_symbolic_legacy_builder_retirement_red.py`.
- Red verification: **1 failed, 3 passed**, with no collection errors. The
  failure proves the canonical compatibility view still invokes the direct
  legacy AST builder.
- No production implementation was changed in this phase.

Human review of the Red contract is required before Phase 2 Green.

## Phase 2 Green result

- Rebuilt `build_symbolic_compatibility_view()` from `ScientificSemanticIR`
  without calling `_build_symbolic_ir_legacy()` or inspecting the AST.
- Added source-derived operator alias/provenance metadata to the canonical IR,
  preserving legacy dictionary keys, canonical source IDs, binder classification,
  and no-allocation evidence.
- Kept explicit `build_symbolic_ir(unit)` available as an isolated legacy API;
  the canonical pipeline does not call it.
- LISS-0500, LISS-0489, and symbolic expression regressions **15 passed**;
  `py_compile` and `git diff --check` passed.
- Mapping/discretization/second-quantized legacy projections and full removal of
  the explicit legacy API remain separate migration units.

## Phase 3 result

- Extracted `_build_canonical_symbolic_payload()` from the compatibility-view
  function, separating stable dictionary construction from canonical authority
  and node attachment.
- Preserved legacy dictionary shape, canonical IDs, operator aliases, binder
  classification, no-allocation evidence, and explicit legacy API isolation.
- Same-context review found no blocking finding.
- Verification: LISS-0500, LISS-0489, symbolic expression, and consumer
  migration regressions **27 passed**; `py_compile` and `git diff --check`
  passed.

Process review: no operating-contract deviation or operational problem found.

Issue complete. The next safe action is a new consumer-migration Phase 1 Red
contract.
