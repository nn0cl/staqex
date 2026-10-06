# LISS-0583 guard migration: Phase 2 implementation / verification

## Current local-commit verification gate

Human `LISS-0583 ローカルコミット／実SHAで全blocking再検証承認`
on2026-10-06 authorizes the bounded17-file local unit and all-blocking rerun,
not push/PR/merge or Phase 3. Prior pending commit statements below historical.
This record is committed before verification; final evidence stays outside the
tree at `/private/tmp/liss0583-committed-verification.json`, with SHA/clean state,
environment, commands/times/exits/counts and XML/log references. Its `all_passed`
must be true and tested SHA must equal current HEAD before reporting Green.
No post-verification record commit; any subsequent commit invalidates applicability.
Issue remains review pending human next-phase approval; no issue done claim.
Next requested approval when all blocking passes: Phase 3 Refactor/review.

## Review target and authority

Feature Path / phase-2-green, AIP-0583-003 M; existing Issue/branch reused.
Human `LISS-0583 guard移行 Phase 2 Green／implementation承認` authorizes
only [G01–G07](../../specs/evaluator-static-foreach-repair-guard-migration.md)
after [human Phase 1 test acceptance](2026-10-06-liss-0583-guard-phase1-review.md).
Implementation allowed yes for the bounded guard dispatch, post-review yes,
batch N/A. Phase 3, commit, push/PR/merge and final acceptance not authorized.

## Implementation / protection mapping

Only `tests/test_liss_0584_repair_boundary_red.py` changed for implementation:
existing test identity, original boundary digest/base/owner/adopted-node assertions
and remaining TypeChecker guards retained. Exact evaluator path invokes existing
F08 import and full AST checks; exact compatibility path invokes its existing
projection guard; exact context path hashes the existing projection against the
unchanged F08 baseline. Every other dependency keeps its original byte assertion.
No generic algorithm, prefix exemption, changed hash, new exclusion or runtime
change. Guard module69→86 physical lines, one repair-boundary responsibility;
qualitative budget retained, no numeric budget configured or facade body hidden.

G01 original fixture digest unchanged; G02 positive extracted/baseline shapes and
five byte mutations pass; G03 real-entrypoint delegation passes; G04 all source,
installer and retained-body mutations reject while positives pass. This closes
the Red-phase vacuity limitation. G05 original numeric/TypeChecker/runtime and
consumer sets pass; G06 accepted new tests/helper and parked runtime unchanged;
G07 no exclusions, final committed all-blocking evidence still pending.
Accepted limitation unchanged: comments/formatting of the three exact paths
are not byte-frozen; unaffected executable/import AST is protected instead.

## Evidence / baseline comparison

Tested HEAD/base `6d1b851bff292ae496145b71e7a15a9be757cfd1` plus dirty parked
source, new tests and records, branch `codex/liss-0583-phase1-rereview`;
cwd `/Users/nn0cl/Documents/git/qpex`, macOS27.0.1arm64,
`/usr/local/bin/python3.12`3.12.6 / pytest9.0.3. Provisional, not committed evidence.
Run timestamps/durations/counts for pytest retained in external JUnit XML.
Focused start18:42:55.441318JST duration2.116s; consumer start18:43:06.593143JST
duration25.679s; reviewer start18:43:25.210388JST duration0.897s.
Root start18:43:05.451153JST, end18:48:28.282153JST, XML duration322.831s.

| Suite | Result | Evidence |
|---|---|---|
| Focused165 | passed165, exit0, failures/errors/skips/exclusions0,2.12s | `/private/tmp/liss0583-guard-phase2-focused.xml` |
| Reviewer guard rerun33 | passed33, exit0, failures/errors/skips/exclusions0,0.90s | `/private/tmp/liss0583-guard-phase2-review.xml` |
| Actual consumer/adjacent77 | passed77, exit0, failures/errors/skips/exclusions0,25.68s | `/private/tmp/liss0583-guard-phase2-consumer-adjacent.xml` |
| Root2450, no deselection | passed2450, exit0, failures/errors/skips/exclusions0,322.84s | `/private/tmp/liss0583-guard-phase2-root.xml` |
| Spec | passed161/161, exit0 | `/private/tmp/liss0583-guard-phase2-spec.log` |
| Local non-PR sanity10 | failed:9pass/1copy-smoke failure, aggregate exit1 | `/private/tmp/liss0583-guard-phase2-sanity-*.log` |

Focused and consumer exact selectors equal the Phase 1 packet commands with
`guard-phase2` evidence prefix. Reviewer command:
`/usr/local/bin/python3.12 -m pytest tests/test_liss_0583_repair_boundary_migration_red.py tests/test_liss_0584_repair_boundary_red.py -q --junitxml=/private/tmp/liss0583-guard-phase2-review.xml`.
Root: `/usr/local/bin/python3.12 -m pytest tests/ -q --junitxml=/private/tmp/liss0583-guard-phase2-root.xml`.
Spec/sanity: `/usr/local/bin/python3.12 /private/tmp/liss0583-phase2-checks.py /private/tmp/liss0583-guard-phase2`.
The inspected runner executes spec and all10 current CI non-PR sanity steps,
explicit Python3.12, scratch cleanup omitted/retained; each external log remains.
Tool output records each SHA, dirty state, cwd, exact command, UTC start/end/exit.
Spec run09:43:13.751661–09:43:14.383034UTC. PR-only traceability not_run; no CI claim.

Compared with guard Phase 1 focused161pass/4fail, all four exact failure IDs
resolved without modifying accepted new tests: two legitimate shapes, existing
helper delegation and original readonly guard. Numeric/runtime/consumer remain
passing. Compared with previous original Phase 2 root2422pass/1readonly failure,
current root2450pass includes27 new guard cases and the now-passing old guard.
No current failing IDs; no exhaustive semantic-coverage claim. Full all-blocking
Green remains false due source-clean copy smoke and absent committed evidence.

## Review, consumers, gaps and next gate

Same-context reviewer reread actual guard diff/source and existing protection
helpers from disk; reran33 guard cases without implementing during review.
Findings: bounded protection mapping and positive/negative coupling already
closed with focused/review evidence. Fixture SHA and four parked source SHA256
values match prior trace; original helper, F08 tests and numeric fixture/test
diffs empty. Reviewed migration tests unchanged during implementation.
Static consumer search finds new migration tests calling the exact old function,
F08/public-import tests sharing the helper, and pytest collection of original
boundary suite; no runtime import of these test helpers. Global dynamic/out-of-tree
graph remains unassessed, not a claim of exhaustive consumer coverage.

Effective routing from `review-change.py --root . --base 6d1b851b --head HEAD`:
same_context (weaker), host implementation, empty models, no enabled large-change
override. Dirty metrics unknown; zero committed diff is not total-change evidence.
Existing bounded-guard lesson applied; no new policy/ADR/provider/dependency.
Included accepted specs/tests, actual projections/consumers and policies; omitted
other ranks, Rust/providers/secrets and unrelated history. Model/reasoning/token
estimates/actuals N/A, host unavailable; issue-only attribution.

**Blocking finding, do not bypass:** source-clean copy smoke still reports
`Uncommitted distributed source: docs/specs/evaluator-static-foreach-elaboration.md`.
Disposition: request bounded local commit approval for reviewed existing0583
source/tests/records, then rerun root/spec/all10 sanity at the actual committed
SHA. A later record commit also requires rerun. No full Green, Phase 2 completion
or issue done claimed; Phase 3/final/delivery remain separate. No commit/push/merge.

Next requested approval type: bounded **local commit and actual-SHA all-blocking
verification**, not Phase 3. Human approval remains separate from self-review.
Commit scope: existing0583 evaluator/context/compatibility/static_foreach source;
accepted new guard migration tests and bounded old0584 guard dispatch;
previously retired lifecycle entries;0583 Issue/specs/WP/representative trace,
phase review/verification records and existing lesson applications. No unrelated
changes, new exclusions, instruction/policy edits or external delivery included.
Stage explicit reviewed paths, not repository-wide unknown changes. After that
approval, commit the synchronized bounded unit and rerun every blocking suite;
do not request Phase 3 until these gaps close.

After phase-record synchronization, spec and all10 sanity repeated via the same
runner with `/private/tmp/liss0583-guard-phase2-record` prefix: spec161pass and
same9pass/1source-clean copy-smoke failure. Start09:45:36.836924UTC for spec;
separate external logs and tool SHA/command/time records retained. Document
lifecycle, test lifecycle0entries and diff whitespace checks pass.
