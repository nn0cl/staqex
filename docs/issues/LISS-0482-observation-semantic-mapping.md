# LISS-0482: Observation-to-semantic-IR mapping

| Field | Value |
|---|---|
| Status | **Phase 1 Red complete; Phase 2 Green approval required** |
| Phase | phase-1-red |
| Parent | WP-0092 |
| Design authority | [Quantum mental-model follow-up specification](../specs/staqex-v1-quantum-mental-model-follow-up.md#detailed-follow-up-issue-design) |
| Depends on | LISS-0481; ADR 0211 |
| Implementation permission | None |
| Next approval | Typed Phase 2 Green approval |

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
