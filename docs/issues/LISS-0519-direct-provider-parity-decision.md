# LISS-0519: Direct-provider parity decision

| Field | Value |
|---|---|
| Status | **in_progress — direct routes deferred by approved technology decision** |
| Phase | phase-0-design |
| Type | provider route decision |
| Priority | P1 |
| Initial size | M |
| Current size | M |
| Parent | WP-0136 |
| Depends on | LISS-0514, LISS-0516, LISS-0517 |
| Blocks | any direct Quantinuum, IonQ, Rigetti, or QuEra adapter work |
| Implementation permission | None |
| Post-review requirement | None unless a demonstrated gap reopens a route |

## Review outcome

Recommend `defer` for direct Quantinuum, IonQ, Rigetti, and QuEra routes. A
direct adapter requires a demonstrated gap after AWS/Azure route evidence;
Rigetti has the clearest future trigger through Quil-T/pulse or direct
calibration control. See the [provider technology-selection review](../collaboration/reviews/2026-09-10-provider-technology-selection-review.md).

## Objective

Decide separately for Quantinuum, IonQ, Rigetti, and QuEra whether direct API
access closes a demonstrated gap left by AWS or Azure aggregation.

## Phase 0 scope

- Compare route-level lifecycle, capability metadata, artifact formats,
  measurement ordering, calibration evidence, availability, and cost model.
- Preserve separate `access_route`, `hardware_provider`, and `device_id`.
- Assign one of `add`, `defer`, or `reject` to every candidate direct route.
- Create no adapter Issue for `defer` or `reject`.

## Luna execution packet

- Model: `gpt-5.6-luna`; reasoning: `high`; official provider documentation
  plus the accepted AWS/Azure gap records only.
- Include: this Issue, WP-0136, LISS-0514, completed LISS-0516/LISS-0517
  records, dependency policy, and provider-neutral job/result contracts.
- Omit: credentials, account data, provider SDK source, live calls, and
  speculative implementation.
- Allowed changes: this Issue, WP-0136, one parity decision note, and trace.
- Output: one evidence row per provider, `add/defer/reject`, rationale summary,
  compatibility state, risks, and any requested technology approval.
- Stop after the decision record. Do not create tests or code.

## Acceptance criteria

- No provider is selected merely because a direct API exists.
- Every `add` names a specific aggregated-route gap and bounded first device.
- Unknown availability, price, or access remains `unknown`, not inferred.
- D-Wave and other non-gate-model lanes remain out of scope.

## Verification

- Every nontrivial claim has an official source URL and capture date.
- `git diff --check` and documentation-link check pass.
