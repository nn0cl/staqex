# B08 — Operators and Hamiltonians

Teaches `Operator` binds, indexed Pauli sites, an explicit Hamiltonian
exact propagator `U(t)=exp(-iHt/hbar)`, sparse `expect`, and terminal
`measure … tracing_out …`.  Finite QPU realization is demonstrated separately
by the explicit `Limit` + `Realize` acceptance examples.
(ADR 0173). **Minimal dialect face** (WP-0088 / ADR 0176):
`// staqex-profile: experiment` — no package / `main` wrapper, no inspect museum,
no ritual `|0>` “uncompute.”

Legacy sources: `examples/06_statistical_physics/quantum_ising.sqx`,
`examples/10_topological_physics/operators/hamiltonian_builder.sqx` (concept).
