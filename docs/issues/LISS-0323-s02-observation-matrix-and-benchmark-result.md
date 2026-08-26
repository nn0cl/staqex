# LISS-0323: S02 observation matrix and `BenchmarkResult` (WP-0093 work unit D)

## Metadata

- Local issue ID: LISS-0323
- Status/phase: **final-review-ready** / `phase-3-refactor` (2026-08-05) —
  Phase 3 complete; awaiting Adjudicator Completion approval and PR
- Type: Feature Path (Host-side DTO + builder; no Kernel/grammar/type-system
  change; no new architecture decision)
- Priority: P1
- Initial planning size: `M`
- Current planning size: `M`
- Owner / agent: Claude Code
- Program: [WP-0093](../work-plans/WP-0093-s02-language-expressiveness-and-selection.md)
  work unit D
- Parent: [S02 acceptance specification](../specs/staqex-v1-s02-drug-discovery-benchmark.md)
  (Accepted) §"Result contract" and §"Acceptance scenarios — observation
  matrix and `BenchmarkResult`"
- Depends on: [LISS-0321](LISS-0321-s02-host-domain-and-finite-boundary.md)
  (`SelectionProblem`/`Candidate`/`Constraint` shapes this Issue's DTO
  references)
- Blocks: work unit E (conformance scenarios need a `BenchmarkResult` to
  assert against)
- Related: [LISS-0322](LISS-0322-s02-projector-region-semantics.md)
  (unrelated Kernel slice, same work plan)
- Branch: `feature/liss-0323-s02-observation-and-benchmark-result`
- GitHub Issue / PR: none yet

## Intent

Implement WP-0093 work unit D items 2–4 as a Host-side DTO and builder,
reusing already-shipped Kernel primitives rather than inventing new
semantics:

1. **`expect` stays non-destructive, separate from `measure`** (item 2) —
   already true generically in the shipped Kernel
   (`runtime/evaluator.py`'s `expect` op binds a classical scalar without
   consuming the joint state); this Issue does not change that. No code
   change needed for this item; it is confirmed and referenced, not
   reimplemented.
2. **An empty or unverifiable terminal selection is a failed result, not a
   fabricated score** (item 3) — implemented via a `BenchmarkResult`
   builder that inspects `MeasurementEnvelope.vacuum` (already shipped;
   the same field the S01 showcase's `ticket_dto.py` uses for
   `IncompleteMeasurementError`) and sets an explicit `"failed"`
   feasibility verdict instead of a zero/default score.
3. **Resource and provenance metadata at the Host boundary** (item 4) —
   the builder copies `JobResult.metadata` into `BenchmarkResult` verbatim;
   it never invents a resource field the `JobResult` did not provide.

Item 1 (`State<Selection<CandidateId>>` as the conceptual quantum carrier)
is a documentation/conceptual point, not new code: no `Selection` Kernel
type exists (confirmed absent from `compiler/staqex/typecheck.py`), and
this Issue does not add one — LISS-0321's `SelectionProblem` is the only
typed carrier this Issue references.

## Explicitly out of scope

- Any new Kernel type (`Selection<T>`, `Observable<T>`, `Projection<T>`,
  `Observation<T>`) — those remain WP-0092's own open decision (work unit
  3); this Issue does not wait for or depend on their resolution.
- Any change to `Projector<Selection>` semantics (LISS-0322 / ADR 0192) —
  unrelated Kernel slice.
- Classical baselines (greedy/exact), full resource *estimation* logic
  (this Issue passes through what a `JobResult` already carries; it does
  not compute new resource estimates) — deferred to work unit E.
- Any `.sqx` example program — no S02 program exists yet to actually
  produce a `JobResult`; tests build synthetic `JobResult`/
  `MeasurementEnvelope` objects directly, following the established
  pattern in `tests/test_s01_tonight_ticket_export.py`.
- Score/reranking computation — `baseline_score`/`objective_score`/
  `reranked_score` fields exist in the DTO per the spec's Result contract,
  but this Issue does not compute them from real candidate data (no real
  S02 execution exists yet); it only threads through what's already on the
  `JobResult`/measurement value, or leaves them `None` when unavailable.

## Acceptance reference

[S02 acceptance specification §"Acceptance scenarios — terminal
observation and resource reporting"](../specs/staqex-v1-s02-drug-discovery-benchmark.md),
four scenarios: vacuum/empty → failed result, not fabricated score; valid
measurement → real verdict; resource metadata passed through, not
invented; default optimality claim is `"none"`. The spec states these
requirements abstractly ("a Host report"); `BenchmarkResult` is this
Issue's own implementation choice for the concrete Host-side
representation, not part of the normative spec text (Adjudicator feedback,
2026-08-05 — the spec should stay implementation-agnostic like the rest
of its Result contract section).

## AI planning record (size M)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-05
- Size: `M` — one new Host-side module (DTO + builder function) plus its
  test suite; no Kernel change, no new type system, bounded by
  already-shipped primitives (`MeasurementEnvelope.vacuum`,
  `JobResult.metadata`) confirmed by direct source reading before drafting
  this Issue.
- Route: direct implementation by this session (no external AI/model call
  planned).
- Estimate: N/A — no token/time budget tracked for this environment.
- Assumptions: tests construct synthetic `JobResult`/`MeasurementEnvelope`
  objects directly (no real S02 `.sqx` program exists to produce one),
  matching the precedent in `tests/test_s01_tonight_ticket_export.py`.
- Confidence: high — `MeasurementEnvelope`/`JobResult`'s exact fields were
  read directly from `compiler/staqex/host.py` before drafting this Issue.
- Revision links: none yet.

## Exit criteria

- [x] Phase 1 Red: acceptance tests for the four spec scenarios (plus two
      extra sub-cases: missing measurements entirely, and no resource
      metadata) exist and fail for a documented reason. Commit `deb4a63`:
      `ModuleNotFoundError` (compile failure) —
      `examples/showcase/S02_drug_discovery/host/benchmark_result.py` did
      not exist yet; baseline confirmed unaffected (`pytest tests/ -q
      --ignore=tests/test_liss_0323_s02_benchmark_result_red.py` → 1222
      passed).
- [x] Phase 2 Green: minimal Host-side implementation makes those tests
      pass without editing the tests. Commit `dff99a0`: 6/6 passed.
- [x] Phase 3 Refactor: no behavior change; reviewer empathy summary
      below. Code reviewed for readability; no refactor needed.
- [x] Full regression: full `pytest tests/ -q` → 1228 passed (1222
      baseline + 6 new); `python3 tests/spec_verification/run_all.py` →
      161/161; `git diff --check` → clean.
- [x] WP-0093 work unit D marked with implementation evidence (this same
      reviewable unit).

## Reviewer empathy summary

**何を目的として何を変更したか**: WP-0093 work unit D(観測マトリクスと
`BenchmarkResult`)を実装した。`expect`の非破壊性・終端`measure`・
`MeasurementEnvelope.vacuum`という既存の汎用Kernel機能を、S02の
Result contractへ束ねるHost側のDTOとビルダー関数を追加した。
終端測定がvacuumまたは欠落している場合は`feasibility_verdict="failed"`
かつ`terminal_selection=None`とし、捏造した選択結果を返さない。
resourceメタデータは`JobResult.metadata`からそのままコピーし、
存在しない項目を作り出さない。Kernel(`compiler/staqex/`)には
一切触れていない。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- `BenchmarkResult`のフィールド形状(`feasibility_verdict`/
  `terminal_selection`/`resource_metadata`/`optimality_claim`)は
  本Issueの実装判断であり、仕様書自体はDTO名を規定していない
  (Adjudicatorのフィードバックにより、仕様書は「Host report」という
  抽象表現に留めた)。将来baseline/objective/rerankedスコアの
  フィールドを追加する際は、このIssueのスコープ外(実スコア計算なし)
  である点を踏まえる必要がある。
- テストは実在するS02プログラムから得た`JobResult`ではなく、
  S01の`test_s01_tonight_ticket_export.py`と同じパターンで合成した
  `JobResult`/`MeasurementEnvelope`を使用している——実行可能な
  S02プログラムがまだ存在しないため。

**人間がコードレビューで重点的に見るべきポイント**:
- `BenchmarkResult`のフィールド形状が、将来のwork unit E(分類
  ベースライン・resource見積り)との統合に適しているか。
- `feasibility_verdict`の値("feasible"/"failed"のみ)が、仕様書の
  Result contractが将来要求しうる"infeasible"(制約違反はあるが
  測定は成功)との区別に十分か。

## Non-goals

- Defining `Observable<T>`/`Projection<T>`/`Observation<T>` as Kernel
  types.
- Real score computation or classical baselines.
- Any `.sqx` example program.
