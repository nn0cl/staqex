# Agent Operating Contract

This repository is prepared for multiple AI coding agents. All agents must use
the same workflow and architectural boundaries.

## Prime Directive

No implementation without a reviewed acceptance specification.

No phase skipping.

No hidden business logic in adapters.

## Expected Workflow

1. Read `docs/architecture/agent-quickstart.md`.
2. Select the smallest matching operating path from that quickstart:
   Fast Path, Feature Path, or Architecture Path.
3. Read only the documents required by the selected path.
4. Check `docs/architecture/implementation-readiness.md` before Phase 1, 2, or
   3 starts.
5. Output the path-appropriate design note.
6. Execute only the requested phase.
7. Report Red, Green, Refactor, or Fast Path status honestly.

## Session Entry

- Treat each new session as having no prior chat context.
- Before acting, recover state from repository artifacts: cited handoff or
  trace, spec or ADR, branch, and changed files — not chat memory. Read an
  ISSUE or work plan only when resuming that work or updating the ledger.
  Current rules come from policy documents, ADRs, and specifications, not
  from ISSUES or work plans.
- If the Adjudicator message and immediately preceding exchange lack an
  operating path, phase, or authoritative spec (or explicit Architecture Path
  scope), stop after design intake and ask.
- Read `docs/collaboration/project-conventions.md` when present. It holds
  project name, stack, ports, boundaries, non-decisions, and extra
  project-specific rules. Do not store those facts in this file. If the
  conventions file is missing, stop and ask to create it from
  `docs/templates/project-conventions.md`.
- If a relied-on contract, architecture, or conventions file still contains
  an unfilled `<...>` placeholder, stop after design intake and ask the
  Adjudicator to set the value. Do not treat placeholder text as a project
  name, stack, datastore, provider, or domain fact.
- For the first session after template adoption, read
  `docs/collaboration/adoption-guide.md` before changing target-owned files.
- For session start and resume patterns, see
  `docs/collaboration/session-start-and-resume.md`.
- After selecting an operating path, if
  `docs/collaboration/runtime-routing.toml` exists, apply its review and
  implementation isolation and optional model identifiers. If it is missing,
  keep capability-class routing on the host agent and do not invent model
  names. After first adoption, recommend
  `scripts/configure-ai-collaboration.sh` rather than guessing. These
  settings do not replace Adjudicator approval. See
  `docs/collaboration/runtime-routing.md`.

Relevant architecture documents:

- Quickstart: `docs/architecture/agent-quickstart.md`.
- File placement: `docs/architecture/project-structure.md`.
- Readiness checklist: `docs/architecture/implementation-readiness.md`.
- Test placement: `docs/architecture/testing-strategy.md`.
- Dependency policy: `docs/architecture/dependency-policy.md`.
- AI request routing: `docs/architecture/ai-request-routing.md`.
- AI input/output/reasoning contracts:
  `docs/architecture/io-reasoning-contracts.md`.
- AI-human collaboration scheme:
  `docs/collaboration/ai-human-scheme.md`.
- Source code quality for AI-TDD:
  `docs/collaboration/source-code-quality.md`.
- Definition of Done:
  `docs/collaboration/definition-of-done.md`.
- Model/tool routing:
  `docs/collaboration/model-tool-capability-matrix.md`.
- Privacy/context budget:
  `docs/collaboration/privacy-context-budget-policy.md`.
- Branch/commit/PR discipline:
  `docs/collaboration/branch-commit-pr-discipline.md`.
- Local issue planning:
  `docs/collaboration/local-issue-planning.md`.
- Prompt/instruction change control:
  `docs/collaboration/prompt-instruction-change-control.md`.
- Session start and resume:
  `docs/collaboration/session-start-and-resume.md`.
- Document lifecycle and citation direction:
  `docs/collaboration/document-lifecycle.md`.
- Project conventions (target-owned facts and extra rules):
  `docs/collaboration/project-conventions.md`.
- Runtime routing (optional target-owned settings):
  `docs/collaboration/runtime-routing.md`.
- Process lessons (meta-level, reused at design and implementation):
  `docs/collaboration/process-lessons.md`.
- Completion process review:
  `docs/collaboration/process-review.md`.
- On-demand procedures: `.agents/skills/`.
- Stack-specific architecture documents listed in
  `docs/collaboration/project-conventions.md`.

## Clean Architecture Dependency Rule

Allowed dependencies:

- Domain -> nothing project-specific.
- UseCase -> Domain and Ports.
- Adapter -> UseCase, Ports, framework SDKs, DB SDKs, file system, network.
- UI/Delivery -> application command/query contracts and presentation state.

Forbidden dependencies:

- Domain -> Adapter.
- Domain -> Framework.
- UseCase -> DB schema.
- UseCase -> migration files.
- UseCase -> UI component.
- UseCase -> framework request/command handler.
- UI -> DB.
- UI -> external provider SDK.
- Adapter -> business policy not present in UseCase or Domain.

## External Resources Must Be Ports

Represent every external resource listed in
`docs/collaboration/project-conventions.md` as a port before using a
concrete implementation. Do not add project ports to this file.

## Adjudicator Interaction

When a decision affects architecture, capture it as an ADR. When a decision is
unknown, list it in the path-appropriate design note as an ambiguity boundary.

Every request starts from design intake. Load
`.agents/skills/design-intake/SKILL.md` and output its `[DESIGN CHECK]`
scaffold for Feature Path and Architecture Path work. Fast Path uses the
compact note in that skill. Do not skip this step when the host does not
auto-discover the skill directory.

## Approval Model

Treat these approvals as distinct decisions. A short `承認`/`approved` may be
accepted for the single approval target that is uniquely established by the
immediately preceding exchange; otherwise require the typed approval form.
Never infer a later approval from an earlier approval:

- `Scope approval`: permission to investigate or design the named scope.
- `Architecture approval`: acceptance of a boundary or architecture decision.
- `Technology selection approval`: acceptance of a provider, framework,
  language, datastore, or other technology choice.
- `Phase approval`: permission to execute the named AT-TDD or process phase.
- `Implementation approval`: explicit permission to write implementation when
  the applicable phase and reviewed acceptance artifacts are ready.

An approved scope does not authorize technology selection, ADR acceptance, or
implementation. Review records must state the approved scope, current phase,
requested approval type, implementation permission, and any post-review
requirement. A proposed ADR is a design artifact, not implementation approval.

Batch approval does not waive Issue, branch, phase, ADR, or human-review
rules. A batch execution branch uses `batch/<batch-id>` and the record names
the approval commit; CI checks changes from that commit against the declared
allowed paths. CI success is not Adjudicator approval. When writing or
executing a bounded batch, follow `.agents/skills/execution-batch/SKILL.md`.

When handing off or stopping before completion, follow
`.agents/skills/agent-handoff/SKILL.md`. When asking the Adjudicator for
approval, follow `.agents/skills/adjudicator-review/SKILL.md`. When an agent
review packet is required and review isolation is `same_context` (or routing
is missing), follow `.agents/skills/same-context-review/SKILL.md`.

Generated source code must minimize human cognitive load. Prefer clear
responsibility boundaries, small functions, straightforward names, and
reviewable tests. Do not compress implementation into dense code just to be
minimal.

Before reporting completion, check `docs/collaboration/definition-of-done.md`.
When the trace policy requires a trace, follow
`.agents/skills/ai-work-trace/SKILL.md`. Use feature-unit branches for feature
work. For feature work, identify local issue or GitHub issue dependencies
before creating the branch.

When an agent review packet is produced, or at the next design intake and
before implementation, follow `.agents/skills/process-lessons/SKILL.md`.
When marking a local issue or work plan `done`, follow
`.agents/skills/process-review/SKILL.md`.
