# LISS-0593: Scientific Semantic pure-family body migration batch

- Local issue ID: LISS-0593
- GitHub issue: none; local planning
- Status: done — PR #624 merged to main as `e7387a53`; PR checks and main merge checks passed
- Phase: Phase 3 Refactor and final verification complete; committed SHA `6b8f0091b905ed023971876cf3e11a64222cb9e8` passed all blocking local checks; delivery completed 2026-10-23 JST
- Type: behavior-preserving refactor; bounded-batch proposal
- Priority: first proposed low-state-coupling batch under WP-0175
- Initial / current planning size: L / L; no reclassification
- Owner: Codex host / Adjudicator
- Parent: WP-0175
- Depends on: accepted core decomposition; delivered LISS-0590/0591/0592
- Blocks: no unrelated work
- Related branch: codex/liss-0593-pure-semantic-batch-design
- Specification: [F01–F10](../specs/scientific-semantic-pure-family-batch.md)
- Trace/handoff: [2026-10-22](../collaboration/traces/2026-10-22-liss-0593-pure-semantic-batch.md)

## Scope and decisions

User requested grouping safely movable responsibilities to reduce context
cost. Continuation authorizes candidate selection/Phase0 design, not acceptance
of previously unnamed functions or unwritten tests. Proposed batch owns only
fingerprint and inspection/rejection view generation: three functions,86 span
lines,three existing production files. No line-count target or deletion.

Historical authored checkpoint:human explicitly accepted F01–F10/limited guard policy
and Phase0 and separately authorized Phase1 Red. Authored249 new cases:
240 PASS/9 expected Red;inherited431 PASS/2 test-path Reds;adjacent28 PASS;
root3492 PASS/11FAIL,same exact union;spec161/161 PASS. Error/skip/exclusion0.
Production/three live carriers remain unchanged;no test acceptance or Green
authority. Evidence:/private/tmp/liss-0593-red-20261022.Sv1yMV/result.json.
Review execution subsequently approved and performed:changes_requested/R1,
missing independent relation.kind/node_ids mutation cases required by F02.
N1 recommends persistent mixed inspection data. No tests fixed during review;
next gate is R1 test-only correction/re-review approval,not test acceptance.
[Review packet](../collaboration/reviews/2026-10-22-liss-0593-phase1-red-review.md)
owns fresh receipts and bounded correction request. Earlier Phase0 next-decision
statements below are historical.

Historical corrected-Red checkpoint:R1 test-only correction/re-review explicitly approved and
performed. Added relation.kind/node_ids individual mutations and one persistent
mixed lane/exactness/type-dimension input. R1/N1 closed in agent re-review;
focused252:243PASS/9Red,inherited431PASS/2FAIL,adjacent28PASS,spec161PASS.
Fresh root3506:3495PASS/11FAIL,prior3503 node IDs retained plus3 PASS,unchanged
failure IDs/error0/skip0/excluded0. Original algorithms/live guards,other nine
cohort artifacts and accepted F clauses unchanged. Current
[re-review](../collaboration/reviews/2026-10-22-liss-0593-phase1-r1-review.md)
owns exact corrected cohort and counterexamples. Human corrected-test
review/acceptance subsequently explicitly approved2026-10-22 JST for exact
cohort496c5d8a11a57a6ce2c42262812d684dcb8f99a2c2e015cd0eb027486a116c1c
and R1/N1 closure. Next:separate Phase2 Green/implementation approval;no source
or live-carrier application,commit or remote delivery authority yet.

Historical implementation checkpoint:Phase2 Green/implementation explicitly approved. Applied
exact reviewed three-source/three-carrier changes,accepted cohort unchanged.
Focused252 PASS,adjacent28 PASS,spec161 PASS,compileall PASS. Inherited433:
431PASS/2FAIL,new IDs:0591 B04/B05 liss_0590 carrier diagnostic regex and B08
synthetic test inventory;old P10/R06 path failures resolved. Root3506:
3504PASS/2FAIL in443.74s,same two new guard failures;all prior11 failures
resolved,all3506 node IDs retained,error0/skip0/excluded0. Template-copy smoke independently refuses uncommitted distributed
spec. No full Green,Phase3,commit or delivery claim. Stop before changing the
accepted inverse or further carriers;request guard-consumer compatibility
supplement Scope/Phase0 design. Trace owns exact receipts and next gate.

Historical guard-consumer supplement Phase0 handoff2026-10-23 JST:[G01–G09](../specs/scientific-semantic-pure-family-batch.md),
2-file repair policy and supplemental Phase0 explicitly accepted. The accepted
G table56d9c156…c55498c is unchanged;no Red authoring/helper/caller edits yet.
Keep old0591 test file/regex/negative assertions
unchanged;propose explicit caller diagnostic and complete declared26path union.
No fourth existing carrier or production edit. Future Green repair limited to
0593 helper and0591 helper;future Red additions limited to existing0593
composition test. At that point Phase0 acceptance was not Red execution or
implementation approval.
Parent Phase2 remains not Green;copy smoke still needs later authorized clean
actual-SHA verification. Next at that point:separate supplement Phase1 Red execution approval
for G01–G09 tests and read-only adoption of the two existing failures.
No commit/Phase3/delivery authority.

Supplement Red execution subsequently explicitly approved2026-10-23 JST.
Appended83cases/staged TEST plumbing only to existing0593 composition test;
all old231lines/assertions and other933compiler/test artifacts unchanged.
Focused335:330PASS/5expected live-contract Red;new cohortcb85f98a…8851c.
Readonly inherited433:431PASS/2same failures;root3589:3582PASS/7FAIL,exactly
5new+2adopted. Original3506nodes retained plus83,error/skip/excluded0.
Adjacent28PASS,spec/compileall exit0. No live helper/caller/production/fixture change.
## Human guard-consumer supplement Phase1 Red acceptance —2026-10-23 JST (historical)

Adjudicator explicitly accepted the reviewed83-case supplement Red cohort
`cb85f98ae0752650b6dac5ff494ee6967586c74c58395ca3b3a24a0a78b8851c`, agent
review and exact test scope. Review packet:
[2026-10-23 supplement review](../collaboration/reviews/2026-10-23-liss-0593-supplement-phase1-review.md).
Focused335:330PASS/5expected Red;inherited433:431PASS/2same blockers;
adjacent28PASS;root3589:3582PASS/7FAIL,exactly5new+2inherited. All3506 prior
root node IDs remain plus83;error/skip/excluded0. This decision accepts tests
only and does not authorize helper/caller repair,commit or delivery.

At acceptance, no code/test/fixture/accepted-clause
change was made and no test rerun was needed for the metadata-only decision. The tested dirty
HEAD103fba434ab01db5534981bd5784d833a457b222 and cohort hashes remain unchanged;
document/spec/lifecycle/link/whitespace checks were rerun. Full sanity/source-clean
copy smoke and actual-final-SHA checks remain open. Phase2 approval and outcome
are recorded below; acceptance itself did not authorize implementation.

## Phase2 Green implementation —2026-10-23 JST

Adjudicator separately approved **LISS-0593 guard-consumer補足 Phase2 Green／implementation approval**.
Implemented only the accepted two-file repair in
`tests/liss_0593_guard_support.py` and `tests/liss_0591_guard_support.py`:
keyword-only rejection diagnostic with unchanged default/error propagation,
0591 public test/fixture set composition by private aliases, and the matching
exact corrected-post carrier generator. Accepted tests and fixtures were not
changed;the inherited0591 migration test remains byte-identical.

Verification at dirty HEAD `103fba434ab01db5534981bd5784d833a457b222`:
focused335/335, inherited433/433, adjacent28/28, root3589/3589,
spec161/161, compileall all pass; zero errors/skips/exclusions. All3506 prior
root IDs remain plus83 accepted supplement cases;the two inherited failure IDs
are resolved. Repository sanity:9/10;template-copy source-clean smoke rejects
the uncommitted distributed spec. No full all-blocking Green or final-SHA
verification is claimed. Evidence:
`/private/tmp/liss-0593-phase2-20261023-result.json`.

Issue remains review/not done. Next request: **LISS-0593 ローカルコミット／実SHAで全blocking再検証承認**.
No commit,Phase3,PR,push or merge was performed/authorized by this Phase2 gate.

## Phase2 local commit / actual-SHA verification —2026-10-23 JST

Adjudicator authorized the local commit and actual-SHA all-blocking rerun.
Commit `ebde7eb210c2a3d458a4b7fb013c44e1ac387044` is the tested Phase2 code
SHA. Focused335, inherited433, adjacent28, root3589, spec161, compileall,
source-clean template copy, CI-style template-copy smoke, and applicable local
sanity checks passed. All prior3506 root IDs were retained and83 accepted
supplement IDs added; errors/skips/exclusions0. The working tree was clean.
The raw evidence fixture `tests/fixtures/liss_0593/source-fingerprint.txt`
retains its intentional frozen trailing blank line; no fixture bytes were
normalized. Receipts are under `/private/tmp/liss-0593-final-ebde7eb2-*.xml`.

## Phase3 Refactor / same-context review —2026-10-23 JST

Adjudicator authorized Phase3 Refactor/review. The readability-only change is
limited to `tests/liss_0593_guard_support.py`: common exact dispatch generation
is expressed once, and `historical_carrier_bytes` names the requested artifact
and allowed shapes explicitly. No accepted test, assertion, fixture, exclusion,
or production module changed. A first candidate that reformatted the pinned
0591 carrier was rejected by G05 and reverted; the accepted raw shape remains
unchanged.

The same-context reviewer pass is recorded in the
[Phase3 review packet](../collaboration/reviews/2026-10-23-liss-0593-phase3-review.md).
On the dirty tree at HEAD `ebde7eb210c2a3d458a4b7fb013c44e1ac387044`, final
focused335/inherited433/adjacent28/root3589 all passed, spec161 passed,
compileall and applicable local checks passed, errors/skips/exclusions0. The
root test IDs exactly match the Phase2 committed root; no failure changed.
The Phase3 helper edit remains uncommitted. Review-change module ownership for
the overall feature remains unknown because no source module map/budget is
configured; this is reported as a measurement gap, not a zero-risk claim.
## Final verification —2026-10-23 JST

Adjudicator authorized final verification. Ran against dirty tree at HEAD
`ebde7eb210c2a3d458a4b7fb013c44e1ac387044` (no commit or delivery action).
Environment: CPython3.12.6, pytest9.0.3, numpy2.4.6, PyYAML6.0.3,
Darwin27.0.0 arm64. Focused335/335, inherited433/433, adjacent28/28,
root3589/3589, spec161/161 passed; compileall passed. All four JUnit
cohorts have zero failures/errors/skips; IDs and statuses exactly match their
Phase3/Phase2 comparison receipts, with no additions, removals, or changed
outcomes. Receipts:
`/private/tmp/liss-0593-final-phase3-{focused,inherited,adjacent,root}.xml`.

Repository checks passed: required docs89/89, ADRs10/10, batch review records
20/20, document lifecycle1, coverage ledger, active-Red lifecycle0, refactor
baseline3/3, shell syntax, compileall, and `git diff --check`; conflict-marker
search found no matches. The CI-equivalent template-copy smoke exited1 because
`docs/specs/scientific-semantic-pure-family-batch.md` is an uncommitted
distributed source. This blocker is not waived. Runtime and local checks pass,
but final all-blocking Green is **not established**.

Working tree remains dirty with the Phase3 helper and review/trace/issue/spec/
WP/process-lesson records. Helper SHA256:
`ab57c9f4ff5076d3eac4fdc634ef4497e66e8f5459a557391ab97d9b3f1c0fce`.
Uncommitted evidence is provisional. Next gate is separate local-commit and
actual-SHA all-blocking verification approval; no commit, push, PR, or merge
was authorized or performed here. Status remains review/not done.

Follow-up authorization: the user explicitly authorized committing this
reviewed Phase3/record set, then pushing, opening/updating a PR, verifying CI,
and merging only after CI succeeds. This does not waive the fresh actual-SHA
blocking rerun. Delivery is in progress; issue remains review/not done until
the required checks, merge, and status synchronization are complete.

The following was the pre-supplement planning checkpoint (historical). The
product bodies are independent of shared mutable state. Guard composition
is not automatically low risk: three frozen-production manifests and the
0591 B06 no-project-import contract require the explicit F07–F09 supplement.
Do not start Red, change an accepted test, or migrate production here.

At that checkpoint the next decision was acceptance of the dedicated
Issue/spec F01–F10, bounded three-carrier guard proposal and Phase0, followed
by separately authorized Phase1 Red. Those gates are historical and have since
been completed as recorded above.

## Completion / delivery —2026-10-23 JST

- Reviewed Phase3/refinement and synchronized records were committed as
  `6b8f0091b905ed023971876cf3e11a64222cb9e8` and delivered in
  [PR #624](https://github.com/nn0cl/staqex/pull/624). The PR was merged after
  all three required checks succeeded; merge commit `e7387a53` is on `main`.
- Actual-SHA verification at the committed head: focused335/335,
  inherited433/433, adjacent28/28, root3,589/3,589, spec161/161; compileall,
  source-clean template-copy smoke, CI-style copy smoke, and applicable
  repository sanity checks passed. Zero failures, errors, skips, or exclusions.
  Environment and receipts are recorded in the trace and PR description.
- The PR's repository-sanity, kernel-root-suite, and spec-verification checks
  all succeeded; the merge page also reported three successful merge checks.
- Process review: no operating-contract deviation or unresolved operational
  problem found. The GitHub connector denied write access, so the already
  authorized merge was completed in the authenticated browser after confirming
  all checks; the PR visibly reached merged/closed state.

## AI planning record — AIP-0593-001

- Status: accepted with F01–F10/Phase0,2026-10-22 JST; author: Codex desktop host.
- Size: L/L; three source files plus cross-generation guard composition,
  consumer verification and multiple gated phases. Pure bodies alone do not
  make the whole task S. No calibrated elapsed-time/token estimate available.
- Route: host design/implementation when authorized; same_context review,
  weaker than independent review; model/reasoning/token identifiers N/A,
  not exposed as stable recordable values. No external AI or private payload.
- Basis: baseline103fba43; exact AST spans67/9/10, dependencies limited to
  stdlib/model; existing family owners; immutable guard/copy consumers.
- Confidence: high for measured bodies, medium for proposed bounded guard
  composition; validation/mutation controls remain future Red evidence.
- Assumptions: signatures/exports and diagnostics remain unchanged; no new
  import cycle. Unknown dynamic consumers are a limitation,not a waiver.
- Revises/superseded by: none. Product/guard scope expansion requires review.

Planning update2026-10-22:guard-consumer supplement keeps L/L;the pure runtime
move is already applied but diagnostic/public-inventory and exact raw-projection
composition still cross historical test boundaries. G01–G09 proposes2repair
files with no new carrier;confidence remains medium until inherited positives
and all negative/missing-artifact cases pass. No time/token estimate;old phase
measurements are evidence,not an effort prediction. Same host/same_context route.

## Verification / remaining work — historical pre-supplement snapshot

At the original checkpoint Phase1 R1/N1 was accepted and three-source/three-
carrier implementation had exposed two inherited compatibility gaps. That
snapshot's limited diagnosis and root receipts are historical, not current
verification. The guard-consumer supplement and Phase2 repair are now recorded
above. Remaining gates are local commit/actual-SHA full-blocking verification,
Phase3/refactor review, final verification and separately authorized delivery;
no failure waiver.
