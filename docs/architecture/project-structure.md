# Project Structure

This document defines the target repository shape for implementation. Create
directories only when a Phase 1 or Phase 2 task needs them.

## Target Layout

This document is template-owned. Put the actual layout in target-owned
`docs/collaboration/project-conventions.md`, or in a project-specific document
linked there. Do not replace this shared document with target facts.
The following is an illustrative layout, not unfilled project configuration:

```text
.
├── docs/
├── frontend-example/
│   └── src/
│       ├── app/
│       ├── features/
│       ├── entities/
│       └── shared/
└── backend-example/
    └── src/
        ├── delivery/            # HTTP/RPC handlers, CLI entry points, UI glue
        ├── core/
        │   ├── domain/
        │   ├── application/
        │   └── ports/
        └── adapters/
            ├── persistence/
            ├── settings/
            └── external-service-example/
```

## Ownership

The frontend owns UI rendering and presentation state.

Domain modules own pure domain types and domain behavior.

Application modules own use cases and application
orchestration.

Ports own interfaces for external resources.

Adapters own concrete implementations of ports.

Delivery owns request/command handlers and DTO
conversion.

## Forbidden Placement

Do not put business rules in:

- UI component files.
- delivery/request handlers.
- adapters.
- persistence structs.
- provider SDK clients.

Do not put framework, file-system, network, or database imports in:

- `core/domain/`.
- `core/application/`, except through core-owned ports.

## Creation Rule

Create the smallest directory and module set needed by the current AT-TDD phase.
Do not scaffold unused adapters, providers, or UI features.

Smallest does not mean densest. Split files and modules when it reduces human
review cost or separates architectural responsibilities. Do not split only to
create speculative layers.
