# LISS-0584 Phase 1 Red test review request

## Review Target

- Artifact: new acceptance tests and boundary fixture under
  [accepted R01–R07](../../specs/opaque-foreach-wire-arithmetic-repair.md).
- Current phase: Feature Path / phase-1-red.
- Requested approval/type: Phase 1 Red test review/acceptance (phase).
- Approved scope: LISS-0584 numeric Wire repair; Phase 0 accepted and explicit
  Phase 1 test creation/existing F05 adoption authorized on2026-10-05.
- Implementation allowed: no. Post-review required: yes. Execution batch: N/A.
- Decision: human `LISS-0584 Phase 1 Red テストレビュー／acceptance`
  accepts this unchanged packet on2026-10-06; no Phase 2 permission inferred.

## What Changed / Why

Added `tests/test_liss_0584_opaque_wire_arithmetic_red.py`,
`tests/test_liss_0584_repair_boundary_red.py` and
`tests/fixtures/liss_0584/repair-boundary.json`.
They expose the missing numeric Wire guard while protecting supported neighboring
behavior. No production, existing F05, lifecycle exclusion or baseline edits.

The exact existing F05 node is adopted in place, not copied:

```text
tests/test_liss_0583_static_foreach_successor_red.py::test_compile_opaque_arithmetic_and_observation_remain_rejected[Int i = q + 1]
```

The whole parameterized function is selected for review: its index/Measure/
Snapshot neighbors pass. New public binary tests deliberately omit its left-+
duplicate. The boundary fixture pins original test and transitive behavior
fixture bytes. SHA256 of the new candidate fixture:
`d0d2c74d0552fd31a6894ea7d2908e4ea506fd639e5d986c2ed40423f3fc4bd3`.
Fixture acceptance received with this unchanged packet on2026-10-06.

## Clause-to-Test Inventory

| Clause | Actual evidence | Result |
|---|---|---|
| R01 | `test_wire_operand_rejects_with_binary_source_diagnostic`: both sides × five operators; public `test_public_compile_rejects_other_wire_numeric_forms` plus original F05 | 10 direct + 9 new public + 1 original Red |
| R02 | `test_alias_nested_and_renamed_handles_remain_rejected`; numeric named q positive; State/Qubit positive | 4 Red; positive neighbors pass |
| R03 | Direct binary span/message assertions and public hard diagnostic/ok=False, including advisory-bearing sources | Red until missing guard exists |
| R04 | `test_legal_gate_operation_retains_all_ordered_qasm_members` H/X; original three observation/index neighbors | 5 pass |
| R05 | `test_non_wire_numeric_kind_payload_and_dimension_are_preserved` 10 cases; no-Wire foreach positive; existing numeric suites12 | all pass |
| R06 | `test_alias_kind_and_nested_loop_environments_do_not_leak`: actual Ty identity, outer env identity/restoration, no alias leak | 1 pass |
| R07 | Boundary/provenance tests6; existing repair/consumer/adjacent cohort74 | all pass; all-blocking suites not_run |

New behavior file:38 cases (23 Red,15 passing). Boundary file:6 passing.
Original function:4 cases (1 Red,3 passing). Total48 cases.

## Verification / Failure Comparison

HEAD `a287be51da358eed195f836afa21b07286128940` plus pre-existing0583/new584
dirty tests/docs, not a final committed SHA. Branch
`codex/liss-0584-opaque-wire-arithmetic-phase0`; cwd
`/Users/nn0cl/Documents/git/qpex`. macOS27.0.1 arm64, Python3.12.6
(`/usr/local/bin/python3.12`), pytest9.0.3. Exact commands in
[trace](../traces/2026-10-05-liss-0584-opaque-wire-arithmetic-repair.md).

- Initial author run44 cases:25 failed/19 passed. One positive fixture wrongly
  assumed Classical Int addition stays Int. Changed only that new fixture to
  `Float k = q + 1`, consistent with existing promotion; no acceptance weakening.
  Added four boundary projection/mutation cases afterward.
- Corrected author run48:24 failed/24 passed,0 errors/skips,0.406s,
  start2026-10-05T23:48:10.697193+09:00, exit1.
- Reviewer rerun48:24 failed/24 passed,0 errors/skips,0.396s,
  start2026-10-05T23:49:58.286576+09:00, exit1.
- Consumer/adjacent74 passed,0 errors/skips,25.138s,
  start2026-10-05T23:48:11.338959+09:00, exit0. Breakdown: repair37,
  consumer8, adjacent17, numeric12. Includes actual baseline capture byte
  comparison and five cold consumer imports, not mocked imports.
- All-blocking root/spec/sanity: not_run. No Green, merge-readiness or final-SHA
  claim. No new Red exclusion/waiver. Four existing0583 structural exclusions
  are unchanged and are not part of the584 focused selector.

All24 failures are the missing guard:23 new cases lack the required hard code;
the original F05 incorrectly compiles successfully. No collection/fixture error.
The initial positive fixture error is closed; existing tests were not edited.

## Same-Context Review / Findings

Host switched from author to reviewer, reread accepted spec, all new test/fixture
files and original adopted assertion, then reran the focused suite. Routing is
same_context (weaker than separate_context), host implementation; empty model
IDs, no enabled large-change override. No independent-review claim.

- Expected24 product Reds remain open for separately approved Green, not flaws
  to hide by skip/xfail or changed F05 assertions.
- `_infer_binop` body is the permitted AST projection hole; signature and all
  other TypeChecker AST are guarded, plus frozen runtime/compatibility/capture
  files. Mutation tests prove unrelated body/signature/shared-state changes are
  detected. Projection alone cannot prove the future body change is guard-only:
  R01–R06 and explicit Phase 2 diff review remain required.
- Local ownership separation is read-only exact-node adoption plus standalone
  new tests. Original0583 test/behavior files remain untracked, not a committed
  dependency. Before any commit/delivery, arrange a reviewed test-carrier
  dependency commit or agreed separation; never stage the entire dirty tree.
- Comparisons, arbitrary call/return escapes and global assignment redesign
  remain outside the accepted numeric scope; no comprehensive opacity claim.

Test preparation is internally consistent; human review/acceptance received2026-10-06.
Full blocking evidence is mandatory at Green/Refactor completion and must be
rerun after final commit under verification policy.

## Adjudicator Checklist / Decision

- [ ] Phase and numeric-only scope are correct.
- [ ] Existing F05 adoption, fixture provenance and branch dependency are accepted.
- [ ] Positive/negative coverage and omitted context are adequate for Phase 1.
- [ ] Verification limits and outstanding24 product Reds are understood.
- [ ] Approval is test acceptance only; implementation remains a separate gate.
- [ ] Post-review is required; no execution batch or lifecycle waiver applies.

- [x] Approved
- [ ] Approved with comments
- [ ] Rejected
- [ ] Needs ADR

## Acceptance Record / Historical Next Approval Target — 2026-10-06

Human names the sole preceding Phase 1 test acceptance target. Accepted scope:
R01–R07 mapped tests, original F05 read-only adoption and unchanged boundary
fixture. No test/production edit, exclusion, dependency-history waiver or
commit/delivery authorization. Prior results remain2026-10-05 evidence, not
fresh2026-10-06 test execution.

- Artifact: accepted R01–R07 and this reviewed test set.
- Current phase: Feature Path / phase-1-red, accepted; Phase 2 not started.
- Requested approval: Phase 2 Green/implementation (phase + implementation).
- Approved scope: numeric Wire repair only; preserve reviewed assertions.
- Implementation allowed: no until explicit approval. Post-review: yes. Batch: N/A.
- Open: reviewed test-carrier dependency/separation before commit/delivery;
  full blocking verification and final-commit reruns later remain mandatory.

Subsequent explicit Phase 2 implementation approval received2026-10-06.
[Current verification/handoff](2026-10-06-liss-0584-phase2-verification.md)
records focused Green and an unresolved sanity/committed-dependency gap;
Phase 3 not started. The accepted tests above remain unchanged.
