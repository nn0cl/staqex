# LISS-0548 Scientific Semantic IR decomposition trace

- Date: 2026-09-15
- Issue/WP: LISS-0548 / WP-0160
- Path: Feature Path
- Phase: Phase 0 design
- Route: host implementation; same-context review

## Phase 0 design intake

- Scope: decompose the approximately 2,029-line canonical Scientific Semantic
  IR module into model, fingerprint, builder, runtime-plan, QPU-projection,
  and realization families while preserving its public facade.
- Authority boundary: source-derived Scientific Semantic IR remains the sole
  semantic authority; projections and compatibility DTOs cannot execute or
  override source meaning.
- State/build boundary: builder performs the canonical construction sequence;
  QPU projection and realization consume the built core and never rebuild or
  finiteize a second time.
- Consumer boundary: 10 direct production import consumers remain on the
  facade initially and are audited against the pre-change export manifest.
- Applied lessons: compatibility-authority-boundary,
  coverage-authority-boundary, quantitative-traceability, and
  boundary-completeness.
- No provider, network, filesystem, Rust, or language-semantics work is in
  scope.

## Next Safe Action

Request `LISS-0548 Phase 0 acceptance 承認`.

### Phase 0 acceptance review

- Approval received: `LISS-0548 Phase 0 acceptance 承認`, 2026-09-15.
- Same-context review accepted the six-unit dependency graph, stable public
  facade, canonical-build one-time boundary, and 10-consumer audit scope.
- No blocker found; circular imports and duplicate projection construction are
  explicit Phase 1 Red risks.

## Next Safe Action

Request `LISS-0548 Phase 1 Red 承認`.

### Phase 1 Red

- Approval received: `LISS-0548 Phase 1 Red 承認`, 2026-09-15.
- Added four structural tests for family ownership, facade thinness, import
  direction, and canonical build/projection ownership.
- No production implementation changed; all four tests fail as expected.
- Active-Red ownership is recorded in the lifecycle manifest.

## Next Safe Action

Request `LISS-0548 Phase 1 Red テストレビュー承認`.

### Phase 1 Red review

- Approval received: `LISS-0548 Phase 1 Red テストレビュー承認`, 2026-09-15.
- The four tests were accepted as the bounded contract.

### Phase 2 Green

- Approval received: `LISS-0548 Phase 2 Green / Implementation 承認`,
  2026-09-15.
- Added internal family modules, immutable model definitions, and a stable
  facade backed by a compatibility bridge; preserved existing imports and the
  `source_id` call signature.
- Verification: structure 4 passed; semantic-core/consumer suite 50 passed
  with 2 pre-existing QASM expectation failures; compile and diff checks pass.

## Next Safe Action

Request `LISS-0548 Phase 3 Refactor 承認`.

### Phase 3 Refactor

- Approval received: `LISS-0548 Phase 3 Refactor 承認`, 2026-09-15.
- Same-context review re-read the facade, internal family modules, legacy
  bridge, structural tests, and canonical specifications.
- Result: public exports, DTO/function ownership, dependency direction, and
  `source_id` compatibility are preserved. The remaining legacy bodies are
  explicitly successor scope.
- Verification: structure 4 passed; semantic-core/consumer suite 50 passed
  with 2 pre-existing QASM expectation failures; static and lifecycle checks
  passed.

## Next Safe Action

Request `LISS-0548 Phase 3 最終レビュー 承認`.

### Final review and completion

- Approval received: `LISS-0548 Phase 3 最終レビュー 承認`, 2026-09-15.
- LISS-0548 is complete and its four Active-Red nodes were removed.
- Process review: no operating-contract deviation or operational problem
  found; no new lesson was required.
- Successor scope remains explicit: migrate the legacy bodies one family at a
  time with exact semantic snapshots.
