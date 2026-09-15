# LISS-0549 QASM lowering decomposition trace

- Date: 2026-09-15
- Issue/WP: LISS-0549 / WP-0160
- Path: Feature Path
- Phase: Phase 0 design
- Route: host implementation; same-context review

## Phase 0 design intake

- Scope: split the approximately 1,520-line QASM lowerer into profiles,
  preflight, canonical semantic lowering, AST compatibility, evolution, and
  resource families.
- Authority boundary: executable output is produced only from canonical
  Scientific Semantic IR/QPU IR. The AST path remains diagnostic-only and
  cannot authorize or silently finiteize a program.
- Atomicity boundary: preflight rejects before allocation; unsupported inputs
  leave all artifact and allocation fields empty; resource validation cannot
  create semantic meaning.
- Compatibility boundary: `backend.qasm.lower` remains the public facade and
  emitter formatting is untouched.
- Applied constraints: no provider SDK, network, live QPU, Rust, syntax, or
  semantic change.

## Next Safe Action

Request `LISS-0549 Phase 0 acceptance 承認`.

### Phase 0 acceptance review

- Approval received: `LISS-0549 Phase 0 acceptance 承認`, 2026-09-15.
- Same-context review accepted the six-unit graph and the canonical semantic
  versus diagnostic-only AST boundary.
- No blocker found; authority leakage and allocation atomicity are Phase 1
  Red risks.

## Next Safe Action

Request `LISS-0549 Phase 1 Red 承認`.

### Phase 1 Red

- Approval received: `LISS-0549 Phase 1 Red 承認`, 2026-09-15.
- Added four structural tests for family ownership, facade thinness, import
  direction, and canonical lowering/atomicity.
- No production implementation changed; all four tests fail as expected.
- Active-Red ownership is recorded in the lifecycle manifest.

## Next Safe Action

Request `LISS-0549 Phase 1 Red テストレビュー承認`.

### Phase 1 Red review

- Approval received: `LISS-0549 Phase 1 Red テストレビュー承認`, 2026-09-15.
- The four structural tests were accepted as the bounded contract.

### Phase 2 Green

- Approval received: `LISS-0549 Phase 2 Green / Implementation 承認`,
  2026-09-15.
- Added six lowering family entrypoints and a stable `lower.py` facade backed
  by `legacy.py`; relocated import paths were corrected while preserving the
  public surface.
- Verification: structure 4 passed; nearest QASM suite 40 passed with 1
  pre-existing rotation-diagnostic expectation failure; static checks pass.

## Next Safe Action

Request `LISS-0549 Phase 3 Refactor 承認`.

### Phase 3 Refactor review

- Approval received: `LISS-0549 Phase 3 Refactor 承認`, 2026-09-15.
- Same-context review re-read the canonical decomposition documents, public
  facade, six family entrypoints, legacy bridge, structural tests, and
  lifecycle ledgers.
- Accepted bounded disposition: the public facade and explicit family seams
  are complete for this issue; `legacy.py` remains a named compatibility
  bridge, while body-by-body migration is successor scope.
- Verification: structure 4 passed; nearest QASM suite 40 passed with one
  pre-existing rotation-diagnostic expectation failure; compile, diff,
  lifecycle, document, and coverage checks pass.
- No decomposition blocker; live-QPU verification is not applicable.

## Next Safe Action

Request `LISS-0549 Phase 3 最終レビュー 承認`.

### Phase 3 final review and completion

- Final review approval received: `LISS-0549 Phase 3 最終レビュー 承認`,
  2026-09-15.
- LISS-0549 is complete. The public facade, six family ownership seams,
  canonical authority boundary, and atomic preflight contract are recorded as
  verified. The legacy bridge remains explicit successor scope for any future
  body-by-body migration.
- The four LISS-0549 Active-Red entries were removed after completion.
- Process review: no operating-contract deviation or operational problem found.
- No new process lesson beyond the recorded decomposition-boundary lesson.

## Next Safe Action

Request `LISS-0550 Phase 0 acceptance 承認`.
