# LISS-0582 public-import repair — Red acceptance request

## Review target

- Artifact: [new tests](../../../tests/test_liss_0582_public_import_repair_red.py),
  [accepted R01–R07](../../specs/evaluator-public-import-compatibility-repair.md).
- Current phase: Feature Path / Phase 1 Red; execution approved 2026-10-05.
- Requested approval: Phase 2 Green execution / implementation; types phase and implementation.
- Approved scope: ten original-object exports, frozen baseline and ownership.
- Implementation allowed: no. Post-review required: yes. Batch N/A.
- Same-context test review passed 2026-10-05; human test acceptance approved
  by `Phase 1 Red acceptance を承認` on 2026-10-05.
- User `Phase 1 Red テストレビュー／acceptance` treated as review request;
  no explicit acceptance decision or Phase 2 implementation approval inferred.

## Clause-to-test inventory

| Requirement | Exact test or retained gate | Current evidence |
|---|---|---|
| R01 | `test_direct_import_preserves_original_identity`, ten named parameters | 10 expected ImportError failures; resolve outside exception assertions |
| R02 | `test_wildcard_preserves_exact_manifest_and_identity` | expected missing-ten manifest failure; full export and object identities asserted |
| R03 | `test_capture_equals_frozen_baseline_bytes`; `test_capture_preserves_each_public_manifest`, six parameters; `test_capture_preserves_complete_case_payload_and_hash`, three parameters | byte mismatch + evaluator manifest fail; five other manifests and all complete case payloads/hashes pass; real fresh-process capture exit0 |
| R04 | `test_actual_consumer_imports_in_fresh_process`, five consumer-first parameters; `test_legacy_rejection_keeps_evaluator_error_identity`; `test_private_rational_consumer_remains_usable` | 7 pass; old public types/private function available; actual rational regression 4 pass |
| R05 | `test_only_original_facade_imports_are_restored`; `test_evaluator_executable_ast_is_unchanged`; `test_accepted_ownership_and_baseline_files_are_unchanged`, seven parameters; existing five ownership tests | approved-route restoration fails; existing body/import snapshots and protected files retained; 8 new preservation guards pass; existing 5 pass |
| R06 | separate focused / consumer / adjacent runs below; final root, spec, capture/cmp and CI at final SHA | final all-blocking not_run; not satisfied by Red evidence |
| R07 | PR #604 green-head gate, downstream new-SHA/merge-result verification | not_run; no delivery or branch propagation in this phase |

14 failures describe one ten-name removal defect, not 14 independent defects.
No fixture/collection errors, skipped tests, xfails, weakened assertions or
modification of accepted tests. Five node-scoped active-Red entries cover only
the 14 failures (10 direct-import parameters plus four single nodes), deadline
2026-10-12. The 23 passing cases remain blocking; no whole-file exclusion.
Baseline capture/cmp CI itself is not exempted, so PR #604 remains blocked.

The R05 snapshots are bounded repair guards at base 423c003b, not a claim that
future approved refactors may never change those bodies. Later feature heads
require explicit reviewed disposition of these guards against their own specs;
do not silently remove/update hashes or bypass failures. This is a downstream
review obligation, not authorization to change tests now.

## Verification

Tested HEAD/baseline `423c003b0b39c292731f6a8c7456a0b40cbd03f2`, dirty
documentation/new-test/lifecycle tree; no production modifications. cwd
`/Users/nn0cl/Documents/git/qpex`, macOS27.0.1 arm64, Python3.12.6,
pytest9.0.3. Commands use `/usr/local/bin/python3.12 -m pytest ... -q`
with `--junitxml=PATH`; focused also `--tb=short`.

| Scope / selection | Result | Start JST / duration / exit | Evidence |
|---|---|---|---|
| new repair file | 37 total; 14 fail, 23 pass; errors/skips0 | 2026-10-05 10:55:53.253015 / 0.995s / 1 | `/private/tmp/liss0582-repair-red-final.xml` |
| `test_classical_rational_red.py`, `test_liss_0543_refactor_baseline_red.py` | 8 pass; failures/errors/skips0 | 10:55:54.423099 / 0.763s / 0 | `/private/tmp/liss0582-repair-consumers.xml` |
| original 0582, 0493–0499, 0544, 0560, 0561, 0581 files listed in representative trace | 52 pass; failures/errors/skips0 | 10:55:55.410007 / 0.517s / 0 | `/private/tmp/liss0582-repair-adjacent.xml` |

End times are start + recorded duration. Compared with same-environment Phase 0,
the same original 52 cases still pass; all 14 newly exposed failures reproduce
the previously diagnosed compatibility gap. No full-suite comparison claimed.
Initial focused run before adding the approved-route guard: 13 fail / 23 pass;
the final additional failure is deliberate R05 coverage, not fixture repair.
Protected evaluator/old test/JSON/generator/cases are unchanged. No local
root/spec run this phase, no final SHA or merge-result verification, no Green.

Lifecycle entries5, document lifecycle, coverage ledger and whitespace checks
all exit0. Applying only validated checker-generated node deselections to the
new file yields 23 pass / 14 deselected, errors/skips0, exit0, 0.963s at
2026-10-05 10:59:13.436199 JST (end start+duration);
`/private/tmp/liss0582-repair-blocking-characterizations.xml`. This verifies
positive cases stay blocking; it does not waive baseline CI or establish Green.
New test SHA256: `88c949852d81846a5ff28b90a7fd226f25017f0aba69bd0a94a3381e48036a8f`.

## Human checklist / next safe action

- Confirm exact export names and identity, full byte comparison, consumer coverage.
- Review the bounded ownership/import snapshots and downstream obligation.
- Red tests accepted unchanged. Obtain separate Phase 2 Green execution /
  implementation approval; no implementation permission inferred.
- No commit/push/merge; [trace/handoff](../traces/2026-09-29-liss-0582-runtime-plan-eligibility.md)
  contains changed files and resumable evidence. Existing historical review and
  lessons changes are inherited from Phase 0, not new test-review approval.

## Same-context reviewer pass — 2026-10-05

Role switched to reviewer. Re-read the accepted repair spec, this request,
actual new/old ownership/rational tests, active-Red metadata, current trace,
Issue/WP, consumer import sites and capture script from disk. Review used
`same_context`, weaker than `separate_context`; no independent review claimed.
Live review/implementation routes same_context/host, empty model IDs. The
large-change section and numeric structure budgets are absent. Runtime policy
does not override normal isolation by size alone.

`/usr/local/bin/python3.12 scripts/review-change.py --root . --base
423c003b0b39c292731f6a8c7456a0b40cbd03f2 --head HEAD`: exit0, isolation
same_context/status normal. Committed metrics zero because base == HEAD;
unknown `working tree contains changes not represented by the committed diff`.
Those zeros are not measurements of the dirty change. Manual source counts:
new test 204 physical lines, existing evaluator1139, successor181,
orchestration154, installer317. No production-body reduction/change claimed.
Test responsibility is one bounded compatibility repair; retain current test
structure rather than invent abstractions. Existing large runtime bodies and
global/dynamic dependency graph remain outside this repair review, not waived.

### Findings and dispositions

- R01/R02: missing direct import cannot pass via `raises`; copies/wrappers
  fail original-object `is`, lost/added exports fail exact wildcard manifest,
  and new restrictive `__all__` fails. Already closed with test evidence.
- R03: determinism alone is insufficient; capture must exit0 and match frozen
  bytes, all six inventories and all three complete case records. A constant
  reference regenerated with the defect would be caught by the frozen hash
  guard. Already closed with evidence; reference/generator/cases unmodified.
- R04: actual five consumer-first cold imports, lazy legacy error import and
  private rational consumer are exercised. Already closed within the named
  consumers; out-of-tree dynamic consumers and global cycles out of scope,
  with limitations retained rather than universal compatibility claims.
- R05: restoration via direct legacy import/alias, old-body duplication,
  changed state/installer/orchestration or modified accepted test fail the
  route/import AST, executable AST or protected-file guards. Already closed
  within this repair. Snapshot guards are base-bound: legitimate future
  refactors require explicit reviewed disposition, not silent hash updates;
  later scope out of this review, human obligation retained.
- Lifecycle: five entries select exactly all14 failures and no passing case;
  23 passing cases stay blocking. Already closed with XML/manifest comparison.
  Retire all five entries on repair Green; failed baseline CI is not exempt.
- R06/R07: final root/spec/CI, final-SHA and downstream/merge-result evidence
  out of Phase 1 scope. Not satisfied, not waived; still block completion and
  delivery. Neither self-review nor Red acceptance permits implementation.

No test assertions/fixtures, accepted requirements, production source or
exclusion metadata changed in review. Review blockers: none for bounded Red
acceptance; unresolved defect and later approval/verification gates remain.

### Fresh reviewer verification

Same HEAD/base/environment/cwd as above, dirty test/document/lifecycle tree.
Commands exactly repeat the earlier scoped selections, with evidence below;
focused command keeps `--tb=short`. End = start + recorded duration.

| Scope | Result | Start JST / duration / exit | Evidence |
|---|---|---|---|
| focused37 | 14 expected failures, 23 pass; errors/skips0 | 2026-10-05 11:01:26.142176 / 1.017s / 1 | `/private/tmp/liss0582-repair-red-review.xml` |
| consumer8 | 8 pass; failures/errors/skips0 | 11:01:27.204971 / 0.775s / 0 | `/private/tmp/liss0582-repair-review-consumers.xml` |
| adjacent52 | 52 pass; failures/errors/skips0 | 11:01:28.213016 / 0.525s / 0 | `/private/tmp/liss0582-repair-review-adjacent.xml` |

Compared to Red creation run, identical14 failure IDs/cause; no new/resolved
focused failures and no consumer/adjacent failures. Full root/spec/remote CI
not_run, no full-suite comparison or Green claim. Eight protected files
(evaluator, successor, orchestration, installer, old test, JSON, capture script,
case TOML) byte-equal to `git show 423c003b:PATH`; new-test SHA256 unchanged.
Lifecycle entries5, document lifecycle, coverage ledger and whitespace exit0.
XML-to-manifest check: uncovered failures0, passing cases deselected0.

Historical reviewer recommendation: accept this unchanged Red test set.
Human `Phase 1 Red acceptance を承認` received 2026-10-05 accepts the reviewed
37-case set at SHA256 `88c949852d81846a5ff28b90a7fd226f25017f0aba69bd0a94a3381e48036a8f`,
its R01–R07 mapping and bounded repair-guard dispositions. No test change.
Next requested approval: Phase 2 Green execution / implementation (phase and
implementation). Approved scope ten original-object compatibility re-exports
only, with immutable baseline/body/ownership. Implementation allowed no until
that separate gate; post-review yes, batch N/A. R06/R07 final verification and
delivery remain unsatisfied. No root/spec or focused-suite rerun at this
approval-sync step; review evidence above is historical, not new Green.
