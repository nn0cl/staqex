# LISS-0381: Dynamic QPU timing intent (`within <name>`, `TimingRegion`)

## Metadata

- Local issue ID: LISS-0381
- Status/phase: **complete** (2026-08-08) — Adjudicator Completion
  approved; PR [#479](https://github.com/nn0cl/staqex/pull/479)
- Type: Feature Path (Kernel — grammar/AST + Quantum Semantic IR witness;
  no dynamic-lane execution)
- Priority: P1
- Initial planning size: `M`
- Current planning size: `M`
- Owner / agent: Cursor (Grok)
- Program: [ADR 0193](../architecture/adr/0193-dynamic-qpu-timing-region-intent.md)
  Follow-up item 1
- Parent: [ADR 0193](../architecture/adr/0193-dynamic-qpu-timing-region-intent.md)
  (Accepted 2026-08-05)
- Depends on: [ADR 0193](../architecture/adr/0193-dynamic-qpu-timing-region-intent.md)
  (Accepted — this Issue implements Decisions 1–4 only)
- Related: [LISS-0028](LISS-0028-dynamic-qpu-lane.md) (dynamic-lane
  rejection/capability boundary already Phase 3 reviewed;
  mid-circuit / qubit reuse / JobResult composition remain separately
  open), [LISS-0322](LISS-0322-s02-projector-region-semantics.md)
  (`ProjectorRegion` witness precedent)
- Blocks: none (a future per-backend timing-name ADR and LISS-0028's
  remaining open items are separate)
- Branch: `feature/liss-0381-dynamic-qpu-timing-region-intent`
- GitHub Issue / PR: [#479](https://github.com/nn0cl/staqex/pull/479)

## Intent

Implement ADR 0193 Decisions 1–4 in full (no partial / MVP cut of the
Accepted shape):

1. **Surface syntax** (Decision 1): optional prepositional clause
   `dynamic qpu within <name> { ... }`, matching `evolve … under H for t`.
   `<name>` is one free-form identifier. `dynamic qpu { ... }` without
   `within` remains valid and unchanged.
2. **AST** (Decision 2): `DynamicQpuStmt` gains
   `timing_intent: str | None`. It stays a `Stmt`; no expression
   promotion, no method-chain, no trailing-block call form.
3. **Quantum Semantic IR** (Decision 3): a distinct `TimingRegion`
   witness carries the source-derived `timing_intent` string when the
   clause is present — inspectable provenance, never silently dropped,
   never a hardcoded placeholder. Absent `within` ⇒ no `TimingRegion`.
4. **Rejection boundary unchanged** (Decision 4): with or without
   `within`, typecheck still emits
   `DYNAMIC_CAPABILITY_REQUIRED_ERROR` and
   `DYNAMIC_UNSUPPORTED_FEATURE_ERROR`. A malformed `within` clause
   (e.g. `within` with no following identifier) fails with its own
   explicit diagnostic rather than silent accept or crash.

## Explicitly out of scope

- Making the dynamic QPU lane executable (unchanged project boundary).
- Closed vocabulary of timing-intent names (rejected by ADR 0193; deferred
  until a real QPU adapter is selected — future ADR).
- Concrete per-backend durations, alignment, `dt`, pulse-level control.
- Mid-circuit `observe` / `branch` / classical feed-forward (ADR 0193
  Decision 5 / LISS-0028 remaining item).
- Qubit reuse, controller values, JobResult composition (LISS-0028
  remaining items).
- Keyword-argument form `dynamic qpu(timing = …)` (rejected as primary by
  ADR 0193; not implemented here).
- New Host/QPU adapter or provider SDK.

## Acceptance reference

[Dynamic QPU lane specification § "Acceptance scenarios — timing intent
(ADR 0193, LISS-0381)"](../specs/staqex-dynamic-qpu-lane.md).

## AI planning record (size M)

- Status: proposed, pre-Plan-approval
- Authoring environment: Cursor (Grok 4.5), this session
- Date: 2026-08-08
- Size: `M` — parser/lexer keyword + AST field + new `TimingRegion` in
  `quantum_semantic_ir.py` + pipeline append parallel to
  `_append_selection_projector_region`; typecheck regression preserved;
  no execution path. Bounded by Accepted ADR 0193 Decisions 1–4.
- Route: direct AT-TDD by this session after Plan + Phase approvals
  (no external AI/model call planned).
- Estimate: N/A — no token/time budget tracked for this environment.
- Assumptions:
  - `within` is a **contextual / soft keyword** only in the
    `dynamic qpu within <name>` position (parallel to evolve's soft
    `using`), **not** a global hard keyword — vision §2.2 forbids
    stealing ordinary identifiers such as a binding named `within`.
  - `TimingRegion` subclasses `_TransformationRegion` and adds
    `timing_intent: str`, parallel to `ProjectorRegion.constraint_ref`.
  - IR append runs even when typecheck already recorded the two dynamic
    rejection diagnostics (same pattern as ProjectorRegion append after
    soft QSem lowering), so tooling can inspect the witness without
    implying executability. Multiple `dynamic qpu within …` statements
    in one `main` append one `TimingRegion` each.
  - Malformed-clause diagnostic code:
    `DYNAMIC_TIMING_INTENT_MALFORMED` (missing identifier, or
    non-identifier forms such as `within 1` / `within foo(bar)`).
- Confidence: high — current `DynamicQpuStmt` / `_dynamic_qpu_stmt` /
  unconditional typecheck rejection confirmed by direct source read;
  ADR 0193 verification plan (a)–(d) maps 1:1 to the acceptance
  scenarios.
- Revision links: none yet.

## Exit criteria

- [x] Phase 1 Red: acceptance tests for the timing-intent scenarios
      exist and fail for a documented reason. File:
      `tests/test_liss_0381_dynamic_qpu_timing_region_intent_red.py`
      (**10 failed / 1 passed**, 2026-08-08 after §2.2 composition
      expansion; 11 scenarios total):
      - `within <name>` does not parse (`unit` empty / `PARSE_ERROR`);
      - `DynamicQpuStmt` has no `timing_intent` attribute;
      - no `TimingRegion` in Quantum Semantic IR;
      - malformed / non-identifier `within` yields `PARSE_ERROR`, not
        `DYNAMIC_TIMING_INTENT_MALFORMED`;
      - evolve-inside / multi-block / adjacent-Static composition cases
        likewise fail to capture timing intent;
      - **passed (regression guard):** `within` as an ordinary identifier
        outside the clause still works — Green must keep this (soft /
        contextual `within`, not a global hard keyword).
- [x] Phase 2 Green: full ADR 0193 Decisions 1–4 implementation makes
      those tests pass without editing tests to force Green, without
      making the dynamic lane executable, and without changing existing
      `dynamic qpu { … }` rejection diagnostics. Soft/contextual `within`
      and all §2.2 composition scenarios are in scope.
      Verification 2026-08-08:
      `.venv/bin/pytest tests/test_liss_0381_dynamic_qpu_timing_region_intent_red.py
      tests/test_static_parametric_dynamic_boundaries_red.py -v` → **16/16
      passed**.
- [x] Phase 3 Refactor: no behavior change; reviewer empathy summary
      below. Extracted `_optional_dynamic_timing_intent` and
      `_make_timing_region_witness`; fixed a refactor bug where keyword
      argument evaluation called `_block()` before parsing `within`
      (re-verified green after).
- [x] Full regression: targeted timing + dynamic-boundary tests 16/16;
      `pytest tests/ -q` → **1356 passed**;
      `python3 tests/spec_verification/run_all.py` → **161/161**;
      `git diff --check` → clean.
- [x] Status sync: LISS-0028 / open-work-register / ADR 0193 follow-up
      pointer updated; Issue marked **complete** after Adjudicator
      Completion approval (2026-08-08). Commit / PR still on request.

## Reviewer empathy summary

### 変更の要約 (PR Summary)
- **何を目的として何を変更したか**: ADR 0193 Decisions 1–4 と vision §2.2
  合成安定性を Kernel に実装した。`dynamic qpu within <name>`（contextual
  soft keyword）、`DynamicQpuStmt.timing_intent`、`TimingRegion` 証人、
  `DYNAMIC_TIMING_INTENT_MALFORMED` を追加。レーン実行化はせず、既存の
  `DYNAMIC_CAPABILITY_REQUIRED_ERROR` /
  `DYNAMIC_UNSUPPORTED_FEATURE_ERROR` を維持した。

### 残存リスク・検証の溝 (Verification Gap)
- **AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
  - TimingRegion に添える placeholder の acting space（dimension=2 /
    label=`dynamic_timing`）は、ProjectorRegion 先例に合わせた実装判断。
    ADR は「inspectable provenance」のみ要求し、space 形状は規定していない。
  - soft keyword 方針は Issue 側で hard keyword から §2.2 により変更した
    もの（ADR 本文は under 類似の前置詞とだけ述べ、hard/soft を固定していない）。
- **人間がコードレビューで重点的に見るべきポイント**:
  - `_block` が名前付き hard `ParseError.code` を握りつぶさないこと
  - `within` をグローバル予約していないこと（識別子回帰テスト）
  - timing 証人があっても dynamic レーンが実行されないこと
  - 複数 `within` で Region が 1:1 対応すること

