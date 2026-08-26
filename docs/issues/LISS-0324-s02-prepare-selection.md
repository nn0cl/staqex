# LISS-0324: `prepare_selection` quantum selection state (WP-0093 work unit E, first slice)

## Metadata

- Local issue ID: LISS-0324
- Status/phase: **complete** (2026-08-05) — PR
  [#363](https://github.com/nn0cl/staqex/pull/363) merged, commit
  `746d002`
- Type: Feature Path (Kernel — `compiler/staqex/runtime/evaluator.py` new
  op; no grammar/parser change, no new ADR)
- Priority: P1
- Initial planning size: `M`
- Current planning size: `M`
- Owner / agent: Claude Code
- Program: [WP-0093](../work-plans/WP-0093-s02-language-expressiveness-and-selection.md)
  work unit E (first slice — the "quantum selection State" step of the
  normative benchmark shape)
- Parent: [S02 acceptance specification](../specs/staqex-v1-s02-drug-discovery-benchmark.md)
  (Accepted) §"Normative benchmark shape", §"Fixture limits" ("Encoding:
  one logical selection carrier per candidate")
- Depends on: none at the Kernel level. Conceptually follows
  [LISS-0321](LISS-0321-s02-host-domain-and-finite-boundary.md) (Host
  domain records) and precedes real use of
  [LISS-0322](LISS-0322-s02-projector-region-semantics.md)'s Projector
  lowering with a genuine prepared state (today's
  `test_projector_is_explicitly_lowered_from_selection_constraints` feeds
  it an unrelated `finiteize(...)` placeholder — see "Scope clarification"
  below).
- Blocks: any real end-to-end S02 `.sqx` example (still doesn't exist);
  the rest of work unit E (classical baselines, conformance scenarios
  spanning full execution).
- Related: none needing an ADR — this Issue resolved the earlier
  "does Host→Kernel need a new structured data-passing mechanism"
  question by confirming candidate *identity* never needs to cross the
  boundary at all; only the finite width (a plain `Int`) does.
- Branch: `feature/liss-0324-s02-prepare-selection`
- GitHub Issue / PR: none yet

## Intent

Implement `prepare_selection(n: Int)` as a real Kernel operation:
given a classical candidate count `n`, produce an equal superposition
over all `2^n` possible selection patterns (each an `n`-tuple of 0/1
flags, one per candidate slot), using the exact same `Joint.bind_split`
primitive that `coin()` and `finiteize(...)` already use — verified
directly:

```python
Joint.unit().bind_split("selection", {pattern: 1/2**n for pattern in
    itertools.product((0, 1), repeat=n)})
```

produces `2**n` correctly normalized worlds (confirmed live for `n=3`:
8 worlds, each amplitude `1/√8`, `norm() == 1.0`). This mirrors
`_bind_finiteize`'s existing structure in
`compiler/staqex/runtime/evaluator.py` almost exactly, just replacing
the continuous-histogram distribution with a uniform distribution over
`2^n` discrete bit-patterns.

## Scope clarification found during design intake

**Why not `QubitRegister<N>` or a real multi-qubit register?** Verified
directly: `QubitRegister<N>` is a compile-time-only static resource-shape
annotation for the QFT/IQFT lowering path — the evaluator comment states
"Static Hilbert shape is compile-time metadata; it has no runtime
allocation or state coordinate in the Kernel." `forEach` bodies cannot
`measure` (`FOR_EACH_MEASURE_ERROR`), and no shipped example measures a
whole register as one combined classical outcome — every example
entangles individually-named `state` qubits and terminally measures a
single one. A `measure (a, b, c)` tuple was tried and rejected by the
linear-use checker (`LINEAR_IMPLICIT_DISCARD` on each tuple item; tuples
are not wired into `Measure`'s linear consumption analysis). The
single-coordinate `bind_split` approach above sidesteps all of this by
representing the whole `n`-candidate selection as one Joint coordinate,
exactly like `coin()` already represents one qubit — `measure` therefore
needs **no** new code path; it already works for any `bind_split`-produced
coordinate.

**Why `prepare_selection(n: Int)` and not `prepare_selection(candidates)`
with a Host `SelectionProblem`?** Confirmed: `compile_source` never
evaluates the Kernel (only `run_source`/`Evaluator.run_unit` does), so
today's `tests/test_s02_selection_surface_red.py::test_projector_is_explicitly_lowered_from_selection_constraints`
— which calls `prepare_selection(candidates)` where `candidates` comes
from an unrelated `finiteize(0.0, 1.0, 8, 16, 0)` placeholder — has never
actually executed this call and imposes no real constraint on its
signature. This Issue defines `prepare_selection`'s first real,
executable signature as `prepare_selection(n: Int)`, per this spec's own
rule that candidate identity (descriptors, scores, tags) never becomes a
Kernel value — only the finite count crosses the boundary. The existing
compile-only structural test is unaffected and left unchanged (it tests
Projector IR shape, not `prepare_selection`'s real semantics).

## Explicitly out of scope

- `Projector`/constraint application to the prepared state (LISS-0322
  covers the IR-lowering side only; wiring a real `prepare_selection`
  result through a real `project ... onto feasible(...)` execution is
  separate, later work).
- Any Host→Kernel structured-data-passing mechanism — confirmed
  unnecessary; only a plain `Int` crosses.
- `QubitRegister<N>`, `forEach`-based multi-qubit preparation, or any
  multi-coordinate/tuple `measure` fix — not used, not touched.
- Any real end-to-end S02 `.sqx` example program.
- Classical baselines, objective evolution, reranking (remaining work
  unit E scope).
- Enforcing the S02 fixture's 8–16 candidate bound inside the Kernel —
  that is Host-side business logic already implemented in LISS-0321's
  `validate_manifest`; `prepare_selection` itself only requires `n >= 1`
  (general-purpose, not S02-specific).

## Acceptance reference

[S02 acceptance specification §"Acceptance scenarios — quantum selection
state preparation"](../specs/staqex-v1-s02-drug-discovery-benchmark.md),
three scenarios: equal superposition over `2^n` patterns; terminal
measure yields one reproducible pattern; candidate identity never crosses
into the Kernel.

## AI planning record (size M)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-05
- Size: `M` — one new op branch in `runtime/evaluator.py`'s existing
  call-dispatch chain (mirroring `coin`/`finiteize`'s exact shape) plus
  its test suite; no grammar, no typecheck rule (generic `Call` inference
  already applies), no new ADR.
- Route: direct implementation by this session (no external AI/model call
  planned).
- Estimate: N/A — no token/time budget tracked for this environment.
- Assumptions: tests use `compiler.staqex.host.run_source` (the
  `KernelDiagnosticError`/`KernelError`-catching entry point, per the
  LISS-0320/0323 precedent), not the lower-level `compiler.staqex.run`
  module.
- Confidence: high — the exact `Joint.bind_split` call shape was verified
  directly against `runtime/joint.py`, and the current failure mode
  (`RUNTIME_ERROR: unknown function \`prepare_selection\``) was confirmed
  live via `host.run_source` before drafting this Issue.
- Revision links: none yet.

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0324_s02_prepare_selection_red.py`
      added (white-box `Evaluator._bind_call` distribution check,
      full-program `host.run_source` reproducibility check, non-Int
      argument rejection check). Commit `8e69017`: 2/3 failed for the
      documented reason (`unknown function \`prepare_selection\``); the
      non-Int-argument scenario already passed today (any call to a
      nonexistent function raises regardless of argument type) —
      kept as a real Green acceptance criterion, not removed.
- [x] Phase 2 Green: `Evaluator._bind_prepare_selection` added, mirroring
      `_bind_finiteize`'s structure exactly as designed. Commit `43582bc`:
      3/3 passed; `test_s02_selection_surface_red.py`'s existing
      structural test (4/4) unchanged; no `QubitRegister<N>`/`forEach`/
      tuple-`measure` code touched.
- [x] Phase 3 Refactor: no further change — reviewed for unused
      imports/dead branches, none found; local `import itertools` matches
      the file's existing convention (`import math as _math` in
      `wavepacket`). Reviewer empathy summary below.
- [x] Full regression: `pytest tests/ -q` → 1236 passed; `python3
      tests/spec_verification/run_all.py` → 161/161; `git diff --check` →
      clean.
- [x] WP-0093 work unit E's first-slice row marked with implementation
      evidence.

## Reviewer empathy summary

**何を目的として何を変更したか**: `prepare_selection`が
`unitarity_check.py`のホワイトリスト名としてのみ存在し、実行時には
「未知の関数」として必ず失敗していた問題を、実際に動作するKernel演算
として実装した。`prepare_selection(n: Int)`は、既存の`_bind_finiteize`
と全く同じ構造で、`coin()`が使う`Joint.bind_split`をn個のタプルラベル
付き`2^n`パターンに一般化して呼び出すだけで実現でき、`measure`側の
変更は一切不要だった(`bind_split`が生成する座標はラベルの型を問わず
既存の測定経路がそのまま動作することを確認済み)。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- Phase 1 Redのシナリオ1(「測定前に2^nパターンが等確率で存在する」)は
  `run_source`経由では検証できない(プログラムは終端`measure`を要求する
  ため、測定前の状態を外部から観測する手段がない)。そのため
  `Evaluator._bind_call`を直接呼び出すホワイトボックステストとした。
  これは`_bind_call`という非公開メソッドに依存しており、将来その
  シグネチャが変わった場合はこのテストも追随が必要。
- タプルラベル付き`bind_split`座標に対する`measure`の再現性
  (同一seedで同一パターン)は、Green実装後の実行で初めて確認された
  もので、事前に完全に保証されていたわけではない(設計段階では
  `coin()`の2値ケースでのみ`bind_split`の正規化を検証していた)。

**人間がコードレビューで重点的に見るべきポイント**:
- ホワイトボックステスト(`Evaluator._bind_call`直接呼び出し)が、
  この種のPhase 1 Redとして適切なテスト境界か、それとも将来的に
  Kernel側に「測定前検査」の公式な仕組み(`inspect`等)を用意すべきか。
- `prepare_selection(n)`が`n >= 1`のみを要求し、S02の8〜16候補という
  fixture制約をKernel側で強制していないこと(Host側`LISS-0321`の
  `validate_manifest`が担う設計)への同意。

## Non-goals

- Real Projector-constrained execution.
- Any end-to-end runnable S02 benchmark program.
- Classical baselines or resource/provenance computation beyond what
  LISS-0323's `BenchmarkResult` already threads through.
