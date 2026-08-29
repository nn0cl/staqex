# LISS-0476: Non-explicit `symbolic_ir` consumer migration

| Field | Value |
|---|---|
| Status | **Phase 1 Red complete; Phase 2 Green approval required** |
| Phase | phase-1-red |
| Parent | WP-0107 |
| Design authority | [Scientific Semantic Core](../specs/staqex-scientific-semantic-core.md#consumer-wide-follow-up-design) |
| Depends on | LISS-0445, LISS-0446 |
| Implementation permission | None; Phase 2 Green not approved |
| Next approval | Typed Phase 2 Green approval |

## Scope

Replace direct non-explicit `symbolic_ir` semantic authority in simulator and
inspection consumers with one compile-owned canonical projection. Preserve a
named compatibility adapter only where its boundary and retirement condition
are accepted.

## Acceptance scenarios

- A caller-only symbolic DTO cannot satisfy source semantic acceptance.
- One compile produces one canonical inspection projection with stable source
  identity and provenance.
- Exact/symbolic inspection allocates no finite artifact and does not collapse
  `State<T>`.
- Unresolved meaning returns a provenance-bearing rejection and no artifact.

## Exclusions and stop conditions

No finite target lowering, provider/network behavior, Hilbert-space storage,
Rust migration, or public API break. Stop for an ADR if evaluator semantics or
the current Scientific Semantic IR authority must change.

## Phase 1 candidate files

Named Red tests/fixtures, this Issue/WP/spec/review records, and the minimal
inspection projection boundary only; no production implementation in Phase 1.

## Phase 1 Red result

The Adjudicator approved `LISS-0476 Phase 1 Red` on 2026-08-30. Added only
`tests/test_liss_0476_symbolic_ir_consumer_migration_red.py`.

The Red packet covers non-explicit `symbolic_ir` authority removal, the
no-rebuild boundary, compile-owned inspection identity/source provenance, and
the no-finite-artifact/no-collapse inspection contract. The two migration
gates fail against the current pipeline because it still exposes and builds
`symbolic_ir` for `ordinary_gate.sqx`; the two already-satisfied canonical
inspection invariants pass. No production code was changed.

Verification: `./.venv/bin/pytest -q
tests/test_liss_0476_symbolic_ir_consumer_migration_red.py` reports `2 failed,
2 passed`, and `git diff --check` passes. Phase 2 Green requires separate
Adjudicator approval.
