# LISS-0591: Parser operator-primary本体分離

## Metadata

- Local issue ID:LISS-0591
- GitHub issue:none;local planning only
- Status:blocked — actual serialization repair LISS-0592 prerequisite
- Phase:phase-1-red (readiness probe only;tests not authored)
- Type:refactor / behavior-preserving body migration
- Priority:high,next selected WP0175 candidate
- Initial planning size:L
- Current planning size:L
- Reclassification reason:none
- Owner/agent:Codex host / Adjudicator
- Related branch:codex/liss-0591-parser-operator-phase0
- Base:22335a5768c17a41eb94682e7dd14d3e6df004bd

## Summary / acceptance notes

Scope/Architecture Path Phase0 design-start explicitly approved2026-10-16.
Dedicated Issue/spec P01–P10,limited3-carrier policy and Phase0 explicitly
accepted by Adjudicator2026-10-16. Canonical agreement:
[dedicated P01–P10 spec](../specs/parser-operator-primary-successor.md).
Move only117-line operator-primary algorithm to existing family;retain single
Parser state,public/private hooks,AST/ParseError identity,token/error timing.
No actual code/test/fixture/guard edits;no implementation permission.
Three named test carriers may be migrated only after dedicated policy acceptance
and separate Phase1 execution approval. That execution approval was received
2026-10-16,but readiness check exposed the P08 mismatch below;no tests authored.

## Dependencies

- Parent:WP-0175 (I01–I08 inventory accepted2026-10-15).
- Depends on:accepted core decomposition;LISS0590/record delivery resolved.
  New unresolved prerequisite:LISS0592 actual ParseError repair and accepted
  repaired-baseline handoff;no waiver. Previous original source base historical.
- Blocks:none selected;future Parser work has separate gates.
- Related:LISS0547 existing families;BUG-WP0175-002 is separate and not touched.

## Adjudicator decision points

- Received2026-10-16:dedicated Issue/spec P01–P10,exact3-carrier policy,Phase0 acceptance.
- Approval type:phase/design acceptance;approved scope:operator-primary design.
- Implementation allowed:no;post-review required:yes;execution batch:N/A.
- Phase1 execution separately approved2026-10-16;paused before authoring tests.
- Next:LISS0592 final result accepted at2c1a3cae;acceptance-record/SHA and delivery gates pending;
  0591 waits for full review and accepted repaired-baseline handoff.
  Actual repair and repaired-baseline handoff still required;no failure waiver.
- No commit,push,PR,merge,bug repair or further candidate authority inferred.

## Context / design

- Included:accepted core boundary,WP0175,actual parser/entry/context/consumers,
  four manifest provenances,actual copy utilities,selected neighboring tests.
- Omitted:unrelated grammar,Rust,provider/service choice,secrets,history-wide audit.
- Assumptions:mechanical algorithm move,callbacks remain on live Parser.
- Open decisions:P08 baseline discrepancy below;return to design if another
  protected path must change. Narrow protocol/error-factory/guard design accepted.
- Trace/handoff:[representative trace](../collaboration/traces/2026-10-16-liss-0591-parser-operator-primary.md).

## AI planning record — AIP-0591-001

- Status:accepted2026-10-16 with dedicated Issue/spec/Phase0 acceptance;
  size/estimate/scope unchanged,no implementation approval inferred.
- Created by:Codex host,desktop macOS27.0.1 arm64 repository.
- Model/reasoning setting as displayed:N/A;stable identifiers not exposed.
- Created at:2026-10-16 Asia/Tokyo.
- Planning size:L/L;multi-phase split with nested immutable guard/copy closure,
  callback/error boundary and broad regression. Not an ETA.
- Intended route:host scoped design/deterministic checks;review.same_context
  (weaker);implementation.host only after explicit future approval;modelIDs empty.
- Intended scope:sole primary algorithm plus narrow declarations/factory/wiring,
  exact3 test-carrier plumbing under approved guard policy.
- Estimated token range/midpoint/metric:N/A;no calibrated estimator exposed.
- Basis:Parser3679/class3504,body117;3 exception-construction sites,11 callbacks,
  3 actual production imports and4 readonly manifest provenances.
- Assumptions:preserve actual constructor/types and private binding;static
  consumers are not a full dynamic/serialization graph.
- Confidence:high source measurements;medium planned guard closure;unknown
  full dynamic graph/custom serialization/coverage completeness.
- Revises/revision reason/superseded by:none.

## Verification / work notes

Source baseline22335a57;initial tree clean. Inventory14 actual-context probes,
adjacent46PASS,inherited45PASS,spec161/161PASS at clean source SHA. Environment,
commands,timestamps/exits in `/private/tmp/liss-0591-phase0.8hzegU/`.
Root/all-sanity not freshly run;no all-blocking Green or new acceptance test.
Final doc/no-source-change checks are recorded in trace after execution.
Current documents uncommitted;no tested design-commit SHA is claimed.

## P08 readiness conflict (historical discovery;live repair owner LISS-0592)

- Observed2026-10-16 at unchanged source22335a57,macOS27.0.1 arm64,
  CPython3.12.6. Command/dirty-doc state/timing/exit/output captured externally:
  `/private/tmp/liss-0591-phase0.8hzegU/phase1-p08-baseline.json` and .out/.err;
  diagnostic script `/private/tmp/liss-0591-red.DtUMQj/p08-baseline.py`.
- Existing `ParseError.__init__` calls `super().__init__(message)` so args
  contain only message. Standard pickle reconstruction invokes the class with
  that one argument;required line/col are absent. Dumps succeeds,loads fails
  with TypeError. Ordinary OpLit with Span round-trips successfully.
- Accepted P08 expects representative AST/error round-trip,while the accepted
  boundary forbids changing the ParseError class/constructor. Both cannot be
  claimed satisfied by a pure body migration under current default behavior.
- This was a Phase0 design evidence omission by the authoring agent. Not a
  new product regression,not a structural extraction Red,not proof that
  normal parsing or compilation is broken. No coverage/behavior waiver.
- Proposed disposition (not yet approved):change only P08's error serialization
  expectation to characterize/preserve the existing default-load TypeError,
  retain successful AST round-trip and public class/error field identity.
  Tests must explicitly distinguish dump success from load failure,not skip
  the path or install a custom reducer. A serialization fix requires a
  separate behavior-change scope/spec/Red/implementation gate.
- Current P01–P10 bytes and guard policy unchanged. No production/test/fixture/
  guard edits performed;remaining Phase1 work paused at readiness.
- Approval requested:bounded P08 correction proposal authoring only;then human
  corrected-spec acceptance before resuming Phase1. Previous Phase1 approval
  is retained,not inferred as acceptance of a changed contract. No Phase2,
  constructor fix,commit or remote action allowed. AIP0591-001 L/L unchanged.

Update2026-10-17:human rejected the failure-preservation direction and requested
proper repair/completion. Above limited-correction proposal is superseded.
Live repair contract/planning now belong to
[LISS-0592](LISS-0592-parseerror-serialization-repair.md),not a duplicated bug
ledger here. P08 success requirement retained. Repair needs its own reviewed
specification/Red/implementation;0591 retains prior Phase1 authorization but
waits for repair and accepted fresh-baseline/guard-composition handoff.

## References

- [Accepted core decomposition](../specs/staqex-core-module-decomposition.md).
- [WP-0175](../work-plans/WP-0175-source-responsibility-inventory.md).
- Original source evidence is repository Git22335a57;no external technology chosen.

## Process review

- Outcome:not yet;issue blocked on specification disposition,not done.
- Lesson written:no new rule;existing ownership/private consumer/guard/typed
  approval/real-site/quantitative lessons applied in design.
- Template-feedback path:none requested.
