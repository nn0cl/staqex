# LISS-0476: Non-explicit `symbolic_ir` consumer migration

| Field | Value |
|---|---|
| Status | **ready — design complete; Phase 1 Red approval required** |
| Phase | phase-0-design |
| Parent | WP-0107 |
| Design authority | [Scientific Semantic Core](../specs/staqex-scientific-semantic-core.md#consumer-wide-follow-up-design) |
| Depends on | LISS-0445, LISS-0446 |
| Implementation permission | None |
| Next approval | Issue/spec review, then typed Phase 1 Red approval |

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
