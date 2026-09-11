# Staqex multi-provider QPU execution contract

| Field | Value |
|---|---|
| Status | **accepted contract baseline — Phase 3 reviewed; provider pilot pending** |
| Owner | WP-0131 / LISS-0514 |
| Authority | [Real-QPU readiness](staqex-real-qpu-readiness-acceptance.md), [hybrid workflow](staqex-hybrid-workflow.md), DEC-0006, [ADR 0217](../architecture/adr/0217-qpu-observation-and-capability-freshness.md) |
| Implementation permission | Phase 3 complete; provider integration and live submission remain gated |
| Scope approval | LISS-0514 Phase 0 started by user direction, 2026-09-10 |
| Architecture approval | Typed approval received, 2026-09-10 |

## Artifact families and target build

The source and deployment artifacts are distinct:

- `.sqx`: Staqex source.
- `.sqxa`: **Staqex eXecution Artifact**, used for both portable and
  target-resolved execution packages.

Target-resolved `.sqxa` retains the common source, semantic, execution-policy,
and provenance identity and adds target-specific capability and payload data.
The Runtime may target-build from portable `.sqxa` or execute a pre-built
targeted `.sqxa`.
Provider SDKs, credentials, and human approval prose remain in the Host
execution environment. The detailed design is proposed in [ADR 0219](../architecture/adr/0219-sqxa-target-build-boundary.md)
and [LISS-0520](../issues/LISS-0520-sqxa-target-build.md); implementation
is not authorized by this proposal.

## Design note

- Target: one provider-neutral execution contract carries a source-derived
  artifact through IBM Quantum, AWS Braket, Azure Quantum, Google QCS, or an
  approved direct-provider route.
- Included: `compiler/staqex/qpu_submit.py`, Host lifecycle/result contracts,
  WP-0119–0126, and provider-route WPs.
- Omitted: provider SDKs, credentials, live payloads, and device code.
- Current phase: Phase 3 reviewed; provider-specific approval is next.
- Evidence: source and semantic fingerprints, artifact identity, route/device
  identity, lifecycle, result disposition, and human authorization.

## Boundary

Staqex owns source meaning, finite realization policy, artifact identity, and
measurement interpretation. A Host adapter owns transport, SDK use,
credentials, provider job state, and payload conversion. An adapter may not
alter Scientific Semantic IR, introduce a measurement, or silently choose an
approximation.

```text
Scientific Semantic IR -> finite ExecutionArtifact -> provider-neutral JobRequest
  -> access-route adapter -> provider job -> JobResult / RunEvidence
```

This contract covers gate-model and explicitly declared dynamic-QPU execution.
Quantum annealing is a separate future lane.

## Identity rules

| Identity | Meaning | Owner |
|---|---|---|
| `source_identity` | source/file and semantic fingerprint | compiler/Host |
| `artifact_identity` | finite artifact serialization fingerprint | compiler |
| `access_route` | service path used to submit | Host |
| `hardware_provider` | organization operating the QPU | provider profile |
| `device_id` | provider-issued target identifier | Host configuration |
| `provider_job_id` | provider job identity | adapter |

`access_route` is not a hardware capability. Azure/IonQ and direct/IonQ may
share `hardware_provider` while having different `access_route` values.

## Candidate immutable records

These are candidates, not implementation authorization.

```text
CapabilityProfile {
  access_route, hardware_provider, device_id, artifact_formats,
  native_operations, qubit_capacity, connectivity, measurement_modes,
  dynamic_features, parameter_features, limits,
  source: declared | observed,
  availability: online | degraded | offline | retired | unavailable,
  profile_fingerprint, calibration_reference?,
  captured_at, expires_at, freshness_policy
}

JobRequest {
  source_identity, artifact_identity, artifact,
  access_route, hardware_provider, device_id,
  execution_policy, idempotency_key, attempt
}

JobStatus {
  provider_job_id,
  normalized_state: queued | running | succeeded | failed | cancelled | unknown,
  observation_state: observed | timed_out | unreachable | stale,
  provider_state?, terminal,
  observed_at, last_successful_observation_at?, diagnostic?
}

JobResult {
  provider_job_id, status, measurements, raw_result_reference,
  result_schema, source_identity, artifact_identity,
  access_route, hardware_provider, device_id, shots,
  calibration_reference?, diagnostics, completed_at
}

RunEvidence {
  evidence_kind: synthetic | fake | simulator | real,
  source_identity, artifact_identity, capability_profile_reference,
  job_request_reference, job_status_history, job_result_reference,
  compiler_version, adapter_version, sdk_version?, shots, seed?,
  calibration_reference?, human_authorization_reference?, limitations,
  captured_at
}
```

### HostSubmissionApproval

Provider authentication and human approval are separate concerns. Provider
credentials are resolved by the Host execution environment through its normal
credential/configuration chain and never enter a Staqex artifact, JobRequest,
log, or evidence payload.

```text
HostSubmissionApproval {
  approval_reference,
  artifact_identity,
  access_route,
  hardware_provider,
  device_id,
  shots,
  cost_ceiling,
  approved_at,
  expires_at?,
  operator_reference
}
```

`HostSubmissionApproval` is a Host control/evidence record, not provider
authentication. It binds one human decision to one artifact and execution
scope. `RunEvidence.human_authorization_reference` may reference it without
exposing credentials or approval prose to the provider adapter.

For the AWS Braket CLI, the non-secret execution scope is loaded from the Host
TOML configuration described in [ADR 0218](../architecture/adr/0218-host-qpu-config-and-interactive-approval.md).
Immediately before submission, the CLI displays the resolved device, shots,
and declared cost ceiling and requires interactive `y`/`yes` confirmation.
Any other response cancels before adapter construction or provider access.
Credentials remain in the Host environment/credential chain and never enter
the config file, JobRequest, or evidence payload.

### Lifecycle observation rules

The provider lifecycle state and the Host's ability to observe that state are
separate dimensions. `provider_state` is retained as the raw provider value;
`normalized_state` is the provider-neutral mapping; `observation_state` records
whether the Host currently has a trustworthy observation.

- `timed_out` means that the Host stopped waiting or polling. It is not a
  provider terminal state and therefore always has `terminal = false`.
- `unknown` means that the current provider state cannot be established, for
  example because the API is unreachable, a permission check failed, or the
  provider returned an unmapped state. It is never mapped to `failed`,
  `queued`, or `running` by guesswork.
- `unreachable` and `stale` are observation diagnostics and do not authorize a
  result projection.
- Only an observed provider state normalized to `succeeded` may permit
  `JobResult` projection. Provider-confirmed `failed` and `cancelled` may also
  be terminal, but never produce successful measurements.
- AWS `CANCELLING` and equivalent provider states remain in `provider_state`
  and map to non-terminal `running` until cancellation is confirmed.
- A `timed_out` or `unknown` observation must not trigger automatic
  resubmission. Re-query, cancellation, or retry requires an explicit Host
  policy and the original idempotency key.

### Capability freshness and expiry

`CapabilityProfile` is a time-bounded Host snapshot, not a permanent device
contract. Static capability data may be cached, but it must be revalidated
before live submission. Dynamic availability must be checked immediately
before submission. Calibration and noise data are valid only for the captured
calibration reference.

A profile is expired or unusable for live preflight when any of the following
is true:

- `expires_at` has passed or the provider-specific freshness policy is absent;
- the provider/device identity or `profile_fingerprint` changed;
- the calibration reference changed or is no longer current;
- availability is `offline`, `retired`, or `unavailable` (and `degraded` is
  rejected unless the Host policy explicitly allows it);
- the capability API returned an error, an unknown schema, or an identity that
  cannot be verified.

Stale profiles may support offline planning and display only. By default they
must not authorize live submission. If a fresh profile cannot be obtained, the
Host fails closed before provider payload creation or job submission.

`freshness_policy` is provider-adapter metadata: it may express provider
calibration cadence and an operational TTL, but it may not alter Staqex source
semantics or silently permit stale execution.

Unknown, stale, failed, cancelled, or incomplete states cannot be presented as
successful measurements. `evidence_kind = real` requires observed provider
execution, a non-expired capability reference, and human authorization.

## Acceptance scenarios

### Route/provider/device separation

```gherkin
Given an artifact submitted through an aggregator route
When evidence is created
Then access_route, hardware_provider, and device_id are recorded separately
And none is substituted for another
```

### Atomic unsupported rejection

```gherkin
Given an artifact requiring a capability absent from the selected profile
When Host preflight runs
Then a provider-neutral diagnostic is returned
And no provider payload, allocation, or job is created
```

### Idempotent submission

```gherkin
Given a validated artifact and idempotency key
When the same request is retried
Then the adapter returns the existing tracked job or a typed duplicate result
And it does not create an untracked second submission
```

### Lifecycle integrity

```gherkin
Given a provider job with queued, running, failed, cancelled, timed-out, or unknown states
When the adapter maps the lifecycle
Then the mapping is deterministic and preserves the provider state
And timeout is represented as a non-terminal observation state
And unknown is never guessed as queued, running, or failed
And only an observed succeeded state permits result projection

### Capability freshness

```gherkin
Given a capability profile that is expired, stale, identity-mismatched, or unavailable
When Host preflight runs for a live submission
Then the submission is rejected before provider payload creation
And the rejection identifies the freshness or identity reason

Given a fresh capability profile whose availability is online
When Host preflight runs immediately before submission
Then the artifact requirements are checked against that profile
And the profile fingerprint and calibration reference are recorded in evidence
```
```

### Evidence classification

```gherkin
Given a fake, simulator, or real provider result
When RunEvidence is produced
Then evidence_kind matches the observed execution source
And missing identity links mark evidence incomplete
And no AI or adapter message upgrades evidence to real
```

### Provider-neutral local operation

```gherkin
Given no provider SDK or credentials are installed
When local compile or fake-provider tests run
Then the Kernel remains importable and deterministic
And no provider network call is attempted
```

## Existing contract gap table

| Existing asset | Reuse | Gap to resolve |
|---|---|---|
| `QpuArtifact` | yes | source/semantic identity mapping |
| `QpuSubmitRequest` | baseline | route/provider/device metadata placement |
| `ProviderJobId` | opaque handle | route/provider naming must not be overloaded silently |
| `ProviderJobState` | minimum state | Host observation envelope and raw-state preservation |
| `QpuSubmitPort` | yes | preflight, idempotency, authorization boundary |
| `QpuJobPort` | yes | normalized failure/result semantics |
| AWS adapter/CLI/demo | completed | gap analysis only; no wholesale rewrite |

## Provider route matrix

| Route | Hardware provider | Role |
|---|---|---|
| IBM Quantum direct | IBM | direct gate-model baseline |
| AWS Braket | IonQ/Rigetti/QuEra candidate | aggregator and existing adapter extension |
| Azure Quantum | Pasqal/Quantinuum/IonQ/Rigetti candidate | aggregator and neutral-atom comparison |
| Google QCS direct | Google | access-controlled direct route |
| Direct provider APIs | provider-specific | add only after a demonstrated gap |

## Explicit non-goals

- No SDK selection or installation in Phase 0.
- No changes to `compiler/staqex/qpu_submit.py` in Phase 0.
- No network, credentials, or real-QPU submission.
- No automatic provider selection or cost-policy invention.
- No D-Wave annealing semantics or changes to `State<T>`/`measure`.

## Remaining decisions

1. Extend existing DTOs or add an adapter-owned envelope for the proposed
   `HostSubmissionApproval` reference.
2. Select OpenQASM 3, QIR, or a bounded wrapper as first-pilot artifact.
3. Select the first route/device after provider-specific Phase 0.

## Phase 0 exit

After typed Architecture and Phase 1 approvals, the fake port/contract tests
were added at `tests/test_liss_0514_multi_provider_qpu_contract_red.py` and the
Phase 2 Green slice was reviewed. Phase 3 requires separate approval.
