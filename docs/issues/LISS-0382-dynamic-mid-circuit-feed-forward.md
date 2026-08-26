# LISS-0382: Dynamic-lane mid-circuit `measure` and feed-forward (ADR 0197)

## Metadata

- Local issue ID: LISS-0382
- Status/phase: **complete** (2026-08-09) — Adjudicator Completion
  approved; PR [#480](https://github.com/nn0cl/staqex/pull/480)
- Type: Feature Path (Kernel — surface/AST + QSem lowering + diagnostics;
  capability rejection retained; Fake-exec out of Plan)
- Priority: P1
- Initial planning size: `L`
- Current planning size: `L`
- Owner / agent: Cursor (Grok)
- Program: [ADR 0197](../architecture/adr/0197-dynamic-mid-circuit-feed-forward.md)
  Follow-up item 1
- Parent: [ADR 0197](../architecture/adr/0197-dynamic-mid-circuit-feed-forward.md)
  (Accepted 2026-08-09)
- Depends on: [ADR 0197](../architecture/adr/0197-dynamic-mid-circuit-feed-forward.md)
  (Accepted); LISS-0077 Fake vocabulary (shipped); LISS-0381 (complete)
- Related: [LISS-0028](LISS-0028-dynamic-qpu-lane.md); ADR 0071 / 0106 D2;
  ADR 0193 Decision 5
- Blocks: JobResult composition / qubit reuse Issues (ADR 0197 Follow-up
  #2–#3)
- Branch: `feature/liss-0382-dynamic-mid-circuit-feed-forward`
- GitHub Issue / PR: [#480](https://github.com/nn0cl/staqex/pull/480)
- Plan-locked surface: `Controller<Bit> bit = measure q` inside
  `dynamic qpu`; contextual `match bit { … }`; IR+diagnostics only

## Intent

Implement ADR 0197 Decisions 1–4 and 6–7 **boundary** in full (no MVP cut
of the Accepted meaning):

1. **Lane law** (Decision 1): mid-circuit collapse only inside explicit
   dynamic-lane regions; Static Kernel NLTS / terminal `measure` unchanged.
2. **Spelling** (Decision 2): lane-local `measure` (not `observe`, not
   method-chain, not `branch`). Define AST product / bind sugar for the
   paired `OutcomeToken` + post-measure Joint (exact destructuring form
   chosen in Phase 1 Red against acceptance scenarios — must remain
   physicist-readable and vision §2.2 stable under rewrite).
3. **Feed-forward** (Decision 3): `Controller<T>` + finite `match` +
   one-merge laws, diagnostics aligned with LISS-0077 code family /
   Fake vocabulary.
4. **QSem** (Decision 4): source-derived lowering produces
   `DynamicMeasurementRegion` / `DynamicControlRegion` (not silently
   dropped; not hardcoded placeholders unrelated to source).
5. **Capability** (Decision 6): unsupported reset/reuse/latency/feedback
   demands fail closed; no Host silent emulation.
6. **Non-execution** (Decision 7): do **not** remove today's
   `DYNAMIC_CAPABILITY_REQUIRED_ERROR` /
   `DYNAMIC_UNSUPPORTED_FEATURE_ERROR` rejection of `DynamicQpuStmt`
   unless this Issue's Plan explicitly adds a Fake-exec slice — default
   Plan is **IR + diagnostics only**, parallel to LISS-0381.

## Explicitly out of scope

- Reviving `observe` / introducing classical `branch` / method-chains.
- JobResult composition DTO redesign (ADR 0197 Follow-up #2).
- Full qubit reuse/reset model beyond capability reject flags (Follow-up #3).
- OpenQASM dynamic emission; live QPU provider; claiming physical execution.
- Closed timing-intent vocabulary (ADR 0193 Follow-up #2).
- Weakening Static Kernel NLTS.

## Acceptance reference

[ADR 0197](../architecture/adr/0197-dynamic-mid-circuit-feed-forward.md)
Decisions 1–7; scenarios to be written into
[`staqex-dynamic-qpu-lane.md`](../specs/staqex-dynamic-qpu-lane.md) under
Plan approval before Phase 1 Red (normative Gherkin for mid-circuit /
Controller / QSem / rejection retention).

## AI planning record (size L)

- Status: **complete** (Completion approved 2026-08-09)
- Authoring environment: Cursor (Grok 4.5), 2026-08-09
- Size: `L` — parser/AST sugar, typecheck/effect boundary, QSem lowering,
  diagnostics aligned with existing Fake module; touches multiple Kernel
  layers; surface sugar locked by Phase 1 Gherkin
  (`Controller<Bit> bit = measure q` + soft `match`).
- Route: AT-TDD; Fake module remained read-only vocabulary (no Fake-exec).
- Estimate: N/A
- Assumptions: default Plan excludes Fake executor wiring and keeps
  unconditional dynamic-lane capability rejection (ADR 0197 Decision 7);
  `within` timing intent remains orthogonal and regression-tested.
- Confidence: high after Green + Refactor verification.
- Revision links: none yet.

## Exit criteria

- [x] Spec: mid-circuit acceptance Gherkin added to
      `staqex-dynamic-qpu-lane.md` under Plan approval.
- [x] Phase 1 Red: failing tests for those scenarios; documented reasons.
      File: `tests/test_liss_0382_dynamic_mid_circuit_feed_forward_red.py`
      (**4 failed / 2 passed**, 2026-08-09):
      - no `DynamicMeasurementRegion` / `DynamicControlRegion` from source;
      - Static `Controller<Bit> = measure` currently lacks
        `EARLY_COLLAPSE_ERROR` (pre-existing hole; Green must emit it);
      - `match` inside dynamic does not parse (swallowed → `PARSE_ERROR`);
      - **passed:** `observe` stays `RETIRED_KEYWORD`; Static terminal
        measure unchanged.
- [x] Phase 2 Green: full ADR 0197 Decisions 1–4/6–7 Plan scope makes Red
      tests pass without editing tests to force Green; Static NLTS /
      EARLY_COLLAPSE for out-of-lane Controller=measure; dynamic rejection
      retained; Fake-exec still out of scope.
      Evidence (2026-08-09):
      `.venv/bin/pytest tests/test_liss_0382_dynamic_mid_circuit_feed_forward_red.py`
      → **6 passed**; related dynamic/QSem/early_collapse filter → **90 passed**.
- [x] Phase 3 Refactor + full regression + status sync.
      Refactor: extract `_controller_measure_bind_name` in pipeline;
      clarify mid-circuit region-index locals. Behavior unchanged.
      Status sync: open-work-register, LISS-0028 notes, lane spec header,
      ADR 0197 Follow-up #1 pointer.
      Full suite (2026-08-09): `.venv/bin/pytest tests/` → **1362 passed**.
- [x] Completion approval before merge (Adjudicator 2026-08-09).
