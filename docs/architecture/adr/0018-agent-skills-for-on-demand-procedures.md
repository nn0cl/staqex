# ADR 0018: Agent Skills for On-Demand Procedures

## Status

Accepted

## Context

Contract files currently embed both standing rules (always in force) and
task-triggered procedures (design-intake scaffold, completion process review,
same-context review, handoff). Several coding agents now load
[Agent Skills](https://agentskills.io/specification) (`SKILL.md`) on demand.
Keeping those procedures only in always-loaded files duplicates checklists
across AGENTS.md, CLAUDE.md, Copilot, Grok, and Cursor, and spends context
on work the current task may not need.

Vendor skill directories differ (`.claude/skills/`, `.cursor/skills/`,
`.github/skills/`, `.grok/skills/`). A portable overlap is `.agents/skills/`,
which Codex, Cursor, Copilot, Gemini CLI, and Grok Build scan. Claude Code's
documented project path is `.claude/skills/`; a contract-file path remains
the portable discovery mechanism when a host does not auto-scan
`.agents/skills/`.

LISS-0018 showed that removing an explicit Claude design-check obligation
causes the scaffold to be skipped. The obligation must stay in the
always-loaded contract even if the scaffold body moves.

## Decision

1. On-demand procedures live in `.agents/skills/<name>/SKILL.md`. Frontmatter
   uses only the Agent Skills fields `name` and `description`. Do not add
   vendor-only frontmatter.
2. Skills wrap existing Canonical documents and templates; they do not
   replace them. The set is `design-intake`, `process-review`,
   `same-context-review`, `agent-handoff`, `process-lessons`,
   `adjudicator-review`, `ai-work-trace`, and `execution-batch`.
3. The `[DESIGN CHECK]` scaffold body moves to the design-intake skill.
   Contract files keep the requirement to output that scaffold for Feature
   Path and Architecture Path work, and name the skill path.
4. Standing rules stay in the contract files: Prime Directive, Session Entry,
   typed Approval Model, ports, phase gates, and the bounded-batch safety
   rules (`batch/<batch-id>`, CI is not Adjudicator approval).
5. Copy and later sync treat `.agents/skills/` as template-authoritative.
   Do not ship duplicate trees under `.claude/skills/`, `.cursor/skills/`,
   `.github/skills/`, or `.grok/skills/`.
6. These skill files are agent operating contract files. Changes require
   Adjudicator review and a trace, same as other contract files.

Follow-up work: `docs/issues/LISS-0025-agent-skills-procedures.md`,
`docs/issues/LISS-0026-more-agent-skills.md`.

## Consequences

Positive:

- Task-triggered checklists load when the task matches.
- One scaffold body instead of paraphrases in five contract surfaces.
- Canonical policy documents remain the source of truth.

Negative:

- A host that neither auto-discovers `.agents/skills/` nor follows the
  contract-file path can skip a procedure. The obligation sentence in the
  contract files is the mitigation, not a second copy of the scaffold.
- Claude Code project auto-discovery still prefers `.claude/skills/`.
  Agents in that host must follow the path in `CLAUDE.md`.

## Changed context files

- `.agents/skills/*/SKILL.md`
- `AGENTS.md`
- `CLAUDE.md`
- `.github/copilot-instructions.md`
- `.grok/rules/*.md`
- `.cursor/rules/*.mdc`
- `docs/collaboration/prompt-instruction-change-control.md`
- `docs/collaboration/adoption-guide.md`
- `scripts/lib/collaboration-template-paths.sh`
- `.github/workflows/ci.yml`

## References

- `docs/issues/LISS-0025-agent-skills-procedures.md`
- `docs/issues/LISS-0026-more-agent-skills.md`
- `docs/architecture/adr/0006-prompt-instruction-change-control.md`
- Agent Skills specification: https://agentskills.io/specification
