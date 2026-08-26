# AT-TDD Process

This project uses **AT-TDD** as a repository-local name for an
**ATDD + TDD hybrid workflow**.

AT-TDD is not treated here as a separate industry-standard method name. In this
template, it means:

- acceptance specifications drive the first tests.
- reviewed failing tests drive the minimum implementation.
- refactoring happens only after verified Green.
- phase transitions require human Adjudicator approval.

The workflow combines:

- **ATDD**: EARS/Gherkin acceptance behavior, external dependencies, data
  ownership, and out-of-scope behavior are clarified before implementation.
- **TDD**: Red, Green, and Refactor phases are kept separate and verified by
  deterministic tools when available.

## Inputs

Each feature starts with an EARS and/or Gherkin specification.

The specification must identify:

- Preconditions.
- Trigger.
- Expected observable result.
- External dependencies.
- Data ownership.
- Out-of-scope behavior.

## Phase 0: Design Intake

Every user request starts with design intake before tests, implementation,
migrations, or UI changes. The intake may be compact for Fast Path work and
complete for Feature Path or Architecture Path work.

Purpose: select only the necessary context, identify lightweight design
decisions, and route work to the appropriate model, assistant, or deterministic
tool.

Required output for Feature Path and Architecture Path:

- target behavior.
- local issue or work plan reference when applicable.
- phase to execute next.
- context to include in AI requests.
- context to omit from AI requests.
- value object or DTO candidates that are clear enough to define now.
- ports and adapters involved.
- suggested task routing.
- input, output, and reasoning evidence contracts when AI or model output is
  involved.
- ambiguity boundaries.
- Adjudicator decision needed or not needed.

Fast Path output may be a compact design note that states:

- target scope.
- context included and omitted.
- deterministic checks to run.
- why no feature phase, architecture decision, VO/DTO, port, adapter, or AI
  output contract is involved.

Rules:

- Do not include the whole repository, full source documents, full private
  data exports, or secrets when a smaller payload is enough.
- Lightweight value objects may be named during design, but implementation
  still waits for the requested AT-TDD phase.
- AI output must be treated as untrusted until it satisfies the declared output
  and reasoning evidence contracts.
- Deterministic tools should be used instead of AI for formatting, linting,
  dependency checks, migration ordering checks, and test execution.
- Phase transitions require Adjudicator approval.

## Mandatory `[DESIGN CHECK]`

Before Feature Path or Architecture Path work, agents load
`.agents/skills/design-intake/SKILL.md` and output its `[DESIGN CHECK]`
scaffold. For Fast Path work, agents may output the compact design note in
that skill instead of the full scaffold.

The design check is concise, auditable decision metadata. It must not expose
hidden chain-of-thought. Scope approval, architecture approval, technology
selection approval, phase approval, and implementation approval remain
separate decisions. A proposed ADR does not authorize implementation.

## Phase 1: Red

Purpose: convert acceptance criteria into failing tests.

Allowed:

- Test files.
- Test fixtures.
- Test-only interface declarations when the language requires a compile target
  for mock types and the Adjudicator has accepted this convention.

Forbidden:

- Production implementation.
- Database migrations.
- UI components.
- Framework controllers.
- Real network, file-system, or external provider calls.

Red may mean:

- Compile failure because production types do not exist yet.
- Failing assertions against intentionally empty skeletons.

Phase 1 exit gate:

- The Adjudicator reviews and accepts the failing tests before Phase 2 starts.

## Phase 2: Green

Purpose: pass reviewed tests with the minimum production code.

Allowed:

- Domain objects required by tests.
- Use cases required by tests.
- Ports required by tests.
- Minimal adapters only when the reviewed test requires an integration boundary.

Forbidden:

- Changing the reviewed tests to pass.
- Adding speculative behavior.
- Adding persistence, UI, or provider details not required by tests.

Phase 2 exit gate:

- Deterministic verification is run when available.
- The agent reports whether reviewed tests were changed. They should not be.

## Phase 3: Refactor

Purpose: improve design while preserving test behavior.

Allowed:

- Rename for clarity.
- Extract domain concepts.
- Move logic out of adapters.
- Reduce duplication.
- Improve test readability without changing assertions.

Required final output:

```markdown
### 変更の要約 (PR Summary)
- **何を目的として何を変更したか**: ...

### 残存リスク・検証の溝 (Verification Gap)
- **AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**: ...
- **人間がコードレビューで重点的に見るべきポイント**: ...
```
