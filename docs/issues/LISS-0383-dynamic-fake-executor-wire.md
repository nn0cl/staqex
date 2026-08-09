# LISS-0383: Wire Dynamic lane AST/QSem to FakeDynamicExecutor (supplied outcomes)

## Metadata

- Local issue ID: LISS-0383
- Status/phase: **proposed** / `phase-0-design` — Plan drafted; awaiting
  Plan approval (no Red until approved)
- Type: Feature Path (Kernel — Fake-exec wire under supplied outcomes;
  `physical_execution_claimed=False`)
- Priority: P1
- Initial planning size: `L`
- Current planning size: `L`
- Owner / agent: Cursor (Grok)
- Program: [ADR 0197](../architecture/adr/0197-dynamic-mid-circuit-feed-forward.md)
  Follow-up #4 / Decision 7 Option B lineage
- Parent: ADR 0197 (Accepted); Fake vocabulary [LISS-0077](../architecture/documentation-compression-map.md)
  (complete)
- Depends on: ADR 0197 / LISS-0382 (**complete**); LISS-0077 Fake module
  (shipped). Soft-depends on [ADR 0198](../architecture/adr/0198-dynamic-jobresult-composition.md)
  (Proposed) for JobResult envelope — see Plan defaults if 0198 not yet
  Accepted. Soft-depends on [ADR 0199](../architecture/adr/0199-dynamic-qubit-reuse-reset.md)
  (Proposed) for reset/reuse — retain reject-on-demand until 0199 Accept
  + profile Issue.
- Related: LISS-0028; ADR 0071; `compiler/staqex/dynamic_qpu.py`
- Blocks: live provider feed-forward; OpenQASM dynamic emission (still
  separate)
- Branch: TBD at Plan approval (`feature/liss-0383-…`)
- GitHub Issue / PR: none yet

## Intent

Connect **source-derived** dynamic mid-circuit / match programs (already
parsed and witnessed by LISS-0382) to the existing
`FakeDynamicExecutor` under **supplied outcomes**, without claiming
physical execution, and without silently Host-emulating missing reset /
reuse / latency capabilities.

This is ADR 0197 Decision 7's optional Fake path: a dedicated Feature
Issue may change today's unconditional
`DYNAMIC_UNSUPPORTED_FEATURE_ERROR` / capability rejection **only** under
an explicit, reviewable Plan (e.g. gated Fake profile + supplied
outcomes), never as a silent default for all targets.

## Explicitly out of scope

- Live QPU provider submit / credentials / network (LISS-0100 lineage).
- OpenQASM dynamic emission (LISS-0097-E).
- Inventing JobResult field names if ADR 0198 is still Proposed — use
  Plan default below.
- Enabling reset/reuse on Fake profiles unless ADR 0199 Accept + a
  profile Issue say so (keep P0 reject-on-demand).
- Weakening Static NLTS; reviving `observe` / classical `branch`.

## Plan (draft — awaiting Adjudicator Plan approval)

### Surface / behavior

1. Programs with `dynamic qpu { Controller = measure …; match … }` that
   today compile to QSem witnesses + `DYNAMIC_*` rejection become
   **optionally** Fake-executable when an explicit Host/settings gate
   selects a Fake dynamic profile (exact flag/API named at Red; must be
   fail-closed if absent).
2. Outcomes for mid-circuit tokens are **supplied** (fixture / Host
   input), matching LISS-0077 honesty — not sampled as live hardware.
3. `DynamicExecResult.physical_execution_claimed` remains `False`.
4. Reset/reuse/latency demands continue to reject on P0 feedback-only
   profiles.

### JobResult default if ADR 0198 not yet Accepted

Ship Fake results primarily as `DynamicExecResult` (and/or diagnostics)
without inventing a permanent `JobResult` field. When ADR 0198 is
Accepted, a follow-on slice (same Issue or child) projects into the
additive JobResult channel.

### Non-goals inside Plan

- Removing capability rejection for non-Fake targets.
- Claiming SIM0/CH1 runs are physical feed-forward.

## Acceptance reference (to lock at Plan approval)

Extend [`staqex-dynamic-qpu-lane.md`](../specs/staqex-dynamic-qpu-lane.md)
with Gherkin for Fake-gated execution vs continued rejection without the
gate; assert `physical_execution_claimed is False`; assert reset/reuse
demands still fail closed on P0 profiles.

## AI planning record (size L)

- Status: proposed Plan draft (batch A–D, 2026-08-09)
- Authoring environment: Cursor (Grok 4.5)
- Size: `L` — touches typecheck rejection gating, Host/settings seam,
  Fake executor wire from AST/QSem, tests across Kernel + Host; high
  risk of over-claiming execution.
- Route: AT-TDD after Plan + Phase approvals; Architecture Accept of
  ADR 0198/0199 preferred before JobResult/reset slices but not required
  for a FakeExecResult-only MVP per Plan default above.
- Assumptions: LISS-0382 witnesses remain the source of measurement /
  control correlation; LISS-0077 verifier stays authoritative for match /
  merge / escape rules.
- Confidence: medium — gate spelling and JobResult timing vs ADR 0198
  Accept are Adjudicator choices.
- Revision links: none yet.

## Exit criteria

- [ ] Plan approval (this document).
- [ ] Spec Gherkin locked under Plan approval.
- [ ] Phase 1 Red / Phase 2 Green / Phase 3 Refactor (only after Plan).
- [ ] Completion approval before merge.

## Adjudicator decision points (before Plan approval)

1. Exact Fake gate spelling (CLI flag vs settings key vs Host API).
2. Whether Plan requires ADR 0198 Accept before any JobResult touch.
3. Whether unconditional `DYNAMIC_UNSUPPORTED_FEATURE_ERROR` is replaced
   by profile-gated diagnostics or kept in addition to Fake success path.
