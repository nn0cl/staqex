# ADR 0202: AWS Braket as the selected live QPU provider adapter

## Status

**Accepted** (2026-08-10) — Architecture approval by the Adjudicator.
Implements ADR 0127's own condition: "Kernel must not claim live submit
until an adapter ADR selects a provider under Adjudicator technology
approval." The Adjudicator named AWS Braket explicitly (2026-08-10,
in-conversation) — this ADR records that selection formally and defines
the adapter boundary. Acceptance approves Decisions 1–6 below,
**including the standing safety constraints in Decisions 3 and 5** — it
does **not** itself perform or authorize any real submission, and does
**not** authorize adding `amazon-braket-sdk` to the dependency manifest
(Decision 4's Open items remain unresolved).

## Design check

- **Scope and expected behavior:** Select AWS Braket
  (`amazon-braket-sdk`) as the concrete provider behind the already-shipped
  provider-neutral `QpuSubmitPort` / `QpuJobPort` (ADR 0127/0083) and
  `CredentialPort` (ADR 0161). Define what the adapter does and — just as
  important — what it explicitly does not do without further, separate,
  real-time authorization.
- **Specifications and files inspected:** `compiler/staqex/qpu_submit.py`
  (**confirmed shipped**: `QpuArtifact`, `QpuSubmitRequest`,
  `ProviderJobId`, `QpuSubmitPort.submit`, `QpuJobPort.status/wait/result/cancel`
  — all Protocol-based, provider-neutral, ready for a concrete adapter);
  `compiler/staqex/credentials.py` (**confirmed shipped**:
  `CredentialPort`, `EnvCredentialAdapter` — reads named credentials from
  env, never invents values; `CredentialGatedMockSubmit` — fail-closed on
  missing credentials, **"Does not call any cloud SDK. On success returns
  a local opaque job id"** — confirms today's shipped submit path is
  mock-only by design); original ADR 0127 text (recovered from
  `docs/pre-canonicalization-2026-08-03` tag —
  `docs/architecture/adr/0127-live-qpu-credentials-boundary.md`):
  "Honesty catalog stays normative: Kernel must not claim live submit
  until an adapter ADR selects a provider under Adjudicator technology
  approval," "Non-goals: Shipping a concrete cloud provider SDK in this
  ADR; inventing API keys"; `docs/architecture/dependency-policy.md`
  (Dependency Adoption Checklist — security posture, version-specific
  examples, troubleshooting depth, minimal real-file test, POC
  feasibility, boundary fit); [ADR 0201](0201-openqasm-dynamic-lane-emission.md)
  (both Static QPU and, as of this session, Dynamic-lane QASM3 text are
  now available as `QpuArtifact.qasm` payload candidates).
- **Component boundaries, ports/adapters, VO/DTO candidates:** A new Host
  adapter module (candidate path
  `compiler/staqex/adapters/aws_braket.py`, outside the Kernel package
  proper) implementing `QpuSubmitPort` and `QpuJobPort` against the
  `amazon-braket-sdk` client, injected via constructor (Dependency
  Inversion — the adapter depends on an injectable Braket client
  interface, not a hardcoded SDK singleton, so tests substitute a fake
  client and never touch the network). Credentials continue flowing
  through the existing `CredentialPort` — the adapter reads AWS
  credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, or an AWS
  profile name) via that same port, never hardcoded, never logged.
- **Applicable constraints (safety-critical, this ADR's core content):**
  - Claude Code (this agent) **never enters, stores, or transmits AWS
    credentials** at any point — building the adapter is code authorship,
    not credential handling.
  - Claude Code **never invokes a real submission** against AWS Braket
    autonomously, regardless of any "proceed without stopping" direction
    given elsewhere in this session — that direction applied to a
    same-session Kernel/language Feature Issue with zero external cost or
    side effects; AWS Braket submission has neither property (it costs
    real money per AWS's published Braket pricing, on both QPU **and**
    managed simulator targets, and creates real external account state).
    Any real `submit()` call requires the user's own AWS credentials
    (configured by the user, in their own environment) **and** the user's
    explicit, real-time confirmation immediately before that specific
    call — the same standard this agent's operating rules already apply
    to any purchase or paid external service action.
  - All tests for this adapter must run against an injected fake/mock
    Braket client — CI must never require real AWS credentials or make
    real network calls (mirrors `CredentialGatedMockSubmit`'s existing
    "does not call any cloud SDK" pattern, extended to the real adapter's
    *test* boundary, not its production code path).
  - The adapter must not weaken `physical_execution_claimed` honesty
    (ADR 0071): a `QpuSubmitPort.submit` call that actually reaches this
    adapter's real (non-mock) implementation **does** claim physical
    execution — unlike every Dynamic-lane Fake/local path this session
    built, which is the entire reason this ADR treats it with more
    caution, not less.
  - Dependency Adoption Checklist items for `amazon-braket-sdk` are
    tracked below (Decision 4) — some are marked as needing the
    Adjudicator's own confirmation (e.g. current account/quota posture)
    rather than resolved unilaterally.
- **Decisions, assumptions, unresolved ambiguities:** Exact `QpuArtifact`
  → Braket circuit translation (OpenQASM3 string → Braket's
  `Circuit.from_ir` or equivalent) and result-schema mapping
  (`QpuJobPort.result` → Braket's measurement counts / IR result) are
  Feature Issue implementation detail. Whether Dynamic-lane QASM3
  (mid-circuit measure/reset/if, LISS-0391) is accepted by Braket's own
  OpenQASM3 support today is an open verification item for the Feature
  Issue (Braket's OpenQASM3 support has historically been partial/
  device-dependent) — flagged here rather than assumed.
- **Included and omitted AI context:** Included direct reads of the
  shipped port/credential modules and the recovered ADR 0127 text.
  Omitted: this agent has not verified `amazon-braket-sdk`'s current
  PyPI version, changelog, or CVE history against a live advisory
  database in this pass — that verification is listed as an open
  Dependency Adoption item (Decision 4), not silently assumed clean.
- **Task routing:** Architecture proposal; deterministic source
  inspection; dependency adoption verification is explicitly incomplete
  and named as such.
- **Evidence contract:** N/A — no AI runtime output; no network call was
  made to verify package metadata in this pass.
- **Verification plan (after Accept + Feature Issue):** (a) the adapter's
  unit tests run fully offline against an injected fake Braket client;
  (b) a real submission is never exercised by CI or by this agent; (c)
  missing AWS credentials fail closed through the existing
  `CredentialPort` pattern, mirroring `CredentialGatedMockSubmit`; (d)
  `physical_execution_claimed` is `True` only on the genuine non-mock
  path, verified by a dedicated test asserting the mock path still
  returns `False`.

## Context

ADR 0127 (2026-07-31) deliberately left provider selection open: "Kernel
must not claim live submit until an adapter ADR selects a provider under
Adjudicator technology approval." ADR 0161 shipped the provider-neutral
`CredentialPort` and a fail-closed mock submit specifically so that this
boundary could be exercised safely before any real provider was chosen.

This session's Dynamic QPU lane work (ADR 0197–0201) now gives a live
provider adapter something real to submit: `LISS-0391` emits OpenQASM3
text for `dynamic qpu` programs (mid-circuit measure/match/reset) in
addition to the existing Static QPU surface — both are valid
`QpuArtifact.qasm` payloads.

The Adjudicator named AWS Braket as the target provider directly in this
session (2026-08-10), satisfying ADR 0127's "Adjudicator technology
approval" condition for provider selection.

## Decision proposal

### 1. AWS Braket is the selected provider (technology selection)

`amazon-braket-sdk` (AWS's official Python SDK, Apache 2.0 license) is
adopted as the concrete backend for `QpuSubmitPort`/`QpuJobPort`. Braket
supports OpenQASM3 circuit submission to both real QPU devices (multiple
hardware vendors: IonQ, Rigetti, QuEra, and others via one account) and
AWS-managed simulators, under one provider-neutral integration.

### 2. New Host adapter module, not a Kernel dependency

`compiler/staqex/adapters/aws_braket.py` (or equivalent Host-layer
location — exact path is Feature Issue detail) implements
`QpuSubmitPort`/`QpuJobPort`. The Kernel package never imports
`amazon-braket-sdk`; only this Host adapter does, matching the existing
Clean Architecture boundary (`CredentialPort`/`QpuSubmitPort` already
kept provider SDKs out of the Kernel by design).

### 3. Credentials remain exactly as ADR 0161 already shaped them

The adapter reads AWS credentials via the existing `CredentialPort`
(`EnvCredentialAdapter` or an equivalent Host-supplied adapter) — no new
credential-handling mechanism, no hardcoded values, no logging of secret
values. Missing credentials fail closed with a stable diagnostic, same
shape as `CredentialGatedMockSubmit`'s existing `CREDENTIAL_MISSING`.

### 4. Dependency Adoption Checklist status (per `dependency-policy.md`)

| Item | Status |
|---|---|
| Security posture (CVE/advisory check) | **Open** — not verified in this pass; Feature Issue must run `pip-audit` / check PyPI advisories before the dependency is actually added to the project manifest. |
| Version-specific examples | **Open** — Feature Issue must pin an exact version and confirm current official docs match it. |
| Troubleshooting depth | Likely adequate — `amazon-braket-sdk` is an official, actively maintained AWS package with public documentation and issue tracker, but not independently confirmed here. |
| Minimal real-file test | **Deferred by design** — this ADR requires all tests to run against an injected fake client, never the real SDK's network path (Applicable constraints above); a "minimal real-file test" against the actual service is explicitly **not** performed by this agent. |
| POC feasibility | Recommended before full adapter build-out — a Feature Issue should start with the smallest translation slice (submit a trivial Static QPU circuit's QASM through a mocked client) before extending to Dynamic-lane QASM. |
| Boundary fit | **Confirmed** — Host adapter only, mirrors `CredentialPort`'s existing boundary; does not leak into Kernel/domain code. |

Items marked **Open** must be resolved (or explicitly re-flagged as
accepted risk by the Adjudicator) before `amazon-braket-sdk` is added to
the project's dependency manifest — this ADR does not by itself authorize
that addition.

### 5. Real submission is never autonomous (restated as a hard rule)

Independent of any other authorization in this session, this agent will
not call the real (non-mock) `submit()` path against AWS Braket without
the user's own configured credentials **and** explicit, real-time
confirmation for that specific call. This is not a Feature Issue detail —
it is a standing constraint on this agent's own behavior, restated here
because it is the entire reason this ADR exists as a separate, cautious
document rather than a same-session "続けて" continuation.

### 6. Out of scope for this ADR

- Actual `amazon-braket-sdk` dependency-manifest addition (gated on
  Decision 4's Open items).
- Exact `QpuArtifact` → Braket circuit / result-schema translation
  (Feature Issue detail).
- Any other live provider (IBM Quantum, etc.) — this ADR selects Braket
  only; a different provider would need its own ADR.
- Cost/budget controls, quota management, or AWS account setup — the
  user's own AWS account and billing remain entirely the user's
  responsibility and outside this agent's authority to configure or
  spend against.

## Consequences

Positive:

- Gives the already-shipped provider-neutral ports (ADR 0127/0161/0083) a
  concrete, real target for the first time.
- Both Static and Dynamic-lane QASM3 output (LISS-0391) have a genuine
  submission path once implemented.
- Preserves every honesty boundary this session's work built:
  `physical_execution_claimed` becomes meaningfully `True` only on a path
  this agent will never trigger autonomously.

Negative / residual open:

- Real submission requires the user to independently run the adapter with
  their own credentials — this agent cannot verify end-to-end behavior
  against the real service itself, only against mocks.
- Dependency Adoption Checklist has open items (Decision 4) that block
  actually adding the package, separate from this ADR's own Accept.
- Braket's OpenQASM3 dynamic-circuit (mid-circuit measurement/reset)
  support is device/simulator-dependent and not verified here — a
  Feature Issue may discover Braket-side capability gaps requiring
  additional fail-closed diagnostics.

## Rejected alternatives

### Build the adapter against a raw `boto3` Braket client instead of `amazon-braket-sdk`

Rejected for now — the official SDK provides circuit/result modeling
AWS's own low-level `boto3` Braket API does not; using it reduces
translation risk. A Feature Issue may revisit if the SDK's abstractions
prove a poor fit.

### Let this agent perform a live test submission during Feature Issue implementation to "prove it works"

Rejected — violates this agent's own operating rules around paid external
services and credential handling (Decision 5). Verification stays
mock-based; real verification is the user's own action.

## Follow-up work required after acceptance

1. Resolve Decision 4's **Open** Dependency Adoption items (security
   posture, version pin) before adding `amazon-braket-sdk` to the project
   manifest.
2. Feature Path Issue: adapter module + injectable client interface +
   `QpuArtifact` → Braket circuit translation (Static QASM first,
   Dynamic-lane QASM as a follow-on slice) + result-schema mapping, all
   tested against a fake client.
3. User-run (not agent-run) end-to-end verification against real AWS
   Braket, entirely outside this agent's authority.

## Acceptance boundary

Acceptance of this ADR approves **AWS Braket as the selected provider**
and the **adapter boundary / safety constraints** above (Decisions 1–6).
It does **not** authorize adding `amazon-braket-sdk` to the dependency
manifest (Decision 4's Open items remain), does not authorize any real
submission by this agent (Decision 5, standing), and does not authorize
Kernel implementation — a Feature Path Issue is required separately.

## Dependency Adoption Evidence

See Decision 4 table above — **incomplete**, by design, pending the
Open items before any actual dependency addition.
