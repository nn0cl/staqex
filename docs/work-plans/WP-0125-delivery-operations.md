# WP-0125: Provider-neutral delivery and operations

| Field | Value |
|---|---|
| Status | **ready — design reviewed READY; conditional and Phase 1 not approved** |
| Type | architecture/release work plan |
| Size | XL |
| Parent | [WP-0119](WP-0119-real-qpu-readiness-roadmap.md) |
| Issues | LISS-0470 |
| Depends on | WP-0124 |
| Blocks | none |
| Canonical authority | Project conventions; new delivery ADR if work is unblocked |
| Owner boundary | Host delivery/operations, never Kernel semantics |
| Implementation permission | None; conditional architecture design only |
| Scope approval | User approved all Work Plans, 2026-08-27 |
| Post-review requirement | Post-pilot need decision; ADR and Phase 1 approval if unblocked |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md) |

## Goal

Only if the pilot demonstrates a need, define delivery, retention, monitoring,
audit, incident response, cancellation, and cost controls outside the Kernel.

## Release exit

Either an accepted provider-neutral delivery contract and separate deployment
ADR exist, or the item is explicitly deferred because local Host operation is
sufficient. No cloud, datastore, or topology is selected implicitly.

## Included / excluded

Included only if WP-0124 identifies a real operational need: delivery contract,
retention, monitoring, audit, incident response, cancellation, cost controls,
and privacy boundaries. Excluded by default: cloud selection, datastore,
deployment topology, public service API, and provider-specific operations.

## Acceptance scenarios

- Delivery exposes only provider-neutral Job/Result evidence and no secrets or
  internal AST/Joint buffers.
- Retention, deletion, audit, cancellation, and incident behavior are explicit
  and testable, or the item is closed as deferred with evidence.
- Operational failure cannot mutate source meaning or silently resubmit a job.

## Phase and evidence gates

Phase 0 is a post-pilot decision whether this WP is needed. If needed, an ADR
and Phase 1 Red contract tests precede implementation. Phase 2/3 are limited to
the accepted delivery boundary and its operational verification.

## Risks / stop conditions

Stop if the work requires a datastore, cloud, network topology, or public
deployment contract without a separate ADR and technology approval. The default
disposition is deferred when local Host operation is sufficient.

## Required deliverables

- post-pilot decision record stating needed or deferred;
- if needed, accepted provider-neutral delivery/operations ADR;
- retention, audit, cancellation, monitoring, incident, and cost-control
  acceptance matrix;
- operational verification and explicit deployment exclusions.

## Planning record

- Planning record: `AIP-WP-0125-2026-08-27-001`.
- Author/environment: Codex host agent, local repository.
- Model/reasoning: N/A; runtime does not expose displayed per-task values.
- Planning size: XL; basis is a potential deployment boundary and persistence
  decision. Confidence: low; this WP is intentionally conditional.

## Deferred disposition

- User confirmed on 2026-08-28 that the conditional operations policy should
  be followed and this WP deferred.
- Local Host operation is sufficient; no ADR, deployment, datastore, public
  API, retention, monitoring, or provider-specific operations are added.
- Reopen only after WP-0124 provides an evidenced operational need, followed
  by a new ADR and typed architecture/technology approval.
- Process review: no operating-contract deviation or operational problem
  found.
