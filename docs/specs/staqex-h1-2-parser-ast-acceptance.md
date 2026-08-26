# Staqex H1-2 Parser/AST acceptance specification

| Field | Value |
|---|---|
| Status | **Draft for Phase 1 Red** |
| Parent | [H1 Hamiltonian-authoring direction](staqex-h1-hamiltonian-authoring-direction.md) |
| Scope approval | Adjudicator, 2026-08-03 |
| Phase | Phase 1 — failing tests only |
| Out of scope | H1 numerical lowering, QPU emission, automatic quantization, new backend providers |

## 1. Objective

Replace the H1 compile-entry recognizer with formal parser and AST nodes while
preserving the physicist-first source shape. The compiler must retain source
structure instead of returning `unit=None` with a synthetic Physics IR.

## 2. Candidate AST boundary

The implementation may choose exact class names, but the observable boundary
must contain equivalent concepts:

- `TheoryDecl`: name, typed parameters, domains/bases, and operator declarations;
- `ExperimentDecl`: name, parameter bindings, preparation, state transforms,
  observables, terminal measurement, and optional realization target;
- `H1ParameterDecl`: name and physical type/unit;
- `H1OperatorDecl`: name, parameters, expression, carrier/domain metadata;
- `H1Prepare`, `H1Evolve`, `H1Observable`, and `H1Measure` nodes;
- source spans on all nodes that can produce a diagnostic.

The implementation may reuse existing scientific-scope DTOs internally only if
the public AST still distinguishes H1 equation authoring from legacy phase
metadata.

## 3. Acceptance scenarios

### H1-2-01 — Formal theory AST

```gherkin
Given a H1 theory with typed parameters and a parameterized Hamiltonian
When the source is compiled
Then the CompileResult has a non-null CompilationUnit
And the unit contains a theory declaration node
And the theory node contains parameter and operator declaration nodes
And source spans are retained
```

### H1-2-02 — Formal experiment AST

```gherkin
Given a H1 experiment with prepare, evolve, expect, and terminal measure
When the source is compiled
Then the unit contains an experiment declaration node
And its body preserves the ordered prepare/evolve/observable/measure sequence
And the parser does not lower the program directly to a synthetic result
```

### H1-2-03 — Physics IR receives formal source

```gherkin
Given a formally parsed H1 source
When the compiler builds Physics IR
Then the IR has source-backed theory and operator nodes
And source provenance identifies the original H1 declaration spans
And the normal compile pipeline remains available for diagnostics
```

**Canonical authority note:** The Physics IR named by H1-2-03 is a
consumer-facing, compile-owned projection generated from the source-derived
Scientific Semantic IR defined by ADR 0211. It is not an independent semantic
authority. The projection must retain the canonical source identity,
structural children, carrier, and provenance; caller-injected Physics IR
cannot authorize execution.

### H1-2-04 — Legacy scientific scopes remain compatible

```gherkin
Given an existing legacy `theory X { ... }` / `experiment Y { theory = X }` source
When the source does not use H1 authoring markers
Then the existing ScientificScopeDecl behavior remains unchanged
```

## 4. Phase 1 evidence

The Red tests must fail against the current implementation because H1 currently
returns `unit=None` from a temporary compile boundary. They must not assert
implementation-private class names unless those names become part of the
accepted AST contract.

## 5. Phase 2 gate

Phase 2 requires review of the failing tests and acceptance of the concrete AST
class names, parser ownership, and compatibility strategy. No H1 syntax may be
added to the normative grammar until that review.
