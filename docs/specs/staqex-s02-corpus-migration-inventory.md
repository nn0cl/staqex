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

The official runnable corpus for this inventory is the 26 entrypoints listed
in `tests/spec_verification/suites/sv09_examples.py`: 15 Basics entries and
11 Applied entries. The SV-09 documentation check is a separate 27th case.
S02 is a separate showcase lane and is not silently added to SV-09; it is
inventoried separately because it requires HostInputPort data and has a
finite-target comparison lane. S01 support files are included only through
their SV-09/main entrypoints or the named showcase source under review.

The exact SV-09 set is the source-of-truth list at
`tests/spec_verification/suites/sv09_examples.py:19-51`:

| Set | Entries | Current status | Evidence |
|---|---:|---|---|
| Basics | 15 | supported for compile/run regression | `tests/spec_verification/suites/sv09_examples.py:19-35`; SV-09 result 15/15 |
| Applied | 11 | supported for compile/run regression | `tests/spec_verification/suites/sv09_examples.py:37-51`; SV-09 result 11/11 |
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
| S02 `main_selection` | mathematical `Sigma`/`Set`/projector, exact `U_t`, formal `Limit`, explicit finite `Realize`, Host inputs | partial | source/README, LISS-0438 regression, baseline; broad numerical migration is separate; current Host key is `host("diversity")`, while README predicate prose says `diversity_at_least` |

Unlisted helper modules are not independent runnable programs; they are
covered through their importing entrypoint unless a future Issue explicitly
promotes one to a public example.

### Evidence-complete representative matrix

The following matrix satisfies the seven-field inventory contract for each
representative lane. `N/A` means the property is intentionally not claimed,
not that evidence is missing.

| Representative | Equation and source construct | Classical / mathematical / quantum / finite / Host roles | Compile/run evidence | Provenance | Diagnostic boundary | Baseline preservation |
|---|---|---|---|---|---|---|
| B04 | `U_dur = exp(-i*H*dur/hbar)`; `Evolve() { U_dur * psi }` at `examples/basics/B04_evolve_not_loops/evolve_not_loops.sqx:1-15` | `dur` classical; `H`/`exp` quantum meaning; `Evolve` execution; no Host input | SV-09 B04; SV-13 evolve checks | exact local propagator; no finite claim | `evolve times`/state boundary; QPU limitations are not hidden | N/A; teaching fixture has no numerical baseline |
| B08 | Named `H_chain`, exact `U_dur`, state application at `examples/basics/B08_operators_hamiltonians/operators_hamiltonians.sqx:1-20` | constants/`dur` classical; operator algebra mathematical/quantum; terminal measure | SV-09 B08; SV-19 operator/exponential checks | exact simulator lane | non-unitary/unsupported target lowering fails through existing diagnostics | N/A; no migration baseline |
| B10 | Static target operation and terminal observation at `examples/basics/B10_static_qpu_lane/main_static_qpu_lane.sqx:1-9` | resource profile is Host/target control; observed state is quantum; gate lane is finite target realization | SV-09 B10; SV-10 target-QPU emission | provider-neutral finite static lane; no live submission | target capability/QASM rejection remains explicit | N/A; no numerical migration |
| B12 | Density/open-system source at `examples/basics/B12_open_systems/main_open_systems.sqx:1-25` | coefficients classical; Lindblad structure mathematical/quantum; RK4 is simulator realization; no provider Host | SV-09 B12; SV-19 open-system checks where applicable | exact declared simulator contract, not QPU claim | adaptive/QPU execution remains intentionally unsupported | N/A; no numerical migration |
| B13 | Host `Job`/measurement boundary at `examples/basics/B13_host_job_api/main_host_job.sqx:1-6` | job metadata/shots are Host; measured state is quantum→classical terminal result | SV-09 B13 | local/provider-neutral Host DTO boundary | provider submission remains outside this inventory | N/A; API fixture |
| B14 | Resource profile and terminal measurement at `examples/basics/B14_resource_profile/main_resource_profile.sqx:1-6` | resource budget is Host control; state/measure are quantum | SV-09 B14; resource checks | local resource enforcement; no provider price/SDK | budget/capability rejection remains fail-closed | N/A; resource fixture |
| A03 | H₂-style `H`, `U_t = exp(-i*H*dur/hbar)`, tuple state at `examples/applied/A03_h2_vqe/main_h2_vqe.sqx:1-46` | molecular coefficients classical; Hamiltonian/operator algebra quantum; terminal partial measure | SV-09 A03; SV-19 arbitrary-H checks | exact local evolution; no chemistry/QPU claim | unsupported target lowering remains explicit | N/A; applied example has no locked baseline |
| A05 | Named mixer/cost exponentials and repeated `Evolve` at `examples/applied/A05_qaoa_portfolio/main_qaoa_portfolio.sqx:1-38` | layer durations/parameters classical; cost/mixer mathematical/quantum; repetition is quantum transform, not Host sweep | SV-09 A05 | exact local propagators; not a QAOA optimizer or finite-QPU claim | target limits are existing capability boundaries | N/A; no quality baseline claimed |
| A07 | Open-system sensor and terminal observation at `examples/applied/A07_open_system_sensor/main_open_system_sensor.sqx:1-33` | sensor inputs classical/Host; density evolution quantum; simulator realization | SV-09 A07 | simulator-only partial support | adaptive/QPU follow-up is intentionally unsupported | N/A; no benchmark baseline |
| A11 | Named `U_t` and tuple-state evolution at `examples/applied/A11_noether_forge/main_static.sqx:1-73` | parameters classical; Noether/Hamiltonian expressions mathematical/quantum; explicit state transform; module imports are declarations | SV-09 A11; SV-19 evolution checks; import/link checks | exact local lane; no live target claim | module/link and target capability diagnostics remain explicit | N/A; no migration baseline |
| S02 | `psi_0`, `P_F`, `psi_sel`, exact `U_t`, formal `Limit`, explicit `Realize` at `examples/showcase/S02_drug_discovery/main_selection.sqx:75-155` | Host arrays/baseline classical; `Sigma`/`Set` mathematical; `State`/`Operator` quantum; `Realize` finite target; Host runner controls inputs/shots | direct S02 compile; SV-09 excludes S02; LISS-0438 5/5; Host run; baseline 25/256 | exact local `U_t`; finite `U_qpu` plan is capability-rejected and not submitted | `QASM_TROTTER_UNSUPPORTED_H`; no partial target artifacts/provenance | pre-migration hash/metrics are preserved as reference; current source hash is recorded separately |

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
| `python3 tests/spec_verification/run_all.py` | PASS: SV compliance 161/161; SV-09 has 26 entrypoint cases plus 1 README case |
| `python3 tests/test_liss_0438_residual_reconciliation_red.py` | PASS: 5/5 direct tests |
| `python3 tests/test_liss_0402_s02_selection_example.py` | NOT a test-runner result: module exits without executing pytest assertions |
| `python3 tests/test_liss_0403_s02_benchmark_report.py` | NOT a test-runner result: module exits without executing pytest assertions; long benchmark evidence is separately noted below |
| LISS-0437 direct script | Not rerun in this review correction; prior completion evidence is retained in WP-0104 |
| `python3 -m pytest ...` | NOT RUN: `pytest` module is not installed in this environment |
| S02 single Host run | PASS; selection pattern produced, non-vacuum result |
| S02 classical baseline | PASS; feasible patterns 25/256 |
| `git diff --check` | PASS |
| S02 multi-shot benchmark | Not used as Phase 0 completion evidence; it is long-running and was stopped during independent review |

The S02 fixed-seed reference remains
`examples/showcase/S02_drug_discovery/baseline/s02_explicit_evolution_baseline.json`;
its `source_sha256` is intentionally a **pre-migration reference hash**, not a
claim that the current post-migration source has the same hash. The current
source hash is `d2d548637955a71e50d5db49103abd2f187f0a55d0f08d1e0668117285359ddd`.
This Phase 0 does not alter or claim to revalidate the baseline numerical
metrics.

The README's `diversity_at_least` is the semantic predicate name, whereas the
current HostInputPort key is `diversity`; this is recorded as a documentation
consistency gap and is not silently changed by this inventory.
