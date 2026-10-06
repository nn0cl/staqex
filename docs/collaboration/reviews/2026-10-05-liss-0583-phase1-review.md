# LISS-0583 Phase 1 Red review request

## Review Target

- Artifact: [accepted F01–F08 spec](../../specs/evaluator-static-foreach-elaboration.md),
  [Issue](../../issues/LISS-0583-evaluator-static-foreach-successor.md), tests below.
- Current phase: Feature Path / phase-1-red; AIP-0583-002, size M.
- Requested approval: Phase 1 test review/acceptance, including the bounded
  three-guard migration; separately decide F05 repair scope.
- Approval type: phase; scope decision requested separately, not inferred.
- Approved scope: static foreach extraction test preparation and limited guard
  migration only, human execution approval2026-10-05.
- Implementation allowed: no. Post-review required: yes. Batch: N/A.
- Result: tests prepared; NOT unconditional review passed / Green clearance.

## What Changed / clause mapping

Test paths below are relative to the repository root.

| Contract | Executable evidence |
|---|---|
| F01 | `tests/test_liss_0583_static_foreach_behavior_red.py`: member/body order, two operators, spans/identity, bindings/logs, Joint tokens, empty body |
| F02 | same module: ten invalid bound forms, exact error and zero callbacks; retained `tests/test_kernel_classical_boundary_red.py` measurement-dependent source diagnostic |
| F03 | same module:1024 lightweight bind callbacks,1025 exact diagnostic before callbacks |
| F04 | same module: two unsupported-body and seven invalid-call cases, first bind / prior valid operation preserved |
| F05 | direct register runtime characterization, `tests/test_static_hilbert_migration_red.py` compiled historical spelling, new source index/arithmetic/Measure/Snapshot cases and QASM operation order; arithmetic is failing |
| F06 | `tests/test_liss_0583_static_foreach_successor_red.py`: four structural Red nodes, real execution dispatcher/hook, live context, installer identity, no copied state; adjacent execution/calls/pipes fixed bytes |
| F07 | unchanged R01–R04 repair assertions: full wildcard/direct identity, five cold consumers, real capture equals frozen bytes; additional ForEachStmt/MVP identity |
| F08 | `tests/liss_0583_guard_support.py`, immutable provenance fixture,17 positive/negative guard cases, accepted ownership and adjacent suites |

## Bounded guard equivalence

| Old R05 protection | New protection / exact allowable delta |
|---|---|
| Original import-route snapshot | Full current import AST fixed, including ten repaired names; remove at most one exact underscore installer import before comparison. All other aliases/routes fixed. |
| Entire executable evaluator AST | Entire unaffected AST fixed. Only exact original `_run_foreach` may be removed, plus one exact installer setup. A retained/reintroduced changed body fails. |
| compatibility.py whole-file hash | Old byte hash preserved in pinned audit fixture. Entire existing AST fixed; allow only exact successor import and one exact typed hook installer (optional docstring). Existing wiring mutation, wrong target, extra state, duplicate installer fail. |

The third transition deliberately no longer protects comment/formatting bytes
in compatibility.py; it protects all existing executable/import AST. This is
the declared equivalence boundary, not a claim of identical byte protection.
Other six R05 frozen-file cases remain unchanged. Context accepts only two
exact typed declarations, not method bodies; execution/calls/pipes remain
byte-fixed. No production sources, frozen public manifest, generator, cases or
accepted plan-eligibility test were changed. The fixture hash is
`9cca28c93d06df68081ea2a3c01a54d07a9222aa2dcb002d3948c44325b66dd0`;
human test acceptance will freeze this candidate, not an earlier claimed approval.

## Findings and blockers

1. **F05 blocking, disposition: out of authorized implementation scope.**
   `ForEach q in reg { Int i = q + 1 }` compiles with `ok=True` on unchanged
   a287be51 compiler. Diagnostics are lane-soft/advisory finite-evidence and
   approximation messages, not arithmetic rejection. New acceptance test
   correctly exposes a current contract mismatch; this is not introduced by
   extraction. Root cause and wider arithmetic scope are not established.
   Retain test and accepted F05; no skip, weakening or Active-Red exemption.
   Recommendation: authorize a separate repair design/Issue first. Alternatively
   explicitly authorize expanding this Issue; that requires reviewed revised
   scope/spec before implementation. No decision or new Issue is inferred.
2. Four structural failures, disposition: apply in a later approved Phase 2.
   Missing successor (three nodes) and existing evaluator body (one node).
   Only these four exact nodes are registered Active-Red, review by2026-10-12.
3. Initial fixture failures, disposition: already closed with evidence.
   Strip QASM comments while comparing exact gates/order; use accepted
   `Snapshot q to stdout` syntax. Reviewer rerun has neither fixture failure.
4. Dynamic/out-of-tree consumer graph and global cycle resolution remain
   unassessed. Cold actual imports pass; no exhaustive compatibility claim.

## Deterministic verification / reviewer evidence

- Tested HEAD: `a287be51da358eed195f836afa21b07286128940` + dirty tests/docs,
  branch `codex/liss-0583-static-foreach-phase0`; compiler identical to HEAD.
- Environment: macOS27.0.1 arm64, Python3.12.6, pytest9.0.3, `/usr/local/bin/python3.12`.
- Initial focused:84passed/7failed; four structural, one F05, two fixture errors.
- Corrected focused:89passed/5failed,94cases,1.243s; no errors/skips/exclusions.
  XML `/private/tmp/liss0583-phase1-focused.xml`, start20:28:05.997075JST.
- Same-context reviewer rerun:89passed/5failed,94cases,1.181s;
  XML `/private/tmp/liss0583-phase1-review.xml`, start20:30:53.153665JST.
  Breakdown: behavior28passed, guard17passed, successor7passed/5failed,
  repair37passed (includes cold imports and actual byte capture comparison).
- Additional consumer8 + adjacent69 =77passed,24.594s, no errors/skips/exclusions;
  XML `/private/tmp/liss0583-phase1-consumer-adjacent.xml`, start20:28:29.343308JST.
  Exact selectors are in the representative trace.
- Lifecycle validation:4entries. `git diff --check` passed.
- All-blocking root/spec/sanity: **not_run**. No full Green/final-SHA claim.
  Arithmetic remains unexcluded and would block root even with structural
  exclusions; no CI success is asserted. No commit/push/merge performed.
- Test support/module physical lines110/169/121/123; production structure
  measurements unchanged from Phase 0. Numeric budgets absent, global metrics
  unknown. No production facade/body reduction claimed.

Reviewer role re-read spec, all three new test modules, support/fixture,
entire modified repair suite and its diff, unchanged runtime foreach body,
Static Hilbert Kernel and XML/log outputs from disk. Isolation: `same_context`,
weaker than separate_context; host implementation, empty requested model IDs,
no enabled large-change override. No source/test edits during reviewer role.
Applied existing lessons: compatibility baseline, private consumer identity,
acceptance reconciliation, bounded guard lifecycle, red-contract-scope and
red-fixture-interface. This packet does not replace human acceptance.

## Adjudicator Checklist / Decision

- [ ] Confirm phase and F01–F08 test mapping / bounded guard equivalence.
- [ ] Accept explicitly stated omissions and provisional scoped verification.
- [ ] Decide F05 separate repair vs explicit Issue scope expansion.
- [ ] Confirm implementation permission remains no at this gate.
- [ ] Approved / approved with comments / rejected / needs ADR.

Next safe action: obtain Phase 1 test acceptance and F05 scope disposition.
Do not begin Phase 2, automatically defer the mismatch or integrate old code.

## Subsequent disposition — 2026-10-05

Human `修復の設計開始承認` selects separate repair design:
[LISS-0584](../../issues/LISS-0584-opaque-foreach-wire-arithmetic-repair.md).
This resolves ownership only; the finding remains open and the original test
remains unmodified/unexcluded.0583 test acceptance is not inferred. Next current
target is0584 dependency-separation/commit decision after human
`専用Issue/spec R01–R07 と Phase 0 acceptance` received unchanged2026-10-05,
plus the still-separate
0583 test acceptance gate. Subsequent584 execution approval and prepared tests
are recorded in the [584 packet](2026-10-05-liss-0584-phase1-review.md);
the original F05 remains unchanged and unexcluded.0584 test acceptance received
2026-10-06;584 implementation subsequently approved and guard implemented.
[Current584 verification](2026-10-06-liss-0584-phase2-verification.md) retains
the sanity gap. This does not accept0583 tests or authorize0583 implementation.

Human `はい。` on2026-10-06 accepts the named11-file test carrier and three
prepared F08 guard transitions for0584 dependency delivery/local commits,
as detailed in [approved split](2026-10-06-liss-0584-commit-scope.md).
0583 feature acceptance/implementation remain separate, pending gates.
