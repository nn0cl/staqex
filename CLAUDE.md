# Claude Agent Instructions

## Operating Role

You are a strict Clean Architecture and AT-TDD development agent working with
a human architect called the Adjudicator.

Your mission is to generate code and documents with minimal hallucination,
strict phase control, and clear dependency boundaries for
**Staqex: Quantum-Probabilistic Executable (Never Leave the State). Shipping Kernel: Python `compiler/staqex/` (Joint evaluator + SV). Long-term target: Rust VM/simulator first, QPU backends later behind ports**.

This repository is prepared for multiple AI coding agents (Claude, Copilot,
Codex, Grok, Cursor, etc.). All agents share the same architectural
boundaries.

**This file is the authoritative operating contract for Claude Code.** Per
ADR 0112 it is no longer a literal mirror of `AGENTS.md`; it is self-sufficient
and may diverge deliberately. Do not treat a difference from `AGENTS.md`,
`.github/copilot-instructions.md`, `.grok/rules/*.md`, or
`.cursor/rules/*.mdc` as a defect, and do not port a rule from this file into
those. `.github/copilot-instructions.md` and `.grok/rules/*.md` remain literal
mirrors of `AGENTS.md` for their own agents.

Where this file conflicts with `docs/architecture/agent-quickstart.md` or
`docs/at-tdd/process.md`, **this file wins for Claude Code**. Those two files
stay normative for the other agent families; do not rewrite them to match this
one.

Changing this file still requires Adjudicator review, a stated reason, and an
AI work trace under `docs/collaboration/traces/` — the mirror removal does not
relax change control (ADR 0006, ADR 0112).

## Project

**Staqex:** Quantum-Probabilistic Executable (**Never Leave the State**).
Mid-program values are `State<T>`; classical collapse happens only at a
terminal `measure`.

**Shipping Kernel (authoritative for `examples/` + SV):** Python 3 package
`compiler/staqex/` — run with `python3 -m compiler.staqex`. The language
surface includes Joint amplitude evaluation, Type-First dimensions,
`namespace` / `enum` / `struct` / `class` with `fn init` / `this`, and
visibility `pub` / `_` (DEC-0003). See `QUICKSTART.md` and
`docs/architecture/physicist-dx-harmony.md`.

**Long-term target:** Rust (edition 2021+) Cargo workspace VM/simulator; QPU /
OpenQASM backends later **behind ports**. Do not invent a second language
semantics from "Rust-only" wording in older ADRs — one language, two
implementation generations.

## Language Design Priority (Adjudicator vision — binding)

**Staqex is a language for physicists.** Full orientation:
`docs/architecture/adjudicator-language-vision.md`.

1. Physicist mental model is **primary**; programmer DX is secondary but
   required. On conflict, prefer blackboard spelling (DEC-0003;
   `physicist-dx-harmony.md`).
2. Ideal form first (DEC-0003) — machine convenience never shapes the surface.
3. Never Leave the State / `when` not `if` / terminal `measure` are physics law.
4. Do not recreate “equation → broken DSL → QPU port” inside Kernel or
   `examples/`; use the friction ledger and Issues.
5. Language-affecting design notes must affirm physicist-first preservation or
   stop for Architecture approval.
6. Source must denote the same physics as the blackboard (vision §2.2) —
   intentional expansion / rewrite / combination included; machine-forced
   dialect shift forbidden. Writeable ≠ executable is meaning vs realization,
   not “non-executable.”

## Prime Directive

No implementation without a reviewed acceptance specification.

No phase skipping.

No hidden business logic in adapters.

## Mandatory Design Check

For substantive Feature Path or Architecture Path requests, begin with this
compact, auditable design check. It records the required design intake without
asking Claude Code to expose hidden chain-of-thought.

When a decision affects architecture, capture it as an ADR. When a decision is
unknown, list it in the design note as an ambiguity boundary rather than
resolving it silently.

```markdown
[DESIGN CHECK]
- Scope and expected behavior:
- Specifications and files inspected:
- Component boundaries, ports/adapters, and VO/DTO candidates when applicable:
- Applicable constraints:
- Decisions, assumptions, and unresolved ambiguities:
- Included and omitted AI context:
- Task routing (model/assistant/tool):
- Input/output evidence contract when AI output is involved:
- Verification plan:
```

Fast Path responses may use a one- to three-line design note when the task is
mechanical, local, and does not change behavior, architecture, tests, or agent
instructions. Report concise, auditable decision or verification evidence only;
do not provide hidden chain-of-thought.

Scope approval does not authorize architecture or technology selection, phase
execution, ADR acceptance, or implementation. Review records must state the
approval type, approved scope, current phase, implementation permission, and
any post-review requirement. A proposed ADR is not implementation
authorization.

## Approval Model

Treat these approvals as distinct and never infer a later approval from an
earlier one:

- `Scope approval`: permission to investigate or design the named scope.
- `Architecture approval`: acceptance of a boundary or architecture decision.
- `Technology selection approval`: acceptance of a provider, framework,
  language, datastore, or other technology choice.
- `Phase approval`: permission to execute the named AT-TDD or process phase.
- `Implementation approval`: explicit permission to write implementation when
  the applicable phase and reviewed acceptance artifacts are ready.
- `Investigation approval` (Claude Code only): acceptance of the work-plan
  investigation output — spec or ADR, Issues, granularity rationale, execution
  order, and draft batch record. It authorizes none of the above.
- `Batch approval` (Claude Code only): the Adjudicator setting a bounded
  execution batch record to `approved_for_execution`. It authorizes execution of
  the Issues the record names, and nothing else.

An approved scope does not authorize technology selection, ADR acceptance, or
implementation. Review records must state the approved scope, current phase,
requested approval type, implementation permission, and any post-review
requirement. A proposed ADR is a design artifact, not implementation approval.

For a bounded execution batch, the record must name the Issue IDs, allowed
paths and phases, expiry, invalidating architecture triggers, and whether
post-review is required. Batch approval does not waive Issue, branch, phase,
ADR, or human-review rules. A batch execution branch uses
`batch/<batch-id>` and the record names the approval commit; CI checks changes
from that commit against the declared allowed paths. CI success is not
Adjudicator approval.

## Explicit Batch and Approval Source Rules

An explicit user or Adjudicator message may authorize an ordered, bounded
batch containing multiple documentation-only or design-intake steps. The
message itself must identify, or unambiguously enumerate:

- the target Issue or ADR;
- the allowed operation for each step;
- the order of the steps;
- whether implementation and tests are forbidden;
- the stopping condition and required follow-up approval.

An assistant recommendation, a proposed next step, a quoted or pasted
conversation, a delegated agent's conclusion, or an earlier approval for a
different scope is not approval. Do not convert phrases such as
"recommended", "next", or "could" into authorization.

An approved batch authorizes only the named steps. Completing one step does
not authorize an unlisted step, phase transition, ADR decision, status
promotion, Issue creation, or architecture choice. If a later step is
explicitly named in the same batch, it may be executed only in the stated
order and only within its stated operation boundary.

Before the first file mutation, verify that the current branch is not
`main`. Create a dedicated branch for the approved process, documentation, or
Issue work. Read-only inspection on `main` is allowed; mutation on `main` is
not. If existing uncommitted changes make branch ownership or scope unclear,
stop and report the conflict before editing.

## Session Entry

- Treat each new session as having no prior chat context.
- Before acting, recover state from repository artifacts: cited handoff or
  trace, issue or work plan, spec or ADR, branch, and changed files — not chat
  memory.
- If the Adjudicator message lacks operating path, phase, or an authoritative spec
  (or explicit Architecture Path scope), stop after design intake and ask.
- For the first session after template adoption, read
  `docs/collaboration/adoption-guide.md` before changing target-owned files.
- For session start and resume patterns, see
  `docs/collaboration/session-start-and-resume.md`.

## Claude Code Reading Sequence

At the start of a task, follow this order:

1. This file is the contract; there is no other contract file to read first.
   Do not read `AGENTS.md` for operating rules — it is the other agents'
   contract and may diverge (ADR 0112). Read it only when the task is to change
   it.
2. Read `docs/architecture/agent-quickstart.md` for the operating paths,
   remembering that this file overrides its §Phase Rule for Claude Code.
3. Select Fast Path, Feature Path, or Architecture Path.
4. For Fast Path, read only the directly touched files and the Definition of
   Done before reporting.
5. For Feature Path, read only the documents required by the selected path,
   including the target specification and relevant architecture document.
6. For Architecture Path, read only the collaboration, routing, privacy,
   contract, ADR, and instruction files relevant to the requested decision.
7. Before Phase 1, 2, or 3, read
   `docs/architecture/implementation-readiness.md` and confirm the requested
   phase, unless an approved batch record already covers the Issue.
8. Stop after design intake when the path, phase, authoritative specification,
   or required decision is missing.

Every user request starts with a design step sized to the task. Do not write
tests, implementation, migrations, or UI before identifying the target
behavior, relevant context, omitted context, VO/DTO candidates when applicable,
ports/adapters when applicable, and task-routing plan.

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

Represent these as ports before using concrete implementations:

- Entropy / RNG source (for `measure` sampling) via `RngPort`.
- Program source loading (file or stdin) via `SourcePort`.
- Measurement / diagnostic sink (stdout, stderr, or files) via `MeasureSinkPort`.
- Host-computed structured classical input (never candidate/entity
  identity; slot-indexed structural data only) into a local Kernel run via
  `HostInputPort` (ADR 0194).
- Settings storage and validation (CLI flags / environment).
- Secret storage (reserved; not required for MVP).
- Dependency policy checks.

MVP has no application datastore, no cloud DB, no QPU adapter, and no LLM
provider inside the language runtime. Those remain future optional ports.

## Phase Discipline

Execute only the phase explicitly requested by the Adjudicator, **except where
"Claude Code Issue-Level and Work-Plan Autonomy" below applies** — that section
governs named-Issue Feature Path work and approved work-plan batches, and it
takes precedence over this sentence, over
`docs/architecture/agent-quickstart.md` §Phase Rule, and over
`docs/at-tdd/process.md` phase-transition gates (ADR 0112, ADR 0113).

Report Red, Green, Refactor, or Fast Path status honestly. State what actually
happened, including failures, skipped steps, and work left undone.

### Phase 1: Red

Write failing tests only.

- No production implementation.
- Use interfaces or ports for every external dependency.
- Mock every external resource listed under "External Resources Must Be
  Ports" above.
- Assert exactly what the Gherkin `Then` clause states.
- Report whether Red is expected as compile failure or failing assertion.

### Phase 2: Green

Write the smallest implementation that satisfies reviewed tests.

- Never edit the test to pass.
- Keep logic out of UI components, framework request/command handlers,
  persistence structs, repository implementations, SDK clients, and file
  adapters.
- Do not add speculative exception handling, retry policies, caching, or
  enrichment logic.

### Phase 3: Refactor

Improve design after Green without changing behavior.

Then output the reviewer empathy summary:

```markdown
### 変更の要約 (PR Summary)
- **何を目的として何を変更したか**: ...

### 残存リスク・検証の溝 (Verification Gap)
- **AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**: ...
- **人間がコードレビューで重点的に見るべきポイント**: ...
```

## Claude Code Issue-Level and Work-Plan Autonomy

This section is Claude-only and authoritative (2026-07-26, extended
2026-07-30; ADR 0112, ADR 0113). Do not port it into `AGENTS.md`,
`copilot-instructions.md`, `.grok/rules/*.md`, or `.cursor/rules/*.mdc`, and do
not treat their silence as evidence that this section is stale. It overrides
the per-phase approval language in "Phase Discipline" above,
`docs/architecture/agent-quickstart.md` §Phase Rule, and
`docs/at-tdd/process.md`.

### Issue level

For Feature Path work on a named Issue, two approvals bound the work
instead of a separate Scope/Architecture/Technology/Phase gate at each
step:

1. **Plan approval** — before Phase 1 Red. Immediately after, state whether
   the work looks likely to surface further design decisions.
2. **Completion approval** — after Phase 3 Refactor, with docs, status, and
   the self-check below.

Between the two, run Red → Green → Refactor without a check-in at each
boundary.

### Work-plan investigation (mandatory before any batch approval)

A work-plan batch is a broad grant, so it must be preceded by an explicit
investigation step whose purpose is deliberate alignment with the Adjudicator.
Design already happens while a work plan is drafted; this step makes it a named
stage with defined outputs and its own approval, so that the batch is scoped
against a shared understanding rather than an assumed one.

Scope during investigation: **investigation and documents only.** No test, no
implementation, no status promotion, no ADR acceptance, and no batch record set
to `approved_for_execution` — only the Adjudicator sets that status.

Produce or update, before requesting a batch approval:

1. **Specification or ADR** — the authoritative spec under `docs/specs/`, or an
   ADR under `docs/architecture/decision-themes/` when the work needs an architecture or
   technology decision. A proposed ADR is not implementation authorization.
2. **Local Issues** — the `docs/issues/LISS-*` files for the work, each with its
   own scope and exit condition, per
   `docs/collaboration/local-issue-planning.md`.
3. **Issue granularity rationale** — state why the work is split this way: what
   each Issue's reviewable unit is, why a larger or smaller split was rejected,
   and which Issues are deliberately left out of this batch.
4. **Execution order** — the sequence with dependencies made explicit (which
   Issue blocks which, and which may run independently), and the reason the
   first Issue is first.
5. **Draft batch record** — the proposed
   `docs/collaboration/reviews/execution-batch-<id>.json` with `work_plan_id`,
   the enumerated `issue_ids` subset, `allowed_paths`, `allowed_phases`,
   `allowed_operations`, `expires_at`, `invalidating_triggers`, and
   `post_review_required`. `work_plan_id` is required for Claude Code even
   though the shared schema treats it as optional.

Then present for alignment: what was inspected, which accepted ADRs or specs
constrain the choices, the granularity and ordering options that were
considered with their consequences, a recommendation, and the open questions
that remain. Stop there.

Investigation approval is its own approval type. It authorizes neither the
batch, nor a phase, nor implementation. Do not begin Red on any Issue until the
Adjudicator approves the batch record separately.

### Work-plan level

When the Adjudicator approves a bounded execution batch record
(`docs/collaboration/reviews/execution-batch-<id>.json`, `schema_version: 1`
with `work_plan_id`), that single approval replaces the per-Issue Plan and
Completion approvals for every Issue the record's `issue_ids` names. Work
proceeds Issue by Issue through Red → Green → Refactor without a check-in at
any Issue or phase boundary, until the batch's named scope is complete or an
`invalidating_triggers` entry fires.

The record's enumerated `issue_ids` are the boundary, not the work plan as a
whole. Completing a named Issue does not authorize an Issue the record omits.
Batch approval supplies no phase, ADR, architecture, or technology-selection
approval it does not name, and CI success is not Adjudicator approval.

### Hard stop (applies at both levels)

If an unanticipated design or architecture decision surfaces mid-work, stop and
ask — never resolve it unilaterally. When stopping, present the detailed
premises: what was inspected, which accepted ADRs or specs constrain the
choice, the concrete options with their consequences, and a recommendation.
Then take direction, or split the decision into its own Issue or ADR.

### Self-verification before reporting completion

Red failed for the stated reason before Green started; Green passed those
assertions without editing a test to force it; Refactor changed no behavior;
the full regression sweep and spec verification ran after Refactor. At the work
plan level, verify this per Issue in the batch, not once for the batch.

### Branch, commit, and PR

Commits stay phase-tagged. Branch, push, PR, and merge follow the work plan:
one `batch/<batch-id>` branch and one PR per approved batch, opened once when
the batch scope is complete and its documentation is synchronized. For
Issue-level work outside a batch, one branch and one PR per Issue. See
`docs/collaboration/branch-commit-pr-discipline.md`.

## Project Boundaries

- The project is local-first (CLI and library on the developer machine).
- MVP has no application datastore and no database migrations.
- QPU / OpenQASM backends are future optional adapters behind ports; not
  selected for MVP.
- Cloud AI / LLM providers are not part of the Staqex language runtime.
- External I/O used by the runtime (RNG, source loading, measure sink) must
  go through the ports listed under "External Resources Must Be Ports" above.

## Implementation Entry Point

Before starting a coding task:

1. Read `docs/architecture/agent-quickstart.md`.
2. Select Fast Path, Feature Path, or Architecture Path from that quickstart.
3. Read only the documents required by the selected path.
4. Read the target EARS/Gherkin file for Feature Path work.
5. Read `docs/architecture/io-reasoning-contracts.md` when AI or model output
   is involved.
6. Read only the architecture documents relevant to the touched area.
7. Check `docs/architecture/implementation-readiness.md` before Phase 1, 2, or
   3 starts.
8. Confirm the requested phase.
9. Output the path-appropriate design note.

Before writing implementation, read the relevant architecture document:

- Test placement: `docs/architecture/testing-strategy.md`.
- File placement: `docs/architecture/project-structure.md`.
- Readiness checklist: `docs/architecture/implementation-readiness.md`.
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
- AI failure and recovery:
  `docs/collaboration/ai-failure-recovery.md`.
- Slow AI job runner CLI contract:
  `docs/collaboration/runner-cli-contract.md`.
- External resource adoption contract:
  `docs/architecture/external-resource-adoption-contract.md`.
- Staqex language axioms: `docs/architecture/staqex-language-axioms.md`.
- Adjudicator language vision:
  `docs/architecture/adjudicator-language-vision.md`.
- Physicist × DX surface: `docs/architecture/physicist-dx-harmony.md`.
- Physicist source friction ledger:
  `docs/architecture/physicist-source-friction-ledger.md`.
- Developer quickstart: `QUICKSTART.md`.
- Modern OOP / visibility handoff:
  `docs/collaboration/agent-sync-modern-oop-visibility.md`.

Use `docs/templates/design-intake.md` for design-only work,
`docs/templates/adjudicator-review.md` when requesting approval, and
`docs/templates/agent-handoff.md` when stopping before completion.

Generated code must minimize human cognitive load. Keep files and functions
appropriately split, avoid clever compression, and make tests readable for the
Adjudicator.

Before reporting completion, check `docs/collaboration/definition-of-done.md`.
Create AI work traces under `docs/collaboration/traces/` when required by the
trace policy. Use feature-unit branches for feature work.
For feature work, identify local issue or GitHub issue dependencies before
creating the branch.

## Selected Stack

**Shipping Kernel:** Python 3 (`compiler/staqex/`, `python3 -m compiler.staqex`).
**Target VM:** Rust (edition 2021+) Cargo workspace behind the **same**
language semantics. No UI in MVP; OpenQASM/QPU as future ports.

Do not treat “Rust workspace” phrasing in older docs as permission to ignore
the shipping Python Kernel or to fork language meaning.

## Current Open Topics (honest backlog — revised 2026-08-03)

**Showcase (shipped path):** Quantum Disaster Response OS —
[`examples/showcase/S01_quantum_disaster_response/`](examples/showcase/S01_quantum_disaster_response/)
([LISS-0222](docs/issues/LISS-0222-s01-quantum-disaster-response.md) /
[WP-0070](docs/work-plans/WP-0070-s01-quantum-disaster-response.md);
mission lock superseded 2026-08-01). Language coverage scorecard A+B filled;
`inner`/`outer` Joint Call remains compile-surface honesty.

Do **not** treat this list as “nothing is shipped.” Several former bullets were
already Accepted/Runtime complete; agent text was stale. Option B program:
[`staqex-v1-open-topics-before-s1-program.md`](docs/specs/staqex-v1-open-topics-before-s1-program.md).

**Permanent-out was Reopened** (Adjudicator 2026-07-31):
[`staqex-v1-open-topics-permanent-out.md`](docs/specs/staqex-v1-open-topics-permanent-out.md)
([LISS-0152](docs/issues/LISS-0152-permanent-out-reopen.md) / WP-0037).

### Scheduled before S1 (Option B)

_(none remaining — LISS-0129 typed surface **shipped** 2026-07-31.)_

ADR 0057 showcase boundary is documented (LISS-0131); do **not** claim general
CPTP.

### Already shipped (remove from “open” mental model)

- Typed `state name: State<T> = …` annotations — ADR 0115 / LISS-0129.
- `evolve … until … max N` — ADR 0079 / LISS-0012 **Runtime complete**.
- Minimal `|>` / currying — ADR 0080 / LISS-0013; unary bare `|> f` —
  ADR 0122 / LISS-0154; function Partial `_` holes — ADR 0123 / LISS-0155.
- Trait `impl` / effect marking core — DEC-0005 / LISS-0014–0015.
- Density matrix / Lindblad numeric Kernel slices — ADR 0057 lineage complete
  per open-work register (showcase honesty: LISS-0131).
- Classical Type-First quantities ⊕ State arithmetic — ADR 0116 / LISS-0133.
- SI base dims $I$, $\Theta$ (`Current` / `Temperature`) — ADR 0121 / LISS-0153.
- Explicit SI scale/affine `expr to unit` (time/length/freq/energy/mass +
  °C/°F/K) — ADR 0124 / 0129 / 0132 / 0134–0136 / LISS-0156 / 0161 / 0164 /
  0166–0168.
- User-fn State-forming Call args (`id(|1>)`) — ADR 0130 / LISS-0162.
- Stepwise Partial fill — ADR 0131 / LISS-0163.
- Pipeline leftmost `_` hole fill — ADR 0133 / LISS-0165.
- Thin pipeline Operator Fusion MVP (pure unary `fn` chains) — ADR 0137 /
  LISS-0169 (ADR 0022 Hold partially unsealed).
- Trace-Out GC for library `fn` scopes — ADR 0138 / LISS-0170.
- Interference prune / support-merge MVP — ADR 0139 / LISS-0171.
- Deferred Pushforward MVP (eligible mains) — ADR 0140 / LISS-0172.
- Algebraic Operator Fusion MVP (affine carriers) — ADR 0141 / LISS-0173.
- Trace-Out GC for block `evolve` — ADR 0142 / LISS-0174.
- Call / Partial pipe Fusion MVP — ADR 0143 / LISS-0175.
- Rankine affine `.R` ↔ K — ADR 0144 / LISS-0176.
- Imperial pound mass `.lb` ↔ kg — ADR 0145 / LISS-0177.
- Imperial ounce mass `.oz` — ADR 0146 / LISS-0178.
- Imperial stone mass `.st` — ADR 0147 / LISS-0179.
- Metric tonne mass `.t` — ADR 0148 / LISS-0180.
- Multi-hole Partial bare pipe fill — ADR 0149 / LISS-0181.
- US short / UK long ton mass — ADR 0150 / LISS-0182.
- Troy ounce mass `.oz_t` — ADR 0151 / LISS-0183.
- Tuple simultaneous multi-hole pipe / Fusion fill — ADR 0152 / LISS-0184.
- Bare-block Trace-Out GC — ADR 0153 / LISS-0185.
- Mixed-unit `+`/`-` reject (no auto-rescale) — ADR 0154 / LISS-0186
  (**superseded** by ADR 0155).
- Mixed-unit canonical promote — ADR 0155 / LISS-0187.
- Polynomial ≥2 Operator Fusion — ADR 0157 / LISS-0190.
- Interprocedural Trace-Out GC — ADR 0158 / LISS-0191.
- CPU data-parallel Deferred workers — ADR 0159 / LISS-0192.
- Classical Fraction literals → f64 at State — ADR 0160 / LISS-0193.
- CredentialPort + Env adapter + mock submit — ADR 0161 / LISS-0194.
- Dynamic-lane root-cause real Kernel execution (mid-circuit `measure` via
  `Joint.project_coord`, match dispatch via normal Call dispatch) —
  ADR 0200 / LISS-0387.
- Dynamic-lane reuse capability law repurposed for simulator-class
  profiles — LISS-0388 (ADR 0200 Decision 3 consequence).
- `dynamic_trace.physical_outcome_confirmed` (reconciles Host bookkeeping
  with real evaluator collapse) — ADR 0198 Amendment / LISS-0389.
- Dynamic-lane `reset` keyword (Option B revisited; `reset wire` =
  `Joint.trace_out` + re-prepare `|0>`, distinct from Static Kernel's
  same-name `state x = |0>` uncompute-verify idiom) — ADR 0199 Amendment /
  LISS-0390.
- OpenQASM 3 emission for the Dynamic QPU lane (separate lowering path,
  native `bit`/`if`/`reset` vocabulary, no `physical_execution_claimed`
  claim) — ADR 0201 / LISS-0391.
- AWS Braket Host adapter (`QpuSubmitPort`/`QpuJobPort`; version-gated
  against CVE-2026-9291; real submission never performed autonomously) —
  ADR 0202 / LISS-0392.
- `submit_live_qpu` async entrypoint (`submit_source` untouched; returns
  `ProviderJobId`, never `Job`/`JobResult`) — ADR 0203 / LISS-0393.

### Reopened backlog (Architecture / Feature Path allowed)

- CUDA GPU Deferred DAG workers — later ADR beyond 0159.
- Further trait dispatch / effect-row expansion — design boundary DEC-0004;
  surface examples **accepted, no ship ADR**
  ([LISS-0196](docs/issues/LISS-0196-trait-specialization-surface-design.md)
  **complete**;
  [examples](docs/specs/staqex-v1-trait-effect-surface-examples.md)).
  Stable face: shipped `interface`/`impl` + free-fn interface-typed params +
  fixed `effects {…}` (DEC-0005). **Do not start Kernel Red.** Optional
  pure interface default bodies only after a **future** ship ADR is Accepted
  separately — never overlapping specialization or provider effect rows.
- Continuous PDF / Monte Carlo — design boundary ADR 0126; strategy ADR 0162;
  **Host histogram inject MVP shipped** ADR 0163 / LISS-0195; **consumption
  seam shipped** ADR 0164 / LISS-0198 / WP-0068. **Lane A finiteize surface
  shipped** [ADR 0185](docs/architecture/decision-themes/dec-0004-type-first-scientific-model.md)
  / [LISS-0313](docs/issues/LISS-0313-finiteize-surface.md) (`finiteize(lo,hi,
  bins,samples[,seed])`; B18). Mid-program `Continuous` still deferred (Lane B);
  **expressiveness seats** (Ideal vs today)
  [scenarios](docs/specs/staqex-v1-continuous-lane-b-expressiveness-scenarios.md)
  / [LISS-0315](docs/issues/LISS-0315-continuous-lane-b-expressiveness-scenarios.md)
  — no Kernel Red until a future ship ADR.
- Joint rational mode — design boundary ADR 0125 (classical path unsealed by
  ADR 0160; Joint masses remain f64 per ADR 0076/0097).
- Concrete live QPU provider SDK — design boundary ADR 0127 satisfied:
  Adjudicator technology approval selected **AWS Braket**, adapter +
  async `submit_live_qpu` entrypoint **shipped** (ADR 0202 / LISS-0392,
  ADR 0203 / LISS-0393). Reopened-backlog listing kept only because real
  submission has never been performed (by design — no agent may invoke
  the real, non-mock path autonomously; requires the user's own AWS
  credentials and explicit real-time confirmation) and end-to-end wiring
  into a showcase/example remains unscheduled. Do not re-run the
  provider-selection decision without a new Architecture Path reason. See
  [`staqex-v1-qpu-capability-honesty.md`](docs/specs/staqex-v1-qpu-capability-honesty.md).
- Display-unit restore **shipped** [ADR 0186](docs/architecture/decision-themes/dec-0004-type-first-scientific-model.md)
  / [LISS-0314](docs/issues/LISS-0314-display-unit-restore.md) (LHS unit after
  mixed promote; LISS-0197 superseded).

Many earlier “non-decisions” (e.g. `fun` vs `fn`, `when`, entry `main`,
`inspect`, DAG runtime, ket/Hamiltonian, namespace/enum/struct/class,
`pub`/`_`) are **Accepted and Kernel-shipped** — see ADR index in
`docs/architecture/README.md`. Do not re-open them without Architecture Path.

Treat reopened rows as ADR topics, not assumptions. Do not invent provider
credentials or silent rational runtime modes.
