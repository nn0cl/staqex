# Staqex H1 Hamiltonian-authoring slice — draft acceptance specification

| Field | Value |
|---|---|
| Status | **Draft for review** — no implementation approval |
| Direction | [Democratized language direction](../architecture/staqex-democratized-language-direction.md) |
| Scope | First H-first authoring slice: typed parameters, indexed operator algebra, explicit basis, and honest evolution |
| Out of scope | New `quantize` keyword, arbitrary continuous-to-discrete conversion, live QPU provider integration, automatic uncompute |

This is a design input, not a normative acceptance authority. Normative
acceptance requires the named specification review and typed Phase 1 approval;
implementation approval remains separate.

## 1. Goal

A physicist should be able to state a small Hamiltonian experiment without
manually constructing a gate circuit or introducing Java/Kotlin-style domain
objects. The source must preserve the equation, while the compiler exposes the
operator representation and target limitations.

## 2. Acceptance scenarios

### H1-01 — Typed Hamiltonian parameters

```gherkin
Given a theory with typed parameters J: Energy and h: Energy
When the user defines H = -J * ZZ - h * (X[0] + X[1])
Then H is represented as an Operator expression
And dimensionally invalid additions are rejected before runtime
And the source does not require a classical mutable object
```

### H1-02 — Indexed operator sum

```gherkin
Given a finite lattice domain with a declared site set
When the user writes a neighbor interaction sum
Then the compiler lowers it to a symbolic sparse Operator IR
And the expansion records the domain and boundary condition
And a classical runtime loop is not inserted into the Static Kernel surface
```

### H1-03 — Explicit basis and preparation

```gherkin
Given an operator whose carrier is a declared basis/domain
When the user prepares a State on that carrier
Then a basis mismatch is rejected with a physics-facing diagnostic
And implicit basis conversion is not silently performed
```

### H1-04 — Hamiltonian evolution

```gherkin
Given a Hermitian Operator H and a State ψ on a compatible carrier
When the user writes ψ |> evolve under H for t
Then the result remains a State
And no measurement or classical scalar extraction occurs
And the runtime preserves norm within the declared numeric tolerance
```

### H1-05 — Observable versus terminal result

```gherkin
Given a State ψ after evolution
When the user asks expect(O, ψ)
Then the result is an Observable or non-collapsing State-derived value
When the user writes terminal measure ψ
Then and only then a classical Outcome is produced
```

### H1-06 — Fail-closed realization

```gherkin
Given a valid Hamiltonian source that exceeds a target capability
When the user selects that target
Then compilation or submission rejects the realization explicitly
And the source model is not rewritten into an unrelated gate-tourism program
```

## 3. Evidence contract

An implementation of H1 must produce:

- source fixture;
- typed AST/HIR evidence;
- symbolic Operator IR with source origin, carrier, and boundary metadata;
- one simulator result;
- one invalid-dimension diagnostic;
- one invalid-basis diagnostic;
- one target-capability rejection;
- comparison showing the source is not dependent on Java/Kotlin-style classes.

The “one simulator result” evidence is split by the realization boundary:
exact/symbolic inspection produces only a non-collapsing
`SemanticInspectionResult` with no finite allocation; a numeric simulator
result requires a source-visible finite `Realize` policy and carries its
method, finite parameters, error budget, target, and provenance.

## 4. Open decisions before Red

- exact syntax for indexed sums and lattice domains;
- whether `theory` and `experiment` are accepted as additive syntax;
- canonical terms for `quantize`, `finiteize`, `encode`, and `represent`;
- whether Hermiticity is a type/effect, a verifier property, or both;
- whether `Observable<A>` is a new surface type or a compiler-only phase type;
- compatibility rules for current `Operator H = ...` source.

## 5. Non-goals

H1 does not establish that every classical model has a unique quantization. It
does not hide discretization, truncation, encoding, or basis choice. It also
does not make a QPU backend the acceptance oracle: semantic and simulator
evidence come first, and target realization remains capability-gated.
