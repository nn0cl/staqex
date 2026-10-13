# LISS-0588: Evaluator closed-expression eligibility successor

## Metadata

- Local issue ID: LISS-0588
- GitHub issue: none
- Status: done — local result accepted; acceptance-record verification pending at commit; remote delivery pending
- Phase: phase-3-refactor
- Type: behavior-preserving responsibility extraction
- Priority: WP-0174 rank6, next cohesive slice
- Initial planning size: M
- Current planning size: M
- Reclassification reason: none
- Owner/agent: Codex desktop host
- Related branch: `codex/liss-0588-closed-expression-phase0`

## Summary / acceptance notes

Scope / Phase0 design-start explicitly approved2026-10-13 for `_is_closed`
only. Accepted [C01–C09](../specs/evaluator-closed-expression-successor.md)
extracts the classifier, preserving live scalar/object membership, lazy unit
lookup, recursive private-hook dispatch and short circuit. State remains in
Evaluator. Scalar capture is not included; no semantic cleanup is authorized.
Dedicated Issue/spec C01–C09, bounded guard transition and Phase0 acceptance
explicitly approved2026-10-13. Phase1 Red acceptance-test creation / bounded
guard migration execution explicitly approved2026-10-13.
Phase1 agent test review passed and human exact-test acceptance explicitly
approved2026-10-13. Phase2 Green / implementation explicitly approved2026-10-13;
implementation allowed:yes, C01–C09 only. Local commit d6f70a3f all blocking
passed; Phase3 Refactor/review explicitly approved2026-10-13 and agent review
passed. Source/tests unchanged. Final review-record commit/actual-SHA
verification approved2026-10-13 and passed atbc92d145. Human final-result
acceptance explicitly received2026-10-13. Acceptance-record commit/revalidation
explicitly approved2026-10-13, result pending at commit. Remote delivery separate.

Base: a19cc974a4e0200d74ae012c9b76d2a8f4d18b0a, latest fetched main.
ID assigned after inspecting existing issue filenames and metadata claims;
0588 unclaimed. A historical reference to0602 is not a metadata ID claim and
does not justify reusing any existing/skipped ID.

## Dependencies

- Parent: WP-0174 / WP-0160
- Depends on: delivered LISS-0587; PR611 implementation and PR612 record delivery
- Blocks: no named issue currently declared
- Related: future `_maybe_capture_classical_scalar` scope, not approved here

PR612 merge is the base above; product/record CI completion already verified
in prior delivery evidence. No dependency waiver or repeat delivery is needed.

## AI planning record AIP-0588-001

- Status: accepted by dedicated Issue/spec and Phase0 acceptance2026-10-13
- Created:2026-10-13; agent/environment:Codex desktop local macOS workspace.
- Displayed model/reasoning:N/A; stable host model and setting not exposed.
- Planning size:M; related source, private consumers and inherited guard chain.
- Intended route:host Phase0 and later authorized implementation; review
  same_context, empty model IDs, no enabled conditional override.
- Intended scope:exact28-line classifier relocation and narrow context contract.
- Estimated token range/midpoint/metric:N/A; no calibrated estimator.
- Basis:four external invocation sites, recursive live hook and old guard/copy
  consumers; scope small but verification spans related owners.
- Assumptions:preserve existing node classification even where conservative or
  permissive; dynamic consumer inventory is incomplete.
- Confidence:high in static source inventory, limited in dynamic closure.
- Revises / revision reason / superseded by:none.

## Adjudicator decision points

- Dedicated Issue/spec C01–C09, exact limited guard-carrier migration policy
  and Phase0 design accepted2026-10-13; execution is not inferred.
- Later separately authorize Phase1, review exact tests, Phase2 implementation,
  Phase3 review, final commit/verification and remote delivery.
- Stop for a reviewed amendment if extra protected owners appear; never weaken
  a guard or change a baseline to complete this extraction.

## Adjudicator review target

- Artifact:C01–C09 minimal two-file source move, unchanged accepted11 test
  artifacts and [Phase3 review](../collaboration/reviews/2026-10-13-liss-0588-phase3-review.md).
- Current phase:phase-3-refactor; final verification passed at cleanbc92d145,
  human final-result acceptance received. Local accepted work recorded done;
  acceptance-record commit/revalidation approved, result pending at commit.
- Requested approval:after successful accepted-record verification, remote
  push/PR/CI/successful-CI merge.
- Approval type:delivery phase, not granted; record commit/revalidation granted.
- Approved scope:existing `_is_closed` relocation exactly as C01–C09.
- Implementation allowed:no new source/test work in this acceptance action.
- Post-review required:yes; separately authorized acceptance-record verification
  and delivery gates. No approval inferred from tests.
- Execution batch ID:not applicable.
- What changed:seven new test/helper/fixture files and exactly four allowed
  guard carriers in Phase1; Phase2 adds closed_expressions.py and replaces only
  the Evaluator classifier body/private import. Accepted tests unchanged.
- Why it matters:separate eligibility from evaluation without duplicate state
  or losing private consumer compatibility and historical guard protection.
- Adjudicator checklist:confirm boundary, C01–C09 minimum cases, retained
  semantics, included/omitted context, exact guard scope, verification plan,
  deferred phases and explicit bounds of Phase2 implementation permission.
- Decision:human accepted dedicated Issue/spec C01–C09, bounded guard transition
  policy and Phase0 acceptance2026-10-13. Phase1 test-only execution approved;
  Agent Red test review passed; human Red test acceptance approved2026-10-13;
  Phase2 Green / implementation subsequently explicitly approved2026-10-13.
  Local commit / actual-SHA all-blocking revalidation subsequently explicitly
  approved2026-10-13. Phase3 Refactor/review explicitly approved2026-10-13;
  agent review passed. Final record commit/actual-SHA verification explicitly
  approved2026-10-13 and passedbc92d145. Human final-result acceptance explicitly
  received2026-10-13. Acceptance-record commit/revalidation explicitly approved
 2026-10-13. No new ADR or delivery inferred.

## Context / verification / handoff

Included:target method and actual consumer/guard dependencies, current policies
and lessons. Omitted:Rust, providers, type-system redesign, scalar capture and
unrelated features. No new technology or changed architecture premise.
Design-only evidence and next-safe-action record:
[trace/handoff](../collaboration/traces/2026-10-13-liss-0588-closed-expression.md).
No runtime tests or baseline root run in Phase0. Phase1 evidence recorded
there; uncommitted design is not final-SHA Green evidence.
Process review:closure-time check after local status synchronization recorded
below. Local accepted slice done subject to accepted-record verification;
remote delivery and WP completion not claimed.

## Phase1 clause-to-test inventory / execution evidence

New suites use prefix `tests/test_liss_0588_closed_` and suffix `_red.py`.
Node names below omit repeated `test_c` prefix only where family is clear;
full function names are in the files. Counts are pytest cases, not independent
implementation gaps or proof of complete behavioral coverage.

| Clause | Minimum mapped tests / retained evidence |
| --- | --- |
| C01 | behavior::test_c01_literals_and_unsupported_nodes_do_not_read_or_descend (9 cases) |
| C02 | behavior::test_c02_membership_not_value_truth_or_type (5); test_c02_c05_live_mutation_replacement_and_owner_isolation |
| C03 | behavior::test_c03_math_aliases_win_before_environment_reads (3), test_c03_registered_math_and_object_fields_do_not_validate_fields (2), test_c03_numeric_unit_membership_only (7), test_c03_c07_unit_table_is_live_and_access_is_branch_lazy |
| C04 | behavior::test_c04_nested_recursion_and_operator_spelling (3), test_c04_c05_instance_hook_order_short_circuit_and_exact_return (2), test_c04_subclass_recursion_and_hook_errors_propagate, test_c04_membership_errors_propagate (2) |
| C05 | above live-owner and recursive-hook tests; behavior::test_c05_no_expression_state_or_joint_mutation_and_no_evaluation |
| C06 | consumers::test_c06_actual_execution_single_tuple_capture_and_dirac; test_c06_actual_dirac_constant_and_pushforward_paths (2); test_c06_actual_factory_scalar_and_local_object_fallback (2); seven immutable adjacent suites (26 cases) |
| C07 | ownership::test_c07_successor_owns_exact_algorithm_and_protocol, test_c07_old_algorithm_absent_and_exact_class_assignment, test_c07_runtime_class_and_bound_instance_identity, test_c07_both_cold_requested_import_orders_and_actual_consumers; behavior live/lazy-unit test |
| C08 | ownership::test_c08_unaffected_evaluator_ast_and_exports_still_protected (2), test_c08_readonly_sources_adjacent_tests_and_prior_fixtures (29 readonly paths); independent immutable-Git whole-AST probe |
| C09 | guard_migration::test_c09_real_guard_and_four_actual_copy_fixtures (2), test_c09_real_guard_rejects_algorithm_protocol_dependency_and_hook_mutations (13), test_c09_missing_duplicate_and_extra_state_rejected (5), test_c09_retained_old_body_and_original_foreach_mutation_setup (2), test_c09_original_fixture_is_immutable, test_c09_persistent_byte_guards_still_reject_changes (5) |

Focused execution:73 passed /4 intended structural Red (77 total).
All four failures are the named C07 ownership nodes. Three require the absent
successor; one requires old-body removal. Four nodes are not four root causes.
Characterization37, actual consumers5, C08 preservation3 and guard28 all pass.
Existing0582–0587 suites341 passed; adjacent26 passed; spec161/161 PASS.
Consumer import smoke and independent Git provenance passed. Root result and
exact tested dirty-state/commands/timings live in the trace/external evidence.
No collection errors or new exclusions in the focused run.
Root:2694 passed /the same4 C07 structural Red,334.16s,exit1; no other
failures/errors/skips/exclusions observed in that run. Full pristine-base root
comparison was not run. Sanity9 passed/copy-smoke fails because the new spec
is uncommitted; no all-blocking Green claim. Environment:macOS27.0.1 arm64,
CPython3.12.6/pytest9.0.3; HEAD/base a19cc974, dirty test/docs tree.
Evidence:`/private/tmp/liss-0588-red.2OSDVf/result.md`.
All11 artifact fingerprints verified unchanged after root execution.

Initial focused run had one erroneous characterization setup failure: a
short-circuit rhs-raising hook was reused for UnitConvert, whose child must
always be called. Split the conversion hook, retained the initial log and
reran the full focused suite. No production correction or assertion weakening.

New test-only files:four suites above, `tests/liss_0588_guard_support.py`,
and immutable `tests/fixtures/liss_0588/{original-closed.txt,readonly-boundary.json}`.
Existing edits are exactly the four carriers named in accepted C09.
All prior fixture bytes/hashes/semantic assertions and production unchanged;
guard projection adds exact reconstruction before the old chain. Temporary
post-move AST is never imported. No clean-SHA or all-blocking Green claim.

## Phase1 agent test review —2026-10-13

Explicit review execution authorized; same_context reviewer re-read actual
artifacts and produced [review packet](../collaboration/reviews/2026-10-13-liss-0588-phase1-red-review.md).
No blocking findings. Rerun focused73 pass/same4 structural Red2.93s,
adjacent26 pass5.68s; independent future-shape inherited setup15 pass and
immutable-Git provenance29 paths pass. All11 reviewed fingerprints unchanged.
Whole-root/spec/full inherited/sanity results above re-read, not rerun in this
review; no all-blocking Green or clean-SHA claim. Human exact-test acceptance
subsequently approved2026-10-13; separate Phase2 implementation permission
pending. Tests/source unchanged.

## Human Phase1 acceptance —2026-10-13

Explicit `LISS-0588 Phase 1 Red テストレビュー／acceptance承認` accepts the
reviewed C01–C09 test set and bounded guard carriers unchanged. All11 artifact
hashes match `/private/tmp/liss-0588-red.2OSDVf/test-fingerprints.log` at receipt.
Approval synchronization changes records only; no new runtime test run, full
Green, commit or delivery claim. Current phase remains phase-1-red accepted;
Issue ready for separately authorized Phase2, not done.

## Phase2 implementation / provisional verification —2026-10-13

Phase2 Green / implementation explicitly approved; only evaluator.py and new
evaluation/closed_expressions.py changed in production. Original28-line
algorithm moved to54-line owner with narrow read Protocol; facade976→950.
Same normal bound-method identity/live recursion/lazy units; no semantic cleanup.
All11 accepted tests/helper/fixtures/carriers unchanged, hashes confirmed.
Installed function independently equals immutable Git + approved transforms;
whole unrelated facade AST and29 readonly paths preserved.

Focused77 pass3.59s; inherited341 pass12.13s; adjacent26 pass5.98s; consumer/
cold-import/identity smoke7 pass0.48s; root2698 pass344.20s; spec161/161 PASS.
Sanity9 pass/copy-smoke FAIL on uncommitted distributed spec; PR-only traceability
N/A. No other test failures/errors/skips/exclusions observed; spec aggregate
skip count unreported. Prior dirty Red root's four C07 failures now pass;
pristine-base full-root comparison not available.

HEAD/base a19cc974a4e0200d74ae012c9b76d2a8f4d18b0a, dirty source/tests/docs,
macOS27.0.1 arm64 / CPython3.12.6 / pytest9.0.3. Provisional evidence:
`/private/tmp/liss-0588-red.2OSDVf/green-result.md` and per-run green-*.json/log.
No all-blocking Green, final committed-SHA or Phase2 completion claim.
Next approval:local commit of scoped0588 artifacts / actual-SHA all-blocking
revalidation, then separately Phase3 review. No commit/remote delivery performed.

## Authorized local commit / actual-SHA verification

Human `LISS-0588 ローカルコミット／実SHAで全blocking再検証承認` received2026-10-13.
Persist the exact19 scoped files:two production,11 accepted test/helper/fixture/
carrier and six design/review/ledger/trace/lesson records. No source/test changes
in this action; all accepted hashes and source hashes match prior evidence.
At this record's commit, actual-SHA results are pending; live external entry:
`/private/tmp/liss-0588-sha-verification.xfHtgc/result.md` with per-run SHA and
clean-state evidence. Previous provisional failure/results above are historical.
Issue remains phase-2-green/in_progress, not done. If all declared blocking
suites pass at that SHA, next gate is separate Phase3 Refactor / review approval;
otherwise retain the actual failure as blocking. No push/PR/merge authority.

## Current Phase3 review / next gate —2026-10-13

Human Phase3 Refactor/review approval received. Agent same_context review
passed with no blockers; weaker isolation than separate_context. Actual source
and accepted11 artifact hashes unchanged. No extra refactor warranted.
Fresh clean d6f70a3f verification:focused77, inherited341, adjacent26,
consumer/cold/identity7, root2698(341.32s), spec161 and sanity10 all passed.
Immutable Git algorithm/full unaffected facade AST and29 readonly paths PASS.
No exclusions; pristine-base full-root comparison/dynamic external closure
unavailable, not a universal compatibility proof. See linked Phase3 packet and
external phase3-*.json/log. Previous pending-Phase3 statements are historical.
Current records are uncommitted; they do not change the tested source. Next:
separate final verification / record commit / actual-SHA all-blocking approval,
then final human acceptance and remote delivery. Issue remains open, not done.

## Authorized final record commit / verification —2026-10-13

Final verification / six review-record commit / actual-SHA all-blocking rerun
explicitly approved. No source/test changes; accepted11 artifacts unchanged.
Current result pending at record commit; live entry:
/private/tmp/liss-0588-final-verification.5ZlUe9/result.md.
After all blocking pass,next human gate:final-result acceptance, then separately
delivery. Prior pending-final-verification notes are historical. Status remains
review/phase-3-refactor, not done; no completion process review or remote write.

## Human final-result acceptance / current gate —2026-10-13

Explicit `LISS-0588 最終レビュー結果の受入れ` accepts the Phase3 packet and
final actual-SHA result unchanged. Testedbc92d145df21aa21be031a6e058181a8a4aefad3
passed root2698/spec161/sanity10 plus focused77/inherited341/adjacent26/
consumer7,Git provenance and reviewed hashes. Evidence:
/private/tmp/liss-0588-final-verification.5ZlUe9/result.md.
No assertion/fixture/exclusion/source/acceptance-clause change. Same-context
review limitations/dynamic external/baseline gaps remain as accepted in packet.

Acceptance-time same-context process check inspected named approval gates,
dedicated branch, bounded test changes, trace, effective routing, final commit
evidence and synchronized Issue/spec/WP records. No new reusable lesson or
upstream feedback indicated; existing lessons applied.
Process review: no operating-contract deviation or operational problem found.
This is not a done/remote-delivery claim; reapply process review after final
status synchronization and committed acceptance-record verification.

Current action changes five related records only:Issue,spec,WP,Phase3 packet,
trace. They are uncommitted; no fresh runtime run or new-SHA Green inferred.
Next request:acceptance-record commit / actual-SHA all-blocking revalidation.
Remote delivery remains separate; no push/PR/merge or additional implementation.

## Authorized acceptance-record commit / local closeout —2026-10-13

Explicit acceptance-record commit / actual-SHA all-blocking revalidation
approved. Persist exact five records:Issue,spec,WP,Phase3 packet,trace;
no source/test/fixture/assertion/exclusion/lesson/routing changes.
Local accepted slice recorded done, not delivered; current commit's result
pending at record commit. Actual SHA/clean-state/outcome entry:
/private/tmp/liss-0588-acceptance-verification.n0GRQZ/result.md.
Previous verifiedbc92d145 remains valid predecessor evidence, not new-SHA proof.
After this commit,every blocking suite and focused/inherited/adjacent/consumer/
immutable Git/accepted hash checks rerun. Failure remains blocking,never waived.

Same-context completion process review after status synchronization rechecked
phase/path/typed approvals,dedicated branch,bounded accepted artifacts,trace,
effective review isolation,final-SHA policy and local-versus-delivery status.
Process review: no operating-contract deviation or operational problem found.
No new reusable lesson/template feedback indicated; existing final-commit,
hash/private-consumer and status-drift lessons remain applied. Reconfirm this
process outcome against post-commit verification externally before reporting
local completion; do not create a later unverified evidence-only commit.
After successful verification,next gate:separate push/PR/CI/successful-CI merge
authorization. No main merge,remote CI success or whole-WP completion claimed.
