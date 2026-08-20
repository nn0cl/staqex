# Independent Context Review — consumer-wide migration Phase 1 Red

| Field | Value |
|---|---|
| Trigger | User-approved Phase 1 Red for LISS-0444/WP-0107 |
| Scope | Red acceptance tests and their current production boundaries |
| Excluded | Production implementation, Phase 2 Green, provider/live QPU, S02, solver work |
| Verdict | **READY** for Phase 1 Red; Phase 2 remains unapproved |
| Verification | 4 failed, 2 passed; no collection errors; `git diff --check` passed |

## Findings and disposition

| ID | Priority | Finding | Disposition |
|---|---:|---|---|
| CM-01 | P1 | Fallback test must detect actual AST lowering, not only warning text | accepted / resolved; monkeypatches `lower_unit_to_circuit` |
| CM-02 | P1 | Binder test needs canonical positive evidence | accepted / resolved; compares canonical and QPU binder projection before blocking AST re-lowering |
| CM-03 | P1 | `symbolic_ir` retirement must be separated from positive canonical connection evidence | accepted / resolved; tests are now independent |
| CM-04 | P1 | Source-variable rename must preserve provenance | accepted / resolved |
| CM-05 | P2 | Old helper-name check is supplemental rather than exhaustive | deferred; broad AST-derived helper inventory belongs to Phase 2 |

## Red contract result

The four failing assertions expose the current remaining paths: QASM AST
fallback, old QPU projection helpers, diagnostic-time AST binder lowering, and
live `symbolic_ir` generation/publication. Two positive assertions confirm that
canonical QPU/inspection connections and renamed-source provenance remain
observable while the retirement assertions are Red.

## Reusable perspectives

Contract and acceptance completeness; canonical authority and implementation
reality; projection conservation and authority reachability; realization and
fail-closed behavior; migration/regression safety; phase discipline; evidence
hygiene.

## Terminal state

`COMPLETE` for the Phase 1 Red review loop. Phase 2 Green requires a separate
typed user approval and must use this reviewed Red contract.
