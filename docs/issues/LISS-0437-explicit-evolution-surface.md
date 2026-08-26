# LISS-0437: explicit blackboard evolution expression

## Metadata

- Local issue ID: LISS-0437
- Status/phase: **complete** — finite Realize/Suzuki closeout complete; residual work split to LISS-0438
- Type: Architecture Path
- Planning size: **L**
- Parent WorkPlan: [WP-0100](../work-plans/WP-0100-explicit-evolution-surface.md)
- Acceptance specification: [explicit evolution surface](../specs/staqex-explicit-evolution-surface.md)
- ADR: [ADR 0209](../architecture/adr/0209-explicit-blackboard-evolution-surface.md)
- Branch: `codex/wp-0100-explicit-evolution-surface`
- Implementation permission: **Approved finite realization slice completed and independently reviewed 2026-08-17**
- Phase 1 permission: **Red tests only, approved 2026-08-14 after three
  independent review passes**
- Phase 2 implementation permission: **Approved 2026-08-14** for the minimum
  Green slice; QPU deployment and broad corpus migration remain out of scope.

## Intent

Make the source show the same physics as the blackboard through the explicit
construction of a time-evolution operator. `Evolve` must not silently invent
the exponential, generator, duration, or QPU realization.

## Current gap

`Evolve { psi under H for t }.run()` is physically correct under ADR 0195 but
compresses the derivation into a special form. A reader cannot write or inspect
the intermediate progression from identity and generator to propagator to
state application as source expressions.

## Proposed outcome

```staqex
Operator U_t = exp(-i * H * t / hbar)
State result = Evolve() { U_t * psi0 }.run()
```

The `Evolve()` body receives the state-transforming expression `U_t * psi0`,
not an already-materialized `State` and not an arbitrary identity State. A
bare state body fails closed.

## Architecture boundary

- Language surface: explicit operator algebra and state application.
- Semantic IR: internal `Evolution<T>` value carrying source provenance,
  input/output state shape, generator/propagator structure, and realization
  policy.
- Use case / lowering: validate the requested target profile and lower the
  same denotation to exact simulation, approximate simulation, or a QPU gate
  program.
- Adapters: simulator and QPU ports only; no physics policy in adapters.

## Dependencies

- ADR 0195: real \(\hbar\) Hamiltonian dynamics.
- LISS-0414: bracketed `Evolve { … }.run()` syntax.
- ADR 0084 / LISS-0017: Suzuki/Trotter lowering policy.
- ADR 0085: QPU IR and OpenQASM adapter boundary.
- ADR 0106 / 0111: host/QPU capability and fail-closed delivery.
- S02 `main_selection.sqx`: representative acceptance fixture.

## Risks

- Operator exponentiation could be confused with scalar `exp`; the type and
  diagnostic must make the domain explicit.
- Formal expressions may be writable but not executable on a selected target;
  provenance and capability rejection must remain visible.
- Existing `EvolveExpr` has multiple forms (`times`, duration block,
  Hamiltonian block); migration must not conflate discrete pushforward with
  Hamiltonian exponentiation.
- Existing linear-use checks may reject blackboard-style shared inputs; this
  must be solved in the semantic graph, not by weakening no-cloning laws.

## Next approval

Architecture approval, the companion acceptance contract, and Phase 2
implementation approval are recorded.
Independent review 1 found the contract too open for Red. Reviews 2 and 3
confirmed the corrections: explicit-mode separation, dimensions, migration
diagnostics, MVP `Limit` behavior, and the narrower Red scope are frozen.
Phase 1 Red permission is recorded. The minimum Phase 2 Green implementation,
the approved finite `Realize`/Suzuki target slice, and its correction loop are
complete. The final independent review is recorded in
[`2026-08-17-liss-0437-limit-realization-review-02.md`](../collaboration/reviews/2026-08-17-liss-0437-limit-realization-review-02.md)
with terminal state `COMPLETE` and readiness `READY`.

## Phase 3 Green bounded target-boundary record

The approved bounded slice now carries typed `register_mapping` input through
the target profile. For a finite binder, missing mapping and resource-budget
exhaustion are distinct typed rejection reasons. Both are rejected before
allocation. Formal `Limit` is executable only through source-visible
`Realize`; Suzuki produces a provider-neutral finite gate plan, while the
non-unitary `product` method is explicitly rejected by the QPU gate boundary.
Direct `Limit` remains rejected, and budget overflow leaves no allocation,
gates, partial program, or provenance. S02 numerical migration, live QPU
submission, and provider SDK work remain outside this slice.

## Phase 3 closeout record

- Finite `Realize`/Suzuki synthesis: complete.
- Direct formal `Limit` rejection: complete.
- Non-unitary `product` QPU rejection: complete.
- Pre-allocation resource-budget rejection: complete.
- Independent review loop: `COMPLETE` / `READY`.
- Residual corpus/S02 reconciliation work: [LISS-0438](LISS-0438-explicit-evolution-residual-reconciliation.md), not approved by this record.

## Completion gate

- Final review approval: user-approved 2026-08-17
- Completion PR: **PR #553**
