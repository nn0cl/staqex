# S02 and representative-example migration inventory

| Field | Value |
|---|---|
| Status | **proposed Phase 0 design artifact** |
| Purpose | Inventory the remaining example/S02 migration work without changing source semantics or benchmark results. |
| Related Issue | [LISS-0442](../issues/LISS-0442-s02-corpus-migration-inventory.md) |
| Related Work Plan | [WP-0105](../work-plans/WP-0105-s02-corpus-migration-inventory.md) |
| Existing boundaries | [ADR 0210](../architecture/adr/0210-formal-limit-finite-realization-policy.md), [WP-0100](../work-plans/WP-0100-explicit-evolution-surface.md), [WP-0104](../work-plans/WP-0104-explicit-evolution-residual-reconciliation.md) |

## [DESIGN CHECK]

- **Scope and expected behavior:** Produce an evidence-backed inventory of
  representative `.sqx` examples and the S02 Host lane. Classify equation
  fidelity, compilation, semantic role boundaries, finite realization, and
  numerical-baseline coupling before proposing any migration.
- **Specifications and files inspected:** `AGENTS.md`, the implementation
  readiness checklist, the independent-review perspectives ledger, the S02
  acceptance specification, explicit-evolution specification, ADR 0210,
  WP-0100/WP-0104, SV-09, S02 source/README/Host runner, and existing S02
  regression tests.
- **Component boundaries:** This is documentation and evidence only. Kernel
  semantics, Host DTOs, QASM lowering, adapters, and benchmark algorithms are
  not changed. No new port, result schema, or language construct is proposed
  by this inventory.
- **Applicable constraints:** Physicist-first source; source denotes the same
  blackboard meaning; `Sigma`/`Pi` are mathematical binders; `Evolve` executes
  an explicit transform; `Realize` is the finite target boundary; measurement
  is terminal; unsupported target lowering fails closed.
- **Decisions, assumptions, and unresolved ambiguities:** The inventory may
  recommend a future Issue, but cannot authorize Phase 1 Red, numerical
  migration, automatic finiteization, provider SDK use, or live QPU submit.
  S02's fixed-seed benchmark remains the reference and must not be retuned by
  this work.
- **Included and omitted AI context:** Included source paths, specs, tests,
  and prior review perspectives needed to establish evidence. Omitted secrets,
  provider data, external QPU capabilities, and unrelated implementation
  history.
- **Independent review lenses selected and why:** Contract completeness;
  source-to-domain fidelity; realization/fail-closed behavior; migration and
  regression safety; evidence/context hygiene; phase and approval discipline.
- **Verification plan:** Run deterministic S02 focused tests, SV-09, direct
  compile checks, link-target checks, and `git diff --check`. No source or
  benchmark output may change.

## Inventory acceptance contract

Each inventoried example or lane must record:

1. the blackboard equation or stated physical intent;
2. the source construct that denotes it;
3. the classical, mathematical, quantum, finite-realization, and Host roles;
4. compile/run evidence and any required Host input;
5. exact versus approximate status and provenance;
6. unsupported or deferred behavior, including its diagnostic boundary;
7. whether a future migration can preserve the existing numerical baseline.

The inventory is complete only when every proposed migration is assigned one
of `supported`, `partial`, `unsupported`, or `intentional scope`, with evidence
and a separate Issue recommendation where implementation would be required.

