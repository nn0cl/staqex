# LISS-0591 CI history repair — Phase 1 Red review

Date: 2026-10-21. Result: **agent_pass; human Red acceptance received**.
User authorized Phase1 Red test review only. Implementation permission:no;
post-review:yes;batch:N/A. Not a Phase2 or remote-CI approval.

## Review packet

- Canonical agreement: [accepted CI01–CI07](../../specs/liss-0591-ci-history-repair.md),
  [unchanged P/B/E agreement](../../specs/parser-operator-primary-successor.md).
  Planning:[Issue0591](../../issues/LISS-0591-parser-operator-primary-successor.md),
  [WP0175](../../work-plans/WP-0175-source-responsibility-inventory.md).
- Re-read from disk: existing guard-migration suite, guard support, external
  Phase1 runner, command records, both JUnits, original CI failure log, frozen
  manifest, Git objects, routing/readiness/review/verification rules. Author
  conclusions were not used as proof.
- Effective route:same_context, weaker than separate_context;host implementation
  setting not permission,empty modelIDs,no enabled large-change override.
  `review-change.py --base 5b62ab1a --head HEAD` reports normal same_context;
  committed diff is empty and dirty documents are explicitly unknown to those
  metrics,not zero total work. Independent scope inspection shows no executable
  change. No required isolation was downgraded.

## Findings and dispositions

No blocking finding in the authorized Red scope.

| Check / failure scenario | Evidence / disposition |
|---|---|
| Shallow checkout loses immutable Git evidence | All31 JUnit failures independently show `git show` exit128 for a pinned base. Exact failure-ID set equals original CI,not merely equal counts. Expected Red confirmed. |
| History-only control might accidentally change files or test selection | Same83 unique IDs,925 tracked compiler/test/workflow file hashes independently equal Git archive at5b62ab1a and live clone/checkout. Commands use same interpreter/selection with explicit clone PYTHONPATH,no new exclusions. Closed with evidence. |
| Missing owner,changed algorithm/newlines/carriers/exports might be accepted by guard | Existing named mutation controls and real inherited-reader positives remain unchanged;fresh full83-node control rerun passes. No guard weakening or new snapshot fallback. |
| Local control could be mistaken for actual workflow/full Green | Still not proven:root workflow remains shallow,GitHub checkout of the event/merge revision and all-blocking repair verification are future gates. Out of Phase1 scope,retained as delivery blocker;not waived. |
| Reused test result might be stale or omit failures | Reparsed original JUnit counts,unique IDs,errors/skips,command exits and timestamps;fresh control83PASS. Runtime/root suites beyond this83-node set not_run for this review. |

## Verification and specification mapping

Tested source SHA:`5b62ab1a74261c32bf2c9314ef9ff0b9b0d7e5d2`.
Both original execution runs used clean clone trees. Current repository has
dirty review/status documentation only. Environment:macOS27.0.1arm64,
Python3.12.6,pytest9.0.3;not the Linux CI environment.

- Original authorized Phase1:shallow52PASS/31FAIL;history-only83PASS.
  Same83 IDs,0errors/skips/exclusions;original CI31 failures independently
  matched. Original metadata/commands/times retained without rerunning over them.
- Reviewer rerun:83PASS in42.54s,0failures/errors/skips;no exclusions in command.
  Explicit clone PYTHONPATH;JUnit `review-history-restored.xml` records start
  timestamp,duration/counts. No new shallow test run claimed during review.
- Independent reviewer audit:925 paths equal Git object raw bytes,83 unique
  IDs,all31 failures are historical-object errors,control0failures.
- CI02/CI03:paired object availability,Red and history-only control covered.
  CI04:unchanged source/test/evidence bytes independently checked;accepted
  clauses/scenarios frozen. No assertions/fixtures/test set modified.
- CI01/CI05:not implemented yet;CI06:full blocking not_run for this review;
  CI07:no push/rerun/merge. Current failed CI is neither resolved nor waived.
- Consumer/structure:actual inherited-reader copy controls within83 exercised;
  broader runtime consumer smoke/adjacent/root/spec are not_run,not inferred.
  No split/new body,so no new structure-budget claim;existing Parser/WP0175
  structure gaps remain unchanged.

Evidence directory:`/private/tmp/liss-0591-ci-red-20261021.wGmeGn/`:
`result.json`,`commands.json`,paired JUnits,`review-history-restored.xml`,
`review_audit.py`,`review-audit.json`,`frozen-manifest.json`,stdout/stderr.
Original CI log:`/private/tmp/liss-0591-delivery-20261021.xNStH4/failed-logs.out`.
Temporary evidence must be regenerated if unavailable,not inferred.

## Changed records and next gate

This packet,existing lessons log and the six related Issue/spec/WP/review/trace
records only. No implementation,test,fixture,workflow,index or remote mutation.
Existing raw-byte/PYTHONPATH/final-SHA lessons applied;new reusable history
prerequisite lesson records the already accepted boundary,not a policy change.

Human **LISS-0591 CI修復 Phase 1 Red テストレビュー／acceptance承認** received
2026-10-21. Type:human review/result acceptance of this packet and its unchanged
83-test evidence. No additional execution,implementation or delivery authorized.
Next requested approval:**LISS-0591 CI修復 Phase 2 Green／implementation承認**.
Type:phase execution/implementation for the accepted two-line checkout input
only;post-review:yes,batch:N/A. Not granted by this Red acceptance. The original
rootCI and remaining human phase gates block delivery.
Representative [trace/handoff](../traces/2026-10-16-liss-0591-parser-operator-primary.md).

Subsequent Phase2 implementation separately approved/applied. The accepted
Red verdict is unchanged. Local root3254 and scoped/spec/audits pass
provisionally;copy smoke is blocked by the uncommitted workflow source-clean
guard. Next approval is bounded local commit/actual-SHA all-blocking rerun,
not a new Red acceptance or a claim of completed Phase2/full Green.
That bounded local commit/actual-SHA verification is now authorized2026-10-21;
result stays external in the CI supplement's checkpoint. No future pass implied.

Actual clean-df5e6062 all-blocking verification subsequently passed,copy smoke
included. Authorized [CI Phase3 review](2026-10-21-liss-0591-ci-history-phase3-review.md)
agent_pass;final-review record commit/revalidation remains gated. Red verdict
and accepted tests unchanged;no remote CI success claimed.
Final review-record commit/actual-SHA verification subsequently authorized;
result remains external to keep tested SHA fixed. Human final acceptance pending.
