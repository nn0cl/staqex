# WP-0124: Real-run evidence, pilot, and validation

| Field | Value |
|---|---|
| Status | **in progress — offline evidence/checklist/validation complete; human pilot pending** |
| Type | release/experiment work plan |
| Size | L |
| Parent | [WP-0119](WP-0119-real-qpu-readiness-roadmap.md) |
| Issues | LISS-0467, LISS-0468, LISS-0469 |
| Depends on | WP-0123 |
| Blocks | WP-0125 |
| Canonical authority | ADR 0065, 0103, 0104; experiment/evidence contract to be accepted |
| Owner boundary | Human-operated Host experiment and evidence review |
| Implementation permission | None; pilot design and evidence preparation only |
| Scope approval | User approved all Work Plans, 2026-08-27 |
| Post-review requirement | Human pilot protocol review and separate real-run approval |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md) |

## Goal

Capture reproducible execution evidence and conduct one small, explicitly
human-authorized real-QPU pilot, then compare results with the simulator and
record a scientifically honest disposition.

## Work units

- Run envelope, calibration/noise/compiler/seed/shot evidence (LISS-0467).
- Dry-run, approval, cost, cancellation, and human-operated pilot (LISS-0468).
- Statistical/physics comparison, drift handling, and claim boundaries
  (LISS-0469).

## Release exit

The run is traceable from source to measured result; real/non-mock evidence is
clearly labeled; validation is marked valid, inconclusive, or rejected. The
agent must never autonomously submit to a real device.

## Included / excluded

Included: run envelope, baseline selection, calibration/noise capture, seed and
shot policy, cost guard, dry-run checklist, human confirmation, result
comparison, drift handling, and claim boundaries. Excluded: unattended jobs,
new provider adapters, deployment, and source rewrites to make a result look
successful.

## Acceptance scenarios

- A run record links source, semantic IR, finite artifact, provider/device/job,
  compiler/SDK versions, shots, seed, calibration, and measured result.
- The pilot cannot proceed without human approval, cost/shot review, and a
  supported capability profile.
- A real result is labeled real/non-mock and compared with a declared
  simulator baseline using predeclared statistical/physics criteria.
- Drift, noise, incomplete data, or provider anomalies produce inconclusive or
  rejected evidence rather than an unsupported fidelity claim.

## Phase and evidence gates

Phase 0 accepts the pilot protocol and validation criteria. Phase 1 adds
offline evidence-schema and baseline tests. Phase 2 prepares dry-run tooling
and fake/recorded data only. Phase 3 is human-gated: the human operator runs
the device and supplies evidence, followed by independent validation review.

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
checklist, and validation slices. The remaining release evidence is a
human-operated real-QPU pilot and its supplied raw result; no agent may submit
autonomously. WP-0125 is deferred pending demonstrated operational need.
