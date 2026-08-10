# LISS-0403: S02 multi-shot benchmark report (real scores, resource metadata, quality metrics)

## Metadata

- Local issue ID: LISS-0403
- Status: complete
- Type: Feature Path (Host Python only — no compiler/evaluator/hir.py change)
- Priority: P1
- Planning size: `M`
- Owner / agent: Claude Code
- Parent: [WP-0093](../work-plans/WP-0093-s02-language-expressiveness-and-selection.md);
  follow-on to [LISS-0402](LISS-0402-s02-selection-example.md)
- Related: `examples/showcase/S02_drug_discovery/host/benchmark_result.py`
  (LISS-0323, extended additively)
- Branch: `feature/liss-0403-s02-benchmark-report`
- GitHub Issue / PR: (opened at Completion)

## Intent

LISS-0402 proved S02's workflow is *expressible* (a real `.sqx` program
exists and runs). It deliberately did not prove the workflow *reports like
a benchmark* — the Adjudicator's own follow-up question ("言語の可能性を
測るベンチマーク的な実装も出来ている?") confirmed this gap directly:
`benchmark_result.py`'s own docstring admitted `baseline_score`/
`objective_score`/`reranked_score`/quality metrics were deferred and
never computed. This Issue closes that gap for real, per the S02
acceptance spec's Result contract and the design doc §7 Evaluation
matrix.

## Design verification performed before / during implementation

1. **Confirmed `BenchmarkResult` (LISS-0323) never computed real scores**
   — its own module docstring said so explicitly before this Issue
   touched it.
2. **Caught a real degenerate-scoring bug before it silently corrupted
   every quality metric.** The first `classical_score` implementation
   (reused from LISS-0402, unchanged) summed `Z` per selected candidate
   plus `ZZ` over *all* pairs with uniform weights. Ran it against the
   full feasible set (`exactly_selected=3` over `n=8`) and found **every
   single feasible pattern scored exactly the same** (`-1.3`). Root
   cause, confirmed by hand: `sum_{i<j} s_i s_j = ((sum s)^2 - n) / 2` for
   `s_i = ±1`; once `exactly_selected` fixes `sum(s)`, that formula is a
   constant, not a function of *which* candidates were picked. This is
   exactly the kind of thing a real multi-shot benchmark run — not a
   single "it compiled" check — is supposed to catch, and did.
3. **Fixed by switching to per-candidate synthetic scores**
   (`build_candidate_scores`, a toy deterministic `(activity,
   selectivity)` pair per candidate index) summed over the *selected*
   candidates only — genuinely discriminates between patterns, confirmed
   by checking `len({classical_score(p) for p in feasible}) > 1` (now a
   regression test).
4. **Confirmed, honestly, that the Kernel's own `H_obj` evolution cannot
   score a specific selection either way** — not just a classical-scoring
   quirk. `H_obj` acts on a 2-qubit objective register that never
   receives candidate identity (per the spec's own boundary rule, "only
   the finite width crosses into the Kernel") — there is no Kernel-side
   channel today through which a per-candidate score could reach the
   evolved objective state. This is architectural, not a scoring
   omission this Issue could fix without inventing new Kernel surface
   (explicitly out of scope, see below).
5. **`top_k_overlap` empirically confirms the real, disclosed
   architecture gap LISS-0402 already predicted**: with correctly
   discriminating scores, `top_k_overlap` measured `0.0` across 20 shots
   — `project onto feasible(...)` samples uniformly over the feasible
   subspace regardless of `H_obj`'s evolution, because they are separate
   coordinates (LISS-0402 finding). The benchmark report now surfaces
   this as a `warnings` entry automatically (`top_k_overlap < 0.5`), not
   a silent number — this is the S02 design doc's own stated purpose
   ("record each gap in the friction ledger or a named Issue") working
   as intended.
6. **`feasibility_rate` is definitionally `1.0`** — `project onto
   feasible(...)` restricts the Joint to the feasible subspace *before*
   terminal `measure`, so every shot is feasible by construction. Encoded
   as an explicit regression assertion (not just observed), since a
   future change to the projector semantics silently breaking this would
   otherwise go unnoticed.
7. **Compiled `main_selection.sqx` once, evaluated `shots` times** via
   direct `Evaluator(seed=...).run_unit(compiled.unit)` calls rather than
   `shots` separate `submit_path` calls — avoids redundant recompilation;
   `submit_path`'s extra machinery (HARD_CODES gating, `JobResult`
   construction) isn't needed for this orchestration, which is benchmark
   scoring, not a compile-pipeline test.

## Scope

1. Extended `BenchmarkResult` (`host/benchmark_result.py`) additively:
   `baseline_score`, `objective_score`, `reranked_score`,
   `quality_metrics`, `warnings` fields, all defaulting to
   `None`/empty so the existing LISS-0323 single-shot builder
   (`build_benchmark_result`) is unchanged and still valid.
2. New `host/scoring.py` — shared `classical_score`/`is_feasible`/
   `build_candidate_scores`, extracted so the baseline and the report
   never independently drift on "the same" formula.
3. Refactored `host/classical_baseline.py` to use the shared module
   (`exact_feasible_patterns` now importable, reused by the report).
4. New `host/benchmark_report.py` — `build_report(shots, base_seed)`:
   runs `shots` evaluations, computes real baseline/objective/reranked
   scores, resource metadata (logical width, candidate count, Suzuki
   params — read from the `.sqx` source's own known constants, not
   invented or introspected via a nonexistent Kernel API), quality
   metrics (feasibility rate, mean objective, objective gap to the exact
   baseline, top-k overlap, reproducibility), and auto-generated
   `warnings` when a metric reveals a real limitation.
5. Regression tests: scoring discrimination (catches the class of bug
   found in point 2 above), report shape/honesty, reproducibility.

## Explicitly out of scope

- Any change to `main_selection.sqx`, the compiler, or the evaluator —
  the disconnect between hard-constraint sampling and soft-objective
  evolution (point 4/5 above) is a real, disclosed architecture finding,
  not fixed here. Closing it would require new Kernel surface (e.g. a way
  for `H_obj` to receive per-candidate weights, or for `project onto
  feasible(...)` to sample non-uniformly) — a new Architecture Path
  question, not invented ahead of the Adjudicator's own review, matching
  this session's precedent (Joint rational mode, trait/effect) of not
  opening new Kernel surface without a demonstrated concrete need beyond
  "the benchmark revealed a gap."
- Real chemistry-derived candidate scores — `build_candidate_scores`
  stays a disclosed toy synthetic fixture, per the spec's own "synthetic
  fixture for the first implementation" rule.
- Multiple manifest fixtures / sweeping `n` or `exactly_selected` — one
  fixture, matching LISS-0402's own scope.

## Exit criteria

- [x] `BenchmarkResult` extended additively; existing LISS-0323 builder
  unchanged and still passes.
- [x] `benchmark_report.py` produces real, non-fabricated
  baseline/objective/reranked scores and resource metadata.
- [x] Quality metrics computed for real: feasibility rate (`1.0` by
  construction, asserted), mean objective score, objective gap to exact
  baseline, top-k overlap, reproducibility.
- [x] The degenerate-scoring bug (Design verification point 2) fixed
  before it reached a merged state; regression test guards against
  recurrence.
- [x] `top_k_overlap`'s low value is surfaced as an explicit `warnings`
  entry with an honest explanation, not silently reported as a bare
  number.
- [x] Full regression sweep: **1446 passed**, up from 1443 by exactly the
  3 new tests.
