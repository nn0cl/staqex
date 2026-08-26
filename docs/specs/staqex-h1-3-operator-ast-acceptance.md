# Staqex H1-3 Operator AST and Hamiltonian verification

| Field | Value |
|---|---|
| Status | **Draft for Phase 1 Red** |
| Parent | [H1-2 Parser/AST acceptance](staqex-h1-2-parser-ast-acceptance.md) |
| Scope approval | Adjudicator, 2026-08-03 |
| Phase | Phase 1 — failing tests only |
| Out of scope | Numerical evolution, QPU routing, automatic quantization, optimizer fusion |

## 1. Objective

Replace H1 operator `source_tokens` as the primary representation with a
structured Operator AST and a verified Physics IR projection. The compiler must
distinguish a valid Hamiltonian, a dimensionally invalid expression, and a
non-Hermitian operator before numerical lowering.

## 2. Acceptance scenarios

### H1-3-01 — Structured operator expression

```gherkin
Given `operator H(J, h) = -J * ZZ - h * (X[0] + X[1])`
When the theory is compiled
Then the H1 operator contains a structured expression node
And the expression retains source provenance
And the legacy token tuple is not the only semantic representation
```

### H1-3-02 — Dimension-safe Hamiltonian

```gherkin
Given J: Energy and h: Energy
When H combines them with dimensionless Pauli operators
Then the operator is accepted as a Hamiltonian
And its declared carrier/type is retained in the AST and Physics IR
```

### H1-3-03 — Dimension mismatch

```gherkin
Given J: Energy and dt: Time
When the user writes H = J + dt
Then compilation emits DIMENSION_MISMATCH_ERROR
And no executable operator artifact is produced
```

### H1-3-04 — Hermiticity check

```gherkin
Given H = i * X
When the user declares H as a Hamiltonian
Then compilation emits NON_HERMITIAN_OPERATOR_ERROR
And the target backend is not invoked
```

### H1-3-05 — Operator Physics IR lowering

```gherkin
Given a valid structured H1 operator
When Physics IR is built
Then it contains a source-backed H1Operator node
And the node retains operator atoms, parameters, carrier, and provenance
```

**Canonical authority note:** H1-3-05 consumes the source-derived Scientific
Semantic IR through a typed Physics IR projection. Physics IR does not own
independent meaning and cannot bypass canonical dispatch or authorize an
artifact when source identity, structural children, or provenance are absent.

## 3. Design boundary

The H1-3 implementation may reuse existing `OpBin`, `OpPauli`, `OpVar`,
`OpIndexed`, and `OpBinder` nodes where their semantics match. It must not put
dimension or Hermiticity policy into a backend adapter. Verification belongs in
the compiler/domain boundary; Physics IR remains provider-neutral.

## 4. Phase 2 gate

Phase 2 requires review of the operator expression node, dimension model,
Hermiticity policy, and the exact Physics IR node contract. A valid source must
remain writeable even when a selected target cannot realize it; target rejection
is a separate capability diagnostic.
