# Static foreach: bounded migration of the LISS-0584 repair-base guard

Status: **accepted — G01–G07 / Phase 0 acceptance, 2026-10-06**.
Final review/verification explicitly approved2026-10-06; [final record gate](../collaboration/reviews/2026-10-06-liss-0583-final-verification.md)
requires actual finalSHA all-blocking evidence. G01–G07 unchanged; delivery still
separate. Older pending final-approval wording below historical.
Current Phase 3 explicitly approved2026-10-06; [review passed](../collaboration/reviews/2026-10-06-liss-0583-phase3-review.md).
G01–G07/tests/fixture/guard dispatch unchanged. Fresh clean9165d6d1 all-blocking
passes; final review-record commit/actual-SHA verification approval pending.
Earlier Phase 2 gaps/pending Phase 3 statements below historical.
Owner: [LISS-0583](../issues/LISS-0583-evaluator-static-foreach-successor.md),
WP-0174 rank3; supplement to accepted [F01–F08](evaluator-static-foreach-elaboration.md).
Human `LISS-0583：LISS-0584修復境界guard移行のScope／Phase 0設計開始承認`
authorizes design only. No test/assertion/hash/source/lifecycle edits permitted
by this approval. Existing unfinished Phase 2 source stays parked unchanged.
Subsequent human `LISS-0583 guard移行仕様 G01–G07 と Phase 0 acceptance承認`
accepts this supplement unchanged, including the explicit byte-to-AST boundary.
Human `ISS-0583 guard移行 Phase 1 Red実行承認` subsequently authorizes
LISS-0583 Phase 1 test creation only. [Agent test review](../collaboration/reviews/2026-10-06-liss-0583-guard-phase1-review.md)
passed; human `LISS-0583 guard移行 Phase 1 Red テストレビュー／acceptance承認`
accepts new27 cases and the review unchanged2026-10-06. Phase 1 exit accepted;
guard Phase 2 Green/implementation subsequently explicitly approved2026-10-06.
Bounded dispatch implemented; [verification](../collaboration/reviews/2026-10-06-liss-0583-guard-phase2-verification.md)
reports focused success but unresolved source-clean/committed all-blocking gate.
Requirements unchanged; no full Green or completion claim.
Local commit/actual-SHA all-blocking rerun explicitly authorized2026-10-06;
current verification gate uses external results linked in that packet. No
Phase 3/delivery approval inferred; older commit-pending statements historical.

## [DESIGN CHECK]

- Scope/behavior: Architecture Path / Phase 0, limited disposition of the0584
  readonly-source guard exposed by current0583 extraction; no language change.
- Inspected: accepted0583 F01–F08 and0584 R01–R07, original boundary test and
  fixture, existing F08 projections/mutation tests, actual source/test origins,
  prerequisite source-snapshot search and fresh scoped baseline.
- Boundaries/ports/DTOs: test-protection ownership only; no runtime, TypeChecker,
  semantic authority, dependency, port, adapter, VO/DTO or provider addition.
- Constraints: immutable original audit fixture, unchanged persistent behavior
  tests, complete clause-to-assertion mapping, explicit byte-versus-AST limit.
- Decisions/ambiguities: three exact path exceptions with executable AST
  protection accepted; not rehashed snapshots or blanket runtime exceptions.
  Comment/formatting limitation accepted; test execution/implementation pending.
- Included/omitted: target contracts/tests/provenance only; other ranks, Rust,
  providers, secrets and global dynamic/out-of-tree graph omitted.
- Routing: host design/deterministic tools verified in use; configured
  same_context review (weaker), empty model IDs, large-change override absent.
- Evidence: proposed numbered requirements and old-to-new protection matrix;
  no AI runtime payload or inferred semantic repair.
- Verification: Phase 0 scoped baseline/provenance and source/test immutability;
  subsequent Red, human test acceptance, implementation, committed all-blocking
  verification and Phase 3 gates remain separate.

## Why a disposition is necessary

0584 R07 constrains its numeric-only repair: runtime expansion and unrelated
sources must remain unchanged **during that repair**. Its test
`tests/test_liss_0584_repair_boundary_red.py::test_existing_f05_owner_and_readonly_dependencies_are_preserved`
uses eight whole-file hashes. The successor extraction intentionally changes
three of those sources.0583's originally accepted F08 guard disposition names
the0582 tests only; it did not authorize changing this0584 protection.

This supplement proposes a new bounded0583 disposition, not retroactive
weakening of0584's completed repair or authority to change R01–R06 behavior.
No new ADR/global process policy is proposed; existing bounded-guard policy
governs this specific reviewed exception. Original F01–F08 remain in force.

## Frozen provenance and exact protection mapping

Original `tests/fixtures/liss_0584/repair-boundary.json` stays byte-identical,
SHA256 `d0d2c74d0552fd31a6894ea7d2908e4ea506fd639e5d986c2ed40423f3fc4bd3`.
Its `base_sha` is a287be51da358eed195f836afa21b07286128940; six source/tool/data
hashes match that actual Git ref. The two0583 test hashes match approved carrier
a14ab3af, not a287be51 (the files do not exist there). Fixture first committed
in14973d84. This is audit provenance, not a Git dependency in test execution.

| Existing protection | Proposed persistent successor protection |
|---|---|
| Fixture bytes, base, adopted F05 owner/node | Preserve exact original fixture digest, metadata and adopted node assertions. |
| evaluator.py whole-file bytes | Full import AST and all unaffected executable AST; only exact original foreach body removal and one private installer import/setup allowed, using existing F08 projection. |
| compatibility.py whole-file bytes | Full unaffected executable/import AST; only exact successor import and typed hook installer mapping allowed, using existing F08 projection. |
| context.py whole-file bytes | Full unaffected AST; only exact Mapping declaration and declaration-only private hook allowed, using existing F08 projection. |
| pipeline_legacy.py bytes | Retain original per-path byte hash assertion. |
| Frozen refactor-baseline.json and capture script bytes | Retain original per-path byte hashes; actual capture comparison remains blocking. |
| Two0583 behavior/successor test files bytes | Retain original per-path byte hashes; no assertion/fixture modification permitted. |
| TypeChecker unaffected AST, signature and mutation tests | All existing0584 checks/assertions unchanged; numeric semantic repair tests remain blocking. |

**Accepted equivalence boundary:** for the three exact source
paths, comments/formatting bytes are no longer frozen. Executable/import AST,
original body when retained and every unrelated declaration remain protected.
This is not identical byte-level protection and not an exemption for later
rank4–6 refactors. The other five byte protections do not change.

## Accepted requirements G01–G07

| ID | Contract and minimum executable evidence |
|---|---|
| G01 | Original0584 fixture bytes/digest, base, adopted_owner=LISS-0584, adopted F05 node and TypeChecker baseline remain unchanged. Assert the fixture and metadata through the real0584 guard entrypoint; no regeneration or current-source hash replacement. |
| G02 | Exactly evaluator.py, compatibility.py and context.py use bounded AST preservation. The other five paths retain exact original byte checks. Test baseline and authorized extracted forms, plus mutation of each of the five byte-protected files, through the real guard. No prefix-wide/path-family exemption. |
| G03 | Each AST exception delegates to the already reviewed F08 projections: evaluator imports/unaffected AST, compatibility imports/exact mapping/unaffected AST, context exact declarations/unaffected AST. Existing support and its immutable fixture stay unchanged; no duplicated generic wildcard algorithm or new runtime import. |
| G04 | Mutation-negative cases must reject: removed/rebound evaluator public import, unrelated evaluator body, changed/reintroduced foreach body, wrong or duplicate installer/setup, changed existing compatibility hook, extra mutable state, wrong context field type and context method implementation. Include one unrelated context declaration change. Positive authorized migration must pass the same real entrypoint so a guard that rejects everything cannot satisfy these negative tests. |
| G05 | Preserve the remaining0584 TypeChecker boundary tests and R01–R06 arithmetic/alias/span/positive-neighbor behavior; keep original F05 unchanged and blocking. Run these with0583 F01–F08, actual consumers/cold imports and adjacent regression. Runtime hook/ownership/state tests remain mandatory, not replaced by AST-only evidence. |
| G06 | Phase 1 adds migration acceptance/mutation tests only and leaves the old0584 guard failing; Phase 2 changes only that guard's exact path-to-protection dispatch after human test acceptance/implementation approval. Allowed test change: original existing F05/readonly guard only, retaining its identity and metadata assertions. New test file: tests/test_liss_0583_repair_boundary_migration_red.py. No original fixture, existing F08 helper/test, TypeChecker guard, source or lifecycle change for this supplement. |
| G07 | No skip/deselection/new Active-Red entry for the exposed guard. All root/spec/local sanity blocking checks must pass after bounded local commit; source-clean copy smoke remains unmodified. Commit evidence reruns on actual SHA, then Phase 3/final/delivery require separate approvals. |

EARS: When the original repair-base guard checks the reviewed static foreach
extraction, it shall accept only the explicitly allowed source deltas while
retaining every persistent metadata, byte and behavior contract above. When an
unrelated protected source/import/hook/type/body changes, the guard shall reject.

```gherkin
Scenario: Only the accepted extraction is permitted
  Given the immutable original repair fixture and persistent dependencies
  And the three sources have only the reviewed foreach extraction deltas
  When the existing repair-boundary guard executes
  Then it passes with all persistent protection assertions retained

Scenario: An unrelated change is still rejected
  Given that same permitted extraction
  And an existing compatibility hook is rebound or a protected byte file changes
  When the existing repair-boundary guard executes
  Then it fails instead of silently updating the baseline
```

## Phase 0 evidence and limits

HEAD6d1b851bff292ae496145b71e7a15a9be757cfd1 plus pre-existing dirty Phase 2
source/docs; dedicated branch codex/liss-0583-phase1-rereview. macOS27.0.1arm64,
Python3.12.6/pytest9.0.3, cwd repository. Source/tests/fixtures/lifecycle unchanged
in this design. Fresh scoped baseline:60passed/1failed,61nodes, exit1,
errors/skips/exclusions0; sole failure is the original readonly guard.
Run start16:24:17.781680JST, end16:24:18.245680JST, duration0.464s.
Command: `/usr/local/bin/python3.12 -m pytest
tests/test_liss_0584_repair_boundary_red.py
tests/test_liss_0584_opaque_wire_arithmetic_red.py
tests/test_liss_0583_guard_migration_red.py -q
--junitxml=/private/tmp/liss0583-guard-phase0-baseline.xml`.
Original hashes were independently compared with actual per-path Git origins;
five current bytes match, three authorized sources differ. Existing F08 AST
projections accept the current delta unchanged. A first audit probe incorrectly
used a287be51 for the later tests and stopped on absent files; corrected origin
mapping proves all eight hashes, without fixture edits or hiding the failed probe.

Root/spec/sanity not rerun in this Phase 0; earlier Phase 2 evidence is historical
and still has readonly-guard and source-clean blockers. No full Green, agent
product-review pass or completion claim. Dynamic graphs remain unassessed.
Post-design git diff --check, relative Markdown links and lifecycle0entries pass.
Reviewed-test diff is empty and all four parked implementation SHA256 values
match the Phase 2 handoff; no source/test/fixture/lifecycle edits this design.

## Adjudicator review target / decision

- Approved scope:0584 repair-boundary guard's exact bounded dispatch within0583.
- Current phase: guard Feature Path / Phase 2 implemented, provisional verification;
  original Feature Phase 2 not complete.
- Received approval: dedicated supplement G01–G07 and Phase 0 acceptance,
  including the explicit three-file byte-to-AST equivalence boundary.
- Approval type: Phase 1 test acceptance and guard Phase 2 implementation received;
  no technology/ADR selection.
- Implementation allowed: **yes** for exact dispatch only. Post-review: yes; batch N/A.
- Next requested approval: bounded local commit and actual-SHA all-blocking rerun;
  new27 tests unchanged; guard now passes with bounded dispatch. Original
  feature tests are not reopened or weakened. Commit/all-blocking rerun follows.
- Decision: human accepted G01–G07 unchanged and explicitly approved Phase 1
  execution, test acceptance and explicit guard Phase 2 implementation2026-10-06;
  commit/Phase 3/final/delivery approval not inferred.
