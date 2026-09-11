# Scientific Workflow design correction trace

## Request / current phase

- Date: 2026-09-08 (Asia/Tokyo).
- Request: Sora役で完成形Scientific Workflowの設計を修正。S02実測hit-to-lead優先、S01と全科学分野、WP/LISS/ADR/レビュー/承認分離/Sol指示案を作成。
- Current phase: Architecture Path / phase-0-design; design correction delivered for review.
- Canonical planning record: [WP-0131](../../work-plans/WP-0131-scientific-workflow-program.md), AIP-WP-0131-2026-09-08-001 / LISS-0514.
- Implementation permission: no. Tests/production/branch/commit/PR/mergeは実行しない。
- Issue/WP status: parent review、children proposed。doneにしていないためprocess completion reviewは未起動。

## Context ledger

- Included: AGENTS/Quickstart/AT-TDD/conventions/readiness、current decision/open-work registers、science input/scopes/workflow/semantic/continuous contracts、ADRs 0210–0212、S01 locked/旧S02、既存WP/LISSの関連status/closeout、process lessons、routing/privacy/lifecycle/DoD。
- Public external context: OGC/W3C/IVOA/ChEMBL/RDKit一次資料。出典は設計§4に直接リンク。標準mappingは提案でありSDK/version採用の証拠ではない。
- Omitted: raw scientific datasets、秘密、無関係source、provider logs、historical branch内容、full runtime re-audit。
- Assumptions: existing ports/IRは再利用候補、能力は受入証拠を個別確認。履歴上の成功を今回再実証していない。
- Open decisions: ADR 0217-A/B/C、実測assay/data profile、model/solver/library/version、数値threshold、S01安全/公平policy。

## Routing / execution attempt 1

- Agent/environment: Sora role / Codex desktop / local worktree.
- Displayed model/reasoning: N/A —役割のみ指定、構成表示値は取得していない。
- Route: host design, same_context reviewer, deterministic shell/Python checks. No subagent spawned.
- Estimated token range/midpoint: N/A — profile/technology未確定、信頼できる根拠なし。
- Actual tokens / metric / source / attribution: N/A —このattemptに帰属するusage telemetryなし。推定actualを書かない。
- Variance: N/A。Attempt boundary: one cohesive docs-only design correction; draftの未作成traceリンクは最終生成で解決しreplanningなし。
- Scope/result: 共通設計、ADR案、受入案、親1+子27 WP/LISS、entry/current navigation、review/lessons。

## Cost / reasoning control

- Operating path: Architecture Path。全分野を跨ぐ要求のためXL設計、implementation taskではない。
- Evidence selection: Canonicalから関連spec/ADR、その後関連status evidence。全文repositoryは読まない。
- Deterministic work: ID inventory、Markdown link/field/whitespace検査、WP/LISS dependency DAG、git diff、lifecycle。
- Rework from review: S02量子比較の独立WP追加、reproducibilityをS02/S01の依存に追加、ADR 0217-A/B/C分割、6 WPのM→L再分類とM unit分割。
- Lessons applied: authority-boundary、migration-boundary、status-drift、acceptance-boundary、phase-acceptance-boundary、review-boundary-observability、ID uniqueness。新coverage-authority lessonを記録。
- Escalation: ADR/XLでsame-contextは独立承認の代わりにならない。レビューpacketをAdjudicator判断へ渡す。

## Decisions and next safe action

- Approved scope: この依頼による設計修正のみ。
- Requested next review: ADR 0217-A Architecture + WP-0132/LISS-0515 G01/G02/G03 acceptance (M0)。B/C、Technology、Phase 1、Implementationへ承認を推定しない。
- After approval: Phase 1 Redを別途承認してからLunaへ1 WPまたは1 unit/1 phaseで渡す。
- Post-review requirement: Adjudicator Architecture判断、独立した契約review、各phase別承認。
- Sol instructions are a proposal in WP-0131; no task message or global agent instruction was changed.

## Verification

- `git diff --check`: PASS.
- `python3 /tmp/validate_science_docs.py`: PASS — 70 Markdown files only; new WP-0131–0158 (28) / LISS-0514–0541 (28) unique; 27 child WP / 58 dependency edges form a DAG; WP/LISS dependency sets agree; no broken local links or missing required WP fields.
- `python3 scripts/check-document-lifecycle.py`: PASS (1 template register; scope limitation below).
- Existing duplicate WP-0117 filenames were detected and left unchanged as unrelated ledger work.
- Production/test changes: none. Runtime tests, SDK installation, data download, and hardware checks: not run; not part of this design correction.
- Review: same_context with remaining human/independent Architecture review. No Red/Green/Refactor implementation status is claimed.

The scratch checker `/tmp/validate_science_docs.py` reads all paths from `git status --porcelain -uall`,
checks local Markdown links against disk, rejects non-doc changes, verifies new ID/title uniqueness,
checks required WP fields and proposed/no-implementation state, compares WP and LISS dependency sets,
and performs DFS cycle detection. It does not change repository files or constitute a production test.

`python3 scripts/check-document-lifecycle.py` only checks explicit canonical-document-register files;
this repository has a template register, so a pass does not by itself prove the new design is canonical.
Entry/open-work navigation is checked separately and labels the new design Proposed.

## Changed files

The following is the complete design-task change inventory. Existing files receive proposal navigation,
coverage/lineage notes, or the lesson; accepted runtime semantics and historical approval prose remain intact.

- updated: [docs/README.md](../../README.md)
- updated: [docs/architecture/open-work-register.md](../../architecture/open-work-register.md)
- updated: [docs/collaboration/process-lessons-log.md](../process-lessons-log.md)
- updated: [docs/specs/staqex-hybrid-workflow.md](../../specs/staqex-hybrid-workflow.md)
- updated: [docs/specs/staqex-scientific-input-and-parameter-binding.md](../../specs/staqex-scientific-input-and-parameter-binding.md)
- updated: [docs/specs/staqex-v1-s02-drug-discovery-benchmark.md](../../specs/staqex-v1-s02-drug-discovery-benchmark.md)
- updated: [docs/work-plans/WP-0093-s02-language-expressiveness-and-selection.md](../../work-plans/WP-0093-s02-language-expressiveness-and-selection.md)
- updated: [docs/work-plans/WP-0118-implementation-readiness-backlog.md](../../work-plans/WP-0118-implementation-readiness-backlog.md)
- updated: [docs/work-plans/WP-0119-real-qpu-readiness-roadmap.md](../../work-plans/WP-0119-real-qpu-readiness-roadmap.md)
- new: [docs/architecture/adr/0217-scientific-workflow-metadata-and-projection.md](../../architecture/adr/0217-scientific-workflow-metadata-and-projection.md)
- new: [docs/architecture/scientific-workflow-complete-design.md](../../architecture/scientific-workflow-complete-design.md)
- new: [docs/collaboration/reviews/2026-09-08-scientific-workflow-design-review.md](../reviews/2026-09-08-scientific-workflow-design-review.md)
- new: [docs/collaboration/traces/2026-09-08-scientific-workflow-design.md](2026-09-08-scientific-workflow-design.md)
- new: [docs/issues/LISS-0514-scientific-workflow-program.md](../../issues/LISS-0514-scientific-workflow-program.md)
- new: [docs/issues/LISS-0515-scientific-metadata-graph.md](../../issues/LISS-0515-scientific-metadata-graph.md)
- new: [docs/issues/LISS-0516-scientific-typed-bindings.md](../../issues/LISS-0516-scientific-typed-bindings.md)
- new: [docs/issues/LISS-0517-s02-measured-assay-profile.md](../../issues/LISS-0517-s02-measured-assay-profile.md)
- new: [docs/issues/LISS-0518-s02-leakage-safe-model.md](../../issues/LISS-0518-s02-leakage-safe-model.md)
- new: [docs/issues/LISS-0519-s02-classical-batch-baseline.md](../../issues/LISS-0519-s02-classical-batch-baseline.md)
- new: [docs/issues/LISS-0520-scientific-quantum-projection.md](../../issues/LISS-0520-scientific-quantum-projection.md)
- new: [docs/issues/LISS-0521-scientific-workflow-lifecycle.md](../../issues/LISS-0521-scientific-workflow-lifecycle.md)
- new: [docs/issues/LISS-0522-s02-assay-batch-cycle.md](../../issues/LISS-0522-s02-assay-batch-cycle.md)
- new: [docs/issues/LISS-0523-geographic-sensor-adapter-profile.md](../../issues/LISS-0523-geographic-sensor-adapter-profile.md)
- new: [docs/issues/LISS-0524-s01-rolling-plan-validation.md](../../issues/LISS-0524-s01-rolling-plan-validation.md)
- new: [docs/issues/LISS-0525-astronomy-observation-profile.md](../../issues/LISS-0525-astronomy-observation-profile.md)
- new: [docs/issues/LISS-0526-continuous-field-semantic-contract.md](../../issues/LISS-0526-continuous-field-semantic-contract.md)
- new: [docs/issues/LISS-0527-finite-difference-solver-profile.md](../../issues/LISS-0527-finite-difference-solver-profile.md)
- new: [docs/issues/LISS-0528-finite-element-solver-profile.md](../../issues/LISS-0528-finite-element-solver-profile.md)
- new: [docs/issues/LISS-0529-spectral-solver-profile.md](../../issues/LISS-0529-spectral-solver-profile.md)
- new: [docs/issues/LISS-0530-adaptive-mesh-conservation.md](../../issues/LISS-0530-adaptive-mesh-conservation.md)
- new: [docs/issues/LISS-0531-physical-experiment-gravity-profile.md](../../issues/LISS-0531-physical-experiment-gravity-profile.md)
- new: [docs/issues/LISS-0532-linear-fluid-mhd-profile.md](../../issues/LISS-0532-linear-fluid-mhd-profile.md)
- new: [docs/issues/LISS-0533-discrete-interaction-profile.md](../../issues/LISS-0533-discrete-interaction-profile.md)
- new: [docs/issues/LISS-0534-scientific-reproducibility-evidence.md](../../issues/LISS-0534-scientific-reproducibility-evidence.md)
- new: [docs/issues/LISS-0535-natural-language-observation-candidates.md](../../issues/LISS-0535-natural-language-observation-candidates.md)
- new: [docs/issues/LISS-0536-cross-domain-conformance-completion.md](../../issues/LISS-0536-cross-domain-conformance-completion.md)
- new: [docs/issues/LISS-0537-relativistic-gravity-profile.md](../../issues/LISS-0537-relativistic-gravity-profile.md)
- new: [docs/issues/LISS-0538-nonlinear-fluid-profile.md](../../issues/LISS-0538-nonlinear-fluid-profile.md)
- new: [docs/issues/LISS-0539-solar-mhd-profile.md](../../issues/LISS-0539-solar-mhd-profile.md)
- new: [docs/issues/LISS-0540-inverse-ensemble-scientific-workflow.md](../../issues/LISS-0540-inverse-ensemble-scientific-workflow.md)
- new: [docs/issues/LISS-0541-s02-quantum-baseline-comparison.md](../../issues/LISS-0541-s02-quantum-baseline-comparison.md)
- new: [docs/specs/staqex-scientific-workflow-acceptance.md](../../specs/staqex-scientific-workflow-acceptance.md)
- new: [docs/work-plans/WP-0131-scientific-workflow-program.md](../../work-plans/WP-0131-scientific-workflow-program.md)
- new: [docs/work-plans/WP-0132-scientific-metadata-graph.md](../../work-plans/WP-0132-scientific-metadata-graph.md)
- new: [docs/work-plans/WP-0133-scientific-typed-bindings.md](../../work-plans/WP-0133-scientific-typed-bindings.md)
- new: [docs/work-plans/WP-0134-s02-measured-assay-profile.md](../../work-plans/WP-0134-s02-measured-assay-profile.md)
- new: [docs/work-plans/WP-0135-s02-leakage-safe-model.md](../../work-plans/WP-0135-s02-leakage-safe-model.md)
- new: [docs/work-plans/WP-0136-s02-classical-batch-baseline.md](../../work-plans/WP-0136-s02-classical-batch-baseline.md)
- new: [docs/work-plans/WP-0137-scientific-quantum-projection.md](../../work-plans/WP-0137-scientific-quantum-projection.md)
- new: [docs/work-plans/WP-0138-scientific-workflow-lifecycle.md](../../work-plans/WP-0138-scientific-workflow-lifecycle.md)
- new: [docs/work-plans/WP-0139-s02-assay-batch-cycle.md](../../work-plans/WP-0139-s02-assay-batch-cycle.md)
- new: [docs/work-plans/WP-0140-geographic-sensor-adapter-profile.md](../../work-plans/WP-0140-geographic-sensor-adapter-profile.md)
- new: [docs/work-plans/WP-0141-s01-rolling-plan-validation.md](../../work-plans/WP-0141-s01-rolling-plan-validation.md)
- new: [docs/work-plans/WP-0142-astronomy-observation-profile.md](../../work-plans/WP-0142-astronomy-observation-profile.md)
- new: [docs/work-plans/WP-0143-continuous-field-semantic-contract.md](../../work-plans/WP-0143-continuous-field-semantic-contract.md)
- new: [docs/work-plans/WP-0144-finite-difference-solver-profile.md](../../work-plans/WP-0144-finite-difference-solver-profile.md)
- new: [docs/work-plans/WP-0145-finite-element-solver-profile.md](../../work-plans/WP-0145-finite-element-solver-profile.md)
- new: [docs/work-plans/WP-0146-spectral-solver-profile.md](../../work-plans/WP-0146-spectral-solver-profile.md)
- new: [docs/work-plans/WP-0147-adaptive-mesh-conservation.md](../../work-plans/WP-0147-adaptive-mesh-conservation.md)
- new: [docs/work-plans/WP-0148-physical-experiment-gravity-profile.md](../../work-plans/WP-0148-physical-experiment-gravity-profile.md)
- new: [docs/work-plans/WP-0149-linear-fluid-mhd-profile.md](../../work-plans/WP-0149-linear-fluid-mhd-profile.md)
- new: [docs/work-plans/WP-0150-discrete-interaction-profile.md](../../work-plans/WP-0150-discrete-interaction-profile.md)
- new: [docs/work-plans/WP-0151-scientific-reproducibility-evidence.md](../../work-plans/WP-0151-scientific-reproducibility-evidence.md)
- new: [docs/work-plans/WP-0152-natural-language-observation-candidates.md](../../work-plans/WP-0152-natural-language-observation-candidates.md)
- new: [docs/work-plans/WP-0153-cross-domain-conformance-completion.md](../../work-plans/WP-0153-cross-domain-conformance-completion.md)
- new: [docs/work-plans/WP-0154-relativistic-gravity-profile.md](../../work-plans/WP-0154-relativistic-gravity-profile.md)
- new: [docs/work-plans/WP-0155-nonlinear-fluid-profile.md](../../work-plans/WP-0155-nonlinear-fluid-profile.md)
- new: [docs/work-plans/WP-0156-solar-mhd-profile.md](../../work-plans/WP-0156-solar-mhd-profile.md)
- new: [docs/work-plans/WP-0157-inverse-ensemble-scientific-workflow.md](../../work-plans/WP-0157-inverse-ensemble-scientific-workflow.md)
- new: [docs/work-plans/WP-0158-s02-quantum-baseline-comparison.md](../../work-plans/WP-0158-s02-quantum-baseline-comparison.md)
