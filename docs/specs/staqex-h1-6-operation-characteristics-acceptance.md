# Staqex H1-6 Operation Characteristics

| Field | Value |
|---|---|
| Status | **Phase 3 Refactored; implementation slice accepted** |
| Parent | [H1-5 Control-Lane Classification](staqex-h1-5-control-lane-classification-acceptance.md) |
| Scope approval | Adjudicator, 2026-08-03 |
| Phase | Phase 3 — behavior-preserving refactor complete |
| Out of scope | New surface capability syntax, numerical lowering, QPU emission, extensible effect rows |

This document is a design input for this reorganization; its existing Phase 3
status does not authorize a new Phase 1 or implementation scope here.

## 1. Objective

Expose the physical characteristics of H1 state transformations in the
provider-neutral plan and existing Quantum Semantic IR categories.

The first vocabulary is intentionally small:

- `Unitary`: preserves a pure state carrier and acting space.
- `Adj`: may be reversed as an adjoint transformation.
- `Ctl`: may be coherently controlled.
- `Channel`: produces a density-state channel and is not silently unitary.
- `Observe`: asks a non-collapsing question and is not a state transformation.

This slice does not decide whether characteristics are written as a new
surface clause. It only fixes semantic evidence and diagnostics.

## 2. Acceptance scenarios

### H1-6-01 — Hamiltonian evolution is unitary and adjointable

```gherkin
Given an H1 experiment with `evolve under H`
When the source is compiled
Then the Evolve plan step has Unitary and Adj characteristics
And it is not classified as Channel
```

### H1-6-02 — Coherent control exposes controllability

```gherkin
Given an H1 experiment with a coherent controlled transformation
When the source is compiled
Then the CoherentControl plan step has Unitary and Ctl characteristics
And its semantic region remains CoherentControlRegion
```

### H1-6-03 — Observation and terminal measurement are not transforms

```gherkin
Given an H1 experiment with observe and terminal measure
When the source is compiled
Then the Observe and TerminalMeasure steps have no Unitary characteristic
And neither step is classified as Channel
```

## 3. Semantic boundary

The characteristic set is metadata on the provider-neutral H1 plan and/or
existing Semantic IR. It must not be inferred from a backend gate list. A
Hamiltonian is not itself a unitary transform; `evolve under H` is the
unitary/adjointable transformation in this slice.

The existing fixed effect system remains separate. Extensible effect rows and
provider-specific characteristics are out of scope.

## 4. Phase 2 gate

Phase 2 requires review of characteristic inference, the distinction between
Hamiltonian declarations and state transformations, and the mapping to
`UnitaryRegion`, `ChannelRegion`, and `CoherentControlRegion`. The Red tests
must remain unchanged.
