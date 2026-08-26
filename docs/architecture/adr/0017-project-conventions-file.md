# ADR 0017: Project Conventions File and Overwritable Context Files

## Status

Accepted

## Context

Template context files (`AGENTS.md`, `CLAUDE.md`, Copilot instructions, Grok
rules, Cursor rules) used to carry adopter-filled placeholders. Sync treated
them as Tier 2 so a template update would not overwrite project name, stack,
ports, or extra rules. That blocked clean template-authoritative updates of
the shared contract. Adopters who added project rules inside those files
could not take a later template revision without an AI merge.

Project-specific facts and extra rules belong in a file the template does not
author. Shared operating rules belong in files the template may overwrite.

## Decision

1. Target-owned `docs/collaboration/project-conventions.md` holds project
   name, domain, stack, ports, runtime boundaries, non-decisions,
   stack-specific architecture document list, and additional project rules.
   Copy creates it from `docs/templates/project-conventions.md` when missing.
   Copy and update never overwrite an existing live file.
2. Template context files are template-authoritative. On later sync they are
   overwritten like other process files. They instruct agents to read
   `docs/collaboration/project-conventions.md` and not to store project facts
   in the context files.
3. If the live conventions file is missing, or a relied-on section still has
   unfilled `<...>` placeholders, agents stop after design intake and ask
   they be set.
4. Existing adopters who customized context files move those facts into
   `docs/collaboration/project-conventions.md` before merging a sync that
   overwrites the context files. `docs/templates/contract-file-sync-prompt.md`
   is the migration aid for that one-time extraction.
5. ADR 0008's Tier 2 persona-file exception is retired. Deletion restore
   prompts and `.collaboration-template-ignore` remain.

## Consequences

Positive:

- Template contract updates apply without merging project facts.
- Project rules stay in one file agents are required to read.
- Placeholder filling happens in one target-owned file.

Negative:

- The first sync after this change overwrites customized context files.
  Adopters must migrate facts first, or they lose them in the sync PR.
- Two files must stay aligned in the agent's read order: the template
  contract and the conventions file.

## Changed context files

- `AGENTS.md`
- `CLAUDE.md`
- `.github/copilot-instructions.md`
- `.grok/rules/*.md`
- `.cursor/rules/*.mdc`
- `docs/architecture/agent-quickstart.md`
- `docs/architecture/README.md`
- `docs/collaboration/adoption-guide.md`
- `scripts/copy-ai-collaboration-files.sh`
- `scripts/update-ai-collaboration-files.sh`
- `scripts/lib/collaboration-template-paths.sh`

## References

- `docs/issues/LISS-0022-project-conventions.md`
- `docs/templates/project-conventions.md`
- `docs/architecture/adr/0008-template-update-propagation.md`
