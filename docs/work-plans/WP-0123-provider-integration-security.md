# WP-0123: Provider integration and execution security

| Field | Value |
|---|---|
| Status | **done — bounded provider-neutral Host hardening complete** |
| Type | feature/release work plan |
| Size | XL |
| Parent | [WP-0119](WP-0119-real-qpu-readiness-roadmap.md) |
| Issues | LISS-0463, LISS-0464, LISS-0465, LISS-0466 |
| Depends on | WP-0122 |
| Blocks | WP-0124 |
| Canonical authority | ADR 0083, 0103, 0104, 0161, 0202, 0203; dependency policy |
| Owner boundary | Host adapters and provider-neutral Job ports |
| Implementation permission | Bounded Issues complete; real submission excluded |
| Scope approval | User approved all Work Plans, 2026-08-27 |
| Post-review requirement | Technology/security review and typed Phase 1 approval |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md) |

## Goal

Make the existing provider-neutral ports and AWS Braket adapter safe to use
with an optional provider SDK, explicit credentials/configuration, and a
complete provider job lifecycle.

## Work units

- SDK version/security/install/import posture (LISS-0463).
- Credentials, device selection, redaction, and cost guard (LISS-0464).
- Submit idempotency, mapping, timeout, and error hardening (LISS-0465).
- Status/wait/result/cancel and partial-result integrity (LISS-0466).

## Release exit

Fake-provider integration is green; no secret reaches source/IR/artifact/logs;
dry-run cannot submit; provider failures are typed; JobResult retains all
identity/provenance and never fabricates completion.

Changing provider, dependency range, or deployment technology requires typed
technology/architecture approval.

## Included / excluded

Included: approved AWS Braket adapter hardening, optional SDK packaging,
credential/configuration boundary, fake-provider integration, idempotency,
lifecycle/error mapping, cancellation, and partial-result rules. Excluded:
provider changes, secrets, autonomous submission, cloud deployment, datastore,
and changes to Domain or Scientific IR.

## Acceptance scenarios

- Local CPU/simulator paths work without the optional SDK.
- Missing/invalid/vulnerable SDK or credentials fail closed before submit;
  secrets are absent from source, IR, artifacts, logs, and exceptions.
- Check/dry-run never submits; repeated request identity follows the accepted
  idempotency contract.
- Provider status, timeout, cancellation, failure, and incomplete results map
  to typed Job/JobResult states without fabricated observations.

## Phase and evidence gates

Phase 0 records technology and security decisions. Phase 1 adds fake-adapter
Red tests only. Phase 2 implements the reviewed Host boundary. Phase 3 verifies
isolated imports, redaction, lifecycle behavior, and CI in a pytest-enabled
environment. Real credentials are reserved for the human pilot.

## Risks / stop conditions

Stop for a new ADR if provider or dependency scope changes, or if SDK behavior
leaks into Domain/UseCase or adapter code begins deciding physics meaning.

## Required deliverables

- dependency/security adoption record and isolated optional-import check;
- credential/configuration and redaction contract;
- fake-provider submit/lifecycle matrix with idempotency and failure cases;
- CI evidence in a pytest-enabled environment and security review.

## Planning record

- Planning record: `AIP-WP-0123-2026-08-27-001`.
- Author/environment: Codex host agent, local repository.
- Model/reasoning: N/A; runtime does not expose displayed per-task values.
- Planning size: XL; basis is external-resource, security, and lifecycle
  boundary work. Confidence: low until technology/credential decisions close.

## Closeout

LISS-0463 through LISS-0466 are complete for the bounded optional-dependency,
configuration, submit, and lifecycle contracts. Fake/provider-neutral tests
pass. Actual SDK adoption, production credentials, network, and real QPU
submission remain separately gated by the human pilot.
