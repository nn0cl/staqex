# LISS-0445 Phase 1 Red Independent Review 01

| Field | Value |
|---|---|
| Trigger | User-approved WP-0108 Phase 1 Red execution and independent review |
| Context boundary | Fresh read-only reviewer; no worktree edits, implementation, or approval |
| Result | **NOT READY**; correction and fresh review required |
| Approval status | Phase 1 Red execution approved; Phase 2 Green and implementation not approved |

## Inspected artifacts

- `tests/test_liss_0445_consumer_migration_red.py`
- `tests/fixtures/semantic_consumer_migration/ordinary_gate.sqx`
- LISS-0445 Issue, Spec, WP-0108, and Phase 1 trace
- ADR 0211 and `docs/collaboration/independent-review-perspectives.md`
- scientific semantic, pipeline, QASM, QPU, and Algorithm Plan consumers

## Verification evidence

`.venv/bin/pytest -q tests/test_liss_0445_consumer_migration_red.py` returned
**5 failed, 5 passed**, with no collection error. The five failures were
reviewed as four substantive migration gaps plus one authority-contract
assertion whose original form was too broad.

## Findings and disposition

| Priority | Finding | Disposition | Rationale/correction |
|---|---|---|---|
| P1 | Algorithm Plan test inferred duplicate executable authority from module identity alone. | accepted | Replaced the proxy with a consumer-boundary test: the compile-owned plan must be consumable through the provider-neutral plan projection API. |
| P1 | Phase 1 began with pre-existing production changes, so a clean production baseline could not be attributed to this phase. | accepted/documented | Added an explicit baseline boundary and reproducible commit/branch/path evidence to the Phase 1 trace; no claim is made that the earlier LISS-0444 production diff belongs to this phase. |
| P1 | Spec status said Architecture approval was still required while Issue/WP recorded Phase 1 Red approval. | accepted | Updated the Spec to `Accepted for Phase 1 Red — Phase 2 Green approval required`. |
| P2 | H1 Red test does not yet assert H1 structure/provenance after canonical dispatch. | deferred | This is a Phase 2 Green strengthening item; the current Red failure already proves the canonical result is absent. |
| P2 | Ordinary QASM Red test does not yet assert the full instruction payload/provenance. | deferred | The fixed test now asserts the representative `h q[0]` payload; full source/provenance conservation is a Green acceptance item. |
| P2 | Realize boundary test does not yet assert all method/order/steps/error-budget fields. | deferred | The Red contract proves bare `Limit` rejection and explicit `Realize` provenance; policy-field preservation belongs to the approved Green slice. |

## Reusable reviewer perspectives

- A Red assertion must test the architectural contract directly, not infer it
  from a proxy such as module location.
- A dirty-worktree baseline must be recorded before attributing production
  changes to a phase.
- Issue, Spec, WP, and trace status/approval fields must describe the same
  phase state.
- Red tests establish the migration boundary; complete provenance and payload
  conservation remain explicit Green acceptance criteria.

## Next review condition

Re-run the independent review against the corrected test contract and aligned
Issue/Spec/WP/trace. Do not begin Phase 2 Green until the fresh review is READY
and a separate typed Phase 2 approval is recorded.
