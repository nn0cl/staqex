# Staqex real-QPU readiness acceptance specification

| Field | Value |
|---|---|
| Status | **proposed — LISS-0472 Continuous/Open-system bounded slice done; broader realization not approved** |
| Authority | WP-0119; ADR 0210–0213; ADR 0202–0203; ADR 0065, 0083, 0103, 0104, 0161 |
| Work Plans | WP-0120, WP-0121, WP-0122, WP-0123, WP-0124, WP-0125, WP-0126 |
| Issues | LISS-0456–LISS-0472, LISS-0475 |
| Scope approval | User-approved planning/design baseline, 2026-08-27 |
| Implementation permission | None |

## [DESIGN CHECK]

- **Scope and expected behavior:** define the observable acceptance boundary
  from source-derived Scientific Semantic IR through finite artifact, target
  conformance, provider-neutral job lifecycle, reproducible evidence, and a
  human-authorized real-QPU pilot.
- **Specifications and files inspected:** WP-0119–0126, LISS-0455–0475,
  `open-work-register.md`, ADR 0210–0213, ADR 0202–0203, ADR 0065, 0083,
  0103, 0104, 0161, and the existing semantic-consumer and realization specs.
- **Component boundaries, ports/adapters, and VO/DTO candidates:** the
  compiler owns source identity, semantic meaning, realization policy, and
  target projection; provider execution is accessed only through approved
  provider-neutral ports. Candidate contract values are `SourceIdentity`,
  `RealizePlan`, `ExecutionArtifact`, `CapabilityProfile`, `JobRequest`,
  `JobStatus`, `JobResult`, and `RunEvidence`.
- **Applicable constraints:** no hidden finiteization, no AST/DTO semantic
  bypass, terminal `measure` remains the collapse boundary, unsupported work
  fails closed before artifact/allocation, no provider SDK or credential in
  the Kernel, and no autonomous real-QPU submission.
- **Decisions, assumptions, and unresolved ambiguities:** the existing ADRs
  remain authoritative. Provider SDK packaging, deployment topology, and any
  new artifact/DTO are unresolved until their Issue-specific ADR or contract
  review is accepted.
- **Included and omitted AI context:** include only the roadmap, acceptance
  contracts, current architecture, ADRs, and Issue/WP metadata; omit secrets,
  provider data, unrelated source, and full repository history.
- **Task routing:** deterministic checks validate links, IDs, schemas, and
  offline fixtures; human review decides architecture, technology, phase, and
  live-run gates.
- **Input/output evidence contract:** every acceptance result records the
  source identity, contract version, decision/status, diagnostic or result,
  and whether evidence is synthetic, fake, simulator, or real. AI output is
  planning input only and never runtime evidence.
- **Verification plan:** review each scenario below, create only test/fixture
  changes in Phase 1, run offline deterministic checks, and require explicit
  approval before Green or any provider action.

## Normative invariants

1. Scientific Semantic IR is the source-derived semantic authority. AST,
   caller DTOs, strings, and provider payloads may not override it.
2. Exact or symbolic inspection never creates a finite executable artifact.
   Only an explicit, valid `Realize` policy may cross the finite boundary.
3. Any unsupported meaning, capability, resource, credential, or lifecycle
   state fails closed with provenance and without a partial artifact,
   allocation, or fabricated result.
4. Provider-specific policy belongs in an adapter behind a port. The Kernel
   remains provider-neutral and local-first.
5. Evidence distinguishes source, artifact, target, provider job, measured
   result, and human authorization. A parser-success or fake-provider result
   is not evidence of physical execution.

## Acceptance scenarios

Each scenario is a Phase 1 candidate. Phase 1 may add failing tests and
fixtures only after the relevant Issue-level review and typed approval.

### Semantic authority and meaning families

**LISS-0456 — Canonical consumer authority**

```gherkin
Given a source program with a supported finite meaning and a public QASM entry point
When the entry point compiles the program
Then the consumer uses one compile-owned Scientific Semantic IR identity
And caller-injected AST/DTO/string meaning cannot override source identity or provenance
And an unresolved meaning is reported with provenance and emits no finite artifact
```

**LISS-0457 — Meaning-family readiness**

```gherkin
Given a meaning family in the readiness matrix
When its source example is classified for finite target execution
Then the record contains its typed semantic role, finite boundary, target status, and reason
And unsupported or lossy cases are explicitly rejected or deferred
And no family is silently treated as a different meaning family
```

**LISS-0471 — Measurement-family QPU readiness**

```gherkin
Given a source measurement meaning in the terminal or dynamic lane
When it is classified for finite target execution
Then terminal collapse and dynamic measurement/feed-forward remain distinct
And the source identity and semantic role are preserved
And an unsupported dynamic target is rejected with existing capability diagnostics
And no artifact or QASM is emitted for the rejected case
And POVM or tomography is explicitly deferred rather than fabricated
```

The detailed design and Phase 1 boundary are recorded in
[`LISS-0471`](../issues/LISS-0471-measurement-family-qpu-readiness.md).

**LISS-0472 — Continuous/Open-system QPU readiness**

```gherkin
Given a continuous or open-system source meaning
When it is classified for finite QPU execution
Then its continuous/domain and density/channel/evolution meaning is preserved
And an explicit finite discretization contract is required
And missing authorization is rejected or deferred with provenance
And no hidden resolution, integrator, error tolerance, provider mapping,
  finite artifact, allocation, or QASM is produced
And CPU/Simulator evidence is not reported as physical-QPU evidence
```

The detailed design and Phase 1 boundary are recorded in
[`LISS-0472`](../issues/LISS-0472-continuous-open-system-qpu-readiness.md).

The Phase 0 research matrix is deliberately explicit about what must be
decided before any family enters implementation:

| Family | Meaning questions to resolve | Finite/QPU questions to resolve | Existing evidence | Safe interim disposition |
|---|---|---|---|---|
| Product/tensor | Which tensor/product nodes and dimensions are source meaning, and which are algebraic convenience? | Which finite carrier, basis ordering, and unitary/measurement projection preserve that meaning? | `tests/fixtures/semantic_meaning/mixture_and_product.sqx`; `tests/fixtures/capability_rejection/non_unitary_product.sqx` | Reject or defer until a family-specific contract and fixtures are accepted |
| Continuous/open-system | Which state/operator evolution and physical parameters remain exact or symbolic? | Which numerical method, error bound, and target capability are authorized? | `examples/basics/B12_open_systems/main_open_systems.sqx`; continuous/discretization and Lindblad specs | Defer; no hidden discretization or provider-derived method selection |
| Measurement | Which terminal observation and dynamic feed-forward roles are distinct? | Which basis, shot, result-order, and dynamic-capability constraints apply? | `tests/fixtures/semantic_core/dynamic_measurement.sqx`; existing terminal/dynamic measurement contracts | Accept only the already-defined terminal/dynamic contract; reject unsupported target behavior |

For each row, Phase 0 must record a source fixture, semantic node/role,
provenance requirements, finite boundary, target status, rejection code or
deferral reason, and decision owner. A row with missing evidence is not a
supported QPU capability.

### Finite artifact and target compilation

**LISS-0458 — Realization and artifact atomicity**

```gherkin
Given an ideal or symbolic expression without an explicit finite Realize policy
When a finite artifact is requested
Then no artifact, gate list, allocation, or provider payload is produced
Given an explicit finite Realize policy with finite dimensions, numbers, and budget
When realization succeeds
Then the artifact preserves source/semantic fingerprints, provenance, order, duplicates, and policy metadata
And canonical serialization is stable for equivalent inputs
```

**LISS-0459 — Capability and resource preflight**

```gherkin
Given an execution artifact and a declared synthetic target capability profile
When preflight evaluates dimensions, operations, measurements, parameters, and resource limits
Then every unsupported constraint has an observable diagnostic before allocation
And a passing profile cannot claim provider execution
```

**LISS-0460 — Routing and scheduling**

```gherkin
Given an artifact requiring routing or scheduling
When a target-neutral route is selected
Then inserted operations, ordering, cost, and provenance are reported deterministically
And an unsupported route rejects without emitting a partial target artifact
```

**LISS-0461 — Static QASM conformance**

```gherkin
Given a supported static artifact and a declared OpenQASM subset
When QASM is emitted and checked by the independent offline conformance port
Then the text parses within the declared subset and retains source/result metadata
And an empty, unsupported, or out-of-subset artifact is rejected without simulator fallback
```

**LISS-0462 — Dynamic QASM conformance**

```gherkin
Given a dynamic source meaning with explicit control, measurement, or reset
When the selected target profile does not support the required dynamic feature
Then the compiler rejects with the missing capability and emits no QASM or allocation
Given the profile supports the declared dynamic subset
When QASM is emitted offline
Then control and outcome dependencies are explicit and no physical-execution claim is made
```

### Provider boundary and job lifecycle

**LISS-0463 — Dependency and packaging isolation**

```gherkin
Given a local compile, inspection, or fake-provider test
When the optional provider package is absent
Then local behavior remains importable and provider-neutral
And provider installation is isolated, version-pinned or bounded, and security-reviewed
```

**LISS-0464 — Credential and device configuration**

```gherkin
Given missing, invalid, or conflicting provider/device configuration
When a live-capable host preflights a request
Then it fails before provider submission
And diagnostics redact secrets and expose only approved configuration identity
```

**LISS-0465 — Submit integration**

```gherkin
Given a validated artifact and an approved provider-neutral submit request
When a fake provider port receives the request
Then request identity, idempotency, target, shots, and artifact fingerprint are preserved
And retries cannot create an untracked duplicate submission
```

**LISS-0466 — Job lifecycle and result integrity**

```gherkin
Given a submitted job represented by a provider-neutral job identifier
When status, wait, result, cancel, timeout, failure, or incomplete-result paths occur
Then each provider state maps deterministically to the approved Job/Result contract
And unknown, partial, cancelled, or failed results are never presented as complete measurements
```

### Evidence and human-authorized pilot

**LISS-0467 — Reproducibility evidence**

```gherkin
Given a local, fake, simulator, or provider job
When a run evidence envelope is produced
Then it links source identity, semantic/artifact fingerprints, target profile, request, job state, result, and timestamps
And missing links mark evidence incomplete or inconclusive rather than inventing provenance
```

**LISS-0468 — Human-authorized real-QPU pilot**

```gherkin
Given a small supported program and a reviewed dry-run artifact
When the human operator reviews target, shots, cost, credentials, cancellation, and evidence requirements
Then real submission occurs only after explicit real-time human confirmation
And the run is labeled real or non-mock from observed execution evidence
And the agent does not submit autonomously
```

**LISS-0469 — Result validation and disposition**

```gherkin
Given a completed real-QPU evidence envelope and predeclared validation criteria
When measured results are analyzed
Then raw data, derived statistics, criteria, deviations, and disposition are retained
And validation does not rewrite source meaning or turn inconclusive evidence into a success claim
```

**LISS-0475 — Human real-QPU execution and evidence handoff**

```gherkin
Given a reviewed offline artifact, selected target, and cost/shots ceiling
When the human operator gives explicit real-time approval
Then the human may submit, observe the Job lifecycle, and retrieve a raw result
And source/artifact identity and available calibration/noise metadata are handed off without secrets
Given unsupported capability, missing credentials, unexpected cost, or incomplete provenance
When the gate is evaluated
Then submission stops before execution
```

**LISS-0470 — Delivery and operations boundary**

```gherkin
Given a request for delivery, retention, monitoring, or public service operation
When no provider-neutral delivery ADR and technology approval exist
Then the operation remains deferred and no deployment boundary is introduced
Given a later accepted delivery ADR
When the approved operation runs
Then only the approved Job/Result/evidence contracts cross the delivery boundary
```

## Phase and approval gates

| Gate | Allowed work | Required evidence | Approval still required |
|---|---|---|---|
| Phase 0 design | research, contract/spec, ADR proposal, fixtures plan | reviewed scope, dependencies, ambiguity list | typed Phase 1 Red approval |
| Phase 1 Red | failing offline tests and test fixtures only | Given/When/Then mapping, expected Red, no production changes | typed Phase 2 implementation approval |
| Phase 2 Green | minimum implementation for reviewed tests | unchanged reviewed tests, deterministic Green | Phase 3 approval/review |
| Phase 3 | refactor, regression, evidence review | rollback/no-artifact proof and review packet | release acceptance |
| Real-QPU pilot | human-operated action only | preflight, confirmation, raw result, evidence envelope | explicit real-time human confirmation |

Provider SDK installation, credentials, network calls, deployment selection,
and real-QPU submission are outside the current approval. They require the
relevant technology/security/human gate even if offline tests are Green.

## Issue mapping and exit evidence

| Issue | Primary evidence | Exit condition |
|---|---|---|
| LISS-0456 | consumer inventory, authority/no-bypass tests | all selected facades have one canonical source identity |
| LISS-0457 | family matrix and negative fixtures | every family has an explicit ready/reject/defer disposition |
| LISS-0458 | schema, fingerprint vectors, rejection matrix | atomic finite artifact contract accepted |
| LISS-0459 | synthetic capability profiles and preflight matrix | unsupported resources reject before allocation |
| LISS-0460 | route fixtures and cost/provenance reports | route behavior is deterministic and target-neutral |
| LISS-0461 | offline static QASM corpus and subset manifest | accepted text conforms; rejected text emits nothing |
| LISS-0462 | offline dynamic corpus and capability negatives | dynamic dependencies are explicit or rejected |
| LISS-0463 | isolated import/install/security checks | local path works without optional SDK |
| LISS-0464 | redaction and preflight fixtures | invalid configuration fails before submit |
| LISS-0465 | fake-port idempotency/fault tests | submit identity and retry semantics are stable |
| LISS-0466 | fake lifecycle/result matrix | incomplete/failed outcomes remain non-success |
| LISS-0467 | evidence schema and baseline fixtures | source-to-result chain is complete or marked incomplete |
| LISS-0468 | dry-run checklist and human sign-off record | pilot is human-authorized and auditable |
| LISS-0469 | predeclared criteria and analysis fixtures | result disposition is reproducible and honest |
| LISS-0475 | human approval, target/cost gate, Job lifecycle, and redacted raw-result handoff | real execution is human-owned and traceable |
| LISS-0470 | post-pilot decision and delivery ADR if needed | delivery is accepted or explicitly deferred |

## Non-goals

This specification does not add syntax, select a new provider, install an SDK,
choose a deployment platform, introduce persistence, authorize credentials,
run a network call, or authorize an agent to submit to a real QPU.
