# LISS-0321: S02 Host domain records and finite boundary (WP-0093 work unit B)

## Metadata

- Local issue ID: LISS-0321
- Status/phase: **final-review-ready** / `phase-3-refactor` (2026-08-04) —
  Phase 3 complete; awaiting Adjudicator Completion approval and PR.
  Decisions from Plan approval: (1) domain module lives under
  `examples/showcase/S02_drug_discovery/host/` only — S01's `domain/`
  convention turned out to mean `.sqx` Kernel source, which this
  Host-only Issue does not have, so both the classical records and the
  finite-boundary witness live under `host/`; (2) greedy/exact classical
  baselines stay out of this Issue, deferred to work unit E; (3) work unit
  C's `Projector<Selection>` ADR is filed separately, right after this
  Issue closes, not in parallel.
- Type: Feature Path (Host-side domain records + boundary validation; no Kernel
  grammar/typecheck/evaluator change)
- Priority: P1
- Initial planning size: `L`
- Current planning size: `L`
- Owner / agent: Claude Code
- Program: [WP-0093](../work-plans/WP-0093-s02-language-expressiveness-and-selection.md)
  work unit B; related [WP-0092](../work-plans/WP-0092-quantum-mental-model-follow-up.md)
- Parent: [ADR 0190](../architecture/adr/0190-s02-selection-boundary-and-mix-control.md)
  (Accepted); [S02 acceptance specification](../specs/staqex-v1-s02-drug-discovery-benchmark.md)
  (Accepted)
- Depends on: none. This Issue is deliberately scoped to be Host-side only
  (Python DTOs + Host input hygiene), so it does not need the
  `Projector<Selection>` semantics ADR that work unit C still requires.
- Blocks: work unit C (constraint/objective/Projector semantics — needs its
  own ADR, not started), work unit D (observation/result contract), work
  unit E (conformance scenarios 3, 8, 9 below — reproducibility and
  capability rejection need the fixture this Issue produces)
- Related: [LISS-0320](LISS-0320-superpose-formal-grammar.md) (unrelated
  language-surface slice, same session)
- Branch: `batch/wp-0093-liss-0321-s02-host-domain` (renamed twice: the
  investigation branch → `feature/liss-0321-...` → `batch/wp-0093-liss-0321-...`
  once CI's `check-execution-batch-reviews.py` required the `batch/<batch-id>`
  convention for any branch backed by an execution-batch review record;
  investigation commit `b8bd2de` is first)
- GitHub Issue / PR: none yet

## Intent

Implement the classical (Host-side) half of the S02 benchmark shape defined
in the already-**Accepted** [S02 acceptance specification](../specs/staqex-v1-s02-drug-discovery-benchmark.md#value-model)
§"Value model" / §"Fixture limits", without touching the Kernel language
surface (no new grammar, no new typecheck rule, no evaluator change). This
covers WP-0093 work unit B items 1–4:

1. `CandidateId`, `Candidate`, `TargetProfile`, `Constraint`, `Score`, and
   `SelectionProblem` as Host-side Python domain records (dataclasses),
   matching the spec's "Value model" §"Classical records" exactly — stable
   `CandidateId`, descriptor reference, score components, tags, provenance
   for `Candidate`; named rule + domain for `Constraint`; normalized finite
   component + direction + weight + provenance for `Score`; ordered
   candidates + target profile + hard constraints + soft objective terms +
   selection size + seed + encoding profile + resource profile for
   `SelectionProblem`.
2. An explicit finiteization witness for the 8–16 candidate / 2–4 selection
   synthetic fixture (spec §"Fixture limits"). The Kernel's existing
   `finiteize(lo, hi, bins, samples, seed)` op (already shipped, ADR 0185 /
   LISS-0313) is a **general numeric finiteization primitive**, not a
   candidate-manifest witness — this Issue defines the Host-side witness
   that proves a `SelectionProblem`'s candidate set is finite, bounded, and
   ID-unique *before* it reaches the Kernel boundary. It does not reuse or
   modify `finiteize`.
3. Separate Host input hygiene (malformed/duplicate/missing/out-of-domain
   record rejection — ADR 0190 item 5) from quantum selection constraints
   (which stay in the Kernel boundary per work unit C, not this Issue).
4. Reject missing, duplicate, non-finite, oversized, or unproven finite
   input with explicit, distinct failure reasons (not a single generic
   error).

## Scope note: what already exists vs. what this Issue adds

`tests/test_s02_selection_surface_red.py` (already green, part of PR #337)
demonstrates that the **generic** language building blocks tolerate
S02-shaped names — `finiteize(...)`, `prepare_selection(candidates)`,
`project ... onto feasible(...)` — but verified by direct source inspection
that:

- `prepare_selection` is only a name registered in
  `unitarity_check.py`'s `_QUANTUM_OPS` whitelist (marks a call as
  "quantum-lineage", nothing else) — there is no actual selection-state
  preparation implementation.
- `feasible(...)` is not a registered stdlib function anywhere — the
  `project X onto feasible(...)` test passes because the **general**
  `project ... onto <call-expr>` syntax already produces a `ProjectorRegion`
  regardless of what the callee means, not because S02 constraint semantics
  are implemented.
- No `Selection<CandidateId>` type, `Candidate`/`Constraint`/`Score`/
  `SelectionProblem` record, or finite-manifest witness exists anywhere in
  `compiler/staqex/` or `examples/showcase/`.

So the existing green test confirms the *generic* syntax doesn't misfire on
S02-shaped names; it is not evidence that S02's domain model is implemented.
This Issue adds the actual domain model. It does not change or duplicate
`tests/test_s02_selection_surface_red.py`.

## Explicitly out of scope

- `Projector<Selection>` semantics, constraint lowering, objective
  normalization (WP-0093 work unit C) — needs its own ADR per WP-0093's own
  deliverable list; not started, not this Issue.
- `State<Selection<CandidateId>>` Kernel-side carrier, `expect` usage,
  resource/provenance metadata at the Host boundary (work unit D).
- Reproducibility and capability-rejection conformance scenarios (work unit
  E) — depend on this Issue's fixture plus work unit C's Projector, so they
  come after both.
- Classical baselines (greedy / exact small-instance) — WP-0093 requires
  them before quality claims, but they are not required to prove the finite
  boundary itself; deferred to work unit E unless Phase 1 Red review says
  otherwise.
- Any `.sqx`, grammar, typecheck, or evaluator change.
- Real compound data, chemistry graph semantics, or public datasets (spec
  §"Out of scope").

## Acceptance reference

[S02 acceptance specification](../specs/staqex-v1-s02-drug-discovery-benchmark.md#acceptance-scenarios),
scenarios:

- "candidate data stays classical"
- "finite encoding is explicit"

(Scenarios "hard constraints use a projector boundary", "only terminal
measure crosses the classical boundary", "same execution identity
reproduces the result", and "unsupported width fails before execution" stay
with work units C/D/E.)

## AI planning record (size L)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-04
- Size: `L` — multiple new Host-side modules (domain records, finite-witness
  validation, fixture generation) plus their own test suite; no Kernel
  change, but meaningful new surface area and the first real S02
  implementation code, which carries more uncertainty than a single-module
  change.
- Route: direct implementation by this session (no external AI/model call
  planned).
- Estimate: N/A — no token/time budget tracked for this environment.
- Assumptions: this Issue produces Host-side Python only (likely under
  `examples/showcase/S02_.../domain/` and `.../host/`, mirroring S01's
  `domain/`/`host/` layout) plus its own pytest suite; it does not require a
  `.sqx` example file to exist yet, since no Kernel-side selection state is
  being prepared in this slice.
- Confidence: medium — the Host-side record shapes are well-specified in the
  accepted spec, but exact fixture generation (8–16 candidates, deterministic
  seed policy) and the precise set of fail-closed diagnostic codes are not
  yet decided and may need Phase 1 Red iteration.
- Revision links: none yet.

## Exit criteria

- [x] Phase 1 Red: acceptance tests for "candidate data stays classical" and
      "finite encoding is explicit" (and their fail-closed sub-cases: missing,
      duplicate, non-finite, oversized, unproven-finite input) exist and
      fail for a documented reason. Commit `f722c13`: `ModuleNotFoundError`
      (compile failure) — `examples/showcase/S02_drug_discovery/host/`
      did not exist yet; baseline confirmed unaffected (`pytest tests/ -q
      --ignore=tests/test_liss_0321_s02_host_domain_red.py` → 1209 passed).
- [x] Phase 2 Green: minimal Host-side implementation makes those tests
      pass. Commit `8ff74da`: 9/9 passed. One test-file correction was
      needed (import style: bare `from domain import ...` after inserting
      `host/` into `sys.path`, matching the established S01 test
      convention, not a dotted `examples.showcase...` package path, since
      `examples/` has no `__init__.py` anywhere); no assertion was
      weakened.
- [x] Phase 3 Refactor: no behavior change; reviewer empathy summary below.
      Code reviewed for readability; no refactor needed (already minimal,
      mirrors S01's `host/` module style).
- [x] Full regression: `pytest tests/test_liss_0321_s02_host_domain_red.py
      tests/test_s02_selection_surface_red.py -v` → 13/13 passed; full
      `pytest tests/ -q` → 1218 passed (1209 baseline + 9 new); `python3
      tests/spec_verification/run_all.py` → 161/161; `git diff --check` →
      clean.
- [x] WP-0093 work unit B marked with implementation evidence (this same
      reviewable unit).

## Reviewer empathy summary

**何を目的として何を変更したか**: WP-0093 work unit B(S02のHost側ドメイン境界)
を実装した。`Candidate`/`Constraint`/`Score`/`TargetProfile`/`SelectionProblem`
を既承認のS02仕様「Value model」節どおりのフローズンdataclassとして定義し、
候補マニフェストが有限・境界内・ID一意であることを証明する
`FiniteManifestWitness`/`validate_manifest()`を追加した。不正入力
(空・ID欠落・ID重複・非有限スコア・件数過不足・選択サイズ範囲外)は
それぞれ別の診断コードを持つ`ManifestValidationError`でfail closedする。
Kernel(`compiler/staqex/`)には一切触れていない。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- ディレクトリ配置は当初`domain/`+`host/`の2階層を想定していたが、
  S01の`domain/`が実は`.sqx`(Kernel側)専用だったと判明したため、
  `host/`のみに変更した。これはPlan承認内容からの実装時点の軌道修正であり、
  再承認は求めていない(スコープ境界そのものは変わっていないため)。
- fail-closed診断コード名(`S02_MANIFEST_EMPTY`等)は本Issueの提案であり、
  Adjudicatorの命名選好は未確認。
- 分類ベースライン(greedy/exact)を含めるかは明示的に除外し、work unit Eに
  委譲(Adjudicator決定通り)。

**人間がコードレビューで重点的に見るべきポイント**:
- 診断コード名の最終承認。
- `SelectionProblem`のフィールド形状が、将来のKernel側`State<Selection<CandidateId>>`
  境界(work unit D)と整合するか。
- `host/`のみへの配置変更(`domain/`サブディレクトリを作らなかった判断)への同意。

## Non-goals

- Projector/constraint semantics (work unit C).
- Kernel-side `State<Selection<CandidateId>>` preparation.
- Classical baselines or resource/provenance reporting.
- Any claim that S02's quantum lane is implemented.
