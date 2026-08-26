# S02 drug discovery benchmark design

| Field | Value |
|---|---|
| Status | **Design draft — mission boundary and `mix`/`controlled`/`when` taxonomy accepted via [ADR 0190](../architecture/adr/0190-s02-selection-boundary-and-mix-control.md) and promoted into the [accepted S02 acceptance specification](staqex-v1-s02-drug-discovery-benchmark.md); work unit A (language surface) implemented (PR #337). The remaining design content in this draft — `Projector`/`FiniteDomain` contracts, §8's open items, and work units B–E — is not yet promoted to an ADR or a reviewed target spec; this draft alone still does not authorize `.sqx` implementation** |
| Source prompt | `drug-discovery-benchmark/final-agent-prompt.md` |
| Supporting material | `drug-discovery-benchmark/related-materials.md`, `manifest.json` |
| Current naming decision | Preserve the locked disaster-response S01; this benchmark is **S02** |
| Work plan | [WP-0093](../work-plans/WP-0093-s02-language-expressiveness-and-selection.md) |
| Acceptance specification | [S02 benchmark specification](staqex-v1-s02-drug-discovery-benchmark.md) |
| Intended purpose | Stress-test Staqex expressiveness at the classical/quantum boundary with an indication-agnostic early drug-discovery workflow |

```markdown
[DESIGN CHECK]
- Scope and expected behavior: define a finite, reproducible, disease-agnostic
  early drug-discovery benchmark that exposes Staqex language gaps. This turn
  designs the benchmark and its acceptance boundary; it does not edit .sqx,
  compiler behavior, tests, datasets, or QPU adapters.
- Specifications and files inspected: supplied final-agent-prompt.md,
  related-materials.md, manifest.json; the locked S01 scenario, S01 redesign,
  S0 specification, language axioms, language vision, readiness checklist,
  and open-work register.
- Component boundaries, ports/adapters, and VO/DTO candidates: Host owns
  dataset loading, candidate generation, classical scoring, baselines,
  resource reporting, and terminal result export. The Static Kernel owns only
  the finite quantum selection subproblem. Candidate, Constraint, Score,
  SelectionProblem, Seed, ResourceProfile, and BenchmarkResult are proposed
  value objects / DTOs; no persistence or provider SDK is introduced.
- Applicable constraints: Never Leave the State; `when` is for conditional
  state transformation only, `controlled` is reserved for coherent control,
  and terminal `measure` remains the classical result boundary; fail-closed
  capability checks; provider-neutral QPU boundary;
  current shipping path is Python simulator and no live QPU adapter.
- Decisions, assumptions, unresolved ambiguities: S02 is selected as a new
  benchmark track; the locked disaster-response S01 remains unchanged.
  Dataset family, molecule representation, quantum encoding, selection size,
  and acceptance thresholds remain to be approved. The design uses a small
  synthetic fixture first; real compound data is not required for the language
  benchmark.
- Included and omitted AI context: included only the supplied benchmark prompt
  and project contracts needed for the boundary. Omitted unrelated examples,
  private records, credentials, and unreviewed external scientific claims.
- Task routing: architecture review for naming, scenario, and boundary;
  deterministic tools for fixture validation and reproducibility checks;
  implementation assistant only after an accepted spec and named Issue.
- Input/output evidence contract when AI output is involved: any generated
  candidate annotation must carry source_refs, confidence, review_status,
  assumptions, and warnings. Unreviewed annotations cannot become trusted
  benchmark facts.
- Verification plan: schema validation, fixed-seed replay, classical baseline
  replay, quantum-lane resource estimate, fail-closed unsupported-target
  checks, and comparison of measured selections against constraint invariants.
```

## 1. Naming and relationship to the existing S01

The repository already has an accepted and locked **S01 — Quantum Disaster
Response OS**. Its story, tree, scorecard, and implementation are not
replaceable by this draft without an explicit architecture decision and a
scenario-lock amendment.

The direction is now selected:

| Choice | Meaning | Assessment |
|---|---|---|
| S01 | Keep the accepted disaster-response showcase and its existing implementation tree | **Retained** |
| S02 | Add this indication-agnostic early drug-discovery benchmark as the next showcase benchmark | **Selected** |

This document is the **S02 design draft**. It is not yet the accepted S02
specification and does not authorize `.sqx` implementation.

## 2. Benchmark question

Can a physicist express a useful early-discovery selection experiment in
Staqex while seeing, in one reading, which objects are classical data, which
objects remain quantum states, which constraints are mathematical, and where
the final classical result is obtained?

The benchmark is not a drug-efficacy claim, a clinical recommendation, a
virtual-screening leaderboard, or evidence that quantum computation beats a
strong classical optimizer.

## 3. Fixed benchmark workflow

```text
Dataset manifest
  → classical candidate / fragment generation
  → hard-constraint pruning
  → classical pre-score and baseline ranking
  → finite quantum constrained-selection subproblem
  → terminal measurement of selected-set state
  → classical rescoring / reranking
  → result + provenance + resource report
```

The quantum lane receives a finite `SelectionProblem`, not an unbounded
molecule database. Each candidate has a stable ID, a feature vector or
descriptor reference, a pre-score, and constraint annotations. The first
fixture should contain 8–16 candidates and a target selection size of 2–4 so
that the simulator remains a language test rather than a hardware claim.

## 4. Semantic model

### 4.1 Classical domain objects

- `Candidate`: immutable molecule or fragment record; stable ID and canonical
  representation are required.
- `TargetProfile`: abstract target binding / property profile; no disease name
  is required.
- `Constraint`: hard feasibility rule such as maximum set size, incompatibility,
  diversity, property interval, or resource budget.
- `Score`: named component with provenance, scale, and direction.
- `SelectionProblem`: finite candidate set, constraints, objective weights,
  seed, and resource profile.

Molecules and descriptors are **not** quantum states. Treating a SMILES string,
graph, or classical score as if it were already an amplitude would obscure the
boundary the benchmark is meant to test.

### 4.2 Quantum object

The quantum subproblem represents a candidate-selection state:

```text
State<Selection<CandidateId>>
```

The state contains feasible and infeasible selection world-lines until the
constraint Hamiltonian / projector removes or penalizes invalid support. It is
not measured during candidate generation, pruning, or intermediate scoring.
Only the terminal selection observation collapses it to an executable set.

The initial implementation may use a QUBO-like finite objective internally,
but the public design should name the physical object (`H_selection`, penalty
projectors, expectation, and terminal observation) rather than expose a
vendor-specific optimization API.

## 5. Surface-shape proposal

The following is **ideal chalk**, not a claim about currently shipped syntax:

```text
let problem: SelectionProblem = prepare(candidates, constraints, objective)
let ψ: State<Selection<CandidateId>> = prepare |0⟩

let ψ' = ψ
  |> project onto feasible(problem.constraints)
  |> evolve under H_selection(problem)

let selection: Selection<CandidateId> = measure ψ'
let result = rerank(problem, selection)
```

The example is intentionally short, but its lowering must remain explicit:

```text
Candidate[] / Constraint[] / Score[]  -- Host classical values
        ↓ finiteize + encode
SelectionProblem                       -- boundary DTO
        ↓ lower to State/Hamiltonian IR
State<Selection<CandidateId>>           -- no collapse
        ↓ terminal measure
Selection + BenchmarkResult             -- classical report
```

If the current compiler cannot express this surface, the implementation must
not fake it with ordinary `if`, hidden sampling, or a Host-side classical
optimizer presented as quantum execution. Record each gap in the friction
ledger or a named Issue.

## 6. Required boundary contracts

### Host → Kernel

The finite input envelope must contain:

- schema version and benchmark instance ID;
- ordered candidate IDs and canonical feature references;
- hard constraints and objective terms;
- seed and deterministic ordering policy;
- requested logical width / target capability profile.

The Kernel must reject missing dimensions, non-finite coefficients, duplicate
IDs, unsupported constraint forms, and a requested width beyond the target
profile.

### Kernel → Host

The result envelope must contain:

- terminal measured selection and observation metadata;
- feasibility verdict and violated-constraint list, if any;
- pre-score, quantum objective value, and post-score components;
- seed, logical width, operation count, simulator/QPU lane, and lowering policy;
- warnings, approximation/error budget, and optimality claim (`none` by default).

An empty or unverifiable measurement is a failure, not a zero-score candidate.

## 7. Evaluation matrix

The benchmark compares representations and contracts, not only runtime:

| Dimension | Required evidence |
|---|---|
| Physics reading | State/operator/observation boundary is visible and no mid-program collapse occurs |
| Classical/quantum boundary | Host inputs and terminal outputs are typed and explicit |
| Constraint honesty | Invalid selections cannot silently appear feasible |
| Reproducibility | Same manifest + seed reproduces the same candidate ordering and report |
| Baseline discipline | Greedy and exact small-instance classical baselines are included |
| Quality | Feasibility rate, objective gap to exact baseline, top-k overlap, diversity, and reranking stability |
| Resource honesty | Logical width, operation count, depth estimate, simulator budget, and target capability are reported |
| Failure clarity | Unsupported encodings and resource overflow fail before submission |
| Surface economy | No Java/Kotlin-style object ceremony or vendor-specific QPU calls in the physics spine |

The benchmark must not claim quantum advantage from a single small fixture.
Report quality and cost separately, and retain the classical baseline as the
reference result.

## 8. Missing specification that must be resolved before implementation

1. **Candidate representation:** canonical SMILES, graph IR, or an abstract
   benchmark record. Recommendation: abstract record plus optional canonical
   string; graph chemistry is not required for the first language slice.
2. **Objective:** weighted sum, lexicographic objective, or Pareto frontier.
   Recommendation: weighted finite objective first, Pareto as a later chapter.
3. **Quantum encoding:** one qubit per candidate, compact binary index, or
   grouped register. Recommendation: one Boolean selection carrier per
   candidate for clarity, with an explicit width limit.
4. **Constraint semantics:** penalty Hamiltonian versus projector / filtering.
   Recommendation: preserve both as named physical alternatives; select one in
   an ADR before implementation.
5. **Data policy:** synthetic fixture versus public compound dataset.
   Recommendation: synthetic fixture for the language benchmark; public data
   can be a separately reviewed adapter.
6. **Acceptance threshold:** define tolerances for feasibility, objective gap,
   reproducibility, and resource reporting before Phase 1 tests.

## 9. Recommended implementation slices after approval

| Phase | Scope | Result |
|---|---|---|
| Design approval | Choose ID, naming, fixture, encoding, objective, and constraint semantics | Accepted spec + Issue |
| Phase 1 Red | Contract tests for manifest, finiteization, boundary, seed, and fail-closed diagnostics | Failing tests only |
| Phase 2 Green | Host fixture, classical baselines, and the smallest simulator-backed quantum selection slice | Minimal implementation |
| Phase 3 Refactor | Physicist-readable source, provenance report, resource report, and benchmark README | Reviewed showcase |

No QPU provider, credentials, network adapter, real-data ingestion, or AI
provider belongs in the first implementation wave.

## 10. S02 language expressiveness upgrade

S02 should first reuse the language that already exists. A new syntax layer
would make the benchmark measure syntax volume instead of the quality of the
classical/quantum boundary.

### 10.1 Existing expressive surface to reuse

| Existing surface | S02 role | Assessment |
|---|---|---|
| `State<T>` | `State<Selection<CandidateId>>` | Core semantic fit; keep |
| Operator algebra / finite binders | Named selection Hamiltonians and score terms | Core physics fit; keep |
| `project` | Feasible-subspace projection; hard constraints lower to a Projector | Semantically correct direction; current operand contract needs a projector form |
| `expect` | Non-destructive objective / constraint diagnostics | Keep separate from measurement |
| `evolve under H` | Soft preference evolution | Core quantum experiment; keep |
| `when` → `mix` | Conditional state transformation / state-valued alternatives | `mix` is the S02 spelling; do not use it as a classical constraint filter |
| `controlled` / `Ctl` | Coherent control of an operation | Reserved for coherent control; not a synonym for `mix` |
| terminal `measure` | Final selected set and classical result boundary | Required; no intermediate sampling |
| Host Job / JobResult | Fixture, baseline, resource and provenance envelope | Keep outside the Kernel |

The important correction is that `mix` is not a replacement for every
predicate. In S02, a feasibility constraint should be represented by a
Projector lowering into a feasible subspace or by an explicit operator, not
by an `if`-shaped or `mix`-shaped filter. `controlled` is reserved for
coherent control and is not a synonym for `mix`.

The separate `mix` / `controlled` review is tracked in [WP-0093](../work-plans/WP-0093-s02-language-expressiveness-and-selection.md)
and coordinated with [WP-0092](../work-plans/WP-0092-quantum-mental-model-follow-up.md).

### 10.2 Candidate additions, ordered by value

| Priority | Candidate | Why it improves expressiveness | Proposed boundary |
|---|---|---|---|
| P0 | `FiniteDomain<T,N>` / explicit `finiteize` witness | Makes the classical-to-finite quantum encoding visible | Surface + lowering contract; reject missing or oversized finite evidence |
| P0 | `Selection<CandidateId>` carrier | Gives the state a physics-readable payload instead of anonymous bits | Library type first; no chemistry dependency |
| P1 | `Projector<Selection>` or `project ψ onto P` | Distinguishes hard feasible-subspace projection from soft penalty evolution | New semantic/type specification before implementation |
| P1 | Named objective terms and normalized weights | Keeps `activity`, `selectivity`, `diversity`, and `cost` readable in the Hamiltonian | Domain library / metadata first; avoid new arithmetic syntax |
| P1 | Constraint-to-projector lowering contract | States exactly which hard constraints are encoded and how failures are diagnosed | IR/provenance contract; not hidden compiler policy |
| P1 | Selection/register resource witness | Reports candidate count, logical width, operation count, and target profile | Host DTO + capability diagnostic; reuse `QubitRegister<N>` where applicable |
| P2 | Alternative encodings | Enables one-hot vs compact-index comparisons without changing the benchmark story | Separate encoding profile, never implicit lowering |
| P2 | Lexicographic / Pareto objectives | Tests richer scientific objectives after weighted finite objectives are stable | Later benchmark chapter; not S02 minimum |

### 10.3 Recommended ideal-form sketch

The following is a design sketch, not currently shipped syntax:

```text
finite C = finiteize(problem.candidates, witness = C16)
state ψ0: State<Selection<CandidateId>> = prepare_selection(C)

Projector P = feasible(
  exactly_selected(ψ0, 2..4),
  pairwise_compatible(problem.constraints),
  diversity_at_least(problem.constraints)
)

Operator H = weighted(
  activity(weight = 0.45),
  selectivity(weight = 0.30),
  diversity(weight = 0.20),
  cost(weight = -0.05)
)

state ψ = ψ0 |> project onto P |> evolve under H for τ
measure ψ
```

The desired reading is: prepare a finite selection state, restrict it to the
feasible subspace, evolve under a named physical objective, and observe once.
The compiler must not silently replace this with a classical optimizer.

### 10.4 What should not be added for S02

- No `Molecule` quantum primitive: a molecule record is classical input data.
- No vendor-specific `qubo`, `qaoa`, or provider call in the surface language.
- No implicit conversion from a feature vector to amplitudes.
- No hidden measurement in scoring, pruning, or ranking.
- No new general-purpose collection language solely for this benchmark.
- No Pareto, chemistry graph algebra, or public-dataset adapter in the first
  implementation wave.

These omissions keep S02 focused on the language's mental model rather than
turning it into a chemistry framework.

## 11. Recommendation for adjudication

**Update (2026-08-04):** the recommendation below was acted on. S02 was
accepted as the next benchmark direction (S01 unchanged); [ADR 0190](../architecture/adr/0190-s02-selection-boundary-and-mix-control.md)
covers the mission boundary and the `mix`/`controlled`/`when` taxonomy
(Accepted); the [S02 acceptance specification](staqex-v1-s02-drug-discovery-benchmark.md)
is Accepted; and work unit A (language surface) is implemented (PR #337,
`321de3a`), later refined by the `superpose` formal grammar
([LISS-0320](../issues/LISS-0320-superpose-formal-grammar.md) / PR #345).
The `Projector`/`FiniteDomain` contract and the P0/P1 candidates below
remain **not** promoted to an ADR — WP-0093 work units B–E have no Local
Issue yet. The original recommendation text is kept below for its rationale.

Accept S02 as the next benchmark direction while retaining S01 unchanged.
Accept the P0/P1 language candidates as design work only; do not update the
normative language specification until the `Projector` contract and finite
encoding witness are reviewed. Create or update the S02 ADR for the mission
boundary and selected quantum constraint semantics. After that decision,
promote the selected parts into a target spec and local Issue; do not begin
`.sqx` implementation from this draft alone.
