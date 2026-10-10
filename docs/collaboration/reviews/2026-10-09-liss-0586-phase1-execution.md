# LISS-0586 Phase 1 Red execution / test-review entry

## Review target and authority

- Artifact: accepted [H01–H09 specification](../../specs/evaluator-host-coefficient-resolution-successor.md),
  the three new suites, original Host fixture, exact test-only projection and
  three bounded integration edits listed below.
- Current phase: Phase1 Red, execution authorized by human
  `LISS-0586 Phase 1 Red（受入テスト作成・限定guard移行）の実行承認`.
- Approved scope: acceptance tests / immutable Host evidence / limited guard migration.
- Requested next approval: Phase1 Red test review / acceptance, including the
  explicit H04 unreachable name-only disposition below.
- Implementation allowed:no. Post-review required:yes, human test acceptance
  followed by separate Phase2 Green / implementation approval. Batch:none.
- This is an execution packet, not an agent-review pass or human test acceptance.

## Results and evidence

At HEAD `a661fb1778e97eda3d35fd1615fd8928c031f062` plus uncommitted test/docs edits,
cwd `/Users/nn0cl/Documents/git/qpex`, local macOS arm64, Python3.12.6,
pytest9.0.3. Commands use `/usr/local/bin/python3.12 -m pytest -q ...`;
logs saved with pipefail+tee under `/private/tmp/liss-0586-red.gWkRtY`.

| Scope | Result | Exit | Evidence |
|---|---|---:|---|
| New behavior / ownership / migration suites |56passed /4expected structural Red,3.16s |1 |new.log |
| Inherited0583 /0584 /0585 preservation suites |63passed,2.06s |0 |inherited.log |
| Existing Host consumers and scientific/binder neighbors |31passed,5.74s |0 |consumer-adjacent.log |

No errors/skips/deselections in final selections. Only the four new ownership
nodes failed: successor ownership, original-body absence, installed hook identity,
actual moved algorithm. Missing successor assertions are inside test functions,
not collection failures. They are four contract nodes, not four independent
root causes. All behavioral characterizations and positive/negative guard cases
pass. Root/spec/all-sanity not_run; no full Green claim. ActiveRed remains0;
no exclusion was added, so root would presently include these expected failures.

The final inherited command selects:
`test_liss_0583_repair_boundary_migration_red.py`,
`test_liss_0584_repair_boundary_red.py`,
`test_liss_0585_tensor_guard_migration_red.py`.
Consumer/adjacent command selects:
`test_host_coefficient_tensor_red.py`,
`test_liss_0406_host_coefficient_tensor_evaluator_wiring_red.py`,
`test_liss_0407_operator_resolution_unification_red.py`,
`test_liss_0434_factory_scalar_domain_and_attr_coefficient_red.py`,
`test_liss_0327_host_input_port_red.py`,
`test_scientific_input_contract_red.py`,
`test_scientific_typed_bindings_red.py`,
`test_finite_binder_compatibility_facade.py`.
Only0586ownership produces the four expected failing node IDs. Compared to the
Phase0 selected baseline, reused cases remain passing; whole-root failure
comparison unavailable because root was not rerun.

## Clause-to-node reconciliation

Node prefixes below use `tests/test_liss_0586_host_behavior_red.py` unless noted.
Parameterized functions represent their complete listed case sets.

| Clause | Exact named evidence |
|---|---|
| H01 |`test_h01_no_placeholder_never_reads_or_merges`, `test_h01_no_main_never_reads` |
| H02 |`test_h02_order_deduplication_and_extra_inputs`, `test_h02_missing_repeated_key_is_not_cached` |
| H03 |`test_h03_nested_dtype_and_fresh_live_port` Float/Bool cases |
| H04 |`test_h04_error_code_message_class_and_cause` nine invalid cases; `test_h04_blank_key_preserves_provenance_validation`; `test_h04_later_validation_precedes_earlier_missing_merge_error`; valid neighbors H03/H05 |
| H05 |`test_h05_tensor_arguments_and_real_merge`, `test_h05_merger_first_diagnostic_and_message`, `test_h05_successful_merge_result_is_returned_without_copy` |
| H06 |`test_h06_missing_port_or_none_fails_closed`, `test_h06_same_key_later_shape_rejection`, `test_h06_same_key_mixed_dtype_preserves_first_declaration` both orderings, `test_h06_port_exception_is_not_converted` |
| H07 |`test_h07_live_hook_before_lowering_and_evaluator_owned_arrays`, `test_h07_resolution_failure_stops_lowering`; unchanged real0406/0407 execution tests and0434 Bool selection integration |
| H08 |`test_h08_cold_public_private_consumer_smoke`; all three `test_h08_*` in ownership suite; inherited import/export guards |
| H09 |ownership `test_h09_actual_algorithm_matches_immutable_original`; all26cases in host_guard_migration suite; all63inherited guard cases |

H04 name-only error is unreachable through an unmodified real resolver:
blank/whitespace Host key first constructs `InputProvenance`, which rejects
the input_id before `CoefficientTensor.__post_init__` can report NAME_ERROR.
The real blank-key test protects that precedence, and immutable algorithm
comparison protects unchanged constructor use. Do not monkeypatch this into a
fabricated reachable product scenario or change production to satisfy it.
Request explicit test-review acceptance of this unreachable subcase disposition;
it is not silently omitted. Existing scientific-input validator remains read-only.

## Limited guard integration and test setup

- New `liss_0586_guard_support.py` restores only the original Host method,
  exact private import/setup and installer mapping. It enforces moved algorithm,
  same relative dependency targets, shared diagnostic import, one declaration-only
  context, no module state or evaluator dependency. Its128lines are test-only.
- `liss_0583_guard_support.py`: add Host projection imports and two delegations
  before unchanged Tensor/foreach projections. No digest/assertion removal.
- `test_liss_0583_repair_boundary_migration_red.py`: five setup lines copy a
  present Host successor into temporary dependency roots.
- `test_liss_0585_tensor_guard_migration_red.py`: five analogous copy lines only.
  Existing mutation/assertion nodes retained unchanged.
- Original Host fixture42lines is dedented source from a661fb17:421–462,
  hash db4ab0b67131655cc42649fcbce5f8cf6cd8870bcba14a83ae9695aa70008ad8.
  Restorer reinstates the four docstring-literal spaces lost by source dedenting;
  full original method AST equality passes. Original evidence file never refreshed.
- New temporary AST proposals are not imported or copied into production.
  Current/historical Tensor × pre/post Host shapes assert body/setup/file counts
  before actual0583/0585 fixture copies. Historical foreach reconstruction is
  exercised too; copied Host successor removal then fails explicit successor checks.
- Negatives cover wrong/duplicate setup/import/installer, reintroduced body,
  algorithm/error-import/relative-import/context-state/export/other-hook changes,
  missing successor, changed original body/fixture and all five persistent byte paths.

Setup mistakes during authoring were not accepted Red: dedented multiline
docstring differed in historical AST, then historical-foreach setup lacked its
actual static_foreach dependency. Both corrected within test-only setup; final
26guard cases pass. Lessons on shape invariance/immutable provenance applied,
not a new semantic fix. They require scrutiny in the upcoming test review.

Production, binding/context, all0583/0584/0585 immutable fixtures, baseline
JSON/capture and ActiveRed files unchanged (`git diff --exit-code` exit0 for
production/old-fixture/baseline paths). No existing assertion weakened or retired.
Unknown external/dynamic consumers and resolved cycles remain explicit gaps.

## Test bytes for review

```text
ec4a080982225f4f7a772a7ee95ed5d237c4dd16ac6f4737f6eb3aaf7351c25c test_liss_0586_host_behavior_red.py
94b0ecc06df9b88d3e4638c97019a3822e68f6546c251df97deddf48c0ac2da6 test_liss_0586_host_ownership_red.py
cd22c8a9ba153f8027ed8f83587a951a9eb8140d653378decd31a5e8c432bccc test_liss_0586_host_guard_migration_red.py
2af9a6cdc90d2ace13e13c818287f8d6ebb6f7b44e5eb2ffda7abee5a2289f3c liss_0586_guard_support.py
4738b9e872d8c6304e9aecae2ec394849faedad4080c44051405887c21a9606d liss_0583_guard_support.py
f75b948ab7ecba2f850bdfa0d0bdbccb13c6894d4adcbed0791c0d6249cd6762 test_liss_0583_repair_boundary_migration_red.py
e72b62d0ecc42e883a52b1b15f8be745b6fb12920c5d0e9332861cebb456f485 test_liss_0585_tensor_guard_migration_red.py
```

## Next decision / handoff

Review Phase1 tests and the H04 unreachable disposition, using configured
same_context routing when an agent review is requested. Current state: review
awaiting execution/acceptance, no agent pass inferred from these tests. No
Phase2 implementation, commit/push/delivery authorization.
Changed source-of-truth files: Issue/spec/WP and representative trace synced;
new execution packet plus tests/fixture/helper listed above. All uncommitted.
Runtime model/context/other ranks/private data omitted; no new technology.
After human test acceptance, request separate Green/implementation approval.
