# Staqex H1-4 State Transformer Plan

| Field | Value |
|---|---|
| Status | **Phase 3 Refactored; implementation slice accepted** |
| Parent | [H1-3 Operator AST and Hamiltonian verification](staqex-h1-3-operator-ast-acceptance.md) |
| Scope approval | Adjudicator, 2026-08-03 |
| Phase | Phase 3 — behavior-preserving refactor complete |
| Out of scope | Numerical execution, QPU lowering, automatic quantization, optimizer fusion, new control syntax |

This document is a design input for this reorganization; its existing Phase 3
status does not authorize a new Phase 1 or implementation scope here.

## 1. Objective

Connect the formal H1 `experiment` body to a provider-neutral, ordered State
Transformer plan. The plan is a semantic artifact only; it must preserve the
physicist's experiment order without claiming that the source is executable on
a simulator or QPU.

The implementation should reuse the existing semantic categories and region
contracts where possible. It must not create a second meaning for `when`,
coherent control, or dynamic-QPU feed-forward.

## 2. Acceptance scenarios

### H1-4-01 — Ordered State Transformer plan

```gherkin
Given an H1 experiment containing prepare, evolve, observe, and measure
When the source is compiled
Then the result contains a State Transformer plan
And its ordered steps are Prepare, Evolve, Observe, TerminalMeasure
And every step retains source provenance
```

### H1-4-02 — Terminal measurement boundary

```gherkin
Given an H1 experiment with an operation after measure
When the source is compiled
Then compilation emits H1_MEASURE_NOT_TERMINAL
And no executable plan is produced
```

### H1-4-03 — Observation is non-collapsing

```gherkin
Given an H1 experiment containing observe before terminal measure
When the source is compiled
Then observe is retained as an observation step
And it does not become a measurement or an Outcome step
```

## 3. Semantic boundary

The first implementation may introduce a small immutable plan DTO if the
existing Quantum Semantic IR cannot yet accept H1 source directly. The DTO
must remain provider-neutral and source-backed. It must not perform numerical
evolution, sampling, lowering, or automatic quantization.

The plan is not an approval to add `Transform<A,B>` surface syntax. That is a
separate design decision. This slice only proves that the current H1 trial
surface has an ordered State Transformer interpretation.

## 4. Phase 2 gate

Phase 2 requires review of the plan DTO/IR contract, terminal-measurement
diagnostic, provenance shape, and the mapping boundary to the existing
`QuantumSemanticIR`. The reviewed Red tests must remain unchanged.
