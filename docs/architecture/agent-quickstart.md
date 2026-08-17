# Agent Quickstart

Use this as the first short entry point before coding.

## Session Entry

Each new LLM session starts without prior chat context.

1. Read the Adjudicator message for operating path, phase, spec or ADR, issue,
   and branch.
2. If resuming, read the cited handoff or trace before other documents.
3. Recover progress from repository artifacts, not from assumed chat history.
4. If path, phase, or authoritative scope is missing, stop after design intake
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

Output a compact design note with scope, omitted context, deterministic checks,
and why Feature Path or Architecture Path is unnecessary.

Do not use Fast Path when the task changes behavior, tests, architecture,
agent instructions, collaboration rules, privacy policy, or accepted specs.

### Feature Path

Use for Phase 1, 2, or 3 feature work.

Read:

1. this file.
2. `docs/at-tdd/process.md`.
3. `docs/collaboration/ai-human-scheme.md`.
4. `docs/architecture/ai-request-routing.md`.
5. target specification under `docs/specs/`.
6. area-specific architecture document.
7. `docs/architecture/implementation-readiness.md`.
8. `docs/architecture/io-reasoning-contracts.md` only when AI/model output is
   involved.
9. when the work touches **language surface, semantics, diagnostics, or
   official examples**: `docs/architecture/adjudicator-language-vision.md`,
   `docs/architecture/decision-themes/dec-0003-language-surface-and-physicist-first-dx.md`, and
   `docs/architecture/physicist-dx-harmony.md`.

Output the full `[DESIGN CHECK]` scaffold and execute only the requested phase.
For language-affecting work, the design note must state physicist-first
preservation or stop for Architecture approval (see language vision §6).

### Architecture Path

Use for ADRs, dependency boundaries, privacy-sensitive routing, prompt or
instruction changes, process changes, and conflicts between rules.

Read:

1. this file.
2. `docs/collaboration/ai-human-scheme.md`.
3. `docs/architecture/ai-request-routing.md`.
4. `docs/collaboration/model-tool-capability-matrix.md`.
5. `docs/collaboration/privacy-context-budget-policy.md`.
6. relevant ADRs and touched contract files.
7. `docs/architecture/io-reasoning-contracts.md` when AI/model output is
   involved.
8. for **language** ADRs or surface decisions:
   `docs/architecture/adjudicator-language-vision.md` and
   `docs/architecture/decision-themes/dec-0003-language-surface-and-physicist-first-dx.md`
   (plus `physicist-dx-harmony.md` when DX features are in scope).

Output the full `[DESIGN CHECK]` scaffold and stop for Adjudicator approval when a new
architecture or process decision is required.

## Design First

Every user request starts with a design note before tests or implementation.
Size the note to the selected operating path.

Before writing the design note, read
`docs/collaboration/independent-review-perspectives.md`. Select the applicable
lenses and carry their checklist into the design. Work is prepared on the
assumption that an independent reviewer will inspect those lenses later.

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
- applicable independent-review lenses and why they apply.

Fast Path may omit non-applicable VO/DTO, ports/adapters, and AI output
contract fields when it explicitly states that they are not involved.

## Phase Rule

Only execute the phase explicitly requested by the Adjudicator.

- Phase 1: failing tests only.
- Phase 2: minimum implementation only.
- Phase 3: refactor and reviewer empathy summary.

Phase transitions require Adjudicator approval. Do not start Phase 2 from
unreviewed Phase 1 tests.

### Optional user-triggered independent review loop

The user may explicitly trigger an independent-context review at any point,
for example with “独立コンテキストレビュー” or “レビュー・修正ループ”.
The agent then sends the current scoped artifacts to a fresh, read-only
reviewer context, records prioritized findings, applies only in-scope fixes,
and repeats with a new context until the user stops or no blocking findings
remain. The reviewer cannot edit files or grant approval. The next phase still
requires its own typed Adjudicator approval. Record each iteration under
`docs/collaboration/reviews/` and `docs/collaboration/traces/`; use the
template at `docs/templates/independent-context-review.md`, classify findings
against the perspectives ledger, and update it for new recurring concerns.

**Claude Code exception (non-normative pointer, ADR 0112 / ADR 0113):** for
named-Issue Feature Path work and for Issues named by an approved bounded
execution batch record, `CLAUDE.md` §"Claude Code Issue-Level and Work-Plan
Autonomy" supersedes this section. Claude Code should read that section before
concluding that a phase-transition approval is required. This paragraph does
not change the rule for `AGENTS.md`, Copilot, Codex, Grok, or Cursor, which
remain bound by the per-phase gate above.

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
- The MVP has no application datastore, no cloud DB, no QPU adapter, and no
  LLM provider inside the language runtime; those remain future optional
  ports.
- Runtime external I/O goes through ports only: `RngPort` (entropy for
  `measure` sampling), `SourcePort` (program loading from file or stdin), and
  `MeasureSinkPort` (measurement / diagnostic output). Secret storage is
  reserved and not required for MVP.

## Required Area Documents

- Test placement: `docs/architecture/testing-strategy.md`
- File placement: `docs/architecture/project-structure.md`
- Dependency policy: `docs/architecture/dependency-policy.md`
- AI input/output/reasoning: `docs/architecture/io-reasoning-contracts.md`
- AI-human collaboration: `docs/collaboration/ai-human-scheme.md`
- Language axioms (immutable): `docs/architecture/staqex-language-axioms.md`
- Adjudicator language vision (physicist-first):
  `docs/architecture/adjudicator-language-vision.md`
- Physicist × DX harmony: `docs/architecture/physicist-dx-harmony.md`
- Normative language spec: `docs/specs/staqex-language-specification.md` and
  grammar `docs/specs/grammar/staqex.ebnf`
- Surface lexicon and tokens: `docs/architecture/staqex-syntax-vocabulary.md`,
  `docs/architecture/staqex-token-specification.md`
- AST and type system: `docs/architecture/staqex-ast-design.md`,
  `docs/architecture/staqex-type-system.md`
- Runtime and backends: `docs/architecture/staqex-runtime-execution-model.md`,
  `docs/architecture/staqex-backend-targets.md`
- Spec verification: `docs/testing/staqex-spec-verification-protocol.md`
- Open / deferred capabilities: `docs/architecture/open-work-register.md`
- Full architecture document index: `docs/architecture/README.md`

## Stop Conditions

Stop and ask for Adjudicator decision or ADR when the task requires choosing:

- any application datastore, persistence engine, or schema; the MVP has none.
- an LLM provider, embedding model, or vector store inside the language
  runtime; the project boundaries exclude these.
- secret storage or a credential / vault layout; it is reserved and not
  required for MVP.
- a QPU provider SDK, credentials, network adapter, or retry policy;
  provider-neutral submit/job ports are shipped (ADR 0083), but real provider
  submission stays outside the Kernel.
- any other open technology choice recorded in
  `docs/architecture/README.md` "Remaining Technology Evaluation" or
  `docs/architecture/open-work-register.md`.
