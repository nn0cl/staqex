# LISS-0328: real `project ... onto feasible(...)` Projector execution (ADR 0194, Follow-up item 2)

## Metadata

- Local issue ID: LISS-0328
- Status/phase: **complete** (2026-08-05) — PR
  [#368](https://github.com/nn0cl/staqex/pull/368) merged, commit
  `73580d3`
- Type: Feature Path (Kernel — `compiler/staqex/runtime/evaluator.py`'s
  `project` op dispatch; no grammar/parser/AST change; no change to
  LISS-0322's IR-lowering layer)
- Priority: P2
- Initial planning size: `M`
- Owner / agent: Claude Code
- Program: [ADR 0194](../architecture/adr/0194-host-input-port-and-selection-predicate-semantics.md)
  Follow-up item 2; [WP-0093](../work-plans/WP-0093-s02-language-expressiveness-and-selection.md)
  work unit E
- Depends on: [LISS-0327](LISS-0327-host-input-port-foundation.md) (the
  `HostInputPort`/`host_input_binding.py` this Issue's `pairwise_compatible`/
  `diversity_at_least` handling calls); [LISS-0324](LISS-0324-s02-prepare-selection.md)
  (`prepare_selection`, the only known way to produce a selection-pattern
  Joint coordinate this Issue's `project` handling operates on)
- Blocks: none currently known
- Branch: `feature/liss-0328-selection-projector-predicate-execution`
  (not created yet)
- GitHub Issue / PR: none yet

## Intent

Implement ADR 0194 Decisions 3–5: replace `project`'s current
unconditional crash on a `feasible(...)` target
(`compiler/staqex/runtime/evaluator.py:3797`, `_eval_value` raising `call
cannot be classical value in Phase 2.2 value context`) with real execution
for all three ADR 0192 predicates:

1. **`exactly_selected(n)`**: `sum(pattern) == n` — a pure function of the
   pattern itself, no Host input needed.
2. **`pairwise_compatible = true`**: look up
   `self.host_input.get("pairwise_compatible")` (via LISS-0327's port);
   validate as an `n×n` symmetric `Bool` matrix via
   `host_input_binding.validate_matrix_binding(..., dtype=bool)`; satisfied
   iff every pair of selected slots `i < j` has `M[i][j] is True`.
3. **`diversity_at_least = k`**: look up
   `self.host_input.get("diversity_at_least")`; validate as an `n×n`
   symmetric non-negative `Float` matrix; satisfied iff the **minimum**
   `M[i][j]` over every pair of selected slots is `>= k`.

All predicates present in one `feasible(...)` call combine with logical
AND into one predicate function, applied via the existing
`joint.project_coord(name, predicate)` — the same Hilbert-projector-plus-
renormalize mechanism `project(psi, k)` already uses (line ~3827). `n` (the
pattern width) is read from the actual bound pattern's tuple length at
runtime, not tracked separately.

## Explicitly out of scope

- Any change to `_append_selection_projector_region`'s IR-lowering
  (LISS-0322) — that layer already produces a correct `ProjectorRegion`
  witness; this Issue only makes the *runtime* execution real.
- Any change to `feasible(...)`'s compile-time predicate-name recognition
  or `S02_UNKNOWN_CONSTRAINT_PREDICATE` (unchanged, LISS-0322's scope).
- Any change to `prepare_selection` (LISS-0324, already real).
- A general symbolic/predicate-lambda `project` form — the existing
  `PREDICATE_PROJECTOR_ERROR` guard against a literal `Lambda` target stays
  exactly as-is; this Issue only special-cases the closed-vocabulary
  `feasible(...)` `Call` form, matching how `KetLit` targets are already
  special-cased in the same dispatch.
- Live QPU execution or any target-adapter concern.

## Acceptance reference

New Phase 1 scenarios (extends the existing shipped
[S02 spec's Projector scenarios](../specs/staqex-v1-s02-drug-discovery-benchmark.md#acceptance-scenarios--projectorselection-semantics-adr-0192-phase-1-target-liss-0322),
which are IR-lowering-only today):

```gherkin
Feature: real Projector execution for feasible(...) predicates

  Scenario: exactly_selected filters to only matching patterns
    Given prepare_selection(3) projected onto feasible(exactly_selected = 2)
    When the state reaches terminal measure
    Then the result always has exactly 2 of 3 slots selected

  Scenario: pairwise_compatible rejects an incompatible pair
    Given prepare_selection(3), a bound pairwise_compatible matrix marking
      slots 0 and 1 incompatible, and feasible(exactly_selected = 2,
      pairwise_compatible = true)
    When the state reaches terminal measure
    Then the result never selects both slot 0 and slot 1 together

  Scenario: diversity_at_least rejects a below-threshold pair
    Given prepare_selection(3), a bound diversity_at_least matrix, and
      feasible(exactly_selected = 2, diversity_at_least = k)
    When the state reaches terminal measure
    Then the result's selected pair's diversity is always >= k

  Scenario: a missing required Host input fails closed at runtime
    Given feasible(pairwise_compatible = true) with no bound
      "pairwise_compatible" host input
    When the program runs
    Then it fails with HOST_INPUT_BINDING_MISSING, not a fabricated result

  Scenario: an infeasible constraint set produces vacuum, not a silent pass
    Given constraints that no pattern can satisfy
    When the state reaches terminal measure
    Then the terminal measurement is vacuum/empty, matching the existing
      empty-projector contract project(psi, k) already has
```

## AI planning record (size M)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-05
- Size: `M` — one new `target`-handling branch in the existing `project`
  dispatch (mirrors the existing `KetLit` special-case exactly), plus
  predicate-combination logic and Host-input lookups via LISS-0327's port.
  No new AST, no new Joint method (`project_coord` already supports an
  arbitrary label predicate — confirmed by the existing `KetLit` case's own
  use of it).
- Route: direct implementation by this session.
- Assumptions: `feasible(...)`'s `target` AST shape (a `Call` with
  `.kwargs: list[tuple[str, Expr]]`) matches what LISS-0322 already reads
  in `_append_selection_projector_region` — confirmed by that Issue's own
  documented AST-shape verification, not re-verified independently in this
  design intake (re-verification planned before Phase 1 Red).
- Confidence: medium — the Hilbert-projector mechanism and Host-input
  lookup are both individually verified/shipped; their combination
  (reading `feasible(...)`'s kwargs at the runtime layer, which currently
  never inspects them at all) has not yet been directly probed and may
  surface a smaller implementation-detail surprise during Red, per this
  session's established pattern.
- Revision links: none yet.

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0328_selection_projector_predicate_execution_red.py`
      added (the five scenarios above). Commit `846c83b`: 5/5 failed for
      the documented reason (unconditional `RUNTIME_ERROR: call cannot be
      classical value in Phase 2.2 value context`, regardless of which
      predicates were present or whether Host inputs were bound).
- [x] Phase 2 Green: `project`'s runtime dispatch gained a new
      `feasible(...)`-Call branch (parallel to the existing `KetLit`
      special-case) and `_bind_feasible_predicate`. Commit `d3ba3e6`: 5/5
      passed on the first implementation attempt (no Red-then-fix
      iteration needed — the AST-shape assumption from design intake was
      re-verified live before writing any code, per the "medium
      confidence" note in this Issue's own AI planning record);
      `test_s02_selection_surface_red.py` (4/4) unchanged; LISS-0322's
      IR-lowering layer untouched.
- [x] Phase 3 Refactor: no further change — reviewed for unused
      imports/dead branches via `python3 -W error -c "import ..."`, none
      found. Reviewer empathy summary below.
- [x] Full regression: `pytest tests/ -q` → 1248 passed; `python3
      tests/spec_verification/run_all.py` → 161/161; `git diff --check` →
      clean.
- [x] ADR 0194's Follow-up item 2 checked off; WP-0093 work unit E
      updated.

## Reviewer empathy summary

**何を目的として何を変更したか**: `project ... onto feasible(...)`が
常にランタイムでクラッシュしていた問題を解消し、ADR 0192の3述語
(`exactly_selected`/`pairwise_compatible`/`diversity_at_least`)全てに
本物の実行意味論を与えた。`exactly_selected`はパターン自身の
Hamming weightのみで判定する純粋な構造チェック。`pairwise_compatible`/
`diversity_at_least`はADR 0194の`HostInputPort`(LISS-0327)経由で
述語名と同名の束縛を検索し、`validate_matrix_binding`で形状/対称性/
dtypeを一度だけ事前検証してからpredicateを構築する
(predicate関数自体は検証済みデータを高速に走査するのみ)。全て既存の
`joint.project_coord` + 再正規化という、`project(psi, k)`が既に使って
いる仕組みをそのまま再利用しており、新しいJointメソッドは追加して
いない。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- `diversity_at_least`の集約方法(最小値)はADR 0194で決定済みだが、
  実際のS02 fixtureでこの数式が物理的/化学的に妥当な「多様性」の
  定義として機能するかは、実データでの検証はまだ行っていない。
- `feasible(...)`のkwargs順序に依存しない実装(辞書的に述語名で処理)
  になっているが、複数回同じ述語名が現れた場合(例:
  `feasible(exactly_selected = 2, exactly_selected = 3)`)の挙動は
  「後勝ち」で、明示的な重複検出は行っていない。コンパイル時
  (LISS-0322)でも重複は検出されない。

**人間がコードレビューで重点的に見るべきポイント**:
- `_bind_feasible_predicate`が`project`の巨大なdispatchメソッド内に
  追加された新しいbranchとして実装されている点(既存の`KetLit`
  special-caseと並列)が、将来的な可読性・保守性の観点で許容範囲か。
- `pairwise_compatible`/`diversity_at_least`のkwargs重複を明示的に
  拒否すべきか。

## Non-goals

- `HostInputPort` foundation itself (LISS-0327).
- Symbolic/general predicate `project`.
- Live QPU execution.
