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
| Ideal source/meaning | `main_selection.sqx` lines 74–135: normalized ket sum, literal feasible-set projector, projection normalization, weighted Hamiltonian, and exact `exp(-i * H_obj * dur / hbar)` | **Present.** Source preserves the equation structure and keeps the exact local `U_t` lane separate from the finite target lane. README now uses matching `psi_0`, `psi_sel`, and `psi_final` state names. |
| Explicit finite realization | `main_selection.sqx` lines 138–148: `U_formal = Limit ...` and `U_qpu = Realize(source = U_formal, method = "suzuki", order = 2, steps = 8, error_budget = 1e-6)` | **Present.** Method, order, steps, and error budget are source-visible. The finite operation is named separately and is not used as the exact simulator evolution. |
| QPU/QASM scope | README finite-target note; `host/benchmark_report.py` finite-target result fields; `tests/test_liss_0438_residual_reconciliation_red.py` | **Partial / capability-rejected.** The deterministic host comparison returned `status=capability-rejected`, code `QASM_TROTTER_UNSUPPORTED_H`, `submitted=False`, `partial_program=None`, and no target-plan provenance. Documentation says SIM-only and no live QPU. |

## Corpus classification

The current S02 directory contains one `.sqx` source example:
`main_selection.sqx`. The Python host files and baseline JSON are supporting
artifacts, not additional Staqex source examples. The selected corpus is
therefore classified as follows:

| Artifact | Classification | Evidence |
|---|---|---|
| `main_selection.sqx` | **partial** | Exact local simulator lane and explicit finite `Realize` are present; the finite target attempt is capability-rejected and no live/provider QPU lane exists. |
| `README.md` + host report | **partial / documentation support** | Four stages and SIM-only boundary are documented, but state-name terminology needs alignment and the rejection evidence is now recorded explicitly. |

## Mismatch and risk inventory

1. **State-name mismatch corrected in documentation.** README sections 1,
   4, and 5 now use the source-owned `psi_0`, `psi_sel`, and `psi_final`
   names. No Staqex source or runtime behavior was changed.
2. **Finite target is not live execution.** The example is intentionally
   unsupported as a live/provider submission; future verification must not
   promote a plan witness to QPU execution.
3. **Finite-plan outcome is now recorded precisely.** The current target
   lowering is `capability-rejected` with `QASM_TROTTER_UNSUPPORTED_H`; no
   target plan provenance or partial program is produced, and no QPU/provider
   was contacted. Phase 1 should freeze this contract if it remains the
   accepted boundary.
4. **Numerical benchmark claims remain separate.** The README discloses
   feasibility leakage and SIM-only status; this audit does not validate or
   alter the numerical baseline, score, or top-k claims.

## Audit conclusion

`main_selection.sqx` is **READY for a separately approved Phase 1 Red request**.
The exact-local versus explicit-realization boundary is recoverable and
physicist-first. The current corpus is classified as a partial, SIM-only
example with deterministic target rejection. The independent review/correction
loop is **COMPLETE**; no Phase 1, implementation, provider integration,
numerical migration, or language/runtime approval is inferred.

## Evidence

- Local command: `./.venv/bin/python -m compiler.staqex check examples/showcase/S02_drug_discovery/main_selection.sqx`
- Result: `ok — no hard compile diagnostics`
- Target comparison: `capability-rejected QASM_TROTTER_UNSUPPORTED_H False None None`
  (`status`, `capability_rejection`, `submitted`, `partial_program`,
  `target_plan_provenance`)
- Focused regression: `tests/test_liss_0438_residual_reconciliation_red.py` — **5 passed**
- Documentation correction: README state names aligned with `main_selection.sqx`;
  no source/runtime behavior changed.
- Final independent re-review: `docs/collaboration/reviews/2026-08-24-liss-0452-corpus-audit-review-02.md` — **READY; no findings**.
- No production/example source files changed by this audit.
