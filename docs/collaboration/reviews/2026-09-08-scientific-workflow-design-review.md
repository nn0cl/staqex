# Independent correction review — Scientific Workflow design

## Trigger

- User request: Solとして、Sora作業ツリーの設計案を独立に再確認し、
  S01/S02に限定しない完成形Scientific Workflowへ修正する。
- Date: 2026-09-08 (Asia/Tokyo).
- Review scope: 設計書、Proposed ADR、受入仕様、後継WP/LISS、review/traceだけ。
- Issue / ADR / Spec / WorkPlan: LISS-0514 / ADR 0217 Proposed /
  Scientific Workflow acceptance proposal / WP-0131.
- Branch: detached worktree at 26596314; branch/commit/PR/merge操作なし。
- Current phase: Architecture Path / phase-0-design correction.
- Allowed paths: docs/** の上記設計成果物とproposal navigation。
- Explicitly excluded paths/actions: production source、tests、runtime、
  provider SDK、credentials、live QPU、既存完了WP/LISS本文、Git mutation。

## Review lenses

- Applicable lenses: 1–11のうち、contract completeness、architecture/adapter boundary、
  source fidelity、type/dimension closure、state/physics safety、Realize fail-closed、
  migration safety、approval discipline、evidence hygiene、canonical authority、
  projection conservation。
- Why: 観測metadataからsource-derived Semantic IR、古典/量子projection、
  Workflow/Plan採用まで複数の権威・変換・人間判断境界を跨ぐXL設計だから。
- Prior review records consulted: 7a62作業ツリーの
  2026-09-08-scientific-workflow-design-review.md。それは
  same_context 自己reviewと明記されており、独立承認としては扱わない。

## Independent reviewer

- Context mode: Sora案とは別のCodex task/worktreeで、Solがrepository artifactsを再読。
- Reviewer task: Sora案を根拠ではなくreview対象として扱い、採否と追加修正を決める。
- Read-only: Iteration 1のreview時はyes。Iteration 2でSolがcorrection authorへ役割変更。
- Implementation permission: no.
- Approval authority: none.

## Iteration log

### Iteration 1 — independent REVIEW

- State entered: REVIEW.
- Artifacts inspected: AGENTS/Quickstart/AT-TDD/conventions/readiness/process lessons、
  current decision/open-work registers、ADRs 0210–0212、scientific semantic/input/
  continuous/hybrid/S01/旧S02 contracts、7a62のcomplete design/ADR/spec/WP/review/traceと
  全child WP/LISSのfield/dependency inventory。
- External evidence: OGC CityGML/SensorThings、W3C SOSA/SSN/PROV-O、
  IVOA ObsCore/VOTableの一次資料。概念の存在と責務だけを確認し、
  version/profile/library採用は認定していない。
- Readiness verdict: **NOT READY for Phase 1 or implementation**。
  Sora案は広いcoverageを持つが、下記修正とfresh contract re-reviewが必要。

| Finding | Priority / lens | Evidence | Disposition |
|---|---|---|---|
| SWR-01 | P0 / 8,9 | 7a62 reviewはsame_context、traceもSora自己review。修正後の独立review成立証拠がない | accepted。現在のrecordをcorrection loopとして作り、terminalをopenにする |
| SWR-02 | P1 / 2,7 | WP-0148がWP-0142天文profileに依存し、汎用Observationではなく分野adapterを横断前提にしていた | accepted。WP-0132/0133/0145へ付替え、astronomy blocksから除去 |
| SWR-03 | P1 / 1,6 | complete designはclassical-only Workflow成立可とする一方、WP-0131の単一completion説明はquantum比較を必須に見せる | accepted。個別classical Workflowとprogram全体のhybrid接続claimを二層化 |
| SWR-04 | P1 / 7,8 | 7a62案は完了済みWP-0093と既存planning baseline本文にnavigationを追記する | accepted。既存完了WP/LISS本文は変更せず、新WP/open-work側だけで後継を記録 |
| SWR-05 | P1 / 2,9 | 標準mapping proposalと具体version/profile/technology decisionの分離はproseのみでgate名が弱い | accepted。完成形設計§4に二段階gateを明記 |
| SWR-06 | P1 / 9 | child計画とtraceのauthor/routeがSoraのままで、Solの判断差分を追えない | accepted。Sol authoringへ更新し、このreviewとtraceに再利用・差分を記録 |

- Finding dispositions: すべてSolが依頼scope内の設計訂正としてaccepted。
  Architecture/technology選択を必要とする内容は決定せずProposedのまま。
- Design-deviation check: no。既存Accepted ADR/spec/runtime behaviorは変更せず、
  新proposalの依存と説明を修正した。
- Reviewer perspective to retain: 「共通coreが分野adapterを依存先にしないか」と
  「個別Workflow成立とprogram capability completionを同じgateにしていないか」を確認する。
- New recurring perspective: process-lessons-logの
  coverage-authority-boundary に記録。perspectives ledger自体は変更しない。

### Iteration 2 — DISPOSITION / CORRECT

- State entered: DISPOSITION then CORRECT。
- Corrections applied: SWR-01–06。Sora案の共通意味モデル、分野coverage、
  Gherkin/EARS matrix、M0分割、27 child WP/LISSは再読後に採用した。
- Deliberately not reused: Sora自己reviewの完了含意、Sora著者表記、
  WP-0093/0118/0119本文への追記、天文依存の物理profile。
- Files changed: complete design、ADR 0217、acceptance、WP-0131–0158、
  LISS-0514–0541、proposal navigation、process lesson、本record、trace。
- Remaining blockers: 修正後成果物に対するfresh independent contract re-review、
  Adjudicator Architecture 0217-A判断、M0 acceptance review。
- Next review condition: current worktreeの修正後filesと最終決定的検査結果を、
  編集しないfresh reviewer contextが再読する。

### Terminal decision

- Terminal state: not terminal.
- Completion basis or abort reason: 設計訂正は完了したが、修正後の独立契約reviewは未実施。
- User/Adjudicator decision required: ADR 0217-A Architecture判断とM0受入審査。
- Evidence path: 本record、[trace](../traces/2026-09-08-scientific-workflow-design.md)、
  [WP-0131](../../work-plans/WP-0131-scientific-workflow-program.md)。

## Gate status

- Requested approval type: next minimum is **architecture** for ADR 0217-A,
  paired with review of M0 G01/G02/G03 acceptance wording.
- Approved scope: design correction only, per user request.
- Approval authority / approver: Adjudicator; pending.
- ADR status: 0217-A/B/C all Proposed.
- Specification status: Proposed; M0 not independently contract-reviewed.
- Phase approval: none. Phase 1 Red is not authorized.
- Implementation approval: none.
- Post-review requirement: fresh independent contract review, then explicit
  Phase 1 approval; later reviewed Red and separate Implementation approval.
- Gate evidence path: ADR 0217、acceptance M0、WP-0132/LISS-0515、本record。

## Evidence

- Finding evidence: 上表のartifact/sectionと、traceのdeterministic checks。
- Deterministic checks: final results are recorded in the linked trace.
- Related trace: [Scientific Workflow design correction trace](../traces/2026-09-08-scientific-workflow-design.md).
- User/Adjudicator decision still required: Architecture 0217-A、M0 acceptance、
  fresh independent contract review。Technology、Phase 1、Implementationは未承認。

## Review Target

- Artifact: ADR 0217-A、Scientific Workflow acceptanceのM0、
  WP-0132/LISS-0515。
- Current phase: Architecture Path / phase-0-design correction.
- Requested approval: 0217-Aをaccept/reject/要修正と判断し、
  M0 G01/G02/G03が次のPhase 1審査対象として十分にboundedか確認する。
- Approval type: architecture.
- Approved scope: 2026-09-08依頼の設計訂正だけ。
- Implementation allowed: no.
- Post-review required: yes。修正後packetのfresh independent contract reviewと、
  別のPhase 1 Red承認。
- Execution batch ID: none.

## What Changed

- Metadata/IR権威、Adapter profile、cross-domain意味モデル、M0、
  S02/S01/連続/離散/Workflowの後継設計を一つのProposed packetへ整理した。
- Sora案のreview状態、分野間依存、completion claim、履歴保護、著者帰属をSolが訂正した。

## Why It Matters

- 0217-AだけならDB/ontology/SDK/source syntaxを選ばず、
  観測identity/trustと非実行権威境界を先に審査できる。
- Architecture審査とacceptance審査を終えてもPhase 1/Implementationは自動的に許可されない。

## Adjudicator Checklist

- [ ] Current phase is phase-0-design correction.
- [ ] Included context is sufficient for 0217-A and M0 only.
- [ ] Omitted technology and implementation context is acceptable.
- [ ] Metadata Graph does not become executable Semantic IR.
- [ ] G01/G02/G03 fixtures and negative neighbors are sufficiently bounded.
- [ ] Mapping proposals do not imply external profile/technology adoption.
- [ ] Fresh independent contract review remains a post-correction requirement.
- [ ] Phase 1 and Implementation permission remain explicitly unapproved.

## Decision

- [ ] Approved
- [ ] Approved with comments
- [ ] Rejected
- [ ] Needs ADR

## Post-review correction

The P1 inventory finding is resolved as a counting-convention clarification,
not by adding a missing package. The program contains 28 WP records and 28
LISS records: one parent WP/LISS pair plus 27 child WP/LISS pairs. The same
breakdown is now stated in WP-0131, LISS-0514, the open-work register, and the
design trace. A fresh review remains required for the corrected packet; this
clarification does not grant Architecture, Phase, or Implementation approval.

## Fresh independent contract review — completed

- Reviewer: lightweight fresh Codex context (`gpt-5.4-mini`), read-only.
- Reviewer task: `01a07e8f-15f5-76f3-8070-fd4f05367d61`.
- Target: the corrected packet in `/Users/nn0cl/.codex/worktrees/23ea/qpex`.
- Verdict: **approve** for the design packet; no P0/P1/P2 findings.
- Verification: 28 WP records and 28 LISS records, each consisting of one
  parent pair plus 27 child pairs; dependency and 59-edge DAG claims were
  found internally consistent; the broader scientific scope and approval
  separation were preserved.
- M0 readiness: **yes**, proceed to ADR 0217-A Architecture review together
  with WP-0132/LISS-0515 M0 acceptance review.
- Limitation: this is read-only design review evidence, not Architecture,
  Phase 1, or Implementation approval.

## Architecture decision recorded after review

- Adjudicator decision: `ADR 0217-A Architecture承認` (2026-09-08).
- This decision accepts only the 0217-A boundary described above. It does not
  accept 0217-B/C, technology selection, Phase 1, or implementation.
- The next gate is the WP-0132/LISS-0515 M0 G01/G02/G03 acceptance review; this
  review record is not changed into a Phase 1 approval.

## M0 acceptance decision recorded after review

- Adjudicator decision: `WP-0132 / LISS-0515 M0 G01/G02/G03 acceptance 承認`
  (2026-09-08).
- Accepted: the bounded G01/G02/G03 contract, six in-memory fixtures, and M0
  exit criteria.
- Excluded: Phase 1 Red, Phase 2/Implementation, Phase 3, technology selection,
  provider/SDK, credentials, and live submission.
