# S02 and representative-example migration inventory

| Field | Value |
|---|---|
| Status | **Phase 0 review correction in progress — independent review: NOT READY** |
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
  regression safety; evidence/context hygiene; phase and approval discipline;
  architecture/boundary integrity; type/dimension/validity closure; and
  state/physics safety. The last three are required because the inventory
  explicitly classifies classical, mathematical, quantum, finite, Host, and
  terminal-measurement boundaries.
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

## Phase 0 inventory result

### Corpus boundary

The official runnable corpus for this inventory is the 31 entrypoints listed
in `tests/spec_verification/suites/sv09_examples.py`: 15 Basics entries and
16 Applied entries. S02 is a separate showcase lane and is not silently added
to SV-09; it is inventoried separately because it requires HostInputPort data
and has a finite-target comparison lane. S01 support files are included only
through their SV-09/main entrypoints or the named showcase source under review.

The exact SV-09 set is the source-of-truth list at
`tests/spec_verification/suites/sv09_examples.py:19-51`:

| Set | Entries | Current status | Evidence |
|---|---:|---|---|
| Basics | 15 | supported for compile/run regression | `tests/spec_verification/suites/sv09_examples.py:19-35`; SV-09 result 15/15 |
| Applied | 16 | supported for compile/run regression | `tests/spec_verification/suites/sv09_examples.py:37-51`; SV-09 result 16/16 |
| S02 showcase | 1 | partial: source/Host exact lane works; finite target is capability-rejected and not submitted | `examples/showcase/S02_drug_discovery/main_selection.sqx`; `tests/test_liss_0438_residual_reconciliation_red.py` |

### Representative semantic-role map

| Representative | Blackboard/source role | Status | Evidence and follow-up |
|---|---|---|---|
| B04 `evolve_not_loops` | quantum transform repetition; `Evolve` applies explicit `U_dur` | supported | `examples/basics/B04_evolve_not_loops/evolve_not_loops.sqx`; SV-09/SV-13 |
| B08 `operators_hamiltonians` | named Hamiltonian, exact exponential, state transform | supported | `examples/basics/B08_operators_hamiltonians/operators_hamiltonians.sqx`; SV-09/SV-19 |
| B10 `static_qpu_lane` | finite static target lane and terminal observation | supported with target limitations | `examples/basics/B10_static_qpu_lane/main_static_qpu_lane.sqx`; SV-09/SV-10 |
| B12 `open_systems` | density/open-system simulator semantics | partial by design | `examples/basics/B12_open_systems/main_open_systems.sqx`; SV-09; QPU execution remains out of scope |
| B13 `host_job_api` / B14 `resource_profile` | Host job and resource-control boundaries | supported at local/provider-neutral boundary | respective source paths; SV-09; provider integration excluded |
| A03 `h2_vqe` / A06 `topological_edge_memory` | explicit Hamiltonian evolution and terminal measurement | supported for local lane | respective source paths; SV-09/SV-19 |
| A05 `qaoa_portfolio` | repeated named cost/mixer propagators; not an automatic QAOA solver claim | supported as expression example | `examples/applied/A05_qaoa_portfolio/main_qaoa_portfolio.sqx`; SV-09 |
| A07 `open_system_sensor` | open-system Host/simulator example | partial by design | `examples/applied/A07_open_system_sensor/main_open_system_sensor.sqx`; SV-09; adaptive/QPU follow-up deferred |
| A11 `noether_forge` | multi-register state evolution with explicit source operators | supported for local lane | `examples/applied/A11_noether_forge/main_static.sqx`; SV-09/SV-19 |
| S02 `main_selection` | mathematical `Sigma`/`Set`/projector, exact `U_t`, formal `Limit`, explicit finite `Realize`, Host inputs | partial | source/README, LISS-0438 regression, baseline; broad numerical migration is separate |

Unlisted helper modules are not independent runnable programs; they are
covered through their importing entrypoint unless a future Issue explicitly
promotes one to a public example.

### Boundary and gap register

| ID | Boundary/gap | Classification | Priority | Follow-up |
|---|---|---|---|---|
| G-01 | Exact local evolution versus formal `Limit` and finite `Realize` | supported in S02 source; target capability may reject | P0 | no new implementation; preserve ADR 0210 |
| G-02 | S02 Host inputs and classical baseline are outside Kernel source | intentional scope | P0 | preserve HostInputPort and baseline boundary |
| G-03 | Broader example-by-example equation fidelity beyond the representative set | partial / not yet fully inventoried | P1 | separate example Issue after this Phase 0 |
| G-04 | Provider SDK, live submission, real-device execution | unsupported by this scope | P0 | remain separate unapproved work |
| G-05 | General ODE/PDE solver, automatic finiteization, new Host syntax/result schema | intentional scope | P1 | no implementation without new design approval |
| G-06 | Pytest-based local execution in the current environment | verification gap, not product gap | P1 | record harness limitation; use repository direct-test/SV commands until environment is provisioned |

### Deterministic evidence recorded

| Check | Result |
|---|---|
| `python3 -m compiler.staqex check examples/showcase/S02_drug_discovery/main_selection.sqx` | PASS: no hard compile diagnostics |
| `python3 tests/spec_verification/run_all.py` | PASS: SV compliance 161/161; SV-09 official corpus passes |
| Direct LISS-0437/LISS-0438/S02 scripts | PASS in repository harness; pytest module is not installed in this environment |
| S02 single Host run | PASS; selection pattern produced, non-vacuum result |
| S02 classical baseline | PASS; feasible patterns 25/256 |
| `git diff --check` | PASS |
| S02 multi-shot benchmark | Not used as Phase 0 completion evidence; it is long-running and was stopped during independent review |

The S02 fixed-seed reference remains
`examples/showcase/S02_drug_discovery/baseline/s02_explicit_evolution_baseline.json`;
this Phase 0 does not alter or claim to revalidate its numerical metrics.
