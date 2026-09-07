# B19 — Constrained selection boundary

This Basic example shows a language boundary: Staqex keeps a finite classical input boundary,
quantum state, mathematical constraint, evolution, and terminal measurement
distinct. It is not a drug-discovery program and makes no chemistry or
quantum-advantage claim.

## What it demonstrates

```text
classical Host inputs
  → finite State preparation
  → feasible-subspace Projector
  → Hamiltonian evolution
  → terminal measure
```

The program uses eight binary positions and retains states with exactly three
selected positions. Compatibility and diversity matrices arrive as classical
Host inputs. The Kernel uses them only to define the finite projector.

## Blackboard equation

The initial finite state, feasible-set projector, propagator, and terminal
measurement are written in the source in that order.

## Ideal Staqex expression

`psi_0`, `psi_sel`, `H_obj`, and `U_t` remain semantic values before the
terminal measurement. Projection is not classical sampling.

The local lane applies the explicitly written `U = exp(-i * H * dur / hbar)`.
The separate `Realize` expression records a finite Suzuki policy; it does not
silently replace the exact local evolution or imply live QPU execution.

## Explicit finite realization

`U_qpu = Realize(source = U_formal, method = "suzuki", order = 2, steps = 8,
error_budget = 1e-6)` is an explicit target-plan request.

## QPU/QASM projection

Classification: partial. The target lane is capability-rejected with
`QASM_TROTTER_UNSUPPORTED_H` for this teaching fixture. It records
`submitted=False` and produces no partial target program; there is no live QPU.

## Run

```bash
python3 -m compiler.staqex check examples/basics/B19_constrained_selection/constrained_selection.sqx
python3 examples/basics/B19_constrained_selection/host/run_selection.py
```

The supporting Host fixture is deterministic and local-only. It uses no
credentials, network, provider SDK, or live QPU.

## Boundary rules

- Host inputs remain classical values.
- Intermediate values remain `State` values.
- Projection does not collapse the state.
- Only terminal `measure` produces a classical outcome.
- Unsupported finite target projections must fail closed without an artifact.

This example is a language-boundary teaching sample. The future showcase
benchmark is a separate work item with a different scientific scope.
