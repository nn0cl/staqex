# WP-0126: Human real-QPU execution and evidence handoff

| Field | Value |
|---|---|
| Status | **proposed — separate human-operated task; not started** |
| Type | experiment / human operations |
| Size | L |
| Parent | [WP-0119](WP-0119-real-qpu-readiness-roadmap.md) |
| Issues | [LISS-0475](../issues/LISS-0475-human-real-qpu-execution.md) |
| Depends on | WP-0124, WP-0123 |
| Blocks | WP-0125 and final real-QPU release evidence |
| Owner boundary | Adjudicator / human operator |
| Implementation permission | None; human execution approval required |
| Scope approval | User requested separation of hardware-required work, 2026-08-30 |
| Post-review requirement | Human run approval and evidence review |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md) |

## Scope

This WP contains only actions that require a real device, real credentials, or
provider network access: select a supported device, verify the offline artifact
and cost/shots guard, obtain explicit real-time human approval, submit, observe
the Job lifecycle, retrieve the raw result, and hand the redacted evidence to
the validation process.

## Explicit exclusions

- no agent-operated submission or credential handling;
- no new provider SDK, adapter, deployment, datastore, or Rust work;
- no source/compiler rewrite after seeing hardware data;
- no claim of general hardware support from one run.

## Entry criteria

- WP-0124 offline preparation is complete;
- provider-neutral Host and fake lifecycle checks are green;
- a supported device, region, shots, and cost ceiling are selected by the
  human operator;
- the local Bell-pair dry-run artifact has been reviewed;
- cancellation and evidence-capture steps are ready.

## Human-run procedure

1. Use the user's own AWS/provider setup and verify credentials without
   recording secrets.
2. Run the local dry-run and inspect the exact QASM and target envelope.
3. Confirm device, shots, estimated cost, and cancellation plan.
4. Give explicit real-time approval immediately before submission.
5. Submit and record provider/device/job identifiers, status transitions,
   calibration/noise metadata, compiler/SDK versions, and raw result.
6. Stop on unsupported capability, unexpected cost, missing provenance, or
   anomalous/incomplete result; do not retry silently.
7. Provide redacted run evidence for the separate validation step.

## Exit conditions

- human approval and selected target are recorded;
- raw non-mock result is labeled as such and linked to source/artifact hashes;
- provider lifecycle and anomalies are recorded;
- evidence is handed off without credentials or secret-bearing logs;
- validation disposition is produced by the human/reviewer process.

## Gate

This WP is intentionally not implementation-approved. It becomes executable
only after the human operator supplies target, cost/shots, credential, and
real-time run approval. The agent may inspect supplied redacted evidence but
may never invoke the real submission.

## Planning record

- Planning record: `AIP-WP-0126-2026-08-30-001`.
- No model or provider data is included in this planning record.
