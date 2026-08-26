# Live QPU demo (AWS Braket) — `submit-live-qpu` / `qpu-job-*`

Runnable end-to-end demo of the CLI-level live-QPU path shipped by
ADR 0202/0203 (LISS-0392/0393/0396/0397): compile → emit QASM3 → submit to
a real provider → poll status → fetch result. `main_bell_pair.sqx` is a
minimal 2-qubit Bell pair (`H` + `CNOT` + terminal measure) — small and
cheap enough for a first real-hardware run.

> **This repository's own agents never run the "real hardware" steps
> below.** ADR 0202 Decision 5 forbids any AI agent from invoking a real
> (non-mock) submission autonomously, in this session or any other,
> regardless of other in-session "don't stop" direction. Everything past
> Step 1 is written for **you** to run yourself, from your own terminal,
> with your own AWS credentials.

## Step 1 — local verification (no cost, always safe)

```bash
python3 -m compiler.staqex run examples/host/live_qpu_braket_demo/main_bell_pair.sqx --seed 0
python3 -m compiler.staqex emit-qasm examples/host/live_qpu_braket_demo/main_bell_pair.sqx
```

The second command prints the exact OpenQASM 3 that will be submitted —
inspect it before going any further.

## Step 2 — prerequisites for a real submission

1. `pip install "amazon-braket-sdk>=1.117.0"` — the CLI refuses to
   construct a real client below `1.117.0` (CVE-2026-9291, CVSS 7.1,
   insecure deserialization in job-result processing; see
   [ADR 0202](../../../docs/architecture/adr/0202-aws-braket-provider-adapter.md)).
   This is an optional dependency — it is not in this project's own
   dependency manifest and is never imported unless you actually run the
   commands below.
2. AWS credentials in your environment
   (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`, or anything your AWS
   SDK setup already provides) — read via the standard environment, never
   entered into Staqex source or CLI flags.
3. A device ARN for an AWS Braket device you're entitled to use. Look
   this up yourself in the AWS Braket console or `aws braket
   search-devices` — do not trust a hardcoded ARN from this README, since
   device availability and identifiers are account/region-specific and
   change over time. **Start with an on-demand simulator device**, not a
   real QPU, for your very first run — it costs far less and confirms the
   whole pipeline before you spend real QPU time.

## Step 3 — submit for real (you run this, not an agent)

```bash
python3 -m compiler.staqex submit-live-qpu \
  examples/host/live_qpu_braket_demo/main_bell_pair.sqx \
  --device-arn "<your device ARN>" \
  --shots 100
```

Prints `provider=aws-braket id=<opaque-id>` on success. This call can
incur real cost on real hardware (the CLI prints a one-line reminder to
stderr before submitting) — cost/budget guardrails are your own
responsibility, same as any other AWS Braket usage
([ADR 0203](../../../docs/architecture/adr/0203-live-qpu-submit-entrypoint.md)
Decision 4).

## Step 4 — poll status and fetch the result

```bash
python3 -m compiler.staqex qpu-job-status --id "<opaque-id>" --device-arn "<your device ARN>"
python3 -m compiler.staqex qpu-job-wait   --id "<opaque-id>" --device-arn "<your device ARN>"
python3 -m compiler.staqex qpu-job-result --id "<opaque-id>" --device-arn "<your device ARN>"
```

`qpu-job-wait` calls the provider once and prints whatever state comes
back immediately — it does not loop or retry itself
([LISS-0397](../../../docs/issues/LISS-0397-qpu-job-port-cli.md)); re-run
`qpu-job-status` yourself (or wrap it in your own shell loop) until it
reports a terminal state before calling `qpu-job-result`.

To cancel a job you no longer want to run:

```bash
python3 -m compiler.staqex qpu-job-cancel --id "<opaque-id>" --device-arn "<your device ARN>"
```

## Why this circuit

A Bell pair is the smallest circuit that actually exercises two-qubit
entanglement (not just single-qubit gates), while staying cheap and fast
on real hardware — a reasonable first real-QPU submission before
attempting anything from `examples/showcase/`.
