# ADR 0192: S02 `Projector<Selection>` semantics, constraint lowering, objective normalization, and violation handling

## Status

**Accepted** (2026-08-05) — direction approved by the Adjudicator. WP-0093
work unit C's deliverable ("ADR proposal covering `Projector<Selection>`
semantics, constraint lowering, objective normalization, and violation
handling"). Acceptance approves the semantics/type contract in Decisions
1–5 below; it does **not** by itself authorize the Kernel change, the
`BenchmarkResult` DTO, or any test — see "Acceptance boundary" and
"Follow-up work required" below, which remain gating.

## Design check

- **Scope and expected behavior:** Define what a `Projector<Selection>`
  region actually represents in the Semantic IR (replacing today's
  hardcoded placeholder — see Context), which named constraint predicates
  are recognized at the Kernel boundary, how soft objective terms are
  normalized before composition, and how the Host result contract records
  whether each constraint was Host-validated, projected, or penalized. This
  is a semantics/type decision; it does not implement the compiler change.
- **Specifications and files inspected:** [ADR 0190](0190-s02-selection-boundary-and-mix-control.md)
  (Accepted), the [S02 acceptance specification](../../specs/staqex-v1-s02-drug-discovery-benchmark.md)
  §"Control and observation rules" / §"Constraint and objective contract"
  (Accepted), the [S02 design draft](../../specs/staqex-v1-drug-discovery-benchmark-design.md)
  §10.2–10.3, [WP-0093](../../work-plans/WP-0093-s02-language-expressiveness-and-selection.md)
  work unit C, [LISS-0321](../../issues/LISS-0321-s02-host-domain-and-finite-boundary.md)
  (shipped: `Candidate`/`Constraint`/`Score`/`SelectionProblem` Host records
  and the finite-manifest witness), `compiler/staqex/quantum_semantic_ir.py`
  (`ProjectorRegion`, `_TransformationRegion`, `RegionValidity`),
  `compiler/staqex/pipeline.py` (`_append_selection_projector_region`),
  `tests/test_s02_selection_surface_red.py`.
- **Component boundaries, ports/adapters, and VO/DTO candidates:** Kernel
  semantic-IR region type only (`ProjectorRegion`); no new port or adapter.
  Candidate VO/DTO: a structured `constraint_ref` provenance record
  (replacing today's single hardcoded string), and a Host-side
  `ConstraintDisposition` enum (`host_validated` | `projected` |
  `penalized`) referenced by `BenchmarkResult` (Host-side, future work unit
  E). No persistence or provider SDK involved.
- **Applicable constraints:** Never Leave the State (a hard constraint must
  restrict the feasible subspace, not silently sample or collapse it); ADR
  0190's taxonomy (`mix`/`controlled`/`superpose`/`when`-retirement) is
  unaffected — `Projector<Selection>` is compositionally orthogonal to
  which composition lane produced the state being projected; fail-closed
  capability checks (an unrecognized constraint predicate must be an
  explicit diagnostic, not silent acceptance); the already-Accepted S02
  spec's rule that a penalty Hamiltonian must never claim to guarantee
  feasibility.
- **Decisions, assumptions, unresolved ambiguities:** This ADR proposes a
  fixed, closed set of constraint predicate names for the first S02 slice
  (§Decision 2) rather than an open/extensible predicate DSL — extensibility
  is deferred pending real usage evidence. It also proposes that objective
  normalization is a Host-side responsibility using `Score`'s existing
  `value`/`weight`/`direction`/`provenance` shape (already shipped in
  LISS-0321), not a new Kernel-side arithmetic feature — see Rejected
  alternatives.
- **Included and omitted AI context:** Included the shipped LISS-0321 DTOs,
  the Accepted S02 spec's textual constraint/objective contract, and the
  current (hardcoded-stub) `ProjectorRegion` lowering code, read directly
  from source. Omitted QASM/QPU lowering, real compound data, and any
  claim about quantum advantage.
- **Task routing:** Architecture review for the semantics decision;
  deterministic source inspection for current-implementation claims; no
  external AI/model call.
- **Input/output evidence contract:** Any generated constraint annotation
  in a future implementation must carry `source_refs`, and this ADR does
  not itself constitute implementation evidence.
- **Verification plan:** After acceptance, a named Issue (work unit C's
  Kernel-side slice) adds Phase 1 Red tests asserting: (a) each of the
  fixed predicate names lowers to a distinct, inspectable `constraint_ref`
  entry (not the current single hardcoded string); (b) an unrecognized
  predicate name fails with an explicit capability diagnostic; (c) a
  program using only a penalty Hamiltonian (no `project ... onto`) does not
  produce a `ProjectorRegion` and its Host report must carry a
  penalty-profile disclaimer (Host-side, ties to future work unit E).

## Context

[ADR 0190](0190-s02-selection-boundary-and-mix-control.md) fixed the
composition taxonomy (`mix`/`controlled`/`superpose`/`when`) and, in the
same PR (#337), added a **placeholder** `ProjectorRegion` lowering so that
`tests/test_s02_selection_surface_red.py::test_projector_is_explicitly_lowered_from_selection_constraints`
could assert that *a* `ProjectorRegion` appears in the semantic IR when a
program contains `project ... onto ...`. Reading
`compiler/staqex/pipeline.py::_append_selection_projector_region` directly
shows this is currently a hardcoded stub, not real Projector semantics:

- It only checks whether *any* `project(...)` call exists anywhere in
  `main`'s body (`has_projector = True`) — it does not parse or validate
  what is being projected onto.
- When triggered, it unconditionally appends exactly **one** `ProjectorRegion`
  with a literal `constraint_ref="S02.feasible"` string and a canned
  2-dimensional `ActingSpace` — regardless of the actual constraint
  expression, candidate count, or selection size in the source program.
- `prepare_selection` (the conceptual state-preparation call in the same
  test) is only a name in `compiler/staqex/unitarity_check.py`'s
  `_QUANTUM_OPS` whitelist; it has no real implementation. `feasible` is
  not a registered stdlib function anywhere.

So the existing green test is evidence that the **generic** `project X onto
Y` syntax exists and produces *a* region — not evidence that
`Projector<Selection>` semantics, named constraint predicates, or
constraint/objective lowering are implemented. WP-0093 work unit C's own
deliverable list ("ADR proposal covering `Projector<Selection>` semantics,
constraint lowering, objective normalization, and violation handling") was
never produced. [LISS-0321](../../issues/LISS-0321-s02-host-domain-and-finite-boundary.md)
(merged, PR #349) shipped the Host-side classical records
(`Candidate`/`Constraint`/`Score`/`SelectionProblem`,
`FiniteManifestWitness`) that this ADR's decisions build on, but explicitly
excluded Projector semantics as work unit C's own concern.

The already-**Accepted** [S02 acceptance specification](../../specs/staqex-v1-s02-drug-discovery-benchmark.md)
already states the intended contract in prose ("hard constraints... lower
to a feasible-subspace Projector or an equivalent named operator", "soft
preferences are normalized to a common finite scale before weighted
composition", "if a penalty Hamiltonian is used, the report must identify
it as a penalty profile and must not claim that a low penalty guarantees
feasibility"). This ADR does not change that already-accepted policy; it
formalizes it into a concrete IR/type contract so it can actually be
implemented and tested, replacing the current hardcoded placeholder.

## Decision proposal

### 1. `ProjectorRegion.constraint_ref` becomes a structured, source-derived reference

Today's single hardcoded literal (`"S02.feasible"`) is replaced by a
provenance-carrying reference built from the actual `project ... onto
<predicate-call>` source expression: the predicate name and its resolved
argument set (e.g. `exactly_selected(2)`, `pairwise_compatible`). A program
with multiple named predicates composed under one `feasible(...)` call
produces **one** `ProjectorRegion` whose reference enumerates each
contributing predicate, so a Host report can later show which named rules
contributed to the feasible subspace. A program with no `project ... onto
...` produces no `ProjectorRegion` at all (unlike today, where the
detection is a whole-body scan that could in principle be triggered by an
unrelated `project` call elsewhere in the same function).

### 2. A fixed, closed set of named constraint predicates for the first S02 slice

Only these predicate names are recognized as lowering into a
`ProjectorRegion` reference; any other name inside `feasible(...)` is a
`S02_UNKNOWN_CONSTRAINT_PREDICATE` capability diagnostic, not silent
acceptance:

| Predicate | Meaning | Maps to |
|---|---|---|
| `exactly_selected(n)` | Selection state carries exactly `n` selected candidates | Hard feasible-subspace restriction |
| `pairwise_compatible` | No two selected candidates violate a declared incompatibility | Hard feasible-subspace restriction |
| `diversity_at_least(k)` | Selected set meets a declared minimum diversity score | Hard feasible-subspace restriction |

This list is deliberately narrow (matching the S02 design draft's §10.3
sketch exactly) rather than an open predicate DSL — see Rejected
alternatives. Extending it is a future ADR amendment once real S02 usage
shows a concrete gap, not a speculative extensibility mechanism now.

### 3. Objective normalization stays a Host-side responsibility using the shipped `Score` shape

`SelectionProblem.soft_objective_terms` (shipped in LISS-0321 as
`tuple[Score, ...]`) is the objective's sole representation. Each `Score`
already carries `value`, `direction` (`"maximize"`/`"minimize"`), `weight`,
and `provenance`. This ADR decides: normalization (mapping each term's
`value` onto a common finite scale before weighted composition, per the
Accepted spec) happens **Host-side**, before a `SelectionProblem` is handed
to the Kernel boundary — not as a new Kernel-side arithmetic feature. The
Kernel only ever sees already-normalized, already-weighted terms; it does
not perform normalization itself. A `SelectionProblem` whose
`soft_objective_terms` are not normalized (e.g. a `value` outside a
declared `[0, 1]` or `[-1, 1]` scale, TBD at implementation time) is a Host
input-hygiene rejection, extending `finite_boundary.py`'s
`ManifestValidationError` pattern from LISS-0321 rather than inventing a
second rejection mechanism.

### 4. Penalty Hamiltonian is a separate, explicitly labeled profile — never a silent Projector substitute

A program may express constraints as a penalty Hamiltonian term instead of
(or in addition to) a `project ... onto feasible(...)` restriction. This
ADR decides: a penalty-only program produces **no** `ProjectorRegion` (per
Decision 1, since no `project ... onto` call exists), and the Host result
contract (`BenchmarkResult`, future work unit E) must carry an explicit
`objective_profile: "penalty"` field distinct from `"projector"` whenever a
penalty term is present. A result built from a penalty profile must never
claim `feasibility_verdict: "guaranteed"` — the Accepted spec's existing
rule, now given a concrete field name so it is checkable rather than only
prose policy.

### 5. Violation/disposition tracking per constraint

Each `Constraint` (shipped in LISS-0321 as a Host record with `name` and
`domain`) gets one `ConstraintDisposition` in the eventual `BenchmarkResult`:
`"host_validated"` (rejected or accepted during LISS-0321's Host input
hygiene, before reaching the Kernel boundary — e.g. malformed or
out-of-domain records), `"projected"` (lowered to a `ProjectorRegion`
predicate per Decision 2), or `"penalized"` (a weighted Hamiltonian term
per Decision 4). A constraint that reaches neither disposition is an
implementation bug, not a silently-dropped rule — this ADR requires the
eventual work-unit-E implementation to assert every declared `Constraint`
has exactly one disposition, never zero.

## Consequences

- `ProjectorRegion` becomes a real, inspectable witness of which named
  predicates restricted the feasible subspace, instead of one hardcoded
  string that is identical for every S02 program regardless of source.
- Constraint predicates are a small, closed vocabulary for now — this
  keeps the first implementation slice bounded, at the cost of not yet
  supporting arbitrary user-defined hard constraints (explicitly deferred).
- Objective normalization has exactly one home (Host-side, on the already-
  shipped `Score` shape) instead of being split or duplicated between Host
  and Kernel.
- A penalty-Hamiltonian-only program is now structurally distinguishable
  (no `ProjectorRegion`, `objective_profile: "penalty"`) from a
  Projector-backed program, so the "penalty does not guarantee feasibility"
  rule becomes a field check, not only a documentation promise.
- Implementing this ADR requires replacing
  `_append_selection_projector_region`'s current hardcoded-stub logic;
  that replacement, and the Host-side `ConstraintDisposition`/
  `objective_profile` fields, are the next Kernel-touching Issue after this
  ADR is accepted — not authorized by this ADR alone.

## Rejected alternatives

### Open/extensible constraint predicate DSL now

Rejected for the first slice. An extensible predicate system (user-defined
constraint functions, arbitrary Kernel-side validation logic) is a much
larger surface decision than S02 currently needs, and would make "which
constraints are Kernel-recognized" an open question exactly when this ADR
is trying to close it. Revisit only after the fixed three-predicate set
proves insufficient for a real S02 fixture.

### Kernel-side objective normalization

Rejected. Normalizing scores inside the Kernel would duplicate
`finite_boundary.py`'s already-shipped Host input-hygiene pattern and blur
the classical/quantum boundary the whole S02 benchmark exists to test —
normalization is a classical, Host-side concern per the Accepted spec's own
framing ("Host owns fixtures, classical baselines, resource reports").

### Silently treating a penalty Hamiltonian as if it were a Projector

Rejected — this is exactly the failure mode the Accepted spec already
forbids ("must not claim that a low penalty guarantees feasibility").
Making the two profiles structurally distinguishable (Decision 4) is this
ADR's way of making that prohibition enforceable rather than only stated.

### Keep the current hardcoded `constraint_ref` stub

Rejected. A single literal string identical across every S02 program
cannot support the Accepted spec's own result-contract requirement
("feasibility result and violated constraints, if any") — there is nothing
in `"S02.feasible"` to report a violation *of*.

## Follow-up work required after acceptance

1. File a Kernel-touching Local Issue implementing Decisions 1–2: replace
   `_append_selection_projector_region`'s hardcoded stub with real
   predicate-name recognition and structured `constraint_ref` construction,
   plus the `S02_UNKNOWN_CONSTRAINT_PREDICATE` diagnostic.
2. File a Host-side Local Issue (likely folded into work unit E) adding
   `ConstraintDisposition` and `objective_profile` to a `BenchmarkResult`
   DTO, extending LISS-0321's `finite_boundary.py` hygiene pattern for
   objective-term normalization checks (Decision 3).
3. Add conformance scenarios for: unknown-predicate rejection, penalty-only
   programs never producing a `ProjectorRegion`, and every declared
   `Constraint` resolving to exactly one disposition.

## Acceptance boundary

Acceptance of this ADR approves the `Projector<Selection>` semantics,
constraint-predicate vocabulary, objective-normalization ownership, and
violation-disposition contract described above. It does **not** authorize
the Kernel change to `pipeline.py`/`quantum_semantic_ir.py`, the
`BenchmarkResult` DTO, or any test. Those require their own reviewed scope
and phase approval, per the Follow-up work above.
