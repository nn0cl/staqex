# LISS-0445 Phase 1 Red Independent Review 02

| Field | Value |
|---|---|
| Trigger | Fresh review after Review 01 corrections |
| Context boundary | Independent read-only context; no edits, implementation, or approval |
| Result | **NOT READY**; one contract correction and evidence refinement required |
| Approval status | Phase 1 Red execution approved; Phase 2 Green and implementation not approved |

## Verification

The fixed Red suite returned **5 failed, 7 passed**, with no collection
errors. The ordinary QASM payload, exact rejection artifact checks, terminal
measurement ordering, and Issue/Spec/WP/trace phase fields were consistent.
The H1/QASM provenance and complete Realize policy fields remain appropriately
deferred to Green.

## Findings and disposition

| Priority | Finding | Disposition | Rationale |
|---|---|---|---|
| P1 | The revised Algorithm Plan test still fixed the contract to Python type identity. | accepted | Replaced it with a behavior-level test that sends the compile-owned plan through the provider-neutral plan projection API. This keeps the one-authority requirement while avoiding a representation mandate. |
| P1 | Dirty-worktree baseline was not reproducible enough. | accepted | Added base commit, branch, and exact pre-existing `compiler/staqex` path evidence to the Phase 1 trace. |
| P2 | H1 structure/provenance, complete QASM provenance, and all Realize policy fields are not yet asserted. | deferred | These are explicit Phase 2 Green acceptance candidates and do not invalidate the fixed Red boundary. |

## Reusable perspectives

- Test architectural authority at a consumer boundary rather than by class
  identity.
- When a phase starts dirty, preserve exact commit, branch, and path evidence.
- Keep Green-level provenance completeness separate from Red-level rejection
  and bypass detection.

## Next review condition

Run a fresh independent review against the behavior-level Algorithm Plan
contract and the reproducible baseline evidence. Phase 1 Red may close only
after that review returns READY/COMPLETE.
