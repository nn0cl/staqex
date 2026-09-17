# Testing Strategy

Testing follows AT-TDD phase gates.

This file is template-owned. Actual test locations, selected frameworks,
blocking commands, required environments and approved exclusions belong in
target-owned `docs/collaboration/project-conventions.md` or documents linked
there. Do not store adopter facts in this shared file. Evidence requirements
are defined in `docs/collaboration/verification-policy.md`.

## Test Levels

### Acceptance Tests

Purpose:

- prove Gherkin scenarios.
- drive Phase 1 Red.

Placement:

- Use the project-conventions locations for application and UI acceptance tests.
- E2E tests only after a runnable shell/deployment exists.

### Domain Unit Tests

Purpose:

- prove pure domain behavior.

Rules:

- no mocks needed for pure logic.
- no framework, DB, network, file-system, or SDK imports.

### Application Use Case Tests

Purpose:

- prove orchestration through ports.

Rules:

- use fake or mock port implementations.
- assert outputs and port interactions specified by Gherkin.
- no real adapters.

### Adapter Integration Tests

Purpose:

- prove concrete provider integration.

Rules:

- must be explicitly requested or covered by an ADR.
- must be separable from normal unit tests.
- must not be required for Phase 1 Red of core behavior.

### Dependency Policy Checks

Purpose:

- catch package dependency, license, advisory, and import-boundary drift.

Rules:

- run the project's chosen dependency-policy tool(s) once configured (see
  `docs/architecture/dependency-policy.md`).
- do not treat these checks as substitutes for Clean Architecture review.

### Front-End Tests

Purpose:

- prove UI behavior and user interaction.

Rules:

- Use the selected UI test framework recorded in project conventions.
- mock the shared transport/API client boundary.
- do not mock random request strings inside components.

### E2E Tests

Purpose:

- prove the assembled app flow.

Rules:

- Use the selected E2E framework after the runnable shell/deployment exists.
- do not depend on real external providers unless the test is explicitly
  marked as manual or integration.

## Phase Mapping

Phase 1 Red:

- add failing tests only.
- prefer use-case tests for core behavior.
- prefer UI tests for presentation behavior.

Phase 2 Green:

- add minimum implementation.
- do not edit reviewed tests to pass.

Phase 3 Refactor:

- improve structure.
- keep behavior and assertions stable.

## Mocking Rule

Mock ports, not concrete providers.

Examples:

- mock the external-service port, not the SDK client.
- mock the search port, not a vector DB client.
- mock the knowledge-source port, not an HTTP endpoint.
