# WP-0124: Offline run evidence, pilot preparation, and validation

| Field | Value |
|---|---|
| Status | **complete — offline evidence/checklist/validation preparation** |
| Type | release/experiment work plan |
| Size | L |
| Parent | [WP-0119](WP-0119-real-qpu-readiness-roadmap.md) |
| Issues | LISS-0467, LISS-0468, LISS-0469 (offline preparation slices) |
| Depends on | WP-0123 |
| Blocks | WP-0126; WP-0125 remains conditional on the separated real-run task |
| Canonical authority | ADR 0065, 0103, 0104; experiment/evidence contract to be accepted |
| Owner boundary | Offline Host experiment preparation and evidence review |
| Implementation permission | None; pilot design and evidence preparation only |
| Scope approval | User approved all Work Plans, 2026-08-27 |
| Post-review requirement | Human pilot protocol review and separate real-run approval |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md) |

## Goal

Prepare reproducible execution evidence, dry-run controls, and offline result
validation. Actual device execution and receipt of non-mock results are
separated into [WP-0126](WP-0126-human-real-qpu-execution.md).

## Work units

- Run envelope, calibration/noise/compiler/seed/shot evidence (LISS-0467).
- Dry-run, approval, cost, cancellation, and pilot checklist (LISS-0468).
- Offline statistical/physics comparison, drift handling, and claim boundaries
  (LISS-0469).

## Release exit

Offline artifacts, checklist states, and validation rules are reproducible and
ready for a separately authorized human run. No real/non-mock result is
claimed by this WP.

## Included / excluded

Included: run envelope schema, baseline selection, calibration/noise fields,
seed and shot policy, cost guard, dry-run checklist, offline result comparison,
drift handling, and claim boundaries. Excluded: actual credentials, provider
network calls, device selection/execution, unattended jobs, deployment, and
source rewrites to make a result look successful.

## Acceptance scenarios

- An offline evidence record schema names source, semantic IR, finite artifact,
  target/job/result fields, compiler/SDK versions, shots, seed, and calibration.
- The offline pilot checklist rejects missing human approval, cost/shot review,
  or supported-capability evidence before a run can be authorized.
- Offline validation compares supplied raw/derived data with a declared
  simulator baseline using predeclared statistical/physics criteria.
- Drift, noise, incomplete data, or provider anomalies produce inconclusive or
  rejected evidence rather than an unsupported fidelity claim.

## Phase and evidence gates

Phase 0 accepts the pilot protocol and validation criteria. Phase 1 adds
offline evidence-schema and baseline tests. Phase 2 prepares dry-run tooling
and fake/recorded data only. Phase 3 closes the offline preparation. Human
execution and raw-result handoff are governed by WP-0126.

## Risks / stop conditions

Stop on unexpected cost, missing calibration, unsupported operation, missing
provenance, or any request to submit autonomously. One passing run does not
establish general hardware support.

## Required deliverables

- pilot protocol and human approval checklist;
- evidence schema and simulator-baseline record;
- one human-owned real-run record, if approved and actually performed;
- independent result-validation disposition with limitations and follow-ups.

## Planning record

- Planning record: `AIP-WP-0124-2026-08-27-001`.
- Author/environment: Codex host agent, local repository.
- Model/reasoning: N/A; runtime does not expose displayed per-task values.
- Planning size: L; basis is experiment governance plus provider evidence.
  Confidence: low until pilot target and acceptance thresholds are chosen.

## Current status

LISS-0467, LISS-0468, and LISS-0469 are complete for offline evidence,
checklist, and validation slices. Human-operated real-QPU execution and raw
result handoff are tracked separately in WP-0126; no agent may submit
autonomously. WP-0125 remains deferred pending demonstrated operational need.

## Split record

- Actual real-device work moved to [WP-0126](WP-0126-human-real-qpu-execution.md)
  and [LISS-0475](../issues/LISS-0475-human-real-qpu-execution.md).
- LISS-0467–0469 remain the offline preparation contracts; they are not
  reopened.
- Process review: no operating-contract deviation or operational problem found.
