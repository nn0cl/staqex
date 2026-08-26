# Work Plan: Architecture approval and reassessment gates

## Goal

Evaluate and, if accepted, incorporate the reusable parts of external feedback
about scope-versus-architecture approval, subsystem-boundary drift, and the
failure to revisit accepted server logic when new technical constraints appear.

The plan is stack-neutral and does not adopt the feedback's game-server
technology choices.

## Scope

- In: approval vocabulary, explicit implementation authorization, architecture
  reassessment triggers, impact-summary requirements, separation of human
  approval from automated verification, canonical-artifact decisions when
  directly relevant, and a CI-only validator for bounded execution batches.
- Out: target-project ADRs, game-server implementation, Claude-only Hooks,
  mandatory branch-policy exceptions, new application architecture, and a
  blanket requirement to duplicate every decision across ADR/Issue/WorkPlan/spec.

## Issue Graph

| Issue | Status | Initial size | Current size | Depends on | Blocks | Branch |
| --- | --- | --- | --- | --- | --- | --- |
| LISS-0017 | done | L | L | AIP-0017-001 | - | process/architecture-approval-gates |

## Recommended Order

1. Review the feedback as an intake signal and verify the candidate scope
   against the template's existing contracts.
2. Review AIP-0017-001 and decide whether approval semantics and architecture
   reassessment should stay bundled or become separate issues.
3. Accept the smallest document-only slice and create a dedicated process
   branch.
4. Update the common contract surfaces and relevant templates only after the
   accepted design is reviewed; add only the accepted CI-only validator and
   keep Hook behavior unchanged.
5. Add deterministic document/reference checks where a rule can be verified
   without relying on model behavior.

## Adjudicator Decision Points

- Treat the target repository's cited ADRs/traces as unverified until their
  contents are supplied or otherwise inspected.
- Prefer repository-state approval fields over a rule based only on chat-turn
  boundaries.
- Prefer canonical-artifact references over four-way content duplication.
- Decide whether the gate is normative for every agent or primarily a review
  checklist with optional tool enforcement.
- Allow pre-approved batches only for named, bounded, low-risk work; do not
  pre-approve unknown ADR decisions or architecture changes.
- Require a human transition from post-review-pending to post-reviewed; CI may
  validate the record but must not manufacture that approval.

## Risks

- Adding another mandatory gate may increase cognitive load and cause agents to
  over-classify small changes as architecture work.
- Broad trigger wording may turn ordinary refactoring into repeated redesign.
- Machine-readable approval state may create a second source of truth unless it
  is explicitly tied to the review record.
- Treating a branch as the primary safety mechanism would miss same-branch
  design-to-implementation drift.
- A batch record could become a blanket authorization if its Issue list,
  allowed paths, expiry, or invalidation triggers are not explicit.
- The batch branch and approval-commit binding must remain explicit; a record
  on an ordinary branch is validated for schema and references but does not
  silently authorize that branch's changes.

## Verification Plan

- Review candidate wording against `AGENTS.md`, `agent-quickstart.md`, and
  `implementation-readiness.md` for contradictions.
- Confirm every accepted rule names its authoritative artifact and stop
  condition.
- Run `git diff --check` and the repository's documentation/contract checks
  after implementation.
- Use a synthetic scenario: “administrative capability is approved for
  investigation” must produce design/impact review and no implementation
  authorization.
- Use a synthetic low-risk batch: named docs-only Issues may execute under one
  approval record, while an unlisted Issue or architecture trigger fails CI.
- Use a post-review scenario: CI accepts `post_review_required` while pending,
  but rejects a `post_reviewed` state that lacks the required human review
  fields.

## Current Next Issue

- None. LISS-0017 merged (PR #22). Plan complete.
- 2026-08-26: Ledger status synchronized during LISS-0024. Document-lifecycle
  work that collided on LISS-0017 now lives as LISS-0023 and is not part of
  this plan.

Process review: no remaining open acceptance notes in the merged
implementation. Status was stale after merge and was corrected later.
