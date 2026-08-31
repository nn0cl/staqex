# LISS-0482: Observation-to-semantic-IR mapping

| Field | Value |
|---|---|
| Status | **done — Phase 3 complete** |
| Phase | phase-3-refactor |
| Parent | WP-0092 |
| Design authority | [Quantum mental-model follow-up specification](../specs/staqex-v1-quantum-mental-model-follow-up.md#detailed-follow-up-issue-design) |
| Depends on | LISS-0481; ADR 0211 |
| Implementation permission | Approved for the reviewed observation mapping slice only |
| Next approval | None for this Issue; dynamic/general mapping requires separate approval |

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

## Phase 1 Red result

- Added the LISS-0482 source-operation to Scientific Semantic IR mapping matrix
  to the authoritative specification.
- Added `tests/test_liss_0482_observation_semantic_mapping_red.py` covering
  required role/lane/provenance evidence and explicit projection-loss behavior.
- No IR mapping implementation, evaluator rewrite, finite artifact generation,
  provider, or QPU behavior was changed.

## Phase 2 Green result

- Added `observation_mappings` to Scientific Semantic IR with explicit role,
  lane, source ID, provenance, exactness, dimensions, projection-loss, and
  finite-artifact fields.
- Implemented the reviewed `Inspect` → `DiagnosticView` and `trace_out` →
  `ReducedState` mappings only.
- Reviewed Phase 1 tests were not modified to pass. LISS-0482 and its
  LISS-0481 dependency suites pass: `6 passed`.
- Evaluator rewrites, storage changes, implicit realization, provider, and QPU
  behavior remain out of scope.

## Phase 3 result

- Re-read the mapping implementation against ADR 0211 and the LISS-0481
  observation contract; no boundary violation or behavior-changing refactor
  was required.
- Confirmed mapping evidence is explicit and finite-artifact generation remains
  disabled. Nested/dynamic/general observation mappings remain separate scope.
- Process review: no operating-contract deviation or operational problem
  found.

## Final verification

- LISS-0482 and LISS-0481 targeted suites: `6 passed`.
- `git diff --check`: passed.
