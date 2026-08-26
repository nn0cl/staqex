# ADR 0193: Dynamic QPU lane timing intent as a Region attribute

## Status

**Accepted** (2026-08-05) — direction approved by the Adjudicator. Extends
[LISS-0028](../../issues/LISS-0028-dynamic-qpu-lane.md)'s own listed
remaining item ("Timing, qubit reuse, controller values, and JobResult
composition are specified"). Acceptance approves the grammar/IR shape in
Decisions 1–5 below; it does **not** by itself authorize the Kernel-touching
implementation, and it does not make the dynamic QPU lane executable — see
"Acceptance boundary" and "Follow-up work required" below, which remain
gating.

## Design check

- **Scope and expected behavior:** Define how backend timing *intent*
  (e.g. "this block should execute inside one coherent window") attaches
  to the existing `dynamic qpu { ... }` block (LISS-0028 / ADR 0071)
  without polluting the operations inside it with backend-specific
  numbers, and without changing what kind of AST node `dynamic qpu` is
  (it stays a statement — no expression-status change, no method-chain
  syntax). This ADR defines the grammar/IR shape for capturing that
  intent; it does not implement dynamic-QPU execution, which remains
  capability-rejected exactly as today.
- **Specifications and files inspected:** [LISS-0028](../../issues/LISS-0028-dynamic-qpu-lane.md)
  (Phase 3 reviewed; "Timing... remain open"), `dec-0006-host-qpu-and-external-ports.md`
  (ADR 0071 archived source), `compiler/staqex/ast_nodes.py`
  (`DynamicQpuStmt`, confirmed a `Stmt`, not an `Expr`),
  `compiler/staqex/parser.py::_dynamic_qpu_stmt` (confirmed current
  grammar: `dynamic qpu { <block> }`, no attribute position exists yet),
  `compiler/staqex/typecheck.py` (confirmed every `DynamicQpuStmt`
  unconditionally emits `DYNAMIC_CAPABILITY_REQUIRED_ERROR` and
  `DYNAMIC_UNSUPPORTED_FEATURE_ERROR` today — the lane is not executable
  by any target yet, and this ADR does not change that), ADR 0192 (this
  session's `ProjectorRegion` precedent for a Region witness distinct from
  real execution), ADR 0081 (effect marking precedent), the
  `evolve ψ under H for t` and `feasible(name = value, ...)` surface
  idioms (existing prepositional-clause and keyword-argument patterns).
  Also considered and rejected, per Adjudicator discussion this session: a
  Kotlin-style `.observe { }.measure { }` method-chain surface (requires
  promoting blocks to expressions and a new trailing-block call form
  neither of which exist; conflicts with the physicist-first "state is not
  an object with methods" mental model per DEC-0003) and reviving the
  retired `observe` keyword.
- **Component boundaries, ports/adapters, and VO/DTO candidates:** Kernel
  language surface (parser/AST) and Quantum Semantic IR only. No new
  Host/QPU adapter. Timing intent is a backend-neutral label; concrete
  durations, alignment, and `dt` stay a future target-adapter concern
  (`target_capability.py`/`target_routing.py`'s existing separation — "MVP
  has no... QPU adapter" boundary is unchanged). A new `TimingRegion` (or
  a `timing_ref` field on the existing region shape) is the candidate IR
  witness, parallel to ADR 0192's `ProjectorRegion`.
- **Applicable constraints:** `dynamic qpu` stays a `Stmt`; no expression
  promotion, no trailing-block call syntax, no method-chain. `observe` is
  not revived. No classical mid-circuit branching is introduced (R3 from
  the reviewed external design package is explicitly out of scope, per
  Adjudicator decision this session). Fail-closed: an unrecognized or
  malformed timing clause is an explicit diagnostic, never silently
  ignored. The overall `dynamic qpu { ... }` statement remains rejected by
  typecheck exactly as today (`DYNAMIC_CAPABILITY_REQUIRED_ERROR` /
  `DYNAMIC_UNSUPPORTED_FEATURE_ERROR`) — this ADR adds a capturable
  grammar/IR shape for timing intent, it does not make the dynamic lane
  executable.
- **Decisions, assumptions, unresolved ambiguities:** Surface syntax
  choice (§Decision 1) between a prepositional clause (`within <name>`,
  matching `evolve ... under ... for ...`) and a keyword-argument form
  (matching `feasible(name = value, ...)`) — this ADR recommends the
  prepositional form as primary; the Adjudicator may prefer the other.
  The vocabulary of recognized timing-intent names is intentionally left
  open/opaque for this slice (a single free-form identifier, not a closed
  enum like ADR 0192's predicates) since no real backend exists yet to
  define concrete meanings — assigning meaning to specific names is
  deferred until a real QPU adapter is selected (out of scope, per project
  boundaries).
- **Included and omitted AI context:** Included direct reads of the
  current `dynamic qpu` grammar/typecheck code and LISS-0028's own
  acceptance record. Omitted: any specific QPU vendor's timing model,
  pulse-level control, or error-suppression policy (explicitly deferred
  per LISS-0028's own non-goals).
- **Task routing:** Architecture review for the semantics decision;
  deterministic source inspection for current-implementation claims; no
  external AI/model call.
- **Input/output evidence contract:** N/A — no AI-generated runtime
  output; claims here are grounded in direct source reads performed in
  this session.
- **Verification plan:** After acceptance, a Feature Path Local Issue
  implements: (a) grammar accepts the timing clause on `dynamic qpu`
  without changing its `Stmt` status; (b) the Quantum Semantic IR carries
  a distinct, source-derived timing witness (not silently dropped); (c)
  the overall statement still fails with today's two diagnostics
  (regression: dynamic QPU remains non-executable); (d) a malformed timing
  clause (e.g. empty name) fails with its own explicit diagnostic rather
  than being silently accepted or crashing.

## Context

The reviewed external design package (Perplexity-generated, not part of
this repository's own design process) proposed a `prepare`/`protocol`/
`readout`/`observe`/`branch`/`window` language redesign to give real-QPU
timing requirements an explicit home, distinct from inline backend code
between operations. Verification against the current repository found:

- The package's file inventory was largely accurate, but its concrete
  syntax proposals (`state q0 := |0>`, bare `H q0` gate statements,
  `system Example { ... }` as a top-level container, `.observe { }`
  reviving a retired keyword) either don't exist in or directly conflict
  with the shipped language: `system` is already a keyword (DEC-0005/ADR
  0082's trait/impl marker), `observe` is already `RETIRED` in favor of
  `measure` (confirmed live: compiling `observe x` produces
  `RETIRED_KEYWORD: retired 'observe' → use 'measure'`), and no `:=` token
  or bare-gate-statement grammar exists.
- The package's own §"Timing model" idea — timing as a property attached
  to a wrapping region rather than scattered through instructions — is
  sound and matches a requirement Staqex already has open:
  [LISS-0028](../../issues/LISS-0028-dynamic-qpu-lane.md)'s Dynamic QPU
  lane (Phase 3 reviewed for its rejection/capability boundary) explicitly
  lists "Timing, qubit reuse, controller values, and JobResult composition
  are specified" as unchecked, remaining work.
- The package's mid-circuit `observe`/`branch` escape hatch (its R3) was
  reviewed and explicitly rejected by the Adjudicator for this scope: it
  revives a retired keyword and reopens classical mid-circuit branching,
  which is a separate, harder question already scoped out of LISS-0028's
  Phase 3 boundary ("mid-circuit semantics... remain open" as its own,
  separate item). Not addressed by this ADR.
- The package's Kotlin-style dot-chain surface (`.observe { }.measure { }`)
  was reviewed and rejected: `dynamic qpu` is a `Stmt`, not an `Expr` in
  the current AST, so it cannot be chained without promoting blocks to
  expressions and inventing a trailing-block call form — two new grammar
  categories for what the Adjudicator judged to be a worse fit for
  Staqex's physicist-first "state is acted upon by operators" mental model
  than the already-shipped, already-growing `|>` pipe idiom (ADR 0080 and
  its many extensions).

This ADR scopes only the timing-intent-as-Region-attribute piece — the
part of the reviewed package that both matches a real, already-open
Staqex requirement (LISS-0028) and fits the language's existing grammar
categories without new ones.

## Decision proposal

### 1. Surface syntax: a prepositional clause on `dynamic qpu`

`dynamic qpu` gains an optional `within <name>` clause, following the same
prepositional pattern as `evolve ψ under H for t`:

```staqex
dynamic qpu within coherent_window {
  apply H onto q0
  capply q0, Hadamard, q1
}
```

`<name>` is a single free-form identifier naming a timing intent; this ADR
does not define a closed vocabulary of names (unlike ADR 0192's predicate
set) because no real target adapter exists yet to give any name concrete
meaning. `dynamic qpu` without `within` remains valid (timing intent is
optional, not required) and behaves exactly as today.

**Rejected alternative:** a keyword-argument form
(`dynamic qpu(timing = coherent_window) { ... }`), matching ADR 0192's
`feasible(name = value, ...)` pattern. Rejected as primary because
`under`/`within` clauses in Staqex are conventionally used for a single
named physical resource or intent (as `evolve ... under H` names a
Hamiltonian), which matches "name one timing intent" better than a
keyword-argument bag intended for multiple named parameters. The
Adjudicator may prefer this form instead; it is not ruled out, only not
recommended as primary.

### 2. `DynamicQpuStmt` carries the timing intent; it stays a `Stmt`

`DynamicQpuStmt` gains an optional `timing_intent: str | None` field. No
change to its membership in the `Stmt` union, no new expression category,
no trailing-block call syntax, no method-chain.

### 3. The Quantum Semantic IR records a distinct timing witness

Parallel to ADR 0192's `ProjectorRegion`, a `TimingRegion` (or an
attribute on the region produced for the `dynamic qpu` block, if one
already exists at lowering time) carries the declared `timing_intent`
string as inspectable provenance — not a hardcoded placeholder, and not
silently dropped. This makes the intent visible to tooling and to a
future target adapter without Staqex core ever interpreting what the name
concretely means.

### 4. The dynamic lane's existing rejection boundary is unchanged

`dynamic qpu { ... }` — with or without `within <name>` — continues to
fail typecheck with `DYNAMIC_CAPABILITY_REQUIRED_ERROR` and
`DYNAMIC_UNSUPPORTED_FEATURE_ERROR`, exactly as today. This ADR does not
make the dynamic lane executable; it only defines how timing intent would
be expressed and recorded once a real target adapter exists. A malformed
`within` clause (e.g. `within` with no following identifier) fails with
its own explicit parse diagnostic rather than being silently accepted.

### 5. No mid-circuit observation or branching

This ADR does not introduce `observe`, `checkpoint`, or `branch`. Mid-
circuit measurement and classical feed-forward remain LISS-0028's own,
separately-scoped open item, per the Adjudicator's explicit decision this
session.

## Consequences

- Timing intent gets a real, inspectable home in the language and IR,
  addressing the actual motivating need (backend timing requirements
  without inline backend code between operations) without reopening
  `observe`, redefining `system`, or inventing method-chain syntax.
- `dynamic qpu` remains a statement; no Stmt/Expr architectural change is
  needed anywhere else in the compiler.
- The dynamic QPU lane remains non-executable until a real target adapter
  is selected (unchanged project boundary) — this ADR does not create an
  illusion of working hardware timing control.
- A future ADR is still required to give `within <name>` concrete,
  per-backend meaning once a real QPU adapter is selected; this ADR
  deliberately does not attempt that (no backend exists to ground it in).
- Mid-circuit observation/branching (R3 of the reviewed external package)
  remains a distinct, unresolved, and harder question — explicitly not
  advanced by this ADR.

## Rejected alternatives

### Kotlin-style method chain (`.observe { }.measure { }`)

Rejected. Requires promoting blocks to expressions and a new trailing-
block call form — two new grammar categories — and reframes state as an
object with methods, which the Adjudicator judged inconsistent with
Staqex's physicist-first "operators act on state" mental model (DEC-0003).
The existing, already-growing `|>` pipe idiom already serves the
"sequence of transformations" need this would have addressed.

### `prepare`/`protocol`/`readout` phase blocks

Rejected for this ADR's scope. The problem these were meant to solve
(separating physics logic from I/O boundary, keeping ordinary `measure`
out of the operation core) is already substantially handled by existing
mechanisms (`MEASURE_IN_FUNCTION_ERROR`-style placement rules, the
terminal-measure requirement, and Clean Architecture's Host/Kernel
separation) without new named blocks.

### Reviving `observe` for mid-circuit checkpoints

Rejected. `observe` is `RETIRED` in favor of `measure` (confirmed live);
reviving it under new semantics would overwrite an already-made,
already-shipped decision without its own dedicated Architecture Path
review. If a non-destructive mid-block diagnostic is ever needed, the
already-shipped `inspect(state)` / `DiagnosticView<T>` (ADR 0189, PR #342)
is the existing candidate — not part of this ADR's scope.

### Closed timing-intent vocabulary (mirroring ADR 0192's predicates)

Rejected for this slice. ADR 0192 could fix a closed predicate vocabulary
because the S02 spec already named concrete predicates
(`exactly_selected`, etc.). No real QPU adapter exists yet to define what
timing-intent names should concretely mean, so fixing a vocabulary now
would be inventing backend semantics Staqex core is not supposed to know.

## Follow-up work required after acceptance

1. File a Kernel-touching Local Issue implementing Decisions 1–4: grammar
   for `within <name>` on `dynamic qpu`, the `timing_intent` field, and
   the IR witness. **Complete:**
   [LISS-0381](../../issues/LISS-0381-dynamic-qpu-timing-region-intent.md)
   (branch `feature/liss-0381-dynamic-qpu-timing-region-intent`).
2. A future ADR (after a real target adapter is selected) to give
   specific timing-intent names concrete per-backend meaning.
3. LISS-0028's own remaining items (qubit reuse, controller values,
   JobResult composition, mid-circuit semantics) remain separately
   scoped, not advanced by this ADR.

## Acceptance boundary

Acceptance of this ADR approves the grammar/IR shape for timing intent
described above. It does **not** authorize the Kernel-touching
implementation, does not make the dynamic QPU lane executable, and does
not decide concrete per-backend timing semantics. Those require their own
reviewed scope and phase approval, per the Follow-up work above.
