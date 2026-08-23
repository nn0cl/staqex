# LISS-0448 Phase 1 Red Design Review 01

| Field | Value |
|---|---|
| Trigger | Phase 1 Red approval; independent design review required by ADR 0211/0212 |
| Independent context | Wegener, fresh read-only context `01a024ec-d384-7e22-a142-68f4dbd0b35d` |
| Scope | LISS-0448/WP-0111 Phase 1 Red acceptance and fixture plan |
| Files changed by reviewer | None |
| Verdict | NOT READY; in-scope acceptance clarifications required |
| Phase approval | User approved Phase 1 Red on 2026-08-22; reviewer did not grant approval |

## Findings and disposition

| Priority | Finding | Disposition | Authority and rationale |
|---|---|---|---|
| P1 | Red inventory did not explicitly assert empty QPU instructions, allocation, and partial program. | accepted | ADR 0212 and LISS-0448 require atomic rejection. Add explicit assertions to the Phase 1 test contract. |
| P1 | Exact rejection code/reason were only implicit in the design direction. | accepted | Existing QPU capability rejection matrix fixes `E_QPU_CANONICAL_PROJECTION_UNAVAILABLE` and `mixture_projection_unavailable`; pin both in Red. |
| P1 | Six live SV-10/SV-11 stale H+CX expectations were not named in the Red inventory. | accepted | They are the concrete CI regression boundary and must be covered by the conformance update in the approved LISS-0448 scope. |
| P2 | ADR 0036 contains an old illustrative Coin→H/when→CX example. | accepted as documentation follow-up | ADR 0211/0212 and DEC-0006 prohibit silent unitary substitution. No new ADR is needed unless the example is asserted to remain normative. Record the correction as a later documentation step. |
| P2 | Phase 1 approval and phase boundary must remain explicit. | accepted as record correction | User approval exists; Red only permits tests/fixtures, not production implementation or ADR acceptance. |

## Reusable perspectives

- Source-to-domain fidelity: do not turn `Coin`/`Mix` into a unitary gate node.
- Canonical authority and implementation reality: prove source-derived IR ownership.
- Projection conservation and authority reachability: preserve branch children,
  role, and provenance.
- Realization and fail-closed behavior: assert exact rejection and no artifacts.
- Phase and approval discipline: keep Red separate from Green and documentation
  authority changes.

## Corrections required before Red completion

- Update LISS-0448/WP-0111/Spec Red inventory with exact rejection code/reason,
  no-artifact fields, and the six SV-10/SV-11 cases.
- Add the source fixture and focused tests without changing production code.
- Re-run the focused Red test file and record expected failures.

## Terminal state

`COMPLETE` for this review iteration after the accepted documentation
corrections and fresh Red verification. This review does not approve Phase 2,
implementation, ADR acceptance, or merge.
