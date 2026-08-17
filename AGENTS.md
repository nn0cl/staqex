# Agent Operating Contract

This repository is prepared for multiple AI coding agents. All agents must use
the same workflow and architectural boundaries.

## Prime Directive

No implementation without a reviewed acceptance specification.

No phase skipping.

No hidden business logic in adapters.

## Project (adopter facts — keep in sync across Tier 2)

**Staqex:** Quantum-Probabilistic Executable (**Never Leave the State**).
Mid-program values are `State<T>`; classical collapse only at terminal
`measure`.

**Shipping Kernel (authoritative for `examples/` + SV):** Python 3 package
`compiler/staqex/` — run with `python3 -m compiler.staqex`. Language surface
includes Joint amplitude eval, Type-First dims, `namespace` / `enum` /
`struct` / `class` + `fn init` / `this`, and visibility `pub` / `_`
(DEC-0003). See `QUICKSTART.md` and
`docs/architecture/physicist-dx-harmony.md`.

**Long-term target:** Rust (edition 2021+) Cargo workspace VM/simulator;
QPU / OpenQASM backends later **behind ports**. Do not invent a second
language semantics for “Rust-only” wording in older ADRs — one language,
two implementation generations.

## Language Design Priority (Adjudicator vision — binding)

**Staqex is a language for physicists.** Full orientation:
[`docs/architecture/adjudicator-language-vision.md`](docs/architecture/adjudicator-language-vision.md).

Normative summary agents must not violate:

1. **Physicist mental model is primary**; programmer DX is secondary but
required. On conflict, prefer blackboard spelling (DEC-0003; physicist-dx-harmony).
2. **Ideal form first** — not shortest path to something that runs; machine
   convenience never shapes the surface.
3. **Never Leave the State** / `when` not `if` / terminal `measure` — physics
   law, not style preference.
4. Do **not** recreate “beautiful equation → broken DSL → QPU port” inside
   Staqex or official examples; record gaps in the friction ledger / Issues.
5. Language-affecting `[DESIGN CHECK]` must state physicist-first preservation
   or stop for Architecture approval.
6. **Source must denote the same physics as the blackboard** (vision §2.2) —
   including intentional expansion, rewrite, and combination; machine-forced
   dialect shift is forbidden. Writeable ≠ executable separates meaning from
   realization; it does not mean programs are non-executable.

Companions: DEC-0003, `physicist-dx-harmony.md`,
`physicist-source-friction-ledger.md`.

## Honest backlog pointer (do not re-open settled rows)

Authoritative open / parked work:
[`docs/architecture/open-work-register.md`](docs/architecture/open-work-register.md).
Claude-facing narrative list (may be longer): `CLAUDE.md` §Current Open Topics
— not a second source of truth; if they disagree, prefer the open-work register
and cited Issues/ADRs.

**Trait specialization / effect rows (DEC-0004):** surface examples
**accepted, no ship ADR**
([LISS-0196](docs/issues/LISS-0196-trait-specialization-surface-design.md)
**complete**;
[examples](docs/specs/staqex-v1-trait-effect-surface-examples.md)).
Core `interface`/`impl` and fixed `effects {…}` remain shipped (DEC-0005).
**Do not start Kernel Red** for specialization or extensible effect rows until
a future ship ADR is Accepted.

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

Before design or implementation, consult
`docs/collaboration/independent-review-perspectives.md`. Select applicable
review lenses, use them as a pre-review checklist, and state them in the
design note or work trace.

## User-triggered Independent Context Review Loop

The user may trigger an independent review loop at any time with a request
such as “独立コンテキストレビュー”, “レビュー・修正ループ”, or an
equivalent explicit instruction. This is a reusable process, not a one-time
exception for a particular Issue.

When triggered, the agent must:

1. Identify the review scope, current Issue/ADR/Spec/WP, branch, phase, and
   allowed files from repository artifacts.
2. Spawn a fresh independent context for a read-only reviewer. The reviewer
   must not edit the worktree, grant approval, or perform implementation.
3. Ask the reviewer to return prioritized findings, evidence paths, a
   readiness verdict, and reusable reviewer perspectives. Do not request or
   record hidden chain-of-thought.
4. Record the review in `docs/collaboration/reviews/` and the AI routing and
   evidence in `docs/collaboration/traces/`.
5. Map findings to the reusable review lenses and promote new recurring
   concerns into the perspectives ledger.
6. Disposition each finding as `accepted`, `rejected`, or `deferred`. The
   primary agent may make this disposition under the existing accepted
   ADR/Spec/Issue/phase boundaries. Accept only design-preserving corrections;
   reject only unsupported, duplicate, non-applicable, or already-contract-
   conflicting findings. Record evidence and rationale for every decision.
   Ask the user only when the disposition would require a design deviation,
   new architecture/technology, Issue or phase change, conflicting user
   intent, or an unresolved physics/safety decision.
7. Apply only accepted, in-scope corrections in the main agent context. A
   correction is not a phase or implementation approval.
8. Re-run the review in a new independent context after accepted corrections.
   Every re-review must use the current artifacts, not the previous reviewer's
   context. Repeat the review/correction cycle until a terminal state is
   reached.
9. End the loop explicitly in exactly one of these terminal states:

   - `COMPLETE`: the latest independent review is ready, all findings are
     accepted/resolved or explicitly rejected with recorded authority, and no
     review blocker remains. This only completes the review loop; it does not
     approve a phase, ADR, technology, or implementation.
   - `ABORT`: no action is required, the user stops the review, or a user/
     Adjudicator decision is required because the existing design cannot
     determine the disposition. Record the unresolved decision and stop; do
     not continue by assumption.

   A `NOT READY` result with accepted actionable findings is not terminal; it
   transitions to correction and then to a fresh re-review. A `NOT READY`
   result with AI-rejected findings can transition after the evidence and
   rationale are recorded. A reviewer can report `READY` but
   cannot approve a phase, ADR, technology, or implementation.
10. Before moving to the next phase, record the user's or Adjudicator's typed
    approval separately.

Each iteration must state whether it is read-only review, finding disposition,
documentation correction, Red-test creation, implementation, or verification.
The loop must stop and ask the user when a finding changes an accepted
architecture, technology choice, Issue scope, or requested phase. The agent
must not use the loop to bypass branch, approval, implementation, or
human-review gates.

The minimum review record includes: trigger/request, independent context
boundary, inspected artifacts, findings with priority and disposition,
disposition authority, corrections applied, remaining blockers, reviewer
perspective, next review condition, terminal state (`COMPLETE` or `ABORT`),
and approval status. See `docs/templates/independent-context-review.md`.

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
- Staqex language axioms: `docs/architecture/staqex-language-axioms.md`.
- Adjudicator language vision:
  `docs/architecture/adjudicator-language-vision.md`.
- Physicist × DX surface: `docs/architecture/physicist-dx-harmony.md`.
- Physicist source friction ledger:
  `docs/architecture/physicist-source-friction-ledger.md`.
- Developer quickstart: `QUICKSTART.md`.
- Modern OOP / visibility handoff:
  `docs/collaboration/agent-sync-modern-oop-visibility.md`.

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
- Settings storage and validation (CLI flags / environment).
- Secret storage (reserved; not required for MVP).
- Dependency policy checks.

MVP has no application datastore, no cloud DB, no QPU adapter, and no LLM
provider inside the language runtime. Those remain future optional ports.

## Adjudicator Interaction

When a decision affects architecture, capture it as an ADR. When a decision is
unknown, list it in the path-appropriate design note as an ambiguity boundary.

Every request starts from design intake. Select only the AI payload context
needed for the task, define lightweight VO or DTO candidates when clear, and
route subtasks to an appropriate model, code assistant, or deterministic tool.
When AI or model output is involved, define input, output, and reasoning
evidence contracts before implementation.

Use the `[DESIGN CHECK]` scaffold only for Feature Path and Architecture Path
work. It reports observable requirements, inspected context, boundaries,
assumptions, routing, and verification; it must not request hidden
chain-of-thought. For Fast Path work, use a compact design note that states
scope, omitted context, deterministic checks, and why the full scaffold is
unnecessary.

The common scaffold is:

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
- Independent review lenses selected and why:
- Verification plan:
```

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

### Explicit Batch and Approval Source Rules

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

When handing off or stopping before completion, use
`docs/templates/agent-handoff.md`. When asking the Adjudicator for approval, use the
review points from `docs/templates/adjudicator-review.md`.

Generated source code must minimize human cognitive load. Prefer clear
responsibility boundaries, small functions, straightforward names, and
reviewable tests. Do not compress implementation into dense code just to be
minimal.

Before reporting completion, check `docs/collaboration/definition-of-done.md`.
Create AI work traces under `docs/collaboration/traces/` when the trace policy
requires it. Use feature-unit branches for feature work.
For feature work, identify local issue or GitHub issue dependencies before
creating the branch.
