# LISS-0587: Evaluator partial filling successor

## Metadata

- Local issue ID: LISS-0587
- GitHub issue: none
- Status: in_progress
- Phase: phase-2-green
- Type: behavior-preserving responsibility extraction
- Priority: WP-0174 rank 6, first cohesive slice
- Initial planning size: M
- Current planning size: M
- Owner/agent: Codex desktop host
- Parent: WP-0174 / WP-0160
- Depends on: LISS-0586 delivered; documentation PR610 merged b5ad7402
- Blocks: no other issue currently declared
- Related branch: `codex/liss-0587-partial-filling-phase0`

## Scope and acceptance notes

Human `続けて` on2026-10-12 responds to the uniquely presented rank6
Scope/Phase0 design-start gate. This permits investigation/design only.
Human explicitly accepted dedicated Issue/spec P01–P09, bounded guard
transition and Phase0 acceptance on2026-10-12. Phase1 Red execution separately
approved2026-10-12: acceptance tests and bounded guard migration only.
Human Phase1 Red test review/acceptance approved2026-10-12.
Human `LISS-0587 Phase 2 Green／implementation承認` received2026-10-12.
Implementation allowed for the accepted slice only. Local commit / actual-SHA
all-blocking revalidation separately approved2026-10-12; delivery and Phase3 remain separate.

Accepted design extracts only `_fill_partial` with its `PartialValue` representation.
Do not group `_is_closed` and `_maybe_capture_classical_scalar` with it:
the former reads scalar/object environments recursively, while the latter
reads a Joint marginal and writes Evaluator.scalars. They remain distinct
rank6 candidates requiring their own acceptance boundaries.

Agreement accepted in [P01–P09](../specs/evaluator-partial-filling-successor.md).
Resume via [trace/handoff](../collaboration/traces/2026-10-12-liss-0587-partial-filling.md).
Base: b5ad7402c184a3a79440271e02dd423c53d8bc36. No new architecture,
technology, mutable-state owner or external resource is proposed.

## AI planning record AIP-0587-001

- Status: accepted by dedicated Issue/spec and Phase0 acceptance2026-10-12.
- Created:2026-10-12; author:Codex desktop, local macOS workspace.
- Displayed model/reasoning: N/A; stable host labels not exposed.
- Planning size:M, related source/compatibility/type/guard/test owners.
- Intended route:host design and later authorized implementation;
  review same_context per live routing; model identifiers empty.
- Estimated token range/midpoint/metric:N/A; no calibrated estimator.
- Basis:31-line fill method plus7-line dataclass, existing repair guard chain,
  direct and name-based consumers; low confidence in dynamic consumer completeness.
- Assumptions:exact algorithm and mutable dataclass semantics preserved;
  old import and serialized class identity retained.
- Revisions:none. Guard transition and Phase1 test execution accepted;
  human test acceptance and Phase2 implementation separately approved2026-10-12.

## Adjudicator gate

Agent Phase1 Red review passed2026-10-12:
[review packet](../collaboration/reviews/2026-10-12-liss-0587-phase1-red-review.md).
Human `LISS-0587 Phase 1 Red テストレビュー／acceptance承認` received2026-10-12;
the exact reviewed tests/fixtures are accepted unchanged. Reviewer made no source/test edits.

Dedicated Issue/spec P01–P09, bounded guard transition and Phase0 acceptance
approved2026-10-12; Phase1 execution and test acceptance separately approved.
Phase2 implementation separately approved2026-10-12. Minimal production move
implemented. Human `LISS-0587 ローカルコミット／実SHAで全blocking再検証承認`
received2026-10-12. Commit/revalidation execute only this unchanged unit.
Result pending at record commit; actual SHA and current result entry:
`/private/tmp/liss-0587-sha-verification.fYIOBG/result.md`.
After all blocking pass, next gate:Phase3 Refactor/review approval.
Phase3 and remote delivery remain unapproved. Earlier dirty-run failure is historical.

## Phase2 implementation and verification

`evaluation/partial_calls.py` now owns the exact original mutable dataclass
and hole-filling algorithm. Evaluator re-exports the same class and maps its
static hook directly to the successor. Old bodies removed; old pickle path
retained. No consumer, other helper, accepted test, fixture or exclusion changes.

[Phase2 verification record](../collaboration/reviews/2026-10-12-liss-0587-phase2-verification.md)
links the current committed verification entry and historical dirty-run results.
Historical provisional results:Focused48, inherited143, adjacent16,
spec161 and real import/AST smoke pass. Root2621 passed332.31s,exit0.
Repository-sanity first9 checks pass; copy-smoke fails because new distributed
spec is uncommitted. No guard bypass or full Green/phase-completion claim.
Evaluator1014→976 lines; successor52. Those runs used dirty HEAD b5ad7402;
the approved committed-SHA rerun result above determines current Green status.

## Phase1 execution inventory

Historical Red evidence below predates the approved Phase2 implementation;
current results and remaining gate are in the Phase2 record above.

New tests map to the accepted clauses; P05's seven existing behavior suites
remain byte-for-byte readonly in immutable22-file boundary evidence.

| Clause | New test family / evidence |
| --- | --- |
| P01 | behavior::test_p01_left_to_right_preserves_inputs_and_occupied_identity (3 cases) |
| P02 | behavior::test_p02_repeated_stepwise_fill_keeps_original_values |
| P03 | behavior::test_p03_exact_fill_preserves_order_and_first_argument_span (2 cases) |
| P04 | behavior::test_p04_invalid_arity_has_exact_error_and_no_mutation (6 cases) |
| P05 | seven readonly adjacent suites listed in spec,16 cases; ownership readonly22-file manifest |
| P06 | behavior legacy/current pickle and class/instance static tests; ownership exact reexport/hook |
| P07 | ownership exact successor, absent old bodies and both cold import orders |
| P08 | ownership two unaffected AST/import cases and22-file readonly manifest |
| P09 | guard_migration27 cases: real positive pre/post copies, mutations, historical reconstruction, fixture and byte guards |

Family prefixes mean `tests/test_liss_0587_partial_{behavior,ownership,guard_migration}_red.py`.
New focused run:44 passed /4 intended ownership Red. No collection/setup
failures after correcting an ambiguous field-mutation substring in first run.
Full root:2617 passed /same4 intended Red,341.84s; no other failures/errors/skips.
Inherited guards/imports:143 passed7.61s; adjacent16 passed0.40s; spec161/161 PASS.
Doc/test lifecycle, coverage consistency and git diff --check passed.
Environment:macOS27.0.1 arm64,
CPython3.12.6 / pytest9.0.3. HEAD/base b5ad7402, dirty uncommitted tests/docs;
no committed-SHA Green claim, no exclusions. Evidence:`/private/tmp/liss-0587-red.L9zKc8/`.

Bounded existing test edits:0583 guard support calls exact partial restoration;
0584 real repair guard checks live successor;0583 and0585 fixture-copy carriers
copy the actual new successor when present. Old fixtures, hashes, assertion
and exclusion settings unchanged. New immutable source fixture matches
base whole AST including docstrings; legacy pickle comes from the old class.
The temporary moved AST is never imported or installed as production.

Four Red nodes, all in `test_liss_0587_partial_ownership_red.py`:
`test_p07_successor_owns_exact_class_and_algorithm`,
`test_p07_old_class_and_method_bodies_absent`,
`test_p06_exact_reexport_and_static_successor_identity`,
`test_p07_both_cold_import_orders_have_single_class_and_hook`.
Three require the unimplemented successor; one requires removal of the old
class/method. These are four contract nodes, not four independent root causes.
No new active-Red exclusions were registered; root intentionally exits1.
Cold-import post-move success and all-blocking Green remain unestablished.
Full same-environment baseline root was not rerun; baseline comparison unavailable.
