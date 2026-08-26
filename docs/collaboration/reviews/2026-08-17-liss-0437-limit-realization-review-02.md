# LISS-0437 finite formal-Limit realization review loop

## Trigger

- User request: continue the independent context review/correction loop.
- Date: 2026-08-17.
- Review scope: approved finite gate synthesis for explicit `Realize`.
- Issue / ADR / Spec / WorkPlan: LISS-0437 / ADR 0210 / LISS-0437 Spec and WP.
- Branch: `codex/wp-0100-explicit-evolution-surface`.
- Current phase: finite realization implementation and verification.
- Allowed paths: `compiler/staqex/backend/qasm/lower.py`, focused LISS-0437 tests, and review/trace records.
- Explicitly excluded: live QPU submission, provider SDK integration, and S02 numerical migration.

## Review lenses

- Contract completeness: the source-visible `Realize` boundary must be enforceable.
- Source-to-domain fidelity: a blackboard `Limit` must not silently become a finite gate plan.
- Realization/fail-closed behavior: unsupported or non-unitary target mappings must reject before allocation.
- Evidence hygiene: provenance and focused tests must identify the actual transformation.
- Phase/approval discipline: the correction must remain within the approved finite synthesis scope.
- Prior review records consulted: `docs/collaboration/reviews/2026-08-15-liss-0437-realize-green-review-01.md`.

## Independent reviewer

- Context mode: fresh independent context.
- Reviewer task: read-only review of the current finite realization implementation.
- Read-only: yes.
- Implementation permission: no.
- Approval authority: none.

## Iteration 1 — prior review and disposition

- State entered: `REVIEW`.
- Reviewer: Gibbs (`01a00b71-6c4a-7282-9d3e-ccf96ab95ba7`).
- Readiness verdict: `NOT READY`.
- Findings:
  - F-01: `formal_limit_capability_reject` could allow a direct `Limit` based on a target profile, contrary to ADR 0210's explicit `Realize(source=...)` boundary.
  - F-02: the lowering path could therefore reach finite lowering for a bare `Limit`; the no-implicit-realization rule was not conclusively enforced.
  - F-03: the policy test count in the review evidence was stale (`3/3` observed versus the older `2/2` wording).
- Finding dispositions:
  - F-01 — `accepted`; disposition authority: primary agent under the accepted ADR/Spec/Issue boundary; design deviation: `no`. Evidence: ADR 0210 explicit conversion boundary and `compiler/staqex/backend/qasm/lower.py` preflight.
  - F-02 — `accepted`; same authority and rationale. Evidence: direct-Limit focused test now asserts `EVOLUTION_REALIZATION_REQUIRED` even with a populated target profile.
  - F-03 — `accepted`; documentation/evidence correction only. The focused policy runner is now reported as `2/2` for its two tests.
- Corrections applied:
  - `formal_limit_capability_reject` now records spans of only those `Limit` bindings explicitly named by `Realize(source=...)`.
  - Every other `Limit`, including a bare target source with a complete target profile, rejects as `EVOLUTION_REALIZATION_REQUIRED` before allocation.
  - The direct-Limit acceptance test and policy test were updated to assert the source-visible boundary.
- Files changed: `compiler/staqex/backend/qasm/lower.py`, `tests/test_liss_0437_realize_surface_red.py`, `tests/test_liss_0437_limit_policy_green.py`.
- Remaining blockers: fresh independent re-review.
- Reviewer perspective to retain: target configuration must never substitute for a source-visible realization operation.
- Next review condition: review the current artifacts in a new independent context.

## Iteration 2 — fresh re-review

- State entered: `RE_REVIEW`.
- Reviewer: Avicenna (`01a00b74-e2e5-7803-8ccc-e07076a0478a`).
- Readiness verdict: `NOT READY`.
- Findings:
  - F-04: QASM notes used fallback target-profile order/steps instead of the effective `Realize` policy values.
  - F-05: compile-level `Realize` provenance and product rejection provenance did not expose the complete common envelope required by the Spec.
- Finding dispositions:
  - F-04 — `accepted`; disposition authority: primary agent under the accepted ADR/Spec/Issue boundary; design deviation: `no`. Evidence: finite test now asserts `Suzuki S2 steps=4` for `Realize(... steps=4)`.
  - F-05 — `accepted`; same authority and rationale. Evidence: Spec common envelope and new assertions for compile-level and product-rejection fields.
- Corrections applied:
  - QASM notes now use the effective finite realization order/steps returned by the formal-Limit lowering provenance.
  - `method=product` rejection now includes the common approximation/resource/rejection fields, and compile-level `Realize` provenance includes the same common fields.
- Files changed: `compiler/staqex/backend/qasm/lower.py`, `compiler/staqex/pipeline.py`, `tests/test_liss_0437_limit_realization_red.py`, `tests/test_liss_0437_realize_surface_red.py`.
- Remaining blockers: fresh independent re-review of Iteration 2 corrections.
- Reviewer perspective to retain: verify effective policy values and the full provenance envelope at every semantic-to-target boundary.
- Next review condition: run a new independent read-only review against the current artifacts.

## Iteration 3 — final fresh re-review

- State entered: `RE_REVIEW`.
- Reviewer: Singer (`01a00b79-e72b-7193-a97b-4d6948c4dd94`).
- Readiness verdict: `READY` for the approved finite gate synthesis correction scope.
- Findings:
  - No P0/P1 findings.
  - P2 non-blocker: the overall worktree is dirty and contains pre-existing S02 changes; this finite-synthesis correction did not add S02 migration.
- Finding dispositions:
  - P2 — `deferred`; disposition authority: primary agent; no design deviation. It is pre-existing worktree state and outside this bounded correction.
- Corrections applied: none after Iteration 2.
- Remaining blockers: none for the approved finite gate synthesis scope.
- Reviewer perspective retained: verify effective policy values, full provenance envelope, and allocation-free rejection at every target boundary.
- Next review condition: none for this correction loop; new review only if artifacts or scope change.

## Terminal decision

- Terminal state: `COMPLETE`.
- Completion basis or abort reason: final fresh independent review is READY; all actionable findings are resolved, and the only P2 is explicitly deferred as pre-existing/out of scope.
- User/Adjudicator decision required: none unless a finding requires architecture, technology, Issue, or phase change.
- Evidence path: this record and `docs/collaboration/traces/2026-08-17-liss-0437-limit-realization-review-02.md`.

## Gate status

- Requested approval type: implementation/verification within the already approved finite gate synthesis scope.
- Approved scope: explicit `Realize` finite gate synthesis only.
- Approval authority / approver: user approval recorded in the task history.
- ADR status: ADR 0210 Accepted.
- Specification status: accepted and amended for explicit `Realize`.
- Phase approval: finite synthesis approved.
- Implementation approval: bounded implementation approved.
- Post-review requirement: fresh independent review before completion.

## Evidence

- Deterministic checks before Iteration 2:
  - `GREEN: 5/5 Realize boundary checks passed`
  - `GREEN: 2/2 finite realization checks passed`
  - `GREEN: 2/2 Limit policy checks passed`
  - `GREEN: 6/6 Phase 3 bounded checks passed`
  - `OK — Evolve until runtime tests`
  - Python compilation and `git diff --check` passed.
- Related trace: `docs/collaboration/traces/2026-08-17-liss-0437-limit-realization-review-02.md`.
