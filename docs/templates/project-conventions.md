# Project Conventions

Target-owned. Template sync must not overwrite this file.
Create or refresh from this form with
`scripts/copy-ai-collaboration-files.sh` (first adoption) or by copying this
file to `docs/collaboration/project-conventions.md`.

Put project-specific facts and extra rules here. Do not edit template context
files (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`,
`.grok/rules/*.md`, `.cursor/rules/*.mdc`) to store them; those files are
overwritten on template update.

Unfilled `<...>` placeholders in a section this task relies on must be set
before implementation.

## Project

- Name: `<PROJECT_NAME>`
- Domain: `<one-line domain summary>`
- Stack: `<FILL IN: e.g. backend language, frontend framework, package manager>`

## External resources (ports)

Represent these as ports before using concrete implementations.

- `<External data source A>`
- `<External data source B>`
- `<Primary datastore>`
- `<Secondary datastore, if any>`
- Settings storage and validation
- Secret storage
- Dependency policy checks
- `<Optional local runtime services, e.g. Docker-hosted DB>`
- `<External API / third-party service>`
- `<LLM or agent provider>`

## Runtime and trust boundaries

- The project is `<local-first | cloud-native | hybrid>`.
- `<Optional external system A>` is optional and replaceable.
- `<Primary datastore>` is the primary application database.
- `<Secondary datastore, if any>` is controlled by settings or feature flags.
- Database migrations use `<migration tool>`.

## Current non-decisions

List technology and design choices that are intentionally deferred to an ADR
rather than assumed by an agent.

- `<Provider/vendor choice A>`
- `<Data store or schema detail>`
- `<Model/embedding choice>`

## Stack-specific architecture documents

- `<e.g. React UI: docs/architecture/frontend-architecture.md>`

## Additional project rules

Add operating rules that apply only to this project. Keep them short. Do not
repeat template phase, approval, or dependency rules.
