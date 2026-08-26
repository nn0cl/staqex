# Staqex v1 S02 — indication-agnostic drug-discovery benchmark

| Field | Value |
|---|---|
| Status | **Accepted acceptance specification — Phase 2 implementation in progress** |
| ADR | [ADR 0190](../architecture/adr/0190-s02-selection-boundary-and-mix-control.md) |
| Work plan | [WP-0093](../work-plans/WP-0093-s02-language-expressiveness-and-selection.md) |
| Design | [S02 design](staqex-v1-drug-discovery-benchmark-design.md) |
| Relationship | S02 is additive; the locked disaster-response S01 remains unchanged |
| Representative-program lineage | [Rebaseline §7](staqex-v1-representative-program-rebaseline.md#7-examplesshowcase-two-phase-benchmark-role-and-the-s02-lineage-2026-08-05) (2026-08-05): S02 is the "S2+" successor that document's §4 anticipated; subject to the two-phase examples/showcase benchmark role (current language-coverage validation, future real-hardware gap discovery) and the [P1 coverage ledger](staqex-v1-language-coverage-ledger.md). Row-by-row S02 coverage-ledger population is separate, unstarted future work. |

## Purpose

S02 measures whether Staqex can express a finite early drug-discovery
selection experiment while keeping classical data, quantum state, constraints,
observables, terminal outcomes, and execution resources distinct.

It is a language expressiveness benchmark, not a chemistry, clinical, or
quantum-advantage claim.

## Normative benchmark shape

```text
synthetic manifest
  → Host candidate validation and deterministic ordering
  → explicit finite encoding
  → quantum selection State
  → hard-constraint Projector
  → soft-objective evolution
  → terminal measure
  → classical reranking and report
```

### Fixture limits

- Candidate count: 8–16.
- Selection size: 2–4.
- Candidate IDs: unique and stable within the manifest.
- Seed: required and recorded.
- Dataset: synthetic fixture for the first implementation.
- Encoding: one logical selection carrier per candidate for the first profile.

## Value model

### Classical records

`Candidate` contains a stable `CandidateId`, descriptor reference, score
components, tags, and provenance. A canonical chemical string is optional
evidence; it is not interpreted as a quantum value by the Kernel.

`Constraint` contains a named selection rule and its domain. `Score` contains
a normalized finite component, direction, weight, and provenance.

`SelectionProblem` contains the ordered candidates, target profile, hard
constraints, soft objective terms, selection size, seed, encoding profile, and
resource profile.

### Quantum carrier

The Kernel-facing conceptual type is:

```text
State<Selection<CandidateId>>
```

The state is not measured during validation, pruning, scoring, or evolution.
Feature vectors, strings, scores, and IDs do not become amplitudes implicitly.

## Control and observation rules

| Surface | Meaning | Sampling |
|---|---|---:|
| `mix` | State-valued probabilistic/classified alternatives | No |
| `controlled` / `Ctl` | Coherent operation control | No |
| `superpose` | Reserved for coherent phase-preserving composition | No |
| `project` | Feasible-subspace restriction; hard constraints lower to Projector | No |
| `expect` | Non-destructive observable evaluation | No |
| `measure` | Terminal `Outcome` / classical result boundary | Yes |

`when` is not part of the canonical S02 surface. Its use must fail closed with
a migration diagnostic; the compiler must not treat it as an alias for `mix`.

## Constraint and objective contract

Host validation may remove only malformed or unadmissible input records. The
selection-specific hard constraints remain explicit in the quantum problem and
lower to a feasible-subspace Projector or an equivalent named operator.

Soft preferences are normalized to a common finite scale before weighted
composition. The initial objective is a weighted finite objective; lexicographic
and Pareto objectives are later extensions.

If a penalty Hamiltonian is used, the report must identify it as a penalty
profile and must not claim that a low penalty guarantees feasibility.

## Result contract

The Host report contains:

- manifest ID, seed, compiler/profile identity, and deterministic ordering;
- terminal selection and observation metadata;
- feasibility result and violated constraints, if any;
- baseline score, objective score, and reranked score components;
- logical width, operation count, depth estimate, simulator budget, and lane;
- finiteization / lowering provenance and approximation policy;
- warnings and an explicit optimality claim, `none` by default.

An empty, missing, or unverifiable terminal observation is a failed result, not
a fabricated zero score.

## Acceptance scenarios

```gherkin
Feature: S02 classical and quantum boundary

  Scenario: candidate data stays classical
    Given a valid synthetic candidate manifest
    When the Host constructs a SelectionProblem
    Then candidate records and scores remain classical values
    And no implicit amplitude encoding is introduced

  Scenario: finite encoding is explicit
    Given a candidate set without finite encoding evidence
    When the Kernel boundary is prepared
    Then preparation fails with a finite-evidence diagnostic

  Scenario: hard constraints use a projector boundary
    Given a valid finite SelectionProblem with hard selection constraints
    When the quantum state is prepared
    Then hard constraints lower to a named Projector or equivalent operator
    And no terminal measurement occurs during projection

  Scenario: mix is not classical branching
    Given a state-valued alternative with multiple positive-weight arms
    When `mix` is evaluated
    Then every positive arm remains in the resulting State
    And no RNG call occurs

  Scenario: controlled is not mix
    Given a coherent controlled operation
    When the program requests `controlled`
    Then the operation retains its coherent-control meaning
    And it is not lowered to a probabilistic mixture

  Scenario: removed when spelling fails closed
    Given source containing `when` in the Static Kernel
    When the source is compiled
    Then compilation fails with a migration diagnostic
    And the compiler does not reinterpret the source as `mix`

  Scenario: only terminal measure crosses the classical boundary
    Given a valid evolved selection State
    When the program reaches terminal `measure`
    Then the result is an Outcome / classical selection
    And the Host report records the observation and resource metadata

  Scenario: same execution identity reproduces the result
    Given the same manifest, seed, compiler identity, and execution profile
    When the benchmark is replayed
    Then candidate ordering and report fields are identical

  Scenario: unsupported width fails before execution
    Given a finite encoding wider than the selected target profile
    When lowering is requested
    Then lowering fails with an explicit capability diagnostic
    And no classical optimizer is substituted
```

### Acceptance scenarios — `Projector<Selection>` semantics (ADR 0192, Phase 1 target, LISS-0322)

[ADR 0192](../architecture/adr/0192-s02-projector-selection-semantics.md)
(Accepted) found that `compiler/staqex/pipeline.py::_append_selection_projector_region`
is currently a hardcoded stub: it only checks whether *any* `project(...)`
call exists anywhere in `main`'s body, and if so, unconditionally appends
one `ProjectorRegion` with a literal `constraint_ref="S02.feasible"` —
identical for every S02 program regardless of source. The scenario above
("hard constraints use a projector boundary") is satisfied only in the
loose sense that *a* `ProjectorRegion` appears; it does not exercise the
predicate vocabulary, unknown-predicate rejection, or per-program
provenance. These scenarios define the Phase 1 target that closes that gap:

```gherkin
Feature: Projector<Selection> semantics (ADR 0192)

  Scenario: recognized predicates produce a source-derived constraint_ref
    Given `project selection onto feasible(exactly_selected = 2, pairwise_compatible = true)`
    When the program is lowered to the Quantum Semantic IR
    Then exactly one ProjectorRegion is produced
    And its constraint_ref reflects `exactly_selected` and `pairwise_compatible`
    And it is not the literal string `S02.feasible`

  Scenario: a different recognized predicate set produces a different constraint_ref
    Given `project selection onto feasible(diversity_at_least = 3)`
    When the program is lowered to the Quantum Semantic IR
    Then the resulting ProjectorRegion's constraint_ref differs from a
      program using `exactly_selected`/`pairwise_compatible`

  Scenario: an unrecognized predicate name fails closed
    Given `project selection onto feasible(unknown_rule = 1)`
    When the program is compiled
    Then compilation fails with an explicit capability diagnostic
    And no ProjectorRegion is produced

  Scenario: a penalty-only program produces no ProjectorRegion
    Given a program with a weighted Hamiltonian objective and no
      `project ... onto ...` expression
    When the program is lowered to the Quantum Semantic IR
    Then no ProjectorRegion is produced
    And the program is not rejected merely for lacking a Projector
```

### Acceptance scenarios — terminal observation and resource reporting (work unit D, Phase 1 target)

Work unit D's deliverable maps S02's classical/quantum boundary onto
already-shipped Kernel primitives rather than inventing new ones:
non-destructive `expect` (shipped, general-purpose), terminal `measure`
(shipped), and the terminal-measurement vacuum/incompleteness signal
(shipped; already used by the S01 showcase to detect an incomplete
terminal result under the same rule as the Result contract above). These
scenarios strengthen the Result contract's existing rule ("An empty,
missing, or unverifiable terminal observation is a failed result, not a
fabricated zero score") into checkable acceptance criteria. They do not
define `Observable<T>`/`Projection<T>`/`Observation<T>` as new Kernel
types — those remain WP-0092's own open decision — nor do they depend on
its resolution. The concrete Host-side representation (DTO/record shapes,
field names) is an implementation choice tracked in the implementing
Issue, not part of this normative contract.

```gherkin
Feature: S02 terminal observation and resource reporting

  Scenario: an empty or vacuum terminal observation is a failed result
    Given a Host report whose terminal measurement is vacuum or absent
    When the report is finalized
    Then the feasibility result is "failed"
    And no baseline, objective, or reranked score is fabricated

  Scenario: a valid terminal observation produces a real verdict
    Given a Host report with a non-vacuum terminal measurement
    When the report is finalized
    Then the feasibility result reflects the actual measurement
    And the terminal selection is recorded, not invented

  Scenario: resource and provenance metadata are passed through, not fabricated
    Given execution resource metadata is available
    When the report is finalized
    Then the report's resource metadata matches what execution provided
    And no resource field is invented when execution did not provide one

  Scenario: default optimality claim is none
    Given a finalized report with no explicit optimality evidence
    When the optimality claim is read
    Then it is `none`
```

### Acceptance scenarios — quantum selection state preparation (Phase 1 target, LISS-0324)

The normative benchmark shape's "quantum selection State" step
(`explicit finite encoding → quantum selection State → hard-constraint
Projector`) has no working Kernel implementation today. Direct
verification found `prepare_selection` is only a name in
`unitarity_check.py`'s quantum-lineage whitelist — calling it at runtime
fails with `RUNTIME_ERROR: unknown function \`prepare_selection\``. These
scenarios define the first real implementation: given a candidate count
`n` (a classical `Int`, not the full `Candidate` record set — per this
spec's own "Molecules and descriptors are not quantum states" rule,
candidate *identity* stays a Host concern and is never passed into the
Kernel; only the finite width crosses), `prepare_selection(n)` produces
an equal superposition over all `2^n` possible selection patterns
(matching "Encoding: one logical selection carrier per candidate"),
mechanically identical to `n` independent unconstrained qubits, ready for
a later `project ... onto feasible(...)` restriction (LISS-0322).

```gherkin
Feature: quantum selection state preparation

  Scenario: prepare_selection produces an equal superposition over all patterns
    Given a candidate count n
    When prepare_selection(n) is prepared
    Then the resulting state has exactly 2^n possible selection patterns
    And each pattern carries equal probability mass
    And no measurement or sampling has occurred yet

  Scenario: terminal measure yields one concrete selection pattern
    Given a prepared selection state for n candidates
    When the state reaches terminal measure
    Then the result is one specific n-length selection pattern
    And the same seed reproduces the same pattern

  Scenario: candidate identity never crosses into the Kernel
    Given a Host-side candidate manifest (LISS-0321)
    When the Kernel selection state is prepared
    Then only the finite candidate count crosses the boundary
    And no descriptor, score, or tag becomes a Kernel value
```

## Out of scope

- Real compound data adapters or chemical graph semantics.
- Clinical, efficacy, or ADMET claims.
- Live QPU provider SDKs and credentials.
- Automatic QUBO/QAOA rewriting.
- Pareto and lexicographic objective surfaces.
- General-purpose collection syntax.
- Compiler, grammar, evaluator, IR, or test changes before Phase 1 approval.
