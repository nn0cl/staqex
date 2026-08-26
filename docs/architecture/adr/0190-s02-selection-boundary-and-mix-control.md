# ADR 0190: S02 selection boundary and `mix` / `controlled` control taxonomy

| Field | Value |
|---|---|
| Status | **Accepted; Phase 2 implementation approved 2026-08-04** |
| Date | 2026-08-04 |
| Scope | S02 drug-discovery benchmark and future language surface it exercises |
| Parent | [ADR 0189](0189-quantum-mental-model-and-observation-contract.md) |
| Work plan | [WP-0093](../../work-plans/WP-0093-s02-language-expressiveness-and-selection.md) |
| Target specification | [S02 benchmark specification](../../specs/staqex-v1-s02-drug-discovery-benchmark.md) |

## Context

S02 is an indication-agnostic early drug-discovery expressiveness benchmark.
It must show a clean boundary between classical candidate data and a finite
quantum selection state. The existing `when` spelling collides with common
classical conditional vocabulary and does not denote coherent control. The
benchmark also needs hard feasibility constraints without pretending that a
penalty score guarantees feasibility.

## Decision

1. S02 uses `mix` as the canonical name for a non-collapsing, state-valued
   probabilistic / classified alternative transformation.
2. `controlled` or typed `Ctl` is reserved for coherent control of an
   operation. It is not an alias for `mix`.
3. `superpose` remains reserved for a semantics that preserves coherent
   relative phase; it is not used for the current convex-mixture semantics.
4. `when` is removed from the canonical surface. Backward compatibility is
   not required, and the compiler must not silently reinterpret `when` as
   `mix`. A legacy spelling is a hard diagnostic; any source rewrite belongs
   to a separate migration tool, not a runtime or parser fallback.
5. Host input hygiene may reject malformed, duplicate, missing, or obviously
   out-of-domain candidate records. Selection constraints remain explicit in
   the quantum boundary.
6. Hard selection constraints lower to a feasible-subspace `Projector` (or an
   explicitly equivalent operator contract). Soft preferences lower to named,
   normalized objective terms and may be represented by a penalty Hamiltonian.
7. Candidate data is classical. The quantum carrier is
   `State<Selection<CandidateId>>`; no implicit feature-vector-to-amplitude
   conversion is allowed.
8. Terminal `measure` is the classical result boundary. `expect`, `project`,
   and `mix` do not sample or collapse the state.

## S02 fixed boundary

```text
Candidate records / constraints / scores
  → explicit finite encoding with witness
  → State<Selection<CandidateId>>
  → Projector(feasible hard constraints)
  → evolve under named soft objective H
  → terminal measure
  → classical reranking + resource/provenance report
```

The first fixture is synthetic, deterministic, and small: 8–16 candidates and
selection size 2–4. A strong greedy baseline and an exact small-instance
baseline are required. S02 does not claim chemical validity, clinical value,
quantum advantage, or live-QPU execution.

## Alternatives rejected

- **Keep `when` as the canonical spelling:** rejected because it preserves a
  classical-language collision and obscures the intended state semantics.
- **Use `superpose` for all alternatives:** rejected because a convex mixture
  is not automatically a coherent phase-preserving superposition.
- **Use `when` / `mix` as a constraint filter:** rejected because a state-valued
  alternative is not a feasible-subspace projection.
- **Penalty-only hard constraints:** rejected as the sole semantics because a
  penalty does not guarantee a feasible terminal sample.
- **Implicit compact encoding:** rejected because it hides resource width and
  the classical/quantum boundary.
- **Vendor-specific QUBO/QAOA surface:** rejected because it makes a backend
  API, rather than the physical model, the source language.

## Consequences

Positive:

- Physicists can distinguish mixture, coherent control, and terminal outcome
  by reading the source.
- S02 tests the intended state-transformer mental model rather than chemistry
  preprocessing or vendor API familiarity.
- Feasibility, approximation, resource, and provenance claims remain explicit.

Costs:

- The `when` removal is a deliberate breaking surface change.
- `Projector`, finite encoding witnesses, and objective metadata need explicit
  specifications before compiler work.
- The first S02 implementation is smaller than a general optimization DSL.

## Acceptance boundary

This ADR established the S02 specification and conformance boundary. The
reviewed target specification, Phase 1 tests, and explicit Phase 2 approval
authorize the current implementation batch. Later changes to the grammar,
lexer, parser, evaluator, IR, tests, or official examples require their own
reviewed scope and phase approval.
