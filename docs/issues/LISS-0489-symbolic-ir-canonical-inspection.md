# LISS-0489: Symbolic IR canonical inspection migration

| Field | Value |
|---|---|
| Status | **architecture-approved — awaiting Phase 1 Red approval** |
| Phase | phase-0-architecture-design |
| Parent | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| Related Issues | [LISS-0488](LISS-0488-physics-ir-canonical-projection.md), [LISS-0447](LISS-0447-residual-semantic-consumer-reconciliation.md) |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0489-symbolic-ir-canonical-inspection-migration) |
| Existing authority | [Scientific Semantic Core](../specs/staqex-scientific-semantic-core.md#acceptance-corpus-and-artifact-rules), ADR 0211 |
| Architecture approval | Approved by Adjudicator 2026-08-31; ADR 0211 boundary retained |
| Implementation permission | None; Phase 1 Red test creation is not yet approved |
| Next approval | Phase 1 Red approval |

## Design intake

- Scope: replace the non-explicit `symbolic_ir` AST walk used for inspection
  with the compile-owned `SemanticInspectionResult` built from
  `ScientificSemanticIR`.
- Included context: `symbolic_ir.py`, `pipeline.py`,
  `scientific_semantic_ir.py`, the symbolic-expression Spec, ADR 0211, WP-0107,
  and the existing symbolic/inspection acceptance tests.
- Omitted context: finite QASM, Algorithm Plan, evaluator execution,
  continuous numerical lowering, provider/QPU/AWS, Rust, and solver work.
- Routing: architecture review plus deterministic authority/provenance tests;
  no external provider or AI output is involved.
- Applicable lesson: canonical authority must be observable and legacy
  compatibility must be explicitly diagnostic-only; no hidden AST rebuild is
  allowed.

## Objective

Make exact/symbolic inspection consume one compile-owned canonical semantic
snapshot. Preserve the existing `symbolic_ir` shape only as a compatibility
view where existing consumers require it, and mark it as derived inspection
data rather than a semantic authority. Inspection must not collapse state,
allocate finite resources, create gates, or imply approximation.

## Current boundary and problem

`build_symbolic_ir(unit)` walks `CompilationUnit` and AST/operator DTOs directly,
while the pipeline also exposes `semantic_inspection` from
`ScientificSemanticIR`. This creates two inspection paths with potentially
different node identity, provenance, binder handling, and approximation slots.
Output equality is insufficient evidence because the old walk can produce
plausible text while bypassing canonical source meaning.

## Proposed boundary

```text
CompileResult.scientific_semantic_ir
        │
        ├── build_inspection(core) -> SemanticInspectionResult  (authority)
        │
        └── compatibility_symbolic_view(inspection, core)      (derived only)
```

- `build_inspection()` remains the canonical exact/symbolic inspection
  projection and owns source node IDs, structure, role lanes, type/dimensions,
  exactness, and intent.
- `symbolic_ir` must be generated from that projection or be absent; it must
  not call `build_symbolic_ir(unit)` as a second semantic build.
- Existing dictionary fields (`kind`, `operators`, `provenance`, `resolved`)
  may remain during a bounded compatibility window, but must carry canonical
  source IDs and an explicit derived/inspection role.
- If canonical meaning is unresolved, the compatibility view contains no
  executable or finite artifact and retains the canonical rejection evidence.

## Acceptance scenarios for Phase 1 Red

1. Given a compiled symbolic program, when inspection is requested, then
   `semantic_inspection.source_node_ids` and the compatibility view's source
   IDs are identical and come from the same compile-owned semantic object.
2. Given a monkeypatched legacy `build_symbolic_ir`, when compile and inspect
   are run, then the legacy AST walk is not used as semantic authority.
3. Given a binder, indexed operator, mapping, or discretization source, when
   inspection is built, then its canonical structure and provenance survive;
   no output-only equivalence assertion is sufficient.
4. Given exact/symbolic input without source-visible `Realize`, when
   inspection is built, then allocation, finite plan, gate sequence, and
   collapse record are absent.
5. Given unresolved or unsupported canonical meaning, when inspection is built,
   then no partial finite/executable artifact is published and the diagnostic
   source node IDs remain available.
6. Given two inspections of one compile result, when both are requested, then
   object identity/fingerprint is stable and the canonical semantic build is
   not repeated.

## Phase split and allowed files

- Phase 1 Red: add only the fixed acceptance tests, one representative
  symbolic-inspection fixture if needed, and Issue/Spec/WP/review records.
  No production migration or deletion.
- Phase 2 Green: wire `semantic_inspection` through the local inspection and
  compatibility surfaces with the smallest canonical adapter; preserve only
  tested dictionary compatibility.
- Phase 3: retire the direct AST walk after no-bypass, source-ID, no-allocation,
  and unchanged-neighbor evidence; update deprecation and documentation.

Initial Phase 1 candidate files:

- `tests/test_liss_0489_symbolic_ir_canonical_inspection_red.py`
- `tests/fixtures/semantic_core/symbolic_inspection.sqx`
- this Issue, the linked Spec/WP, and review/trace records

Production files are not authorized until Phase 1 Red is reviewed and Phase 2
implementation approval is granted.

## Non-goals and stop conditions

This Issue does not define a serialized interchange format, numerical solver,
finiteization policy, QASM/QPU behavior, provider integration, Rust runtime,
or broad example rewrite. Stop for a new ADR if canonical inspection requires
new language syntax, changes `Realize`/`Limit` semantics, adds persistence, or
introduces an external execution boundary.

## Architecture approval request

Approve or reject replacing direct `symbolic_ir` AST authority with the
compile-owned `SemanticInspectionResult` boundary, including the derived
compatibility-view window and no-allocation/fail-closed contract. Approval does
not authorize Phase 1 tests or production implementation.

## Architecture approval result

- `SemanticInspectionResult` is accepted as the compile-owned canonical
  inspection projection for this Issue.
- `symbolic_ir` is accepted only as a derived compatibility view during the
  bounded migration; its direct AST walk is not semantic authority.
- The source-ID/provenance conservation, no-allocation, and fail-closed
  contracts are accepted as Phase 1 targets.
- No new ADR, technology choice, provider boundary, or implementation
  permission is created by this approval.

## Phase 1 Red readiness

The exact Phase 1 candidate is fixed to
`tests/test_liss_0489_symbolic_ir_canonical_inspection_red.py` and the
`symbolic_inspection.sqx` fixture named in this Issue. The test batch will
change no production code. Phase 1 Red requires a separate approval before
those files are created.
