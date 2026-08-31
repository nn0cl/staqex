# LISS-0484: Broader observation algebra

| Field | Value |
|---|---|
| Status | **phase-2-green — minimum IR implementation passes acceptance tests; Phase 3 approval required** |
| Phase | phase-2-green |
| Parent | WP-0092 |
| Design authority | [Quantum mental-model follow-up specification](../specs/staqex-v1-quantum-mental-model-follow-up.md#liss-0484-broader-observation-algebra-design) |
| Depends on | LISS-0481, LISS-0482, LISS-0483; ADR 0189/0211 |
| Implementation permission | Phase 2 minimum implementation approved; no Phase 3 completion yet |
| Next approval | Typed Phase 3 approval for refactor and same-context review |

## Scope

Define the compiler/IR-level algebra and composition laws for
`Observable<T>`, `Projection<T>`, `Observation<T>`, `DiagnosticView<T>`, and
`MeasurementEnvelope<T>`. Establish operation kind, lane, lineage, exactness,
dimensions, projection-loss, and capability status as explicit evidence.

## Acceptance scenarios

- `expect`, `project`, `inspect`, and `trace_out` remain non-sampling and retain
  source lineage.
- Only terminal Static Kernel `measure` creates a collapse outcome.
- Nested observation composition preserves the outer operation and inner
  projection meaning without coercion.
- Unsupported operation/lane combinations reject explicitly with stable
  capability evidence.
- Repeated observation requests do not silently become tomography or a finite
  artifact.

## Design decisions to settle

- Operation-kind vocabulary and whether it is a closed enum or extensible
  registry.
- Lineage representation and the minimum provenance fields required for nested
  projections.
- Exactness/dimension representation and the meaning of projection loss.
- Composition laws for `expect(project(...))`, `inspect(project(...))`, and
  `trace_out(project(...))`.
- How capability rejection is represented without altering source meaning.

## Exclusions and stop conditions

No general Hilbert-space storage, POVM numerical semantics, tomography shot
estimation, provider SDK, QPU, Rust, or mandatory public source annotations.
Stop for a new ADR if these decisions become necessary or if `State<T>`
semantics change.

## Phase 1 candidate files

Canonical spec algebra section, composition fixtures, role/lane Red tests, and
review record only.

## Phase 1 Red result

- Added `tests/test_liss_0484_broader_observation_algebra_red.py`.
- The tests require operation kind, non-sampling/non-collapse flags, nested
  lineage, projection-loss evidence, and composition evidence in the
  Scientific Semantic IR.
- No compiler or runtime implementation was changed.

## Phase 2 Green result

- Added `ScientificSemanticIR.observation_algebra`.
- Added minimum algebra evidence for `inspect` and `trace_out`: operation
  kind, lane, sampling/collapse flags, lineage, projection loss, finite
  artifact status, and nested composition metadata.
- The four LISS-0484 acceptance tests pass under direct local execution.
