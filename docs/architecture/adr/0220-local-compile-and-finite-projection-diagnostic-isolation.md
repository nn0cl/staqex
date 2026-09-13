# ADR 0220: Local compile and finite-projection diagnostic isolation

## Status

Accepted — Adjudicator approved 2026-09-13.

## Context

Six LISS-0552 nodes combine stale source fixtures, hard linear-resource
diagnostics, and advisory Quantum Semantic IR evidence diagnostics.
`CompileResult.ok` already ignores the two generic QSEM evidence codes, but
does not name itself as local acceptance. QASM can also emit a measure-only
artifact for canonical source containing unprojected `inner` or `outer`
meaning. The architecture must preserve ideal source expressiveness without
converting local success into target authorization.

This decision refines ADR 0212 and the Quantum Semantic IR contract. It does
not supersede their ideal/finite boundary.

## Dependency Adoption Evidence

Not applicable. No dependency, SDK, provider, datastore, or framework is
selected.

## Decision Proposal

1. Local source/kernel acceptance and finite target projection are separate
   decisions.
2. `CompileResult.local_ok` becomes the explicit local signal;
   `CompileResult.ok` remains its compatibility alias.
3. Generic missing finite-evidence and approximation-obligation diagnostics
   remain non-hard and visible. Their local-compile copies carry stable
   advisory metadata naming the quantum-semantic phase and finite-projection
   blocking scope; the pure QSEM lowering result is not mutated.
4. Linear-resource diagnostics remain local hard failures. Algebraic
   `inner`/`outer` does not implicitly measure or discharge its source states;
   accepted terminal `tracing_out` expresses deliberate disposal.
5. QPU IR owns projection conservation. A canonical semantic operation may be
   emitted only when represented by a meaning-preserving finite projection;
   otherwise QPU IR produces a provenance-bearing rejection consumed by QASM.
6. QASM adapters do not reinterpret source meaning, inspect compile-hard code
   policy, or infer missing finite evidence.
7. Missing/mismatched canonical input remains LISS-0554; present canonical
   input with an unprojected operation is LISS-0552.

## Rejected Alternatives

- Promote both QSEM evidence diagnostics to local compile-hard: rejected
  because ideal/local meaning can be valid without a finite target choice.
- Suppress the diagnostics whenever local execution is possible: rejected
  because it hides unresolved finiteization obligations.
- Add separate source languages or compile modes for local and QPU: rejected
  because they risk two semantic authorities.
- Let the QASM adapter scan AST calls and decide physics: rejected because
  target adapters must consume core projection decisions, not own semantics.
- Treat absent instructions as permission to emit measure-only QASM: rejected
  because omission is not proof of semantic conservation.

## Consequences

Positive:

- Physicist-valid source remains writable and locally inspectable.
- Linear ownership remains explicit and testable.
- Callers can name local success without implying deployability.
- Unsupported canonical operations reject before target allocation or
  artifact emission.
- LISS-0552 and LISS-0554 have non-overlapping failure ownership.

Negative:

- `CompileResult` gains an additive compatibility property and QSEM diagnostics
  gain metadata fields.
- QPU IR must prove operation coverage rather than relying on non-empty gate
  output.
- Existing callers that misuse `.ok` as target readiness must be audited in
  the bounded consumer path.

## Enforcement

Code review should reject:

- any use of `CompileResult.ok` as QASM/QPU authorization;
- removal or hard promotion of the two generic QSEM advisory diagnostics;
- softening `LINEAR_IMPLICIT_DISCARD`;
- AST-based unsupported-operation policy inside a provider/QASM adapter;
- QASM success when a retained canonical semantic operation lacks projection
  evidence;
- rejection that leaves QASM, gates, allocation, or a partial program.

## Approval Effect

Architecture approval accepts this boundary and the companion LISS-0552
acceptance specification. It does not authorize Phase 1 tests or Phase 2
implementation.

Approval received:
`ADR 0220 Architecture / LISS-0552 Phase 0 acceptance 承認` on 2026-09-13.
