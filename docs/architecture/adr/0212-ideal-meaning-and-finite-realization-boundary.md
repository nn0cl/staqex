# ADR 0212: Ideal Meaning and Finite Realization Boundary

## Status

Architecture-approved by user 2026-08-20; independent review required before
Phase 1 Red or implementation.

## Context

The current QPU boundary correctly rejects unsupported finite projections, but
the same rejection can be mistaken for a restriction on writing the ideal
blackboard expression. `Limit`, exact exponentials, `Coin`, `Mix`, non-unitary
products, and other mathematical or quantum meanings must remain expressible
even when a finite QPU circuit is unavailable.

## Decision

Staqex separates four contracts:

1. **Ideal source meaning:** the program may express the blackboard equation,
   including exact, symbolic, mixed, continuous, or non-unitary meaning where
   the language contract supports it.
2. **Scientific Semantic IR:** the compiler preserves that meaning structurally
   with source identity, children, role, type/dimensions, exactness, intent,
   state/mixture distinction, and provenance.
3. **Finite realization:** `Realize` is the explicit transition that chooses a
   finite method, order, steps, error budget, qubits, or target policy.
4. **QPU/QASM projection:** only a meaning-preserving finite realization may
   produce executable target artifacts. Otherwise the target rejects with a
   deterministic, provenance-bearing capability diagnostic.

QPU rejection never deletes or replaces the ideal source meaning. AST-pattern
  fallback, silent unitary substitution, hidden discretization, and implicit
finiteization are prohibited.

## Consequences

- `Coin/Mix` and similar constructs must be represented in the ideal semantic
  layer before their QPU projection is considered.
- CPU or exact/symbolic inspection may remain available without creating a
  finite QPU artifact.
- QPU rejection remains atomic: no QASM, gates, instructions, allocation, or
  partial program.
- Existing pre-allocation resource checks and explicit Suzuki provenance stay
  in force.
- LISS-0449/LISS-0452 and WP-0112/WP-0115 must align their acceptance tests to
  this separation.

## Non-goals

This ADR does not add provider SDKs, live submission, S02 numerical migration,
solver support, or new syntax. It does not grant Phase 1 Red or implementation
approval.

## Review requirement

An independent reviewer must verify that ideal meaning is parser-reachable and
structurally represented, that finite realization is explicit, and that every
QPU rejection is a target-boundary decision rather than a language deletion.
