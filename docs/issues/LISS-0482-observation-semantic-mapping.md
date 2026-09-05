# LISS-0482: Observation-to-semantic-IR mapping

| Field | Value |
|---|---|
| Status | **done — Phase 3 refactor and review complete** |
| Phase | phase-3-refactor-complete |
| Parent | WP-0092 |
| Design authority | [Quantum mental-model follow-up specification](../specs/staqex-v1-quantum-mental-model-follow-up.md#detailed-follow-up-issue-design) |
| Depends on | LISS-0481; ADR 0211 |
| Implementation permission | Granted only for the bounded observation mapping slice |
| Next approval | None for this Issue; broader observation mapping requires a new Issue/phase approval |

## Scope

Map accepted observation concepts to Scientific Semantic IR roles and lanes,
with source IDs, provenance, exactness, dimensions, and projection-loss
diagnostics.

## Acceptance scenarios

- Mapping preserves canonical source identity and provenance.
- Illegal role/lane transitions reject explicitly.
- Observation objects never become implicit finite artifacts.
- Existing terminal and dynamic measurement behavior remains unchanged.

## Exclusions and stop conditions

No evaluator rewrite, storage strategy, provider, or implicit realization.
Stop if the mapping requires changing ADR 0211 or `State<T>` semantics.

## Phase 1 candidate files

Mapping matrix, semantic fixtures, role/lane Red tests, and review records only.

## Phase 1 Red execution record

- Typed approval: user message `LISS-0482 Phase 1 Red 承認`, 2026-09-04.
- Added `tests/fixtures/observation_mapping/observation_operations.sqx` and
  `tests/test_liss_0482_observation_semantic_mapping_red.py`.
- The packet defines mapping expectations for source identity, provenance,
  semantic role, lane, exactness, dimensions, projection loss, and explicit
  rejection of illegal role/lane transitions. It also verifies that mapping
  cannot create an implicit finite artifact.
- Red verification: **5 failed**, with no collection errors. The failures are
  expected because the Phase 2 semantic mapping API is not implemented.
- No evaluator, storage, provider, or State semantics were changed.
- `git diff --check` passed.

Phase 2 Green requires a separate approval and remains limited to the reviewed
mapping contract.

## Phase 2 Green execution record

- Typed approval: user message `LISS-0482 Phase 2 Green 承認`, 2026-09-05.
- Added `compiler/staqex/observation_semantic_mapping.py`.
- The read-only mapper derives `Inspect` and terminal `Measure` entries from
  canonical Scientific Semantic IR, preserving source identity, provenance,
  semantic role, lane, exactness, and dimensions. Illegal role/lane input fails
  closed.
- Observation mapping never creates a finite artifact or provider payload;
  no evaluator, storage, provider, or State semantics were changed.
- Verification: LISS-0482 and neighboring observation/measurement suites
  **17/17 passed**; `py_compile` and `git diff --check` passed.

Phase 3 requires a separate approval and is limited to readability/refactor,
review evidence, and status synchronization.

## Phase 3 closeout

- Typed approval: user message `LISS-0482 Phase 3 承認`, 2026-09-05.
- Refactor: observation role/lane/collapse policy is centralized in immutable
  internal records; node mapping now consumes that policy without changing
  source identity, provenance, or rejection behavior.
- Verification after refactor: mapping and neighboring observation suites
  **17/17 passed**; `py_compile` and `git diff --check` passed.
- Same-context review: `COMPLETE` / `READY`; no blocking finding. Review
  packet: `docs/collaboration/reviews/2026-09-05-liss-0482-phase3-review.md`.
- Process review: no operating-contract deviation or operational problem found.

The bounded mapping contract is complete. Broader observation types,
execution, and provider/real-QPU behavior remain separately gated.
