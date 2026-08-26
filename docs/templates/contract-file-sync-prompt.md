# Project Conventions Migration Prompt

Use this once when a template sync is about to overwrite customized context
files (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`,
`.grok/rules/*.md`, `.cursor/rules/*.mdc`) and project facts still live in
those files.

Do not merge project facts back into the template context files. Move them
into `docs/collaboration/project-conventions.md`.

## Inputs

- Target repository path:
- Context file that still holds project facts:
- Template's new content of that file (what overwrite will apply):

## Steps

1. Read the target's current context file and list adopter facts: project
   name, domain, stack, ports, runtime boundaries, non-decisions, extra
   rules, and stack-specific architecture document paths.
2. Read `docs/collaboration/project-conventions.md` if it exists, or create
   it from `docs/templates/project-conventions.md`.
3. Write those facts into the conventions file. Replace unfilled `<...>`
   placeholders the facts cover. Do not copy template phase or approval
   rules into the conventions file.
4. Leave the context file to be overwritten by the template. Do not re-apply
   project facts onto `AGENTS.md` or `CLAUDE.md`.
5. Stop for Adjudicator review of the conventions file before the sync PR
   merges.

## Output

- Updated `docs/collaboration/project-conventions.md`
- List of facts moved
- List of facts that still need Adjudicator input
