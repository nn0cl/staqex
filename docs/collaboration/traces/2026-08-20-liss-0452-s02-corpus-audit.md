# LISS-0452 S02 Corpus Audit Trace

| Field | Value |
|---|---|
| Mode | read-only corpus audit |
| Scope | `examples/showcase/S02_drug_discovery/main_selection.sqx` and README |
| Phase | Phase 1 preparation; no source change |
| Authority | LISS-0452 / WP-0115 / Spec `staqex-s02-example-boundary-alignment` |
| Excluded | S02 numerical migration, solver, provider SDK, live QPU, credentials, network |

## Four-stage inventory

| Stage | Evidence | Current classification |
|---|---|---|
| Blackboard equation | `main_selection.sqx` comments and README stages 1–4 | documented / source comments |
| Ideal Staqex expression | `psi_0`, `P_F`, `psi_sel`, `H_obj`, `U_t = exp(...)` | source-visible ideal/simulator lane |
| Explicit finite realization | `U_formal = Limit ...` and `U_qpu = Realize(... Suzuki, order=2, steps=8, error_budget=1e-6)` | source-visible target plan |
| QPU/QASM scope | README states finite plan is not used by exact simulator; current CI has known Coin/Mix projection failures tracked by LISS-0448 | partial / capability-bound |

## Findings

1. The source names the exact propagator (`U_t`) separately from the formal
   limit and finite `Realize` plan, so the ideal/finite boundary is visible.
2. README and source agree that `U_qpu` is planning evidence and is not used by
   the exact local result.
3. The audit does not establish successful QPU/QASM compilation. The known
   Coin/Mix projection failures remain an LISS-0448 follow-up and are not
   silently reclassified as S02 numerical work.
4. No source or README mutation is authorized by this audit. Any example
   rewrite requires a separate reviewed Spec and phase approval.

## Evidence inventory

- Source: `examples/showcase/S02_drug_discovery/main_selection.sqx`
- Documentation: `examples/showcase/S02_drug_discovery/README.md`
- Related boundary: `docs/specs/staqex-s02-example-boundary-alignment.md`
- Known target gap: `docs/issues/LISS-0448-canonical-qasm-coin-mix-projection.md`

## Audit conclusion

The S02 example is suitable as a Phase 1 acceptance fixture for boundary
honesty, but it is not evidence of live QPU execution or complete QASM support.
The required next artifact is an executable boundary test; numerical migration
remains a separate Issue.

This audit is complete as a read-only Phase 1 preparation artifact. It is not
part of the LISS-0449–0451 Red test packet, does not mark those tests complete,
and does not authorize any S02 source change.
