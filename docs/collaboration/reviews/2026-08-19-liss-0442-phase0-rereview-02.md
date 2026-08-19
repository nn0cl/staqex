# Independent context re-review: LISS-0442 Phase 0 correction

| Field | Value |
|---|---|
| Trigger | Fresh review after the first NOT READY correction cycle |
| Context | Independent read-only reviewer context `01a019b3-4f3d-7b72-887e-1689cbb95985` |
| Branch | `codex/liss-0438-residual-reconciliation` |
| Scope | Current LISS-0442 Issue/Spec/WP, review/trace, S02, SV-09, ADR 0210 |
| Verdict | **NOT READY** |
| Implementation approval | Not granted |
| Terminal state | `NOT READY`; another correction/re-review cycle is required |

## Findings

1. **P0 — incorrect corpus count.** The current SV-09 list contains 26
   entrypoints (15 Basics + 11 Applied), plus one README case. The documents
   incorrectly stated 31 (15 + 16). Evidence: `tests/spec_verification/suites/
   sv09_examples.py:19-51` and the LISS-0442 Spec corpus table. Lenses: 1, 7,
   9. Disposition: accepted.
2. **P1 — inventory contract still needs per-row completeness.** The
   representative table does not give every required execution result,
   provenance, diagnostic boundary, and baseline-preservation result for every
   row. Evidence: Spec inventory contract versus representative table. Lenses:
   1, 3, 6, 7. Disposition: accepted; expand in the next correction.
3. **P1 — Host key/prose discrepancy.** README uses semantic predicate
   `diversity_at_least`; source and Host use `host("diversity")`. Evidence:
   `examples/showcase/S02_drug_discovery/README.md:36-38`,
   `main_selection.sqx:82-87`, and `host/run_selection.py:59-60`. Lenses: 2,
   3, 9. Disposition: accepted as a documented gap; no source change in Phase 0.
4. **P1 — command evidence overclaimed.** The 0402/0403 files do not execute
   pytest assertions when run as plain scripts, and pytest is unavailable.
   Evidence: `python3 -m pytest --version` fails; the test files lack a direct
   runner. Lenses: 1, 7, 9. Disposition: accepted; execution status is being
   narrowed to what was actually verified.
5. **P1 — review record metadata incomplete.** The first review record lacked
   required branch, phase, allowed/excluded paths, disposition authority,
   deterministic checks, and terminal-state fields. Lenses: 8, 9.
   Disposition: accepted; metadata is being added.

## Confirmed boundaries

No finding requires Phase 1 Red, implementation, an ADR change, numerical S02
migration, Provider SDK work, or live QPU submission. The accepted corrections
remain documentation/evidence-only.

