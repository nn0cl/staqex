# LISS-0592: ParseError pickle/copy serialization repair

## Metadata

- Local issue ID:LISS-0592
- GitHub issue:none;local planning
- Status:review — final accepted;acceptance-record commit/revalidation authorized,delivery pending
- Phase:phase-3-refactor
- Type:bug repair / prerequisite for0591
- Priority:high;blocks requested operator-primary completion
- Initial/current planning size:L/L
- Reclassification reason:none
- Owner/agent:Codex host / Adjudicator
- Related branch:codex/liss-0592-parseerror-serialization-phase0
- Source base:22335a5768c17a41eb94682e7dd14d3e6df004bd

## Summary / acceptance notes

Human2026-10-17 requested proper completion rather than preserving the known
failure. Treat as authority to investigate/design a real repair;not approval
to skip reviewed specification/Red/Green gates. Dedicated R01–R07,guard policy,
0591 dependency policy and Phase0 explicitly accepted2026-10-17. Canonical agreement:
[R01–R07 and guard/dependency policy](../specs/parseerror-serialization-repair.md).
Default ParseError reconstruction lacks required line/col. Repair needs
explicit construction plus state/args preservation,not weaker P08 assertions.

## Dependencies

- Parent:WP0175;related0591 remains blocked.
- Depends on:existing public ParseError/accepted core compatibility boundary;
  no dependency on0591 extraction implementation.
- Blocks:0591 repaired-baseline handoff and resumption of extraction tests.
- Related:0590 readonly guards;no other plan-owned bug repair included.

## Context / decisions

- Included:current exception code/public signature,pipeline/modules/access
  consumers,actual guard path/frozen manifests,read-only protocol/copy probes,
  accepted0591 and current policies.
- Omitted:other grammar/body moves,Rust/providers,secrets,full historical blobs.
- Assumption:base-class standard reconstruction and pickleable extra state.
- Open decision:delivery approval after authorized acceptance-record actual-SHA revalidation;final result accepted2026-10-18.
  R01–R07/exact2 carriers/dependency design accepted. Future repaired-SHA
  handoff acceptance still required.
- Former0591 P08 failure-preservation proposal rejected by user's direction;
  original successful P08 remains unchanged. Defect ownership transfers here;
  older0591 mismatch section is historical discovery/link,not another live ledger.

## AI planning record — AIP-0592-001

- Status:accepted2026-10-17 with dedicated Issue/spec/Phase0;L/L scope/estimate unchanged.
- Author:Codex host,desktop macOS27.0.1 arm64/CPython3.12.6.
- Displayed model/reasoning:N/A;stable attributable host values unavailable.
- Size:L/L;small production delta but multiple phases,immutable nested guards,
  serialization/copy protocols and dependent-baseline coordination. Not an ETA.
- Intended route:host design/deterministic probes;review.same_context (weaker),
  implementation.host only after explicit approval;modelIDs empty,no override.
- Estimated tokens/range/midpoint/metric:N/A,no calibrated estimator exposed.
- Basis:one exception/reconstruction boundary,3 real production consumers,
  6protocols,copy/deepcopy,state identity,2 guarded carriers and0591 dependency.
- Assumptions:standard base-class behavior,no arbitrary subclass/custom decoder.
- Confidence:high reproduced cause;medium guard integration;external stored
  blob demand/full dynamic consumer graph unassessed.
- Revises/revision reason/superseded by:none.

## Verification / current next gate

Phase1 execution explicitly approved2026-10-17. Added four test modules,two
test-only support modules and four immutable fixtures under tests/liss_0592*
and tests/fixtures/liss_0592. Only the two accepted0590 carriers changed;
production remains byte-identical to22335a57. Exact AST/raw repair proposal
exists only as unexecuted guard data in temporary roots,not implementation.

Initial dedicated run:108 nodes,72 expected failures/36 passes. Behavioral Red:
56 R01 protocol/message/code cases,6 R02 fresh-interpreter real errors,
7 R03 state/memo cases and2 copy cases. Structural Red:1 missing repair.
Passing:constructor/export/AST compatibility,real consumer diagnostic snapshots,
all new positive/negative guards and outside-scope byte preservation.
Inherited guard/ownership/0590 behavior-consumer regressions:293 passed;
adjacent parser/Pauli/factory/DiracF/D/PQN/binder:39 passed.

All at dirty HEAD22335a5768c17a41eb94682e7dd14d3e6df004bd,
macOS27.0.1 arm64/CPython3.12.6/pytest9.0.3,explicit repo PYTHONPATH.
Commands/times/exits/full output:
`/private/tmp/liss-0591-phase0.8hzegU/r592-focused-final.*`,
`r592-inherited.*`,`r592-adjacent.*`. Clause mapping and limitations in spec;
fixture provenance,authoring corrections and resumable state in representative
[trace/handoff](../collaboration/traces/2026-10-17-liss-0592-parseerror-repair.md).
Root/spec/all-sanity not_run this Red phase;no exclusions or all-blocking Green.
R07 final-clean-SHA/full-suite/repaired0591 handoff obligations remain open.
Existing6dirty0591 docs preserved when creating dedicated repair branch;
no commit,push,PR or merge authority inferred. Both original branches point to
same source base;uncommitted files exist only in current shared checkout.

Received2026-10-17:dedicated repair R01–R07,guard/dependent-baseline policy,
Phase0 acceptance,and separate Phase1 execution approval.
Review execution explicitly approved2026-10-18. Same-context review finds
R1 [P2]:new inverse read_text() normalizes CRLF/CR and wrongly accepts raw
changes outside the exact approved additions. Independent pre/post probe:
all6 newline mutations wrongly accepted. Current108 nodes still72 expected
Red/36 pass (same exact failure IDs),inherited293/adjacent39 pass. Passing
regressions do not close R1 or authorize acceptance. No tests/source edited.
[Review packet / R1 disposition](../collaboration/reviews/2026-10-18-liss-0592-phase1-review.md).

R1 correction/re-review explicitly approved and executed2026-10-18. Only the
two new authorized test files changed:raw-preserving UTF-8 read and6 newline
negative nodes. Independent Git-built roots accept4 authorized reader checks
and reject6 mutations through both readers(12 checks);R1 closed in agent review.
Fresh114 nodes:72 expected failures/42 passes,0 errors/skips. All original108
IDs/outcomes unchanged;6 added nodes pass. Inherited293/adjacent39 pass.
Full evidence:r1-592-*-20261018.* in the same external runner directory;
corrected cohort3d77b215…65029e and per-file hashes in review packet.
No production/old carrier/fixture/hash/assertion/exclusion changes or commit.

Received2026-10-18:**LISS-0592 Phase 1 Red 修正済みテストレビュー／acceptance承認**.
Human accepts corrected12-artifact cohort
3d77b2159acb72ad9aae73f347e3f85c20492098706bbca58f20618fb765029e,
including R1 correction/re-review. R01–R07/guard/dependency policy unchanged.
This is test/phase acceptance,not implementation or commit/remote permission.
114-node72 expected Red/42 pass,inherited293/adjacent39 evidence above is
historical from R1,not rerun for this metadata-only acceptance record.
Phase2 Green/implementation explicitly approved2026-10-18 and executed:
only parser.py adds exact reviewed __reduce__/_restore_parse_error blocks,
15 physical lines,no constructor/grammar/import change. Accepted12 test artifact
hashes remain unchanged. Fresh114 focused/293 inherited/39 adjacent/spec161
pass;72 previous focused failures resolved,0 new failures in those same114 IDs.
Root3052 pass (0 errors/skips),exit0. Full all-blocking Green not claimed.
Repository sanity:9 applicable checks pass,copy smoke fails with unchanged
pre-implementation dirty-source rejection on the uncommitted repair spec.
No bypass/hash relaxation. All-blocking completion awaits actual clean SHA.
Details/current evidence in representative trace below. No local commit or
remote action authorized by this implementation approval.
Local commit/actual-SHA all-blocking revalidation explicitly approved2026-10-18.
User typed ISS-0592;unique preceding target is this LISS-0592,not a new issue.
The existing24-file unit includes approved tests/implementation/repair records
and related0591 prerequisite design/navigation;no unrelated change or remote write.
This committed record precedes actual-SHA verification;do not infer success from
it. Actual commit/hash/clean-state and every fresh result are retained externally:
`/private/tmp/liss-0591-phase0.8hzegU/sha592-*-20261018.*` and
`/private/tmp/liss-0592-sha-20261018.hlxElM/` (final summary:final-evidence JSON).
No result-record-only commit follows verification in this step.
Next:LISS-0592 Phase 3 Refactor／review承認,only after all blocking passes.
Implementation:bounded approved repair written;no further scope or Phase3.
Post-review:yes;actual-SHA all blocking,Phase3 review/final/delivery and0591
repaired-baseline handoff remain separate gates. Batch:N/A.

## Current Phase3 review —2026-10-18

Explicit Phase3 approval received/executed. No additional source/test refactor
needed;exact15-line repair preserves readability and responsibilities.
[Phase3 packet](../collaboration/reviews/2026-10-18-liss-0592-phase3-review.md):
no new actionable finding;R1 remains closed. Fresh clean
342ea6ccd41191c6b321f5fce705e2712f83ebd3:114 focused/293 inherited/39 adjacent/
3052 root/161 spec and11 local sanity checks pass;0 failures/errors/skips/
exclusions. Same-context is weaker isolation. Consumer/cold imports/raw+AST
inverse/frozen12 artifacts pass. Prior clean same-SHA:0 new/0 resolved failures;
original Red72 resolved. Accepted R01–R07/guard/dependency/P01–P10 unchanged.

Final verification/review-record commit/actual-SHA rerun explicitly approved
2026-10-18. This record precedes that commit and does not pre-claim results.
Actual SHA/clean state and outcomes:external final592 evidence linked in trace.
If all blocking passes,next:**LISS-0592 最終レビュー結果の受入れ**.
Type:phase;implementation allowed:no new change;post-review:yes;batch:N/A.
0591 waits for final repair gates and accepted baseline/guard-composition handoff.

## Final-result acceptance —2026-10-18

Received **LISS-0592 最終レビュー結果の受入れ**. Human accepts final result
at2c1a3caefb61eaf761b29fe48985c79af6d53068,not an untested future commit.
Clean-SHA macOS27.0.1 arm64/CPython3.12.6/pytest9.0.3:focused114,inherited293,
adjacent39,root3052,spec161 and11 local sanity checks passed;0 failures/errors/
skips/exclusions. Root/focused IDs unchanged versus clean342ea6cc,0 new/resolved
failures;original Red72 resolved. Consumer/import/copy/raw/hash checks pass.
Full commands/times/SHA/environment in external final592 evidence linked by
the [trace](../collaboration/traces/2026-10-17-liss-0592-parseerror-repair.md).

Approval type:phase/final-result acceptance. Approved scope:0592 reviewed repair
and actual-SHA evidence. Implementation allowed:no. Post-review required:yes,
acceptance-record final-SHA revalidation and separate delivery;batch:N/A.
Same-context review/full dynamic-graph/remote-CI gaps unchanged. R01–R07,
P01–P10,guard/dependency clauses/tests/fixtures/hashes unchanged. No0591 baseline
handoff accepted or extraction resumed. No commit/push/PR/merge authorized here.
Acceptance-record commit/actual-SHA revalidation explicitly approved2026-10-18.
This record precedes commit/tests;actual SHA/results live in external accepted592
evidence linked by trace. If all pass,next:push/PR/CI-success-then-merge approval.
No future success or remote permission claimed here.

## Process review / current disposition

- Outcome:not yet;final result accepted at2c1a3cae;record delivery gates remain,Issue stays review/not done. Completion process review at closure.
- New lesson:raw-byte-guard-normalization;baseline/typed authority/guard lessons applied.
- Template feedback:none requested.
