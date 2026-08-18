# Staqex explicit evolution residual reconciliation — acceptance specification

## Status and authority

- Status: **Design and independent review complete; Phase 1 and implementation not approved** (2026-08-18)
- Local Issue: [LISS-0438](../issues/LISS-0438-explicit-evolution-residual-reconciliation.md)
- Parent WorkPlan: [WP-0100](../work-plans/WP-0100-explicit-evolution-surface.md)
- This specification does not amend [ADR 0210](../architecture/adr/0210-formal-limit-finite-realization-policy.md).

## Goal

Define the residual S02 reconciliation boundary so a reader can distinguish:

1. the ideal/formal blackboard evolution;
2. the exact local simulator expression used for semantic regression; and
3. the explicit finite target realization used only when a target requires it.

The design must make the correspondence visible without silently replacing the
source expression, changing the local numerical baseline, or claiming QPU
execution.

## Scope

In scope for this design:

- `examples/showcase/S02_drug_discovery/main_selection.sqx` as the representative
  residual fixture;
- a source-to-blackboard mapping for `psi_0`, `P_F`, `psi_sel`, `H_obj`, `U_t`,
  and `psi_final`;
- an explicit formal `Limit` and finite `Realize` relationship for a target lane;
- fixed-seed and benchmark comparison contracts to be executed only after a
  later implementation approval;
- provenance and rejection evidence required by ADR 0210;
- a bounded S02 artifact inventory; broader corpus inventory is deferred.

Out of scope:

- implementation or test changes in this design phase;
- S02 numerical-model migration, retuning, or algorithm redesign;
- changing candidate data, Host scoring, feasibility predicates, or objective
  weights;
- live QPU submission, credentials, provider SDKs, network, or adapters;
- automatic insertion of `Realize`, `Limit`, `N`, order, steps, duration, or
  error budget;
- changing ADR 0210, the accepted explicit evolution surface, or the meaning
  of `Evolve()`;
- broad corpus migration before a separate acceptance decision.

## Frozen source correspondence

The S02 blackboard sequence is:

\[
|\psi_0\rangle = 2^{-n/2}\sum_{x\in\{0,1\}^n}|x\rangle,
\quad |\psi_{sel}\rangle =
\frac{P_F|\psi_0\rangle}{\|P_F|\psi_0\rangle\|},
\quad H_{obj},
\quad U_t=e^{-iH_{obj}t/\hbar},
\quad |\psi_{final}\rangle=U_t|\psi_{sel}\rangle.
\]

The current exact simulator lane must continue to show:

```staqex
Energy scale = 1.0.eV to J
Operator H_obj = scale * objective_hamiltonian(weights, n, activity_w, selectivity_w)
Time dur = 0.6.fs
Operator U_t = exp(-i * H_obj * dur / hbar)
State psi_final = Evolve() { U_t * psi_sel }.run()
```

The target-realization lane may additionally show the formal construction and
its explicit finite conversion:

```staqex
Operator U_formal = Limit N -> Infinity {
    (I - i * H_obj * dur / (N * hbar)) ^ N
}
Operator U_qpu = Realize(
    source = U_formal,
    method = "suzuki",
    order = 2,
    steps = 8,
    error_budget = 1e-6
)
```

`U_formal` and `U_qpu` are distinct values. The design freezes two named lanes
for Phase 1 planning: `U_t` remains the exact local simulator propagator and
`U_qpu` is consumed only by finite-target plan verification. The local
simulator does not execute `Realize` in this residual slice. Combining the
lanes later requires a new acceptance decision because it changes the S02
numerical baseline.

## EARS acceptance scenarios

### R1 — source meaning is recoverable

Given `main_selection.sqx`, a reviewer can identify the equal superposition,
projector, normalization, Hamiltonian, duration, exponential, state
application, and terminal measurement without inferring hidden `Evolve`
semantics.

### R2 — exact local lane remains stable

Given the pre-reconciliation S02 fixture and fixed Host inputs, the exact local
lane preserves compile success, terminal measurement shape, and the recorded
fixed-seed baseline. No approximation policy is applied to this lane.

### R3 — finite target lane is explicit

Given a formal `Limit`, a target plan is produced only through a visible
`Realize` expression containing method, required parameters, and error budget.
Missing or invalid policy rejects before allocation and retains only the
diagnostic/rejection evidence required by ADR 0210; it produces no executable
circuit, qubit allocation, or partial program. A resource-budget overflow is
stricter: it leaves no gates, qubits, partial program, or target-plan
provenance. Diagnostic evidence and target-plan provenance are distinct.

### R4 — numerical comparison is reproducible

Given identical source revision, Host inputs, simulator settings, and seeds, a
comparison report records exact-lane output, finite-lane output when supported,
diagnostics, successful-realization provenance, and successful-plan resource
metadata. For rejected runs it records only the diagnostic outcome; in
particular, budget-overflow estimates and requested budgets are transient and
must not be retained as target-plan provenance. The report must separate
semantic equality, approximation difference, and capability rejection; it
must not call any result a quantum advantage.

### R5 — scope boundaries remain visible

The design and later implementation report explicitly state that no live QPU,
provider SDK, credentials, S02 numerical retuning, or broad corpus migration
was performed.

## Required evidence for a later implementation phase

- fixed Host input snapshot or deterministic input-construction reference;
- source revision/hash, compiler version/profile, target profile, and explicit
  simulator settings;
- seed list and target settings;
- pre-change exact-lane result baseline;
- post-change exact-lane result baseline;
- finite realization provenance (`source_transform`, method, order/steps,
  error budget, realization kind, resource estimate);
- rejection evidence for unsupported or over-budget targets;
- a diff proving no unrelated S02 model or Host scoring change;
- explicit checks that `H_obj` has Energy dimension, `dur` has Time dimension,
  `-i * H_obj * dur / hbar` is dimensionless, and the operator/state acting
  space is compatible;
- explicit record that `X[i]` terms may leak amplitude outside `F` because they
  do not commute with `P_F`; feasibility is measured, not assumed;
- explicit unitary/QPU-profile rejection evidence for non-unitary realization
  inputs;
- independent review of the implementation result.

## Ambiguities requiring a later decision

1. Which fixed-seed set and benchmark metrics are authoritative. The later
   Phase 1 acceptance tests must freeze them before implementation.
2. Whether future broad corpus inventory deserves a separate Issue.

The exact-local/finite-target lane choice is no longer open for this slice:
Phase 1 planning uses separate `U_t` and `U_qpu` names, with local execution
remaining exact and finite realization verified through target-plan evidence.

## Next gate

This specification is ready for independent review only. A reviewer cannot
approve Phase 1 or implementation. After review, the user/Adjudicator must
separately approve Phase 1 Red and then implementation.
