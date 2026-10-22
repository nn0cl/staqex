# LISS-0591 CI history prerequisite repair — accepted supplement

Status: CI01–CI07 and Phase 0 accepted by the Adjudicator on 2026-10-21.
Scope/design-start was approved by the preceding continuation. Acceptance
includes the existing-test/no-guard-change strategy. Phase 1 execution was
separately approved and completed on 2026-10-21; Red agent review passed,
human Red review/acceptance received on 2026-10-21. Phase 2 implementation
separately approved and applied: root-checkout full-history input only.
Local commit df5e6062 and all-blocking verification passed2026-10-21,including
copy smoke. Phase3 review agent_pass;final-record commit bc754065 passed all
local blocking and the Adjudicator accepted the final review/result2026-10-21.
Acceptance-record cd10c261 passed all local blockers;explicitly authorized
delivery completed via PR621/main b9f86298. PR and main CI each all3SUCCESS,
root3254PASS. Verified2026-10-22 JST;closeout-record delivery separately
authorized,with fresh actual-SHA checks and CI required before merge.

Owner: [LISS-0591](../issues/LISS-0591-parser-operator-primary-successor.md).
Parent: [WP-0175](../work-plans/WP-0175-source-responsibility-inventory.md).
Existing [P/B/E specification](parser-operator-primary-successor.md) and
[representative trace](../collaboration/traces/2026-10-16-liss-0591-parser-operator-primary.md)
remain authoritative for the accepted extraction and its history.

## Problem and bounded design

PR621 HEAD `5b62ab1a74261c32bf2c9314ef9ff0b9b0d7e5d2` passed local
full-history verification but failed CI39574222927: root 31 failed / 3223
passed; repository sanity and spec verification passed. Every failed node
needs immutable Git evidence absent from the depth-one checkout.

An independent clean, same-SHA shallow clone reproduced the same 31 failures
among 83 guard-migration nodes (52 passed). Fetching history only, with no
file changes, made those same 83 nodes pass. This is prior diagnostic
evidence, not current CI success or a completed repair phase.

The proposal adds `with: fetch-depth: 0` only to `kernel-tests` Checkout in
`.github/workflows/ci.yml`. Keep its action version and event-default ref.
The existing repository-sanity job already requests full history; no other
job needs changing for this defect. Full history costs additional transfer;
an arbitrary larger finite depth is not a durable availability contract for
fixed historical evidence. No fetch is added to test code.

[Official checkout documentation](https://github.com/actions/checkout#usage)
states the default single-commit behavior and the full-history setting.
This repairs a CI execution prerequisite, not a new runtime architecture,
provider selection, permission grant or accepted language decision; no new
ADR is proposed.

## Accepted requirements — CI01–CI07

| ID | Required behavior and evidence |
|---|---|
| CI01 | When the root job checks out the tested event revision, it obtains full history using `fetch-depth: 0`. Do not change the default ref to main or another revision. Capture the actual PR head and CI checkout/merge SHA separately. |
| CI02 | Before claiming history repair, verify both `22335a5768c17a41eb94682e7dd14d3e6df004bd:compiler/staqex/parser.py` and `dca93187f50594b0417ae88067154baaf3c0ea7c:compiler/staqex/parser.py` are readable, and the clean verification clone is not shallow. Retain failure if evidence is unavailable; no snapshot fallback. |
| CI03 | Reuse the unchanged accepted 83-node `tests/test_liss_0591_guard_migration_red.py` suite. In Phase 1, reproduce shallow 31 failures / 52 passes and history-only 83 passes at the same frozen code SHA; compare failing node IDs to original CI. This diagnoses the environment, not product Green. Obtain Red review/acceptance before Phase 2. |
| CI04 | Preserve all production, tests, fixtures, six carriers, P/B/E clauses and accepted evidence bytes. No fixture regeneration, test addition/removal/skip, threshold relaxation, test-side fetch, or guard migration is needed. Compare these paths with the pre-repair SHA. |
| CI05 | Preserve workflow triggers, permissions, action/runtime versions, checkout ref behavior, root command, lifecycle exclusions and other jobs. The sole executable diff is the two-line full-history input on the root checkout. Inspect this exact diff; no new dependency or token scope. |
| CI06 | After implementation and final commit, distinguish focused, consumer, adjacent and all-blocking results with SHA/environment/dirty state/commands/times/counts. Run the previously declared LISS-0591 blocking set and compare original failure IDs; local pass is not remote CI pass. |
| CI07 | Update PR621 only with separately authorized delivery. Require all applicable PR CI jobs and repository merge gates to pass; never merge red/skipped CI or use an admin bypass. Record the tested head, CI revision and actual merge commit separately. Any later commit needs fresh blocking verification. |

### Acceptance scenarios

- Given the frozen PR head in a clean depth-one clone, when the existing
  guard-migration suite runs, then the historical-object failures remain
  observable and match original CI. When history alone is fetched, then the
  same tests and source bytes pass and both pinned objects are readable.
- Given the proposed workflow change, when its diff is reviewed against
  `5b62ab1a`, then only the root Checkout full-history input is added; test
  execution and all security/ref/trigger boundaries are unchanged.
- Given any new repair commit, when verification or delivery is requested,
  then all declared blocking checks run at that revision; absent history or
  another failing suite blocks Green and merge.

## Execution gates and verification commands

Current: Phase 0 accepted; separately authorized Phase 1 execution completed,
agent review passed and human Red acceptance received. Phase 2 execution and
implementation approved/applied;local actual-SHA verification passed atdf5e6062.
Phase3 review separately approved/executed,agent_pass. The accepted CI01–CI07
include the existing-test/no-guard-change strategy. Final review-record commit/
verification,human final acceptance and delivery were separately authorized
and completed. PR621 and actual-main CI succeeded;no further CI repair gate
remains. Closeout-record commit/push/PR/CI/successful merge separately
authorized2026-10-22 JST;no additional implementation authorized.
No new test authoring is proposed: an already
accepted test reproduces the defect (local-issue-planning exception for
existing regression coverage, not a phase exemption).

Run from the actual verification clone with explicit `PYTHONPATH` set to
that clone, Python 3.12 and recorded pytest version:

```text
git rev-parse HEAD
git rev-parse --is-shallow-repository
git cat-file -e 22335a5768c17a41eb94682e7dd14d3e6df004bd:compiler/staqex/parser.py
git cat-file -e dca93187f50594b0417ae88067154baaf3c0ea7c:compiler/staqex/parser.py
python3.12 -m pytest tests/test_liss_0591_guard_migration_red.py -q
```

Later all-blocking scope retains
the accepted focused/repair/inherited/adjacent/consumer, root `tests/`, spec
`python3.12 tests/spec_verification/run_all.py`, all 11 applicable repository
sanity checks, compile and raw/cohort/export audits; exact prior argv and
node inventories are recoverable from the representative trace's accepted
verification records. Do not substitute only the 83-node suite or describe
unknown totals as zero failures. Root keeps existing lifecycle exclusions;
no new exclusions. CI remains the Linux checkout integration acceptance.

## Evidence and open decisions

Prior diagnostics: `/private/tmp/liss-0591-delivery-20261021.xNStH4/`, notably
`history-reproduction.out`, paired JUnits, `failed-logs.out` and command
metadata. If missing or superseded, repeat rather than infer the outcome.
Original CI-failing source HEAD was `5b62ab1a`;its five dirty delivery records
were retained in repair commit `df5e6062`. Main's separate horizon PR622 does
not repair PR621 and is not silently merged/rebased into this work.

No architecture or technology decision is open. Human decisions remaining:
each subsequent phase. A discrepancy in
node identities, additional required file change or unrelated CI failure
requires reporting and bounded replanning, not automatic scope expansion.

## Phase 1 execution evidence — 2026-10-21

Explicit Phase1 execution approval received. Existing test bytes unchanged;
no new tests or fixture/guard/workflow edits. Independent temporary clean clone
at `5b62ab1a74261c32bf2c9314ef9ff0b9b0d7e5d2`:

- Depth one: 83 nodes, 52 passed / 31 expected failures, zero errors/skips.
- History fetch only: same 83 nodes, 83 passed / zero failures/errors/skips.
- Both pinned parser objects absent before fetch and readable afterwards;
  HEAD unchanged, both runs clean, tracked compiler/tests/workflow hashes equal.
- Failure IDs match the original CI and previous reproduction; no new node or
  exclusion. The passing control is not workflow implementation or full Green.

Evidence: `/private/tmp/liss-0591-ci-red-20261021.wGmeGn/result.json`, runner,
`commands.json`, frozen manifest, stdout/stderr and paired JUnits. Environment:
macOS/Python3.12, exact versions and timings in result. Scope CI02/CI03/CI04
diagnostics only; CI01/CI05 workflow repair, CI06 all-blocking and CI07 delivery
remain unexecuted. Next: Phase1 Red test review, then human acceptance before
Phase2. No review pass is claimed by this execution record.

Subsequent authorized [Phase1 Red review](../collaboration/reviews/2026-10-21-liss-0591-ci-history-red-review.md)
passed in same_context (weaker isolation). Independent JUnit/CI/Git raw-byte
audit passed;fresh reviewer control83PASS. Human Red acceptance remains
received2026-10-21;no Phase2/workflow implementation or remote Green follows.

## Phase 2 implementation / provisional verification — 2026-10-21

Explicit Phase2 Green/implementation approval received. Added only the two-line
`with` / `fetch-depth: 0` input on root Checkout. Raw workflow comparison and
YAML comparison confirm no other setting/ref/command/security change. Production,
tests,fixtures,cohort and accepted clause bytes unchanged.

At uncommitted HEAD5b62ab1a plus workflow/docs:focused202,repair114,
inherited428,adjacent42,root3254 allPASS (same prior local node IDs,zero
failures/errors/skips/exclusions),spec161/161PASS,compile and independent
Git-derived raw/cohort/export/consumer audits PASS. Sanity10/11PASS;
copy smoke exits1 with `Uncommitted distributed source: .github/workflows/ci.yml.
Commit it before distribution.` The existing source-clean guard is preserved.

State:environment_blocked,not all-blocking Green. Failed sanity and aggregate
runner exit1 retained;no waiver,assertion relaxation or product repair retry.
Evidence:`/private/tmp/liss-0591-ci-green-20261021.TJw1Ua/result.json`,individual
command metadata/logs/JUnits. macOS27.0.1arm64,Python3.12.6,pytest9.0.3;
explicit root PYTHONPATH. Local success is not GitHub event-checkout success.
Next:bounded local commit followed by every blocking suite at its actual SHA,
only after separate authorization. No commit,push,CI rerun or merge performed.

## Authorized commit / actual-SHA checkpoint — 2026-10-21

Human approved **LISS-0591 CI修復 ローカルコミット／実SHAで全blocking再検証承認**.
Commit only the workflow and eight related Markdown records;then rerun all
declared blocking checks at the new clean SHA. No additional implementation,
Phase3 reviewer pass or remote delivery permitted. Authoritative outcome:
`/private/tmp/liss-0591-ci-sha-20261021.j6wKf9/result.json`,with command metadata,
logs and JUnits. No tracked post-run result edit;another commit requires a
new full rerun. After success request Phase3 Refactor/review approval;otherwise
report the actual failure without bypass. Earlier blocked result stays history.

## Phase 3 review outcome — 2026-10-21

The authorized commit checkpoint completed:clean df5e6062 passed focused202,
consumer21(included),repair114,inherited428,adjacent42,root3254,spec161/161,
sanity11/11 and compile/raw/cohort/export/checkpoint/routing audits. No pytest
failure/error/skip/exclusion,same prior local node IDs. Original copy-smoke
refusal resolved by committing,not guard modification. Evidence remains at the
checkpoint path above;the remote CI result is unchanged/unverified.

Authorized [Phase3 review](../collaboration/reviews/2026-10-21-liss-0591-ci-history-phase3-review.md)
agent_pass. Fresh guard83PASS and independent1positive/8negative YAML controls,
plus recorded full-blocking evidence audit. No source/test/workflow edits.
These new review/status records are uncommitted;next is final verification/
record commit and full rerun at its actual SHA after separate approval.

## Approved final verification checkpoint — 2026-10-21

Received **LISS-0591 CI修復 final verification／レビュー記録コミット・実SHAで全blocking再検証承認**.
Commit only the nine related review/status/lesson Markdown records,without
changing executable/test/fixture/clause bytes. Then rerun every declared
blocking suite/check at the new clean SHA. Result belongs outside Git:
`/private/tmp/liss-0591-ci-final-20261021.fUCBbu/result.json` plus per-command
logs/JUnits/metadata. No tracked post-run edit;any later commit needs another
full rerun. After success request human final-result acceptance;otherwise
report the actual failure. No push,PR update,remote rerun or merge permission.

## Human final-result acceptance — 2026-10-21

Received **LISS-0591 CI修復 最終レビュー結果の受入れ**. Type:human final
review/result acceptance of clean `bc7540654461a841ee8ad6346c76738dc44e70f8`,
Phase3 packet and final evidence. Verified actual SHA/clean tree and all11
command receipts before receipt edits:focused202/consumer21(included),repair114,
inherited428,adjacent42,root3254,spec161/161,sanity11/11,compile/raw/cohort/
export/checkpoint/routing PASS;pytest0failures/errors/skips/exclusions.

Evidence remains the final-checkpoint result above (macOS27.0.1arm64,
Python3.12.6,pytest9.0.3),not rewritten as new execution. This acceptance does
not cover a later receipt SHA or actual remote CI. Only acceptance metadata
changed;no runtime rerun or executable/test/clause edit. Next:separately
authorized acceptance-record commit and all-blocking rerun at its actual SHA.
No commit,push,PR621 update,CI rerun or merge authorized by this receipt.

## Approved acceptance-record checkpoint — 2026-10-21

Human **LISS-0591 CI修復 受入れ記録コミット・実SHAで全blocking再検証承認**
received. Commit only six related receipt Markdown records,then run every
declared blocker at its actual clean SHA. Workflow/source/tests/fixtures/
accepted clauses unchanged;prior bc754065 result remains historical evidence.
Outcome:`/private/tmp/liss-0591-ci-accepted-20261021.Uujhd0/result.json`,with
per-command metadata/stdout/stderr/JUnits. This pre-run record predicts no
success. No tracked post-run edit;later SHA requires another full rerun.
If all checks pass,next is push/PR update/CI/successful-merge authorization;
otherwise report actual failure. No further record-acceptance loop. No remote
authority or additional implementation inferred from this local checkpoint.

## Delivered / closure evidence — 2026-10-22 JST

Human authorized push/PR update/CI/successful merge,then continued the same
delivery. Non-force push of clean cd10c261,PR621 description update,all3
PR CI39591463535 SUCCESS. Root logs show fetch-depth0 and3254PASS;actual CI
checkout29897a10 has parents c14a7816 andcd10c261. Normal SHA-matched merge
created b9f86298 with those same parents and tree aa775e21…c754. No admin
bypass,rebase,force push or test change. Actual-main CI39620414430 subsequently
all3SUCCESS,root3254PASS,checkout b9f86298. Old31 history failures resolved.
Logs/metadata/parent-tree checks:`/private/tmp/liss-0591-ci-delivery-20261021.tbcLLA/`.
PR:[621](https://github.com/nn0cl/staqex/pull/621). Exact local node-ID evidence
remains at the accepted-record checkpoint;remote logs emit counts,not JUnit IDs.

No extra source refactor or next-family implementation. Existing Parser size/
dynamic-graph limits remain WP0175-owned. Closeout changes only Markdown,
not the tested implementation tree;uncommitted records are not a new verified
SHA or automatically authorized record PR.
