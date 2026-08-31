# LISS-0487: Equation DTO authority retirement

| Field | Value |
|---|---|
| Status | **ready — design complete; Architecture/spec review required** |
| Phase | phase-0-design |
| Parent | WP-0107 |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0487-equation-dto-authority-retirement) |
| Related authority | [Scientific Semantic Core](../specs/staqex-scientific-semantic-core.md#consumer-wide-follow-up-design), ADR 0211 |
| Depends on | WP-0107 and the completed canonical IR boundary slices |
| Implementation permission | None |
| Next approval | Architecture/spec review, then typed Phase 1 Red approval |

## Scope

Retire caller-injected `EquationNode`, string equations, and equivalent
`physics_equation` DTOs as semantic authorities. Preserve their explicitly
typed module-local diagnostic role while requiring source-derived Scientific
Semantic IR for semantic acceptance, execution authorization, and finite
realization.

## Acceptance scenarios

- A caller-only `EquationNode` cannot alter or satisfy canonical source
  meaning.
- A string equation is rejected rather than silently coerced into an equation
  DTO or semantic node.
- Accepted source equations preserve node identity, role, dimensions,
  exactness, intent, and provenance in the canonical IR.
- Injected equation data cannot authorize QPU/algorithm artifacts, allocation,
  or implicit finiteization.
- Existing diagnostic-only Equation DTO validation remains available without
  becoming semantic authority.

## Boundary decisions

- Scientific Semantic IR is the only authority for source meaning.
- `EquationNode` input is diagnostic-only and must carry explicit origin and
  validation status; it is not merged into canonical nodes.
- String payloads have no implicit conversion path.
- Physics IR replacement is a separate future projection migration and is not
  part of this authority-retirement Issue.

## Exclusions and stop conditions

No equation solver, numerical semantics, physics IR replacement, automatic
finiteization, provider/QPU/AWS, Rust, or S02 migration. Stop for a new ADR if
Equation DTOs must become a new semantic authority or public API changes.

## Phase 1 candidate files

Named authority-negative tests, caller-injection fixtures, this Issue/spec/WP
records, and review record only. Production guard changes begin in Phase 2.
