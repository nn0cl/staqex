# Staqex hybrid workflow contract

> Coverage note (2026-09-08): This accepted document owns the bounded Host
> iteration contract. Broader scientific metadata, deadlines, plan approval,
> rolling replanning, and explicit fallback are proposed in the
> [Scientific Workflow specification](staqex-scientific-workflow-acceptance.md)
> and [complete design](../architecture/scientific-workflow-complete-design.md).
> They are not shipped by, or authorized through, this existing slice.

| Field | Value |
|---|---|
| Status | **Accepted provider-neutral workflow boundary; surface/execution follow-up remains open** |
| Decision | [ADR 0072](../architecture/decision-themes/dec-0006-host-qpu-and-external-ports.md) |
| Issue | [LISS-0035](../issues/LISS-0035-hybrid-scientific-workflow.md) |
| Depends on | LISS-0022, LISS-0027, LISS-0034, ADR 0065, ADR 0070 |

## Invariants

1. A Workflow consumes an immutable Experiment contract.
2. Concrete parameter values are Host bindings, never `State<T>` values and
   never Theory-scope variables.
3. A Workflow receives an opaque `JobResult` projection, not AST, `Joint`, raw
   simulator state, or provider SDK objects.
4. Each iteration produces a new `JobRequest`; it does not mutate the prior
   request, Experiment, or Theory contract.
5. A successful result is available only after terminal measurement and result
   persistence.
6. Provider SDK, credentials, retry, session, and optimizer policy are outside
   this acceptance slice.

## Boundary DTOs

```text
ExperimentSpec
ParamBinding { parameter, value }
JobRequest { experiment, bindings, execution_policy }
MeasurementProjection { observable, value, marginal, metadata }
JobResult { status, measurements, diagnostics, metadata }
WorkflowReport { status, iterations, final_bindings, results }
```

All DTOs are immutable and provider-neutral. `ExecutionPolicy` may carry
validated target/shots/seed data, but no provider SDK object.

## Acceptance scenarios

### A — closed experiment input

Given an accepted Experiment contract and declared `Param<Angle>` values, a
Workflow can produce a validated `JobRequest` without modifying the Theory AST.

### B — typed result projection

Given a completed `JobResult`, a Workflow can select a declared observable
projection. An undeclared observable or raw simulator field is rejected.

### C — iteration immutability

Given an update step, the next iteration returns a new binding and request. The
previous request and result remain unchanged.

### D — completion ordering

Given a queued or running Job, no result projection or update step is evaluated
until `wait/result` reaches a terminal result.

### E — phase visibility

Theory cannot reference `Host<T>`, `Job`, `JobResult`, `shots`, `backend`, or
optimizer values. Workflow can consume the Experiment contract and host result
DTOs, but cannot mutate the Theory/Experiment internals.

### F — provider neutrality

The same workflow plan can be validated with a local fake adapter without
loading a provider SDK or credentials.

## Deferred syntax questions

- Whether `workflow Name { … }` is the final surface or only an IR/Host API
  representation.
- Whether update steps are named host callbacks or a restricted declarative
  expression language.
- The exact convergence/termination vocabulary, including `until`.
- Whether cancellation and retry policies belong in this LISS or LISS-0016.

## Host feedback iteration

The Phase 3 Host API provides `WorkflowPlan.run_iterative`. It obtains a
completed `JobResult`, evaluates `until`, and only then invokes `update` to
create the next immutable binding set. The loop is bounded by a positive
`max_iterations` value and returns an immutable `WorkflowReport`. `until` and
`update` are Host callbacks in this slice; they are not Staqex Kernel expressions.
