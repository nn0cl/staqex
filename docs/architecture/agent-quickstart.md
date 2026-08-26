# Agent Quickstart

Use this as the first short entry point before coding.

## Session Entry

Each new LLM session starts without prior chat context.

1. Read the Adjudicator message for operating path, phase, spec or ADR, and
   branch. Read a cited ISSUE or work plan only when resuming that work.
2. If resuming, read the cited handoff or trace before other documents.
3. Recover progress from repository artifacts, not from assumed chat history.
   Current rules come from policy documents, ADRs, and specifications, not
   from ISSUES or work plans.
4. Read `docs/collaboration/project-conventions.md` when present. If it is
   missing, stop and ask to create it from
   `docs/templates/project-conventions.md`.
5. If `docs/collaboration/runtime-routing.toml` exists, apply it when routing
   review or implementation. If it is missing, keep capability-class routing
   on the host agent and do not invent model names. See
   `docs/collaboration/runtime-routing.md`.
6. If path, phase, or authoritative scope is missing, stop after design intake
   and ask the Adjudicator.

For Adjudicator checklists and resume examples, see
`docs/collaboration/session-start-and-resume.md`.

## Operating Paths

Select the smallest path that safely fits the request.

### Fast Path

Use for mechanical, local, and low-risk work such as formatting, typo fixes,
file moves, script syntax checks, README clarifications, or deterministic
verification.

Read:

1. this file.
2. directly touched files.
3. `docs/collaboration/definition-of-done.md` before final reporting.

Load `.agents/skills/design-intake/SKILL.md` and output its compact design
note with scope, omitted context, deterministic checks, and why Feature Path
or Architecture Path is unnecessary.

Do not use Fast Path when the task changes behavior, tests, architecture,
agent instructions, collaboration rules, privacy policy, or accepted specs.

### Feature Path

Use for Phase 1, 2, or 3 feature work.

Read:

1. this file.
2. `docs/at-tdd/process.md`.
3. `docs/collaboration/ai-human-scheme.md`.
4. `docs/architecture/ai-request-routing.md`.
5. target specification under `docs/specs/`. Do not start from an ISSUE or
   work plan unless the Adjudicator cited it for resume.
6. area-specific architecture document.
7. `docs/architecture/implementation-readiness.md`.
8. `docs/architecture/io-reasoning-contracts.md` only when AI/model output is
   involved.

Load `.agents/skills/design-intake/SKILL.md` and output the full
`[DESIGN CHECK]` scaffold. Execute only the requested phase.

### Architecture Path

Use for ADRs, dependency boundaries, privacy-sensitive routing, prompt or
instruction changes, process changes, and conflicts between rules.

Read:

1. this file.
2. `docs/collaboration/ai-human-scheme.md`.
3. `docs/architecture/ai-request-routing.md`.
4. `docs/collaboration/model-tool-capability-matrix.md`.
5. `docs/collaboration/runtime-routing.md` when review or implementation
   routing is involved.
6. `.agents/skills/process-lessons/SKILL.md` when design or implementation
   routing is involved.
7. `docs/collaboration/process-review.md` when closing an issue or work plan.
8. `docs/collaboration/privacy-context-budget-policy.md`.
9. relevant ADRs and touched contract files. ADRs may cite ISSUES or work
   plans as evidence; do not treat those citations as the next required read.
10. `docs/architecture/io-reasoning-contracts.md` when AI/model output is
   involved.

Load `.agents/skills/design-intake/SKILL.md` and output the full
`[DESIGN CHECK]` scaffold. Stop for Adjudicator approval when a new
architecture or process decision is required.

## Design First

Every user request starts with a design note before tests or implementation.
Size the note to the selected operating path.

The design note selects:

- target behavior.
- next AT-TDD phase.
- context to include in AI requests.
- context to omit from AI requests.
- lightweight VO or DTO candidates.
- ports and adapters involved.
- task routing to model, assistant, or deterministic tool.
- input, output, and reasoning evidence contracts when AI or model output is
  involved.

Fast Path may omit non-applicable VO/DTO, ports/adapters, and AI output
contract fields when it explicitly states that they are not involved.

## Phase Rule

Only execute the phase explicitly requested by the Adjudicator.

- Phase 1: failing tests only.
- Phase 2: minimum implementation only.
- Phase 3: refactor and reviewer empathy summary.

Phase transitions require Adjudicator approval. Do not start Phase 2 from
unreviewed Phase 1 tests.

Approval is typed and scoped. Scope approval authorizes investigation or
design only; architecture, technology selection, phase, and implementation
approval must be explicit. A proposed ADR is not implementation authorization.

Return to Architecture Path when a change introduces a subsystem, language,
framework, datastore, concurrency or transaction boundary, authentication or
authorization boundary, deployment boundary, or changes the premise of an
accepted ADR or approved logic.

## Bug Triage

Bug fixes follow the same phase rule as feature work. A minor bug may omit a
separate local issue or work plan only when it is size `S`, within already
approved scope, clear from existing behavior or specification, low risk, and
verified in the same attempt.

Omitting a separate planning artifact does not permit skipping Phase 1, Phase
2, Phase 3, deterministic verification, or Adjudicator review gates.

When a bug is size `M` or larger, needs a second execution attempt, changes
boundaries, or remains ambiguous, record it in a local issue or active work
plan before continuing.

## Core Boundaries

- Domain has no UI framework, DB, file-system, network, or third-party
  provider dependency.
- Use cases depend on domain and ports.
- Adapters implement ports.
- Delivery handlers (UI components, HTTP/RPC handlers, CLI entry points) are
  thin and call use cases only.
- Datastore and runtime facts: `docs/collaboration/project-conventions.md`.

## Required Area Documents

- Test placement: `docs/architecture/testing-strategy.md`
- File placement: `docs/architecture/project-structure.md`
- Dependency policy: `docs/architecture/dependency-policy.md`
- AI input/output/reasoning: `docs/architecture/io-reasoning-contracts.md`
- AI-human collaboration: `docs/collaboration/ai-human-scheme.md`
- Project conventions: `docs/collaboration/project-conventions.md`
- Stack-specific architecture documents listed in that conventions file

## Stop Conditions

Stop and ask for Adjudicator decision or ADR when the task requires choosing:

- a current non-decision listed in `docs/collaboration/project-conventions.md`.
- a new technology, provider, datastore, or schema beyond that file.
