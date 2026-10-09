# LISS-0585 Phase 1 Red execution / test review entry

This is an execution handoff, not an agent-review pass or human acceptance.
Historical initial execution below: subsequent R1/R2 corrections add two
guard-fixture cases. [Current re-review](2026-10-09-liss-0585-phase1-review.md)
passes with168pass/4expected structural Red; human acceptance pending.

## Review target

- Artifact: [accepted T01–T09 spec](../../specs/evaluator-tensor-binding-successor.md),
  three new acceptance suites and bounded shared guard-support diff
- Current phase: Phase 1 Red executed; test review pending
- Requested approval: LISS-0585 Phase 1 Red test review / acceptance
- Approval type: phase (test review / acceptance only)
- Approved scope: one Tensor family, exact hook wiring and test-only guard migration
- Implementation allowed: no
- Post-review required: yes; Green needs separate implementation approval,
  followed by Refactor, final verification and separate delivery permission
- Execution batch: none

## What changed / allowed paths

- `tests/test_liss_0585_tensor_behavior_red.py`: T01–T06 and actual dispatch;
  29 characterization cases against the real current private hook.
- `tests/test_liss_0585_tensor_ownership_red.py`: four structural acceptance
  nodes for successor ownership, old-body absence, installed identity/setup,
  and actual successor algorithm conservation.
- `tests/test_liss_0585_tensor_guard_migration_red.py`: 28 positive/negative,
  immutable-evidence and adjacent-byte cases using real inherited guards.
- `tests/liss_0585_guard_support.py`: exact Tensor projection and immutable
  algorithm comparison, test-only,120physical lines.
- `tests/liss_0583_guard_support.py`: imports and two parse/projection entry
  calls only; all existing baseline comparisons remain intact. Context
  projection and API/call sites unchanged. This is the only existing test file
  changed; existing acceptance test assertions remain unchanged.
- `tests/fixtures/liss_0585/original-tensor-method.txt`: new immutable dedented
  main a349a5b7 method evidence, SHA256
  `8fc41a4cfb69c3dfca1c6f5b29a9eef8f764dc862d65ed32f74173a9ade0cb0f`.
- Issue/spec/WP/representative trace: phase/status/evidence synchronization.

No production file, previous fixture, previous assertion or active-Red manifest
changed. New successor bodies exist only as AST/text inside pytest temporary
copies to exercise authorized guard positives; never in production paths.
No commit, push or PR performed. All changes remain uncommitted.

## Clause-to-test matrix

Names below refer to the new behavior suite unless otherwise qualified.

| Clause | Exact evidence family |
|---|---|
| T01 | `test_t01_output_arity_rejects_before_callbacks`; `test_t01_alias_arity_and_single_name_diagnostics` |
| T02 | `test_t02_relabel_preserves_correlations_complex_amp_and_phases_without_mutation` |
| T03 | `test_t03_missing_coordinates_at_later_world_leave_input_unchanged`; `test_t03_empty_var_joint_does_not_bind_independent_sides` |
| T04 | `test_t04_live_callback_receives_fresh_units_original_expr_and_left_right_order`; `test_t04_callback_error_propagates_at_original_sequence_point` |
| T05 | `test_t05_product_order_amp_and_existing_independent_phase_handling`; `test_t05_duplicate_assignments_coalesce_and_cancel`; `test_t05_both_callbacks_run_before_empty_support_check` |
| T06 | `test_t06_relabel_name_collisions_follow_existing_assignment_order`; `test_t06_independent_identical_output_names_keep_right_assignment` |
| T07 | `test_t07_actual_bind_names_preserves_overridable_private_hook` (TensorExpr + alias); ownership suite's three `test_t07_*` nodes (Red) |
| T08 | Unchanged `test_liss_0582_public_import_repair_red.py`: actual frozen public manifest/identities, cold imports, rejection identity and private rational consumer; existing Joint/qudit source execution and ASCII/Mix/semantic tensor neighbors |
| T09 | ownership `test_t09_actual_successor_algorithm_is_original_except_declared_ownership_changes` (Red); all28 migration cases; inherited0582/0583/0584 preservation and TypeChecker tests |

## Old protection → successor assertion mapping

| Existing protection | Maintained or new evidence |
|---|---|
| Historical unaffected evaluator AST / imports | Shared checks still compare original hashes after reconstructing only the exact old Tensor method at `_eval_times`; unrelated-body, export, state, old-foreach-setup mutations rejected |
| Retained old Tensor algorithm | Original method stays part of old AST if unextracted; modified current body rejected. New immutable method plus canonical algorithm assertion constrain the actual future body |
| Historical unaffected compatibility AST | Only exact new Tensor import/installer stripped; wrong/duplicate mappings, old hooks, extra state rejected |
| Existing foreach positive/negative scope | All existing suites unchanged, rerun; new mutation cases retain foreach setup/mapping rejection |
| Context, binding and TypeChecker | No source/context projection change; binding/context new byte checks, existing TypeChecker preservation suite unchanged |
| Five readonly byte dependencies | Existing repair checker unchanged; each new mutation case still rejects a change |
| Original0583/0584 JSON/provenance/metadata | Original hash checks unchanged; new explicit fixture byte assertions; existing metadata/mutation suite rerun |
| Non-vacuous guard effectiveness | Current and authorized-extracted shapes both pass through real shared/readonly checks; unauthorized negatives pass alongside those positives |

Limits: evaluator/compatibility protection is executable AST, not comment-byte
identity. The source projection alone does not inspect a successor file;
actual-file ownership/algorithm checks and the test-copy composite explicitly
cover missing or altered successor. This pairing remains mandatory in Green.
No guard bypass, blanket extraction allowance or historical hash refresh.

## Verification result

Baseline SHA/HEAD: a349a5b720c59f3a0e288c4751dd012c25514843; dirty test/docs tree,
cwd `/Users/nn0cl/Documents/git/qpex`, Python3.12.6 / pytest9.0.3,
macOS27.0.1 arm64 (uname Darwin27.0.0). Results are provisional uncommitted
Phase1 evidence, not final-SHA completion evidence.

- New characterization/dispatch:29passed.
- New guard migration:28passed.
- Structural ownership:4expected Red; failure IDs are the four exact test
  functions in the ownership suite. No import-collection error after setup fix.
- Existing scoped baseline/consumer/adjacent:109passed, same selectors as Phase0;
  no new/resolved failures in that comparable set.
- Combined execution:166passed /4failed,170collected, errors/skips/exclusions0,
  exit1 in3.25s; final rerun identical counts in3.16s. Final rerun UTC
  2026-10-08T19:35:15.346877Z–19:35:18.758828Z (2026-10-09 JST).
  New guard authorized positives and mutations all pass together.
- `git diff --check`:passed; test lifecycle validator:passed, entries0.
- All-blocking root/spec/Repository sanity:not_run. Four new Red nodes are not
  excluded; CI/root Green cannot be claimed until implemented or a separate
  precise lifecycle disposition is approved. No previous failure hidden.

Initial setup had one collection ImportError from the mistakenly named
`bind_one` test import. Inspection identified the actual existing entrypoint
`bind`; only test setup corrected and rerun. Spec inventory label corrected to
the same real name without changing its accepted single-name rejection rule.
This setup failure is not counted as a product Red or semantic regression.

## Adjudicator checklist / decision

- [ ] Phase1-only changes and exact guard-support allowed paths are acceptable.
- [ ] Clause-to-test inventory and old-protection mapping are sufficient.
- [ ] Included context and omitted rank5/6/Rust context are acceptable.
- [ ] Four structural Red nodes are distinguished from109 passing neighbors.
- [ ] AST-vs-byte limits and unassessed external/dynamic consumers are understood.
- [ ] Tests/fixture/projection accepted unchanged; implementation permission no.
- [ ] Post-review Green/final/delivery gates remain separate.

Decision pending: approved / approved with comments / rejected / needs ADR.
No same-context agent-review pass is claimed in this execution-only packet.
