# LISS-0475: Human real-QPU execution and evidence handoff

| Field | Value |
|---|---|
| Status | **proposed — hardware-required work isolated; not started** |
| Phase | phase-0-design |
| Type | human operations / experiment |
| Priority | P0 |
| Initial size | L |
| Current size | L |
| Owner | Adjudicator / human operator |
| Parent | WP-0119; WP-0126 |
| Depends on | WP-0124, WP-0123 |
| Blocks | LISS-0470 and final real-QPU release evidence |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md) |
| Implementation permission | None; no autonomous real-QPU submission |
| Post-review requirement | Human run approval and evidence review |

## Objective

Execute one small supported program on a human-selected device using the
operator's own credentials, then hand off redacted, traceable, non-mock result
evidence. This Issue is separate from the offline checklist and validation
contracts in LISS-0467–0469.

## Acceptance scenarios

- Given a reviewed offline artifact, selected target, and cost/shots ceiling,
  when the human operator explicitly approves at run time, then the human may
  submit and record provider/device/job identity.
- Given unsupported capability, missing credentials, unexpected cost, or
  incomplete provenance, when the gate is evaluated, then submission stops.
- Given a completed job, when evidence is handed off, then source/artifact
  identity, lifecycle, calibration/noise metadata, and raw result are linked
  without secrets.

## Exclusions

No agent submission, credential acquisition, provider expansion, deployment,
datastore, source rewrite, automatic retry, or general hardware-support claim.

## Required human inputs

- provider/device and region;
- shots and maximum cost;
- explicit run date/time and operator approval;
- redacted Job lifecycle output and raw result;
- calibration/noise/compiler/SDK metadata where available.

## Gate and status

Phase 1/2 are not requested. The Issue remains proposed until the human
operator chooses the target and confirms the run budget. After the real run,
the supplied evidence is reviewed and the result-validation disposition is
recorded before any operations decision.

## Planning record

`AIP-LISS-0475-2026-08-30-001` (L; no model/provider data).
