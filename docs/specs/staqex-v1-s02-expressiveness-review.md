# S02 expressiveness review (Ideal vs Today, 2026-08-10)

| Field | Value |
|---|---|
| Status | **Architecture Path review — documentation only.** Authorizes no `.sqx`, compiler, or evaluator change. |
| Showcase | `examples/showcase/S02_drug_discovery/` (Host-only today — no `.sqx` file exists yet) |
| Parent docs | [S02 acceptance spec](staqex-v1-s02-drug-discovery-benchmark.md); [S02 design draft](staqex-v1-drug-discovery-benchmark-design.md) §10 (ideal-form sketch); [WP-0093](../architecture/../work-plans/WP-0093-s02-language-expressiveness-and-selection.md) |
| Companions | ADR 0190 (mission boundary, `mix`/`controlled`/`when`), ADR 0192 (`Projector<Selection>` predicate semantics), ADR 0194 (`HostInputPort`) — all Accepted |
| Precedent | Mirrors the [Continuous Lane B expressiveness scenarios](staqex-v1-continuous-lane-b-expressiveness-scenarios.md) review format, at the Adjudicator's request for an S01-style full review |

```markdown
[DESIGN CHECK]
- Scope: score S02's Ideal-form sketch (design draft §10.3) against what is
  actually Runtime-real today, surface by surface, and rank the remaining
  gap to close Work Unit E (classical baselines + end-to-end .sqx example).
- Not in scope: writing the .sqx example itself, new compiler/evaluator
  code, or amending ADR 0190/0192/0194.
- Verification: every "Today" cell below is either a direct source read
  (evaluator.py / pipeline.py dispatch confirmed) or an explicit "not
  found" after searching for it.
```

## 1. Why this review, and what it is not

WP-0093's own status line reads "remaining work unit E scope: classical
baselines and an end-to-end runnable `.sqx` example," which undersells how
much is actually already real: `prepare_selection` and `project ... onto
feasible(...)` both genuinely execute today (confirmed by direct source
read, not the acceptance spec's own prose). What is missing is not mostly
Kernel plumbing — it is that **nothing has ever assembled the pieces into
one program**, and one candidate step from the Ideal sketch
(`finiteize(candidates, witness = C16)`) does not exist in the form the
design draft sketched.

This review is a scorecard, like the Continuous Lane B review, not a claim
that S02 is a finished showcase.

## 2. Ideal form (design draft §10.3, unchanged)

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

## 3. Ideal vs Today — surface by surface

| Ideal line | Today (Runtime-real?) | Gap |
|---|---|---|
| `finiteize(problem.candidates, witness = C16)` | **No.** `finite_boundary.py`'s `FiniteManifestWitness` is the real shipped equivalent (LISS-0321) — but it is **Host-only Python**, never a Kernel-callable form, and its own module docstring explicitly disclaims reuse of the Kernel `finiteize` op ("this is a general numeric finiteization primitive, not a candidate-manifest witness"). No `.sqx` source can express "here is my finite-width witness" today — the width just becomes a bare `Int` passed to `prepare_selection`. | **B** — the *ideal* reading (an explicit, source-visible finiteization step naming its own witness) has no Kernel-visible form; only the Host-side Python object exists. This is the design draft's own P0 priority item ("makes the classical-to-finite quantum encoding visible"), still unshipped as Kernel syntax. |
| `state ψ0 = prepare_selection(C)` | **Yes**, real — confirmed `Evaluator._bind_prepare_selection` (LISS-0324): equal superposition over `2^n` selection patterns via `Joint.bind_split`, same primitive `coin()`/`finiteize(...)` already use. Signature is `prepare_selection(n: Int)`, not `prepare_selection(C)` where `C` is a finite witness object — `n` is a bare `Int`, matching the disclosed gap above. | **A** (keep) for the collapse-free equal-superposition semantics; **E** (honesty) that its argument is a bare width, not the witness the Ideal line implies. |
| `Projector P = feasible(exactly_selected(...), pairwise_compatible(...), diversity_at_least(...))` | **Partially yes.** The real shipped grammar (ADR 0192, confirmed in `pipeline.py`) is `project selection onto feasible(exactly_selected = N, pairwise_compatible = true, diversity_at_least = N)` — a `project ... onto` expression whose target is a `feasible(...)` kwargs Call, **not** a separately-named `Projector P = feasible(...)` value bound before use. `exactly_selected`/`pairwise_compatible`/`diversity_at_least` are recognized predicate *keyword arguments*, not the Ideal sketch's own nested Call-per-predicate shape (`exactly_selected(ψ0, 2..4)`). Execution is real: confirmed in `evaluator.py` — `exactly_selected` filters `prepare_selection`'s world patterns by bit-count; `pairwise_compatible`/`diversity_at_least` route through `HostInputPort` (ADR 0194) for Host-computed matrices. | **A** (keep) for the real filtering execution; **E** (surface honesty) — the shipped grammar is flatter and less physics-readable than the Ideal sketch's per-predicate Call nesting; not a functional gap, a spelling gap. |
| `Operator H = weighted(activity(weight=...), selectivity(weight=...), ...)` | **No dedicated form.** WP-0093's own candidate table (P1, "Named objective terms and normalized weights... avoid new arithmetic syntax") never promoted this past design-draft status. The only real path today is S01's own precedent: Type-First `Float` weights combined via ordinary Operator algebra (as `constraint_h.sqx` does for `ConstraintCoeffs`) — reusable, but not yet demonstrated for S02's own named terms (`activity`/`selectivity`/`diversity`/`cost`). | **B** — real Operator-algebra machinery exists and is proven (S01), but no S02-specific worked example proves it reads naturally for named weighted objective terms; this is squarely inside Work Unit E's "end-to-end `.sqx` example" gap, not a new Kernel feature. |
| `ψ0 |> project onto P |> evolve under H for τ` | Each stage is individually real (`project onto feasible(...)`, `evolve under H for τ` — both shipped, pipe composition shipped ADR 0080/0137). **Never composed together for S02** — no `.sqx` file exists to prove the pipe reads cleanly end to end for this specific workflow. | **B** — composition risk, not a missing primitive. Untested combination, not an unshippable one. |
| `measure ψ` | **Yes**, shipped, unchanged. | — (keep) |

**Class key** (same convention as the Continuous Lane B review): **A** = physics/language law, keep as-is; **B** = needs-work but has a real path (not blocked); **E** = surface/honesty polish, not a functional gap.

## 4. What "Runtime-real" actually means today (confirmed by direct source read)

Contrary to WP-0093's own summary line reading as if only "classical
baselines + example" remain, three separate pieces of real Kernel/Host
execution already exist and were individually confirmed in this review:

1. `prepare_selection(n)` — real `Joint.bind_split` equal superposition
   (`evaluator.py::_bind_prepare_selection`).
2. `project ... onto feasible(exactly_selected=…, pairwise_compatible=…,
   diversity_at_least=…)` — real world-filtering execution, confirmed
   against `evaluator.py`'s predicate-handling block (bit-count filter for
   `exactly_selected`; `HostInputPort`-backed matrix lookups for the other
   two).
3. `FiniteManifestWitness` (Host-only) — real input hygiene validation
   (`finite_boundary.py`), confirmed to explicitly *not* touch the Kernel
   `finiteize` op.

None of this was previously scored in one place; the WP-0093 status line
undercounts what is real and leaves an inaccurate impression that Work Unit
E is "mostly plumbing left." It is not — it is one missing Kernel-visible
finiteization step (Class B) plus assembly risk (Class B) plus one
never-written program.

## 5. Language-design findings (ranked)

### P0 — No `.sqx` file exists for S02 at all

Every other showcase surface question is secondary to this: S02 currently
has zero Kernel source. `examples/showcase/S02_drug_discovery/` contains
only `host/domain.py`, `host/finite_boundary.py`, `host/benchmark_result.py`
— no `.sqx`. Nothing in this review is verifiable end to end without one.

### P1 — Finite-witness step has no Kernel-visible form (Class B)

`finite_boundary.py`'s `FiniteManifestWitness` is real but Host-only. The
Ideal sketch's `finite C = finiteize(problem.candidates, witness = C16)`
line is aspirational, not a small syntax gap — no such Kernel-callable
statement is dispatched anywhere in `evaluator.py`. Closing this would need
a genuinely new Kernel surface (a Type-First `finite` binding form, or a
new Call analogous to `field_from_host`/`prepare_selection` that accepts a
Host-side witness object) — itself an Architecture Path question, not
something to invent inside Work Unit E's Feature Path scope.

### P1 — Named weighted objective terms have no S02-specific proof (Class B)

The physics machinery (Type-First `Float` + Operator algebra) is proven by
S01's `constraint_h.sqx`, but never demonstrated for S02's own
`activity`/`selectivity`/`diversity`/`cost` vocabulary. This is squarely a
Work Unit E deliverable (the `.sqx` example itself proves or disproves this
reads naturally) — not a new Kernel feature request.

### P2 — `feasible(...)` predicate spelling is flatter than the Ideal sketch (Class E)

Shipped: `feasible(exactly_selected = N, pairwise_compatible = true,
diversity_at_least = N)` (kwargs on one Call). Ideal sketch:
`feasible(exactly_selected(ψ0, 2..4), pairwise_compatible(problem.constraints),
diversity_at_least(problem.constraints))` (nested per-predicate Calls). The
shipped form is less physics-readable but already Accepted via ADR 0192 —
re-litigating the grammar is out of scope for this review; noted for
completeness, not actioned.

## 6. Recommended next slice (not authorized by this document)

This review's own recommendation, mirroring the Continuous Lane B
precedent's "next gates" section:

| Gate | Artifact | Notes |
|---|---|---|
| Write the end-to-end `.sqx` example (Work Unit E) | New LISS under WP-0093 | Composes `prepare_selection` + `project onto feasible(...)` + Operator-algebra objective + `measure`, using the bare-`Int` width the Kernel already accepts (not the Ideal sketch's witness form) — proves or disproves P1's objective-term finding concretely |
| Classical baselines (Work Unit E) | Host Python, same LISS or a sibling | Greedy + exact small-instance baseline, per the design doc §7 "Baseline discipline" requirement — no Kernel change |
| Kernel-visible finite-witness surface (P1 finding) | Future Architecture Path ADR, only if the `.sqx` example above finds it genuinely needed | Do not invent ahead of demonstrated need — matches this session's own reconfirmed precedent for Joint rational mode and trait/effect: require a concrete requirement before opening new Kernel surface |

This document authorizes documentation/scoring only, per the same boundary
the Continuous Lane B review used.
