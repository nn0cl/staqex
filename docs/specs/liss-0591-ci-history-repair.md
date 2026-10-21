# LISS-0591 CI history prerequisite repair — accepted supplement

Status: CI01–CI07 and Phase 0 accepted by the Adjudicator on 2026-10-21.
Scope/design-start was approved by the preceding continuation. Acceptance
includes the existing-test/no-guard-change strategy. Phase 1 execution was
separately approved and completed on 2026-10-21; Red agent review passed,
human Red review/acceptance received on 2026-10-21. Phase 2 implementation
separately approved and applied: root-checkout full-history input only.
Verification is provisional and blocked by the uncommitted-distribution guard;
local commit/final-SHA verification authorized2026-10-21 and pending execution;
delivery remains separately gated. This receipt does not pre-claim success.

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
implementation approved/applied;local commit/final-SHA verification authorized,
outcome pending in the external record below.
The accepted CI01–CI07 include the
existing-test/no-guard-change strategy. Separate Red review/acceptance,
Phase 2 implementation, Phase 3 and final verification
approvals remain required. No new test authoring is proposed: an already
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
Current local source HEAD is `5b62ab1a`, with five pre-existing dirty delivery
records retained. Main's separate horizon PR622 does not repair PR621 and
is not silently merged/rebased into this proposal.

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
