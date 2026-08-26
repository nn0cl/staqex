# Architecture Overview

The project uses Clean Architecture. Runtime, stack, domain summary, ports,
and non-decisions live in `docs/collaboration/project-conventions.md`.

## Layers

### Domain

Pure domain behavior named in `docs/collaboration/project-conventions.md`.

Must not depend on:

- any UI framework.
- SQL schemas, ORM structs, vector DB SDKs, or file-system APIs.
- LLM SDKs, cloud AI SDKs, or third-party provider APIs.

### UseCase

Coordinates domain behavior through ports.

Examples belong in the target's specifications and stack-specific
architecture documents, not in this file.

### Ports

Interfaces owned by the application core.

Ports isolate every external resource named in
`docs/collaboration/project-conventions.md`.

### Adapters

Framework and infrastructure implementations.

Adapters may use framework APIs, infrastructure libraries, DB or vector DB
SDKs, external file layouts, API clients, and provider SDKs.

Adapters must not define business policy.

### Front-End / Delivery

The delivery layer (UI, CLI, HTTP API) presents domain state and collects
user input.

It must not own:

- confidence, trust, or merge policy for AI-derived data.
- validation or secret-storage policy.
- any policy that belongs in a use case.

## Runtime Direction

See `docs/collaboration/project-conventions.md`.

## Selected Technology

See `docs/collaboration/project-conventions.md`.

## Detailed Rules

- `project-structure.md`: where files belong.
- `testing-strategy.md`: AT-TDD test placement.
- `implementation-readiness.md`: checklist before coding.
- `dependency-policy.md`: package dependency checking policy.
- `ai-request-routing.md`: AI payload selection and task routing.
- `io-reasoning-contracts.md`: AI input/output/reasoning contracts.
- `external-resource-adoption-contract.md`: optional contract for adopting
  AI-generated or human-sourced external content/data resources.
- Stack-specific architecture documents listed in
  `docs/collaboration/project-conventions.md`.

## Accepted Decisions

- `adr/0001-design-first-ai-request-routing.md`
- `adr/0002-input-output-reasoning-contracts.md`
- `adr/0003-ai-human-collaboration-governance.md`
- `adr/0004-human-readable-source-code-quality.md`
- `adr/0005-local-issue-planning.md`
- `adr/0006-prompt-instruction-change-control.md`
- `adr/0007-trunk-oriented-branching.md`
- `adr/0008-template-update-propagation.md`
- `adr/0009-bug-planning-and-ai-usage-records.md`
- `adr/0010-ai-failure-recovery-and-runner-cli-contract.md`
- `adr/0011-external-resource-adoption-contract.md`
- `adr/0012-rename-referee-to-adjudicator.md`
- `adr/0013-document-lifecycle-and-canonical-register.md`
- `adr/0014-delivery-and-subagent-selection.md`
- `adr/0015-runtime-routing-setup.md`
- `adr/0016-process-lessons-and-completion-review.md`
- `adr/0017-project-conventions-file.md`
- `adr/0018-agent-skills-for-on-demand-procedures.md`

## Remaining Technology Evaluation

See Current non-decisions in `docs/collaboration/project-conventions.md`.
