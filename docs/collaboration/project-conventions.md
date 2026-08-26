# Project Conventions

Target-owned for this repository (the collaboration template itself).
Adopting projects get their own copy from `docs/templates/project-conventions.md`.
Template sync must not overwrite an adopting project's live file.

## Project

- Name: Staqex (Quantum-Probabilistic Executable)
- Domain: a physicist-first quantum-probabilistic language and Python Kernel;
  mid-program values remain `State<T>` and classical collapse is terminal
  `measure`.
- Stack: Python 3 package `compiler/staqex/`, Markdown architecture/spec docs,
  Bash/Python repository tooling, and GitHub Actions; Rust VM/simulator is a
  long-term target.

## External resources (ports)

- Git and GitHub CLI for branch, PR, and synchronization operations
- `RngPort`, `SourcePort`, `MeasureSinkPort`, provider-neutral QPU submit/job
  ports, and dependency-policy checks are the relevant runtime boundaries
- No application datastore or cloud database
- No LLM provider SDK inside the language runtime
- No live QPU provider integration in the Kernel

## Runtime and trust boundaries

- The project is local-first and ships a Python language Kernel/runtime.
- Domain and semantic meaning stay independent of adapters, providers, UI,
  persistence, and deployment technology.
- Scientific Semantic IR (ADR 0211) is the source-derived semantic authority;
  Physics IR and other consumer IRs are projections only.
- The source must preserve the physicist's blackboard meaning; machine
  convenience must not create a second language semantics.

## Current non-decisions

- Rust implementation details and the timing of the Rust migration
- QPU provider SDK, credentials, network adapter, and deployment technology
- Application datastore, persistence schema, and cloud service selection
- General Hilbert-space storage strategy and future observation algebra beyond
  the accepted MVP contracts

## Stack-specific architecture documents

- `docs/architecture/adjudicator-language-vision.md`
- `docs/architecture/physicist-dx-harmony.md`
- `docs/architecture/staqex-language-axioms.md`
- `docs/architecture/staqex-runtime-execution-model.md`
- `docs/architecture/staqex-backend-targets.md`
- `docs/architecture/implementation-readiness.md`
- `docs/specs/staqex-language-specification.md`

## Additional project rules

- `when` is state-preserving rather than classical `if`; terminal `measure`
  is the collapse boundary.
- Exact/symbolic inspection is distinct from finite `Realize`; unsupported
  realization must fail closed before artifact emission.
- H1 deployment remains deferred until a separate provider-neutral delivery
  contract is accepted.
- LISS-0129 typed surface **shipped**: `state x: State<Int> = …` is part of
  the current Kernel surface.
- Do not reintroduce stale broad ADR history or merge conflicted branches
  wholesale; use the current canonical Issue, Spec, WP, or ADR owner.
