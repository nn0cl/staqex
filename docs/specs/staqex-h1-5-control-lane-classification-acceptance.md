# Staqex H1-5 Control-Lane Classification

| Field | Value |
|---|---|
| Status | **Phase 3 Refactored; implementation slice accepted** |
| Parent | [H1-4 State Transformer Plan](staqex-h1-4-state-transform-plan-acceptance.md) |
| Scope approval | Adjudicator, 2026-08-03 |
| Phase | Phase 3 — behavior-preserving refactor complete |
| Out of scope | New numerical execution, QPU emission, full effect typing, automatic uncompute |

This document is a design input for this reorganization; its existing Phase 3
status does not authorize a new Phase 1 or implementation scope here.

## 1. Objective

Make the three control meanings explicit in the H1 State Transformer boundary:

1. `when` is probabilistic/classified state composition and remains a mixture.
2. Coherent control is a state-valued controlled transformation and maps to the
   existing `CoherentControlRegion` semantic category.
3. Measurement-dependent classical feed-forward belongs to the Dynamic QPU
   lane and must not be silently represented as Static Kernel control.

The slice must preserve the existing `QuantumSemanticIR` and dynamic-QPU
contracts. It must not introduce a second meaning for `when` or use classical
short-circuit `if` in the Static Kernel.

## 2. Acceptance scenarios

### H1-5-01 — `when` remains mixture classification

```gherkin
Given an H1 experiment with a `when` state classification
When the source is compiled
Then the State Transformer plan contains a Mixture step
And the step is not classified as coherent control
And no terminal measurement is introduced by `when`
```

### H1-5-02 — Coherent control maps to semantic control

```gherkin
Given an H1 experiment with a coherent controlled transformation
When the source is compiled
Then the plan contains a CoherentControl step
And the semantic artifact contains a CoherentControlRegion
And the control and target remain distinct state factors
```

### H1-5-03 — Dynamic feed-forward is not Static Kernel control

```gherkin
Given an H1 experiment that attempts measurement-dependent classical control
When the source is compiled as Static Kernel
Then compilation emits H1_DYNAMIC_CONTROL_REQUIRES_DYNAMIC_LANE
And no Static Kernel control region is produced
```

## 3. Surface trial forms

These forms are trial spellings for this slice and are not yet normative
grammar:

```text
when phase { Ground -> prepare |0>, Excited -> prepare |1> }
capply(control, X, target)
dynamic control measured -> correction
```

The implementation may preserve the source tokens initially, but the semantic
classification must be explicit and source-backed.

## 4. Phase 2 gate

Phase 2 requires review of the lane labels, the mapping to
`CoherentControlRegion` / dynamic-QPU contracts, and the diagnostic contract
for Static Kernel feed-forward. The reviewed Red tests must remain unchanged.
