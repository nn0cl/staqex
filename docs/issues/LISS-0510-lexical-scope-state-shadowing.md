# LISS-0510: Lexical scope and State shadowing implementation

| Field | Value |
|---|---|
| Status | **in_progress — Phase 1 Red tests added; review required** |
| Phase | phase-1-red |
| Parent | WP-0092 |
| Design authority | [ADR 0216](../architecture/adr/0216-lexical-block-scope-and-state-shadowing.md) |
| Depends on | LISS-0480, LISS-0483 |
| Implementation permission | None |
| Next approval | Phase 1 Red test review before Phase 2 |

## Scope

Implement lexical binding support for braced nested blocks while preserving
blackboard shaped source. Scientific display metadata must resolve through the
same binding environment as type checking.

## Acceptance scenarios

- An inner `State psi` shadows an outer `State psi` and is independently
  consumed.
- An inner `Float psi` shadows an outer `State psi` without changing the outer
  State binding.
- Two declarations named `psi` in one scope fail with a duplicate-declaration
  diagnostic.
- After an inner block ends, the outer `psi` resolves again.
- Consuming the inner State does not consume the outer State, and using the
  outer State twice still fails the ordinary linearity rule.
- Lexicon metadata reports the resolved binding identity and declaration span.

## Phase 1 candidate files

Tests and fixtures under `tests/`, plus this Issue and a trace. Production
parser/type-checker changes are Phase 2 only.

Phase 1 evidence: `tests/test_liss_0510_lexical_scope_red.py` contains four
acceptance tests. Against the current compiler all four are Red: nested
binding metadata is absent, same-scope duplicate diagnostics are absent, and
per-binding State scope is not yet represented by the current resolver.

## Exclusions

No new alias inventory, Unicode source policy, public observation type,
provider/QPU integration, Rust implementation, or forced extraction into
functions/files.

## Design notes

Use the existing typed scope model where possible. Do not add a second symbol
table solely for scientific aliases. The same lexical environment must drive
type resolution, linearity diagnostics, and lexicon metadata.
