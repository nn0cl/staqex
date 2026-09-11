# WP-0131: Multi-provider real-QPU connectivity contract

| Field | Value |
|---|---|
| Status | **in_progress — LISS-0514 Phase 3 complete; provider pilot review pending** |
| Type | architecture / multi-provider roadmap |
| Size | XL |
| Parent | [WP-0119](WP-0119-real-qpu-readiness-roadmap.md) |
| Children | WP-0132–WP-0137 |
| Issues | [LISS-0514](../issues/LISS-0514-multi-provider-qpu-contract-readiness.md) |
| Depends on | WP-0122, WP-0123, WP-0124 |
| Blocks | provider-specific implementation and real-QPU pilots |
| Implementation permission | **None** |
| Acceptance authority | [Real-QPU readiness](../specs/staqex-real-qpu-readiness-acceptance.md); DEC-0006 |

## [DESIGN CHECK]

- Scope and expected behavior: define one provider-neutral execution contract
  that can route the same Staqex artifact through IBM Quantum, AWS Braket,
  Azure Quantum, Google QCS, and direct provider APIs.
- Inspected: WP-0119–0126, `staqex-real-qpu-readiness-acceptance.md`,
  `staqex-hybrid-workflow.md`, DEC-0006, testing strategy, and project
  conventions.
- Ports/DTOs: `CapabilityProfilePort`, `QpuSubmitPort`, `QpuJobPort`,
  `CredentialResolverPort`, `RunEvidenceSink`; immutable
  `ExecutionArtifact`, `JobRequest`, `JobStatus`, `JobResult`, `RunEvidence`.
- Constraints: no SDK in Kernel, no credentials in repository, no semantic
  mutation by adapters, fail closed before allocation, human confirmation for
  real submission.
- Open decisions: first device per platform, SDK versions, QASM vs QIR
  artifact priority, cost ceilings, result normalization, access approval.
- Context omitted: secrets, private accounts, raw provider logs, and unrelated
  source history.
- Routing: strong-reasoning architecture review; deterministic schema,
  import-boundary, and fake-provider checks; human provider/technology approval.
- Verification: review child WP dependencies and acceptance scenarios before
  Phase 1 Red; no live submission in this WP.

## Goal

Make provider and access route replaceable while preserving one source,
semantic fingerprint, finite artifact, measurement contract, and evidence
chain.

## Child work plans

| WP | Route | Initial target |
|---|---|---|
| WP-0137 | Artifact packaging / target build | portable to targeted `.sqxa` |
| WP-0132 | IBM Quantum direct | IBM gate-model QPU |
| WP-0133 | AWS Braket | IonQ, Rigetti, or QuEra |
| WP-0134 | Azure Quantum | Pasqal, Quantinuum, IonQ, or Rigetti |
| WP-0135 | Google QCS direct | Google hardware, access-controlled |
| WP-0136 | Direct-provider parity | Quantinuum, IonQ, Rigetti, QuEra |

## Required common acceptance

- The same supported static artifact can be preflighted through every route.
- Provider adapters cannot change Scientific Semantic IR or measurement
  meaning.
- Provider-specific status and result payloads map to one immutable contract.
- Fake-provider tests pass without installing any provider SDK.
- Evidence distinguishes source, artifact, provider route, job, and real result.

## Route identity contract

Every capability, request, result, and evidence record must keep these values
separate:

- `access_route`: `ibm_quantum`, `aws_braket`, `azure_quantum`,
  `google_qcs`, or an approved direct route;
- `hardware_provider`: the organization operating the physical QPU;
- `device_id`: the provider-issued target identifier captured as opaque Host
  configuration.

An adapter may normalize transport and lifecycle vocabulary, but it may not
use an access route as a substitute for hardware capability evidence.

## Issue graph

| Issue | Status | Phase | Size | Depends on | Branch |
|---|---|---|---|---|---|
| [LISS-0514](../issues/LISS-0514-multi-provider-qpu-contract-readiness.md) | in_progress | Phase 0 | M | WP-0122–0124 | `feature/liss-0514-multi-provider-qpu-contract` |
| LISS-0515–LISS-0518 | proposed | Phase 0 | M each | LISS-0514 | one feature-unit branch per Issue |
| [LISS-0519](../issues/LISS-0519-direct-provider-parity-decision.md) | proposed | Phase 0 | M | LISS-0514, 0516, 0517 | `feature/liss-0519-direct-provider-parity` |

## Luna execution contract

Luna tasks must be dispatched as one Issue and one phase per task. Use model
`gpt-5.6-luna` with `high` reasoning for Phase 0 and Phase 1. Do not set the
repository-wide runtime-routing model from this WP.

Each task input contains only `AGENTS.md`, the quickstart and conventions, the
target WP and Issue, the named acceptance/architecture documents, directly
touched files, and one minimal neighboring example. Each task output contains:

1. `[DESIGN CHECK]`;
2. current phase and permission boundary;
3. assumptions and open decisions;
4. changed files;
5. deterministic commands and results;
6. the single next requested approval type.

Luna must stop on an unfilled contract value, provider or dependency choice
not approved for the current Issue, need for credentials, network/live-QPU
access, or work outside the named phase.

## Phase gates

| Gate | Required evidence | Permission after gate |
|---|---|---|
| Phase 0 | accepted common spec or provider adoption decision | request Phase 1 only |
| Phase 1 Red | reviewed failing port/adapter tests using fakes | request Phase 2 only |
| Phase 2 Green | minimum optional adapter; reviewed tests green | request Phase 3 only |
| Phase 3 | readability/import/security review and deterministic checks | request pilot review |
| Real pilot | human target/shots/cost/credential confirmation | one bounded submission only |

## Exclusions

Google access procurement, live credentials, autonomous submission, D-Wave
annealing, deployment topology, datastore selection, and changes to `State<T>`
semantics are excluded.

## Approval gate

This WP authorizes planning and child-WP creation only. Architecture approval,
technology selection approval, Phase 1 approval, and real-run approval remain
separate decisions.

## Next safe action

LISS-0514 Phase 3 review is complete: the contract refactor preserves behavior,
all seven scoped tests run successfully, and provider boundaries remain empty.
Provider-specific selection and live execution remain blocked.
