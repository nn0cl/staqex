# LISS-0329: reject duplicate predicate names in `feasible(...)`

## Metadata

- Local issue ID: LISS-0329
- Status/phase: **complete** (2026-08-05) — PR
  [#370](https://github.com/nn0cl/staqex/pull/370) merged, commit
  `6c5fdec`
- Type: Feature Path (Kernel — `compiler/staqex/pipeline.py`'s
  `_collect_feasible_predicates`; no grammar/parser/AST change, no runtime
  change)
- Priority: P2
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: [WP-0093](../work-plans/WP-0093-s02-language-expressiveness-and-selection.md)
  work unit C/E; found as an open reviewer-empathy question in
  [LISS-0328](LISS-0328-selection-projector-predicate-execution.md)'s
  Completion review
- Depends on: [LISS-0322](LISS-0322-s02-projector-region-semantics.md)
  (`_collect_feasible_predicates`, the function this Issue extends);
  [LISS-0328](LISS-0328-selection-projector-predicate-execution.md)
  (confirmed the concrete silent-misbehavior evidence below)
- Branch: `feature/liss-0329-feasible-duplicate-predicate-rejection`
- GitHub Issue / PR: none yet

## Intent

`feasible(exactly_selected = 2, exactly_selected = 3)` — the same
predicate name repeated with different values — currently compiles clean
and, at runtime, silently resolves to whichever value appears **last**
(`_bind_feasible_predicate` iterates `target.kwargs` and overwrites its
local variable on each match). Verified live:

```python
# compile_source(...).ok == True, only soft QSEM_* diagnostics
# run_source(...) -> status "succeeded", measured pattern (1, 1, 1)
#   (sum == 3, satisfying only the *second*, later `exactly_selected = 3`
#   -- the first `exactly_selected = 2` is silently discarded)
```

This is a fail-closed gap: a source-level contradiction (the same named
constraint asserted twice, with different values) should be rejected
explicitly, not silently resolved by argument order. Fix at the compile-time
layer, `_collect_feasible_predicates`
(`compiler/staqex/pipeline.py:400`), which already walks `target.kwargs`
to validate each name against ADR 0192's closed vocabulary — extend it to
also detect a name appearing more than once, and add a new
`S02_DUPLICATE_CONSTRAINT_PREDICATE` diagnostic (distinct from
`S02_UNKNOWN_CONSTRAINT_PREDICATE`, since a duplicate name is individually
recognized, just repeated).

## Explicitly out of scope

- Any runtime (`evaluator.py`) change. Fixing this at compile time means an
  offending program never reaches `_bind_feasible_predicate` at all —
  consistent with the project's existing pattern of validating malformed
  `feasible(...)` targets once, at the compile-time gate (see
  `S02_UNKNOWN_CONSTRAINT_PREDICATE`'s existing precedent in the same
  function).
- Any change to `_bind_feasible_predicate`'s "last value wins" internals —
  moot once duplicates are rejected before runtime.
- Any change to `exactly_selected`/`pairwise_compatible`/`diversity_at_least`'s
  individual semantics (LISS-0328, unaffected).

## Acceptance reference

New Phase 1 scenarios (no existing spec section covers duplicate-predicate
rejection yet — this Issue's own Red test is the acceptance evidence):

```gherkin
Feature: feasible(...) rejects duplicate predicate names

  Scenario: a repeated predicate name fails closed at compile time
    Given feasible(exactly_selected = 2, exactly_selected = 3)
    When the program is compiled
    Then compilation fails with S02_DUPLICATE_CONSTRAINT_PREDICATE
    And the program never reaches runtime

  Scenario: distinct predicate names are unaffected
    Given feasible(exactly_selected = 2, pairwise_compatible = true)
    When the program is compiled
    Then no S02_DUPLICATE_CONSTRAINT_PREDICATE diagnostic is produced
```

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-05
- Size: `S` — one function, one file, one new diagnostic code; no new
  AST/grammar surface (`target.kwargs` already carries every occurrence in
  source order).
- Route: direct implementation by this session.
- Confidence: high — the exact silent-misbehavior evidence (compiles
  clean, runs to `(1, 1, 1)`) was reproduced live before drafting this
  Issue.

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0329_feasible_duplicate_predicate_red.py`
      added. Commit `2c629dc`: 1/2 failed for the documented reason
      (duplicate `exactly_selected` compiled clean, only soft `QSEM_*`
      diagnostics present).
- [x] Phase 2 Green: `_collect_feasible_predicates` tracks names already
      seen; `S02_DUPLICATE_CONSTRAINT_PREDICATE` added to `HARD_CODES`.
      Commit `202d42e`: 2/2 passed; `test_liss_0322_s02_projector_region_semantics_red.py`
      (4/4), `test_liss_0328_selection_projector_predicate_execution_red.py`
      (5/5), and `test_s02_selection_surface_red.py` (4/4) all unchanged;
      `evaluator.py` untouched.
- [x] Phase 3 Refactor: no further change; reviewed for unused
      imports via `python3 -W error -c "import ..."`, none found.
      Reviewer empathy summary below.
- [x] Full regression: `pytest tests/ -q` → 1250 passed; `python3
      tests/spec_verification/run_all.py` → 161/161; `git diff --check` →
      clean.
- [x] WP-0093 work unit C's row updated. `S02_UNKNOWN_CONSTRAINT_PREDICATE`
      (this diagnostic's sibling, LISS-0322) was never added to
      `docs/specs/staqex-v1-diagnostic-catalog.md` either, so
      `S02_DUPLICATE_CONSTRAINT_PREDICATE` is not added there, to stay
      consistent with existing practice rather than introduce a
      one-off exception.

## Reviewer empathy summary

**何を目的として何を変更したか**: `feasible(...)`内で同一述語名が
複数回現れた場合(例: `exactly_selected = 2, exactly_selected = 3`)、
コンパイルは通り実行時に最後の値が黙って勝つ(矛盾が検出されない)
という問題を修正した。`_collect_feasible_predicates`が既に見た述語名を
追跡し、再出現時に新診断`S02_DUPLICATE_CONSTRAINT_PREDICATE`を返すよう
にした。ランタイム(`evaluator.py`)は無変更 — 該当プログラムはもはや
コンパイルを通過しないため。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 診断コードを`HARD_CODES`に追加してコンパイル失敗として扱う判断は、
  既存の`S02_UNKNOWN_CONSTRAINT_PREDICATE`の扱いに倣ったもの。

**人間がコードレビューで重点的に見るべきポイント**:
- 診断カタログに追記しない判断(既存の兄弟診断も未記載のため一貫性を
  優先)が妥当か。

## Non-goals

- Runtime changes.
- New predicate names or semantics.
