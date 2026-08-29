# WP-0119: Real-QPU readiness roadmap

| Field | Value |
|---|---|
| Status | **approved design baseline — Architecture Path; Phase 1 not approved** |
| Type | Multi-issue roadmap and readiness program |
| Initial size | XL |
| Current size | XL |
| Parent | [WP-0118](WP-0118-implementation-readiness-backlog.md) |
| Authority | `open-work-register.md`, ADR 0210–0213, ADR 0202–0203, ADR 0083/0103/0104, backend/runtime contracts |
| Branch | One feature-unit branch per Issue; no implementation branch authorized by this WP |

| Scope approval | User approved all Work Plans, 2026-08-27 |
| Implementation permission | **None** |
| Post-review requirement | Per-Issue acceptance review and typed Phase 1 approval |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md) |

## [DESIGN CHECK]

- **Scope and expected behavior:** Exhaustively organize the work from the
  current Kernel/semantic projections through a provider-neutral executable
  artifact and a human-authorized run on an actual QPU. The program must
  preserve source meaning, provenance, exact/symbolic versus finite
  realization, fail-closed capability rejection, and terminal measurement.
- **Specifications and files inspected:** `AGENTS.md`,
  `docs/architecture/open-work-register.md`,
  `docs/research/2026-07-23-theory-to-qpu-feature-roadmap.md`,
  `docs/architecture/staqex-backend-targets.md`,
  `docs/architecture/staqex-runtime-execution-model.md`, ADR 0083, 0103,
  0104, 0127, 0161, 0202, 0203, 0210–0213, WP-0108, WP-0113, WP-0114,
  WP-0116–0118, and the project conventions.
- **Boundaries and candidate DTOs:** Scientific Semantic IR is the only
  source-derived semantic authority. Candidate provider-neutral values are
  `CapabilityProfile`, `RealizePlan`, `ExecutionArtifact`, `JobRequest`,
  `ProviderJobId`, `JobStatus`, `JobResult`, and `RunEvidence`; no candidate
  becomes an implementation type without its own accepted contract.
- **Constraints:** no provider SDK in Domain/UseCase; no live QPU call by an
  agent; no credentials in source or repository; no implicit finiteization,
  measurement, fallback, retry, persistence, or provider behavior; no Rust,
  cloud, datastore, or deployment technology selection in this WP.
- **Ambiguities requiring decisions:** provider and device scope after the
  existing AWS Braket technology decision; optional-dependency packaging;
  credentials/configuration boundary; calibration and noise-report schema;
  retry/idempotency; artifact retention; deployment topology; acceptance
  threshold for the first human-run pilot.
- **Included context:** current contracts, shipped adapters, canonical IR,
  accepted examples, local issue history, and deterministic repository
  evidence. **Omitted:** secrets, provider accounts, private device data,
  stale branches, and implementation details not yet accepted.
- **Routing:** architecture and technology decisions go to the Adjudicator;
  inventory, schema, link, and regression checks are deterministic; code
  implementation follows AT-TDD only after typed Phase 1/2 approvals.
- **Evidence contract:** every issue must produce a source/contract pointer,
  explicit acceptance scenarios, provenance/no-artifact evidence, and a
  review status. A real run must produce human-owned run metadata and must not
  be represented by a mock result.

## Completion target

The roadmap is complete only when a human, using their own explicitly
authorized credentials and selected device, can submit a supported Staqex
program, observe provider job lifecycle, retrieve a structured result, and
reproduce the run metadata sufficiently to distinguish source meaning,
finite realization, emitted artifact, provider execution, and measured data.
The agent may prepare and verify the path but must not submit to a real device.

## Current assets that are not reopened

- Scientific Semantic IR bounded projection and Coin/Mix/QPU rejection slices.
- Explicit finite `Realize`/Suzuki target slice and S02 numerical migration.
- Provider-neutral `QpuSubmitPort`, `QpuJobPort`, `CredentialPort`, Job/Result
  DTOs, resource gates, static/dynamic OpenQASM emitters, and the AWS Braket
  adapter/CLI walkthrough already recorded in the register.
- Local CPU/simulator and fake-provider verification.

The remaining work hardens, completes, or verifies boundaries around those
assets; it must not mechanically reimplement completed Issues.

## Release train

| Release | Work Plans | Exit meaning |
|---|---|---|
| R0 — planning baseline | WP-0120–0126 design records | Scope, ownership, dependencies, and approval gates are accepted |
| R1 — semantic/finite boundary | WP-0120–0121 | Supported source meaning has one canonical path to a finite artifact |
| R2 — offline target readiness | WP-0122 | Static/dynamic target artifacts pass offline conformance and preflight |
| R3 — provider-ready Host | WP-0123 | Fake-provider lifecycle is safe, typed, credential-safe, and reproducible in tests |
| R4 — human real-device pilot | WP-0126 | A human-authorized run produces validated, bounded evidence |
| R5 — optional operations | WP-0125 | Only a demonstrated delivery/operations need receives a separate contract |

An R-level is not a release claim until its child WPs are reviewed, their
Issues are complete or explicitly deferred, CI is green, and the register and
trace are synchronized. R4 is specifically a human-operated evidence milestone,
not permission for unattended production execution.

## Ordered phases and Issues

| Phase | Work Plan | Issue | Scope | Gate / exit evidence |
|---:|---|---|---|---|
| 0 | WP-0120 | [LISS-0455](../issues/LISS-0455-real-qpu-scope-reconciliation.md) | Reconcile this roadmap with the register and completed assets | Accepted scope, no stale work reopened |
| 1 | WP-0120 | [LISS-0456](../issues/LISS-0456-semantic-consumer-qasm-entry.md) | Canonical IR ownership through all public QASM entry points | No AST/DTO bypass; Phase 3 reviewed |
| 1 | WP-0120 | [LISS-0457](../issues/LISS-0457-meaning-family-qpu-readiness.md) | Product/tensor, continuous/open-system, and measurement readiness matrix | Family-specific disposition; unsupported cases remain explicit |
| 1 | WP-0121 | [LISS-0458](../issues/LISS-0458-realization-artifact-contract.md) | Provider-neutral finite artifact envelope and serialization | Accepted artifact/provenance/no-artifact contract |
| 2 | WP-0122 | [LISS-0459](../issues/LISS-0459-target-capability-profile-hardening.md) | Device capability, resource, gate, dynamic, and rejection profile | Deterministic preflight matrix |
| 2 | WP-0122 | [LISS-0460](../issues/LISS-0460-transpile-route-schedule-contract.md) | Native-gate mapping, topology routing, depth/timing schedule | Target-aware artifact with explicit approximation/cost |
| 2 | WP-0122 | [LISS-0461](../issues/LISS-0461-static-qasm-conformance.md) | Static OpenQASM conformance and parser/device-envelope checks | Offline conformance against supported subset |
| 2 | WP-0122 | [LISS-0462](../issues/LISS-0462-dynamic-qasm-conformance.md) | Dynamic QASM control, reset, feed-forward, and outcome mapping | Offline dynamic conformance; unsupported device rejection |
| 3 | WP-0123 | [LISS-0463](../issues/LISS-0463-provider-dependency-security-packaging.md) | Optional SDK packaging, version/security posture, install path | Dependency policy and isolated import checks |
| 3 | WP-0123 | [LISS-0464](../issues/LISS-0464-credential-config-boundary.md) | Credential, region/device, config, and secret-redaction boundary | No-secret source/config tests; fail-closed diagnostics |
| 3 | WP-0123 | [LISS-0465](../issues/LISS-0465-provider-submit-integration-hardening.md) | Existing provider adapter integration and provider-neutral mapping | Fake integration, idempotency, request/artifact identity |
| 3 | WP-0123 | [LISS-0466](../issues/LISS-0466-job-lifecycle-result-integrity.md) | Submit/status/wait/result/cancel and structured result integrity | Lifecycle/error/partial-result matrix |
| 4 | WP-0124 | [LISS-0467](../issues/LISS-0467-run-evidence-reproducibility.md) | Calibration, noise, compiler, seed, shot, and provenance evidence | Reproducible run envelope; no invented fidelity claim |
| 4 | WP-0124 | [LISS-0468](../issues/LISS-0468-human-authorized-real-qpu-pilot.md) | Offline pilot checklist and dry-run protocol | Approval/cost/cancellation controls ready |
| 4 | WP-0124 | [LISS-0469](../issues/LISS-0469-real-qpu-result-validation.md) | Offline result validation contract | Criteria and dispositions ready for real evidence |
| 4 | WP-0126 | [LISS-0475](../issues/LISS-0475-human-real-qpu-execution.md) | Human-executed device run and raw evidence handoff | Explicit human approval and captured real evidence |
| 5 | WP-0125 | [LISS-0470](../issues/LISS-0470-provider-neutral-delivery-operations.md) | Optional delivery, retention, monitoring, and incident contract | Separate ADR if deployment is required |

## Dependency graph

```text
0455 scope reconciliation
  ├── 0456 canonical QASM entry
  ├── 0457 meaning-family readiness
  └── 0458 artifact contract
          └── 0459 capability profile
                  └── 0460 route/schedule
                          ├── 0461 static QASM
                          └── 0462 dynamic QASM
                                  └── 0463 provider packaging
                                          ├── 0464 credentials/config
                                          ├── 0465 submit hardening
                                          └── 0466 lifecycle/result
                                                  └── 0467 run evidence
                                                          └── 0468/0469 offline preparation
                                                                  └── 0475 human real-device execution
                                                                          └── 0470 operations (optional)
```

0456–0458 may proceed in parallel after 0455. 0457 can close some families
as deferred without blocking the already-supported static subset. 0468 is
blocked until all safety, artifact, capability, credentials, and lifecycle
issues are reviewed. A real pilot never authorizes unattended or autonomous
submission.

## Research and design work that must be exhausted

1. **Semantic coverage:** classify every source construct by Kernel,
   simulator-only, static-QASM, dynamic-QASM, or unsupported; identify all
   remaining AST/DTO reconstruction paths and public facade ownership.
2. **Finite realization:** define dimension, basis ordering, numeric limits,
   Suzuki order/steps, approximation bounds, non-unitary rejection, and
   atomic no-artifact behavior.
3. **Artifact identity:** settle canonical serialization, NFC strings,
   finite numbers, ordered instructions, duplicate preservation, source
   fingerprint, semantic fingerprint, and provenance chain.
4. **Hardware envelope:** inventory qubit count, native gates, connectivity,
   measurement basis, reset/feed-forward support, timing, shots, queue and
   payload limits; separate declared capability from observed calibration.
5. **Compilation:** decide where decomposition, routing, scheduling, and
   measurement mapping live; retain source-to-artifact mappings and make
   every approximation visible.
6. **Provider integration:** verify SDK version/security, optional install,
   import isolation, request idempotency, provider job IDs, status vocabulary,
   cancellation, timeout, transient/permanent errors, and partial results.
7. **Credentials and privacy:** define environment/config precedence, region
   and device selection, redaction, audit fields, secret lifetime, and
   prohibited logging.
8. **Experimental validity:** define seeds, shot counts, calibration capture,
   noise metadata, simulator baseline, statistical tolerances, drift handling,
   and what claims are explicitly not supported.
9. **Human operations:** write the dry-run checklist, approval checkpoint,
   rollback/cancellation procedure, cost guard, incident handling, retention,
   and post-run review protocol.
10. **Deployment:** only if needed, decide whether a provider-neutral delivery
    port is sufficient; otherwise create a separate ADR before selecting any
    cloud, service, persistence, or topology.

## Approval and stop rules

- This WP authorizes planning and issue creation only.
- Each Issue needs its own accepted specification/ADR, dedicated branch,
  Phase 1 Red approval, and separate Phase 2 implementation approval.
- Any change to `State<T>`, terminal `measure`, Scientific Semantic IR
  authority, `Realize`, provider selection, credentials, deployment, or
  persistence stops for Adjudicator/ADR review.
- CI green is required before merge; a real provider run is evidence for the
  human pilot only, not a substitute for deterministic tests.

## WP readiness contract

Before a child WP moves from `proposed` to `ready`, it must name its accepted
Spec/ADR, issue graph, owner boundary, included files, exclusions, acceptance
scenarios, Phase 1 test locations, rollback/no-artifact behavior, verification
commands, and typed Adjudicator approval. Before implementation, the selected
Issue must also have a dedicated feature branch and its own planning record.

Status changes must distinguish design complete, Phase 1 Red approved, Phase 2
implementation approved, Phase 3 reviewed, and release accepted. A merged PR
does not by itself close a WP or Issue until its evidence and status are
synchronized.

## Definition of done

- All Issues have dispositions and no stale completed work is reopened.
- Supported source-to-artifact paths are canonical, provenance-preserving, and
  fail closed before allocation/emission when unsupported.
- Provider integration is optional, isolated, credential-safe, and tested
  with fakes before any real run.
- The human pilot and result validation are recorded with real/non-mock
  evidence and explicit limitations.
- The open-work register, Issues, WPs, ADRs, and traces agree on status.

## Next safe action

LISS-0456 through LISS-0469 are complete for their bounded offline and
provider-neutral slices. The next safe action is the separately tracked
human-operated WP-0126
pilot: select a supported target, review the dry-run artifact and cost/shots
guard, and provide explicit real-time approval before any human submits. No
provider installation or real-QPU submission is authorized for the agent by
this WP alone.
