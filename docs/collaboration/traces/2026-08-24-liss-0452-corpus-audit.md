# LISS-0452 S02 Example Blackboard/Realization Boundary Corpus Audit

## [DESIGN CHECK]

- Scope and expected behavior: read-only audit of the S02 drug-discovery
  example against four stages: blackboard equation, ideal Staqex meaning,
  explicit finite realization, and QPU/QASM scope or rejection.
- Specifications and files inspected: LISS-0452, WP-0115, the proposed S02
  example-boundary specification, `examples/showcase/S02_drug_discovery/README.md`,
  `main_selection.sqx`, the host boundary/report modules, and the related
  LISS-0449–0452 review trace.
- Component boundaries, ports/adapters, and VO/DTO candidates: no source or
  runtime change. Host candidate data remains outside the Kernel through
  `HostInputPort`; the exact local evaluator and finite target-plan witness
  remain separate lanes.
- Applicable constraints: preserve blackboard spelling and assumptions; do
  not introduce hidden finiteization, provider/QPU execution, numerical
  migration, solver work, or syntax changes.
- Decisions, assumptions, and unresolved ambiguities: the current example is
  a SIM-only benchmark. The finite lane is a provider-neutral plan witness;
  its presence must not be read as live QPU support. A later Phase 1 request
  must freeze the exact evidence for realized versus capability-rejected
  target behavior.
- Included and omitted context: included the S02 source, README, host report
  boundary, accepted realization/semantic boundary ADRs, and review ledger;
  omitted provider adapters, broad S02 numerical migration, and unrelated
  examples.
- Task routing: deterministic source inspection and the local compiler check;
  no AI-generated runtime data is consumed.
- Independent review lenses selected and why: contract completeness,
  source-to-domain fidelity, realization/fail-closed behavior, projection
  conservation, migration/regression safety, and phase/approval discipline.
- Verification plan: retain this read-only inventory, run the local compile
  check, and request independent review before any source or Phase 1 Red
  change.

## Four-stage inventory

| Stage | Evidence | Audit result |
|---|---|---|
| Blackboard equation | README sections “Physics ↔ program” 1–5; equations for `psi_0`, `P_F`, `H_obj`, `U(t)`, and terminal Born-rule measurement | **Present.** The README identifies assumptions, the 8-candidate/3-selection fixture, Host-owned predicates, objective weights, duration, and terminal measurement. |
| Ideal source/meaning | `main_selection.sqx` lines 74–135: normalized ket sum, literal feasible-set projector, projection normalization, weighted Hamiltonian, and exact `exp(-i * H_obj * dur / hbar)` | **Present.** Source preserves the equation structure and keeps the exact local `U_t` lane separate from the finite target lane. `Measure psi_final` remains terminal. |
| Explicit finite realization | `main_selection.sqx` lines 138–148: `U_formal = Limit ...` and `U_qpu = Realize(source = U_formal, method = "suzuki", order = 2, steps = 8, error_budget = 1e-6)` | **Present.** Method, order, steps, and error budget are source-visible. The finite operation is named separately and is not used as the exact simulator evolution. |
| QPU/QASM scope | README finite-target note and `host/benchmark_report.py` finite-target result fields | **Present with an honesty condition.** Documentation says SIM-only and no live QPU. The host report treats the finite lane as a plan witness and records `realized` versus `capability-rejected`; this distinction must remain covered by future Phase 1 evidence. |

## Mismatch and risk inventory

1. **No source/README four-stage mismatch found.** The source and README use
   the same `U_formal`/`U_qpu` separation and the same `U_t` exact-local lane.
2. **Finite target is not live execution.** The example is intentionally
   unsupported as a live/provider submission; future verification must not
   promote a plan witness to QPU execution.
3. **Finite-plan outcome needs explicit evidence.** The current compile check
   proves source reachability only (`ok — no hard compile diagnostics`); it
   does not prove that the finite plan is executable for every target profile.
   Phase 1 should assert the exact realized-or-rejected contract and empty
   artifact behavior on rejection.
4. **Numerical benchmark claims remain separate.** The README discloses
   feasibility leakage and SIM-only status; this audit does not validate or
   alter the numerical baseline, score, or top-k claims.

## Audit conclusion

`main_selection.sqx` is **design-ready for Phase 1 preparation**, not approved
for source changes. The four-stage boundary is recoverable and physicist-first
in the current source/document pair. The next safe step is independent
read-only review of this inventory, followed by explicit Phase 1 Red approval
for boundary tests only. No provider integration, numerical migration, or
example rewrite is authorized by this audit.

## Evidence

- Local command: `./.venv/bin/python -m compiler.staqex check examples/showcase/S02_drug_discovery/main_selection.sqx`
- Result: `ok — no hard compile diagnostics`
- No production/example source files changed by this audit.
