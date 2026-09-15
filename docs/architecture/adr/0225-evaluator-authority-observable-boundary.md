# ADR 0225: Evaluator authority observable boundary

## Status

Accepted — Adjudicator approved `ADR 0225 Architecture 承認` on 2026-09-16.

## Context

LISS-0486 requires the evaluator to receive the exact compile-owned
`ScientificSemanticIR`, but its test observes mutable `Evaluator.semantic_ir`
and expects `ValueError` for caller injection. LISS-0490 and LISS-0493 establish
the runtime-plan boundary, where execution consumes canonical meaning without
allowing AST mechanics or caller DTOs to become a second authority.

## Decision proposed

The canonical observable authority is immutable execution evidence owned by the
compile-to-runtime request/result and, while the internal plan is private, by
the runtime result envelope. It carries the exact compile-owned IR identity,
source identity, fingerprint, execution authority
`scientific_semantic_ir`, and the provenance evidence required by the existing
runtime contract.

`Evaluator.semantic_ir` is not an independent owner. During the migration
window it may expose a read-only compatibility observation of the canonical
object, but it may not accept a caller setter, rebuild meaning, or authorize
execution. Its eventual removal is separate from this Issue.

Invalid, absent, synthetic, or mismatched authority fails through
`KernelDiagnosticError` with the stable code
`E_EVALUATOR_CANONICAL_AUTHORITY`, before runtime state mutation, port effects,
measurement, allocation, or result fabrication. Any compatibility with callers
that catch `ValueError` must be an explicit exception-hierarchy/API decision;
it must not create a second diagnostic path.

## Consequences

- Runtime authority has one owner and remains observable for review.
- Existing result envelopes can gain evidence without making the internal plan
  a public serialization format.
- LISS-0486's identity assertion must move from mutable storage to the
  read-only compatibility observation/result evidence as a bounded migration.
- The `ValueError` expectation is reconciled deliberately rather than silently
  overriding the coded runtime diagnostic contract.

## Alternatives rejected

- Keep a mutable public `Evaluator.semantic_ir` setter: creates duplicate
  authority and permits caller injection.
- Use only `ValueError`: loses the stable runtime diagnostic code and existing
  fail-closed error boundary.
- Rebuild semantic IR inside the evaluator: violates ADR 0211 and source
  identity conservation.

## Approval boundary

This ADR does not authorize Phase 1 tests, Phase 2 implementation, public API
removal, or provider/runtime integration.

## Architecture approval result

- Immutable execution evidence is the canonical observable authority surface.
- `Evaluator.semantic_ir` may remain only as a read-only compatibility view;
  it is not a setter-backed authority or semantic rebuild source.
- `KernelDiagnosticError` with `E_EVALUATOR_CANONICAL_AUTHORITY` is the stable
  fail-closed boundary before state, port, measurement, allocation, or result
  effects.
- Any `ValueError` catch compatibility must be handled by an explicit
  exception-hierarchy/API decision without creating a second rejection path.
- Phase 1 Red, Phase 2 implementation, API removal, and provider integration
  remain separately gated.

## Requested approval

`ADR 0225 Architecture 承認`
