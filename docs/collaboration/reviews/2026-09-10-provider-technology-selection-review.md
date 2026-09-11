# Provider Phase 0 / technology-selection review

| Field | Value |
|---|---|
| Date | 2026-09-10 |
| Scope | WP-0132–WP-0136 / LISS-0515–LISS-0519 |
| Current phase | Provider Phase 0 technology-selection review |
| Review isolation | same_context; weaker than separate_context |
| Implementation permission | None |
| Requested approval | Typed technology-selection approval per route |
| Decision | **Approved** — typed approval received 2026-09-10 |

## Decision boundary

This review selects access technology and artifact boundary only. It does not
select a live device, grant credentials, authorize SDK installation, or permit
submission. `access_route`, `hardware_provider`, and `device_id` remain
separate as required by the accepted Staqex contract and ADR 0217.

## Recommendation matrix

| Route | Recommended technology | Artifact boundary | Status | Device/access |
|---|---|---|---|---|
| IBM Quantum | `qiskit-ibm-runtime`, `QiskitRuntimeService`, Sampler V2; use the new IBM Quantum Platform channel where available | OpenQASM 3 input, then backend-specific ISA/transpile in Host | recommended | device and account channel unknown |
| AWS Braket | Reuse the existing adapter; retain Braket SDK/Boto3 boundary and OpenQASM 3 task submission | OpenQASM 3 | reuse / recommended | IonQ remains first candidate, not selected |
| Azure Quantum | Azure Quantum workspace/target/job API; QIR v1 as the first common job format | QIR v1; target-native formats only in provider adapter | recommended | provider target and workspace access unknown |
| Google QCS | `cirq-google` Engine/QCS adapter | Cirq/Google-native Host adapter boundary | recommended for offline adapter | live access requires approved group and user-visible processor |
| Quantinuum direct | no direct adapter now | use Azure route first | defer | direct access/gap unknown |
| IonQ direct | no direct adapter now | use AWS/Azure route first | defer | direct route adds no demonstrated gap |
| Rigetti direct | no direct adapter now; revisit for Quil-T/pulse or Gateway-specific need | use AWS/Azure route first | defer | direct QCS has distinct Quil/calibration behavior |
| QuEra direct | no direct adapter now | use AWS Braket; analog lane remains separate | defer | direct gate-model gap not demonstrated |

## Evidence and compatibility

### IBM Quantum — recommended route

IBM documents `qiskit-ibm-runtime` as the successor to the IBM Provider and
documents `QiskitRuntimeService` with the new `ibm_quantum_platform` channel.
IBM's current primitives path is Sampler V2/Estimator V2; backend configuration
and properties remain the capability sources, with refreshable properties and
timestamps. OpenQASM 3 is a documented input/interchange format.

- Compatibility: **verified** for Host-owned SDK boundary and OpenQASM 3 input.
- Unknown: account channel, instance, backend name, quota, and live access.
- Rejected: legacy `qiskit-ibmq-provider`/deprecated channel as the new route.

Sources: [IBM Qiskit introduction](https://docs.quantum.ibm.com/guides/index),
[IBM channel setup](https://docs.quantum.ibm.com/guides/setup-channel),
[IBM primitives](https://docs.quantum.ibm.com/guides/primitives),
[IBM OpenQASM](https://docs.quantum.ibm.com/guides/introduction-to-qasm),
[IBM backend properties](https://docs.quantum.ibm.com/api/qiskit-ibm-runtime/ibm-backend).

### AWS Braket — reuse existing route

AWS documents OpenQASM 3 task submission through the SDK, Boto3, and CLI for
gate-based devices. The repository already has the Braket adapter, lifecycle
CLI, and fake evidence. Therefore the selection is reuse plus provider-profile
fan-out, not a new AWS transport.

- Compatibility: **verified** for the existing OpenQASM 3 and Host port boundary.
- Unknown: account-enabled devices, region, S3 destination, current queue,
  price, and target availability.
- Decision: do not reopen completed AWS hardening; resolve only a demonstrated
  provider-profile gap.

Sources: [AWS OpenQASM 3 submission](https://docs.aws.amazon.com/braket/latest/developerguide/braket-openqasm-create-submit-task.html),
[AWS GetDevice](https://docs.aws.amazon.com/braket/latest/APIReference/API_GetDevice.html),
[AWS GetQuantumTask](https://docs.aws.amazon.com/braket/latest/APIReference/API_GetQuantumTask.html).

### Azure Quantum — recommended QIR v1 route

Azure's current CLI path submits QIR jobs with `qir.v1`, while provider-native
targets may require different input/output formats. This makes QIR v1 the
common Azure route and keeps provider-native formats behind the adapter.
Workspace, target, permission, and cost are runtime configuration and remain
unknown until an account is inspected.

- Compatibility: **verified** for the QIR v1 Host adapter boundary.
- Unknown: selected provider, target ID, workspace, region, permission, and
  current availability.
- Decision: do not treat Pasqal as selected; retain it as a candidate until
  target evidence exists.

Sources: [Azure OpenQASM/QDK integration](https://learn.microsoft.com/en-us/azure/quantum/qdk-openqasm-integration),
[Azure CLI job submission](https://learn.microsoft.com/en-us/azure/quantum/how-to-submit-jobs-azure-cli),
[Azure provider status](https://learn.microsoft.com/en-us/rest/api/azurequantum/dataplane/providers/list?view=rest-azurequantum-dataplane-2026-01-15-preview).

### Google QCS — access-dependent route

Google documents Cirq and Quantum Engine as the hardware access path. Access
is restricted to approved groups, processor IDs are project/user-visible, and
processor state is online/offline/maintenance. Calibration is retrievable for
the current processor and past jobs. The correct Phase 0 outcome is an offline
adapter contract plus an explicit access blocker, not an invented device.

- Compatibility: **verified** for an offline `cirq-google`/Engine adapter.
- Live status: **unknown / access-dependent** without an approved group and
  project.
- Decision: technology route may proceed offline; live pilot remains blocked.

Sources: [Google QCS concepts](https://quantumai.google/cirq/google/concepts),
[Google QCS setup](https://quantumai.google/cirq/tutorials/google/start),
[Google EngineProcessor](https://quantumai.google/reference/python/cirq_google/engine/EngineProcessor),
[Google calibration](https://quantumai.google/cirq/google/calibration).

## Direct-provider disposition

- **Quantinuum: defer.** Azure already supplies the aggregator route. Direct
  adoption requires a demonstrated access, lifecycle, capability, or result
  gap; the current evidence does not provide one.
- **IonQ: defer.** IonQ's direct API exposes jobs, backend availability, queue
  estimates, and characterization, but AWS/Azure routes already cover the
  current static gate-model contract. Direct access is not justified yet.
- **Rigetti: defer, with a named future trigger.** Rigetti QCS has a distinct
  OpenAPI/gRPC boundary, Quil/Quil-T, QCS Gateway, and calibration-driven
  compilation. Add a direct adapter only if Quil-T/pulse, Gateway, or direct
  calibration control becomes a Staqex requirement.
- **QuEra: defer.** QuEra's Bloqade documentation describes Aquila through AWS
  Braket. A direct gate-model adapter adds no demonstrated gap, and analog
  neutral-atom semantics are outside this gate-model contract.

Direct provider sources: [IonQ jobs](https://docs.ionq.com/api-reference/v0.3/jobs/get-jobs),
[IonQ backends](https://docs.ionq.com/api-reference/v0.3/backends/get-backends),
[Rigetti QCS API](https://docs.rigetti.com/qcs/guides/the-rigetti-qcs-api),
[Rigetti program lifecycle](https://docs.rigetti.com/qcs/guides/the-lifecycle-of-a-program),
[QuEra Bloqade](https://bloqade.quera.com/dev/analog/).

## Review result

The technology review is **approved as the route technology baseline**, with no
live device selected. The approved scope is:

1. IBM: `qiskit-ibm-runtime` / `QiskitRuntimeService` / Sampler V2 route.
2. AWS: reuse existing Braket adapter and OpenQASM 3 route.
3. Azure: Azure Quantum job API with QIR v1 as the common format.
4. Google: offline `cirq-google`/Engine adapter; live route remains access
   dependent.
5. Direct Quantinuum, IonQ, Rigetti, and QuEra: defer pending a demonstrated
   gap.

Each route still requires a separate Phase 1 Red approval and provider-specific
adapter Issue. SDK installation, credentials, and provider calls remain
separately gated.
