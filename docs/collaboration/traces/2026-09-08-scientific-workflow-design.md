# Scientific Workflow design correction trace

## Request / current phase

- Date: 2026-09-08 (Asia/Tokyo).
- Request: Solとして、7a62作業ツリーのSora設計案を独立に評価し、
  S01/S02に限定しない完成形Scientific Workflowへ設計訂正する。
- Current phase: Architecture Path / phase-0-design correction.
- Canonical planning proposal: WP-0131 / LISS-0514.
- Scope approval: design correction only, supplied by the user.
- Implementation permission: none. Tests/production/runtime/provider/Git mutationは実行しない。
- Issue/WP status: parent review、children proposed。doneにしていないため
  completion process reviewは起動しない。

## Context ledger

- Included: AGENTS、Quickstart、AT-TDD、conventions、readiness、process lessons、
  runtime routing、current decision/open-work register、ADRs 0210–0212、
  scientific semantic/input/continuous/hybrid/S01/旧S02 contracts、
  7a62のSora proposal一式と全child dependency inventory。
- External public evidence: OGC CityGML/SensorThings、W3C SOSA/SSN/PROV-O、
  IVOA ObsCore/VOTableの一次資料。標準概念の境界確認にだけ使用した。
- Omitted: raw scientific datasets、秘密、provider logs、無関係source、
  production全体の再監査、Soraの非公開reasoning。
- Assumptions: 既存port/IRは再利用候補に留め、具体的能力は後続受入で検証する。
- Open decisions: ADR 0217-B/C、Phase 3 final review、S02 assay/data/model/baseline、
  S01 safety/fairness、adapter/library/version、Solver/tolerance。

## Routing and independence

- Agent/environment: Sol role / separate Codex task and worktree / detached HEAD 26596314.
- Source proposal: /Users/nn0cl/.codex/worktrees/7a62/qpex at the same base commit.
- Runtime routing file says same_context for ordinary review. This user-triggered
  independent correction loop instead used a separate task/worktree.
- Iteration 1 reviewed the Sora artifacts read-only. Iteration 2 switched Sol
  to correction author. No other model or subagent was used.
- Because Sol authored the corrected packet, a fresh reviewer was required.
  The lightweight independent reviewer completed a read-only review of the
  post-correction state with `approve` and no P0/P1/P2 findings.
- Model/reasoning telemetry: unavailable; no inferred model identity or token count recorded.

## Sol dispositions and differences from Sora proposal

Accepted after independent inspection:

- complete cross-domain metamodel and adapter/profile boundary;
- source-derived Semantic IR authority and explicit Realize/projection chain;
- measured-bioactivity S02 and operational S01 acceptance;
- M0 metadata slice plus 27 proposed child WP/LISS records;
- deadline/approval/replan/fallback, leakage, reproducibility, cost and baseline contracts.

Changed by Sol:

- replaced same-context/self-review framing with a non-terminal independent
  correction record and explicit fresh re-review condition;
- removed proposed edits to completed WP-0093 and existing WP-0118/0119;
- detached physical experiment/Newton gravity from the astronomy adapter
  dependency and made it depend on common metadata/bindings plus FEM;
- split individual classical Workflow validity from the program-wide
  hybrid/quantum capability completion claim;
- made mapping proposal and concrete profile/technology decision separate gates;
- corrected author/routing attribution from Sora to Sol;
- corrected the continuous finiteization reference to ADRs 0210/0212 plus
  ADR 0211 source authority.

## Process lessons applied

- authority-boundary: Metadata Graph is descriptive and cannot inject executable IR.
- migration-boundary/status-drift: completed WP/LISS history is not reopened or rewritten.
- acceptance-boundary/phase-acceptance-boundary: rejection cases have valid neighbors
  and unsupported projection must fail atomically.
- review-boundary-observability: isolation, terminal status, next gate and permissions are explicit.
- ID uniqueness: new WP/LISS ranges are checked against the repository inventory.
- coverage-authority-boundary: bounded examples do not establish complete scientific coverage.

## Approval and next safe action

- Architecture approval: ADR 0217-A accepted 2026-09-08; 0217-B/C and the
  overall ADR remain Proposed.
- Technology selection: pending; no standard version, adapter, library, datastore,
  dataset, model, solver or provider is adopted.
- Independent contract review: complete — lightweight fresh context returned
  `approve` with no P0/P1/P2 findings.
- Phase approval: none.
- Implementation approval: Phase 2 Green approved for the M0 contract only;
  Phase 3 final review remains pending.
- Next minimum packet: WP-0132/LISS-0515 Phase 3 final review. M0 and Phase 2
  approval do not authorize broader profiles or provider work.

## Verification

- Custom read-only document checker: PASS — 67 changed files, all under docs;
  WP-0131–0158 and LISS-0514–0541 are each 28 unique records, consisting of
  one parent WP/LISS pair plus 27 child WP/LISS pairs; the 27 child plans
  form a 59-edge acyclic dependency graph; WP/LISS dependency sets agree;
  required child-WP fields, local Markdown links, requested coverage terms,
  Sol attribution and completed-WP history guards pass.
- git diff --check: PASS.
- python3 scripts/check-document-lifecycle.py: PASS (one registered lifecycle file).
  This only validates the repository lifecycle register and does not make the
  new proposal Canonical or Accepted.
- Placeholder scan over new architecture/spec/WP/LISS artifacts: PASS.
- Trace inventory, Markdown local-link and changed-file extension check: PASS —
  67/67 paths agree and every changed artifact is Markdown under docs.
- Forward Blocks/Depends-on symmetry, WP-0131 inventory, L-sized bounded-unit
  presence and acceptance-ID reference check: PASS.
- Runtime tests, SDK installation, data download and hardware checks: not run;
  out of scope for this design correction.
- Review verification: Iteration 1 was independent of Sora authoring; the
  post-correction fresh independent contract review completed successfully.
  Reviewer task: `01a07e8f-15f5-76f3-8070-fd4f05367d61`.

## Architecture decision recorded after independent review

- Adjudicator decision: `ADR 0217-A Architecture承認` (2026-09-08).
- Accepted: metadata identity/trust/roles, adapter mapping responsibility, and
  the non-executable Metadata Graph / Scientific Semantic IR boundary.
- Excluded from this decision: ADR 0217-B/C, technology selection, Phase 1,
  implementation, provider/SDK, credentials, and live submission.
- Next gate: WP-0132/LISS-0515 Phase 3 final review.

## M0 acceptance decision recorded

- Adjudicator decision: `WP-0132 / LISS-0515 M0 G01/G02/G03 acceptance 承認`
  (2026-09-08).
- Accepted: the bounded M0 acceptance scenarios, six in-memory fixtures, and
  M0 exit criteria.
- Excluded: Phase 1 Red, Phase 2/Implementation, Phase 3, technology selection,
  provider/SDK, credentials, and live submission.
- Next gate: review the Phase 1 Red tests, then request separate Phase 2/Implementation approval.

## Phase 1 Red decision and execution

- Adjudicator decision: `WP-0132 / LISS-0515 Phase 1 Red 承認` (2026-09-08).
- Added: `tests/test_scientific_metadata_graph_red.py` covering G01/G02/G03,
  six fixtures, identity/revision, observation truth, evidence/provenance, and
  the non-executable graph boundary.
- No implementation, provider, database, reader, parser, or Phase 2 action was
  taken.
- Verification: source compilation via `compile()` and `git diff --check` passed;
  local pytest could not run because pytest is not installed in this environment.
- Next gate: Phase 3 final review.

## Phase 2 Green decision and execution

- Adjudicator decision: `WP-0132 / LISS-0515 Phase 2 Green / Implementation 承認`
  (2026-09-08).
- Added: `compiler/staqex/scientific_metadata.py`, a descriptive immutable
  Metadata Graph with G01/G02/G03 validation and no execution/projection APIs.
- Verification: direct M0 contract smoke checks, source compilation via
  `compile()`, and `git diff --check` passed. Full pytest remains unavailable
  locally because pytest is not installed.
- Excluded: Phase 3 refactor, broader profiles, provider/SDK, database, reader,
  parser, credentials, and live submission.

## Phase 3 Refactor decision and completion

- Adjudicator decision: `WP-0132 / LISS-0515 Phase 3 Refactor 承認`
  (2026-09-08).
- Refactor: extracted record and relation normalization helpers without
  changing the M0 public contract or adding execution authority.
- Verification: M0 contract smoke checks, source compilation, `git diff --check`,
  and document lifecycle check passed. Full pytest remains unavailable locally.
- Completion process review: no operating-contract deviation or operational
  problem found.
- Scope boundary: only WP-0132/LISS-0515 M0 is complete; broader profiles and
  provider/QPU work remain separately gated.

## Changed files

- docs/architecture/adr/0217-scientific-workflow-metadata-and-projection.md
- docs/architecture/open-work-register.md
- docs/architecture/scientific-workflow-complete-design.md
- docs/collaboration/process-lessons-log.md
- docs/collaboration/reviews/2026-09-08-scientific-workflow-design-review.md
- docs/collaboration/traces/2026-09-08-scientific-workflow-design.md
- docs/issues/LISS-0514-scientific-workflow-program.md
- docs/issues/LISS-0515-scientific-metadata-graph.md
- docs/issues/LISS-0516-scientific-typed-bindings.md
- docs/issues/LISS-0517-s02-measured-assay-profile.md
- docs/issues/LISS-0518-s02-leakage-safe-model.md
- docs/issues/LISS-0519-s02-classical-batch-baseline.md
- docs/issues/LISS-0520-scientific-quantum-projection.md
- docs/issues/LISS-0521-scientific-workflow-lifecycle.md
- docs/issues/LISS-0522-s02-assay-batch-cycle.md
- docs/issues/LISS-0523-geographic-sensor-adapter-profile.md
- docs/issues/LISS-0524-s01-rolling-plan-validation.md
- docs/issues/LISS-0525-astronomy-observation-profile.md
- docs/issues/LISS-0526-continuous-field-semantic-contract.md
- docs/issues/LISS-0527-finite-difference-solver-profile.md
- docs/issues/LISS-0528-finite-element-solver-profile.md
- docs/issues/LISS-0529-spectral-solver-profile.md
- docs/issues/LISS-0530-adaptive-mesh-conservation.md
- docs/issues/LISS-0531-physical-experiment-gravity-profile.md
- docs/issues/LISS-0532-linear-fluid-mhd-profile.md
- docs/issues/LISS-0533-discrete-interaction-profile.md
- docs/issues/LISS-0534-scientific-reproducibility-evidence.md
- docs/issues/LISS-0535-natural-language-observation-candidates.md
- docs/issues/LISS-0536-cross-domain-conformance-completion.md
- docs/issues/LISS-0537-relativistic-gravity-profile.md
- docs/issues/LISS-0538-nonlinear-fluid-profile.md
- docs/issues/LISS-0539-solar-mhd-profile.md
- docs/issues/LISS-0540-inverse-ensemble-scientific-workflow.md
- docs/issues/LISS-0541-s02-quantum-baseline-comparison.md
- docs/specs/staqex-hybrid-workflow.md
- docs/specs/staqex-scientific-input-and-parameter-binding.md
- docs/specs/staqex-scientific-workflow-acceptance.md
- docs/specs/staqex-v1-s02-drug-discovery-benchmark.md
- docs/work-plans/WP-0131-scientific-workflow-program.md
- docs/work-plans/WP-0132-scientific-metadata-graph.md
- docs/work-plans/WP-0133-scientific-typed-bindings.md
- docs/work-plans/WP-0134-s02-measured-assay-profile.md
- docs/work-plans/WP-0135-s02-leakage-safe-model.md
- docs/work-plans/WP-0136-s02-classical-batch-baseline.md
- docs/work-plans/WP-0137-scientific-quantum-projection.md
- docs/work-plans/WP-0138-scientific-workflow-lifecycle.md
- docs/work-plans/WP-0139-s02-assay-batch-cycle.md
- docs/work-plans/WP-0140-geographic-sensor-adapter-profile.md
- docs/work-plans/WP-0141-s01-rolling-plan-validation.md
- docs/work-plans/WP-0142-astronomy-observation-profile.md
- docs/work-plans/WP-0143-continuous-field-semantic-contract.md
- docs/work-plans/WP-0144-finite-difference-solver-profile.md
- docs/work-plans/WP-0145-finite-element-solver-profile.md
- docs/work-plans/WP-0146-spectral-solver-profile.md
- docs/work-plans/WP-0147-adaptive-mesh-conservation.md
- docs/work-plans/WP-0148-physical-experiment-gravity-profile.md
- docs/work-plans/WP-0149-linear-fluid-mhd-profile.md
- docs/work-plans/WP-0150-discrete-interaction-profile.md
- docs/work-plans/WP-0151-scientific-reproducibility-evidence.md
- docs/work-plans/WP-0152-natural-language-observation-candidates.md
- docs/work-plans/WP-0153-cross-domain-conformance-completion.md
- docs/work-plans/WP-0154-relativistic-gravity-profile.md
- docs/work-plans/WP-0155-nonlinear-fluid-profile.md
- docs/work-plans/WP-0156-solar-mhd-profile.md
- docs/work-plans/WP-0157-inverse-ensemble-scientific-workflow.md
- docs/work-plans/WP-0158-s02-quantum-baseline-comparison.md
- docs/README.md

## Unverified matters

- Scientific correctness of future domain fixtures and numeric tolerances.
- Availability, license and suitability of a measured S02 dataset/profile.
- Exact external standard versions, encoding subsets and round-trip behavior.
- Any production implementation, parser reachability, consumer wiring or runtime performance.
- Live QPU capability, credentials, provider behavior and end-to-end cost.
