# LISS-0583 Phase 2 implementation / verification handoff

Current guard follow-up: explicit Phase 2 implementation approval received;
bounded dispatch implemented. [Fresh supplemental evidence](2026-10-06-liss-0583-guard-phase2-verification.md)
supersedes old readonly-guard failures below; committed all-blocking verification
and source-clean gap remain. Earlier pending guard approval statements historical.

Current follow-up: human approved Scope / Phase 0 design for the0584 guard on
2026-10-06. [G01–G07 supplement](../../specs/evaluator-static-foreach-repair-guard-migration.md)
subsequently accepted unchanged by human. Explicit guard Phase 1 execution
produced [reviewed Red tests](2026-10-06-liss-0583-guard-phase1-review.md);
human guard test acceptance subsequently received2026-10-06. Next gate explicit
guard Phase 2 Green/implementation approval, not Phase 3 or delivery.
Feature Phase 2 source/tests/fixtures/lifecycle unchanged during design; prior
verification and blockers below remain historical evidence, not fresh passes.

## Review target and authority

Feature Path / phase-2-green, AIP-0583-002 size M. Human
`LISS-0583 Phase 2 Green／implementation承認` authorizes minimal implementation
of [accepted F01–F08](../../specs/evaluator-static-foreach-elaboration.md), after
[human test acceptance](2026-10-05-liss-0583-phase1-review.md). Implementation
permission: yes for this bounded Phase 2 only; post-review yes, batch N/A.
Phase 3, final review and delivery are not authorized.

## Implementation and reconciliation

- New `runtime/evaluation/static_foreach.py` owns the expansion algorithm.
  Evaluator's original method body is removed, not retained behind a facade.
- Existing private hook is installed as the identical successor function.
  Only one private installer import/setup and exact compatibility mapping added.
- Context gains only accepted `static_register_sizes: Mapping[str, int]` and
  `_run_foreach` declarations. Mutable state stays in Evaluator; no map copy,
  new state owner, provider/port/dependency, prevalidation or rollback added.
- All original public imports retained even if internally unused. New context
  and Joint imports are type-only; no successor import from evaluator.
- F01–F05 algorithm AST matches original after only `self`→`context`, ignoring
  docstring/signature. F06 ownership/setup/live-state, F07 actual export/cold
  consumer/byte capture, F08 exact guard/adjacent preservation all pass.
- Reviewed tests, fixture, guard support and frozen baseline unchanged.
  Four lifecycle exclusions retired only after all94 focused nodes passed;
  root is run without any deselection. This is not assertion weakening.

## Verification states

Tested HEAD/base `6d1b851bff292ae496145b71e7a15a9be757cfd1` **plus dirty source
and records**, branch `codex/liss-0583-phase1-rereview`; not committed evidence.
cwd `/Users/nn0cl/Documents/git/qpex`, macOS27.0.1arm64, Python3.12.6
`/usr/local/bin/python3.12`, pytest9.0.3. No network/provider used.

| Scope | State | Evidence |
|---|---|---|
| Focused94 | passed, exit0, failures/errors/skips/exclusions0 | `/private/tmp/liss0583-phase2-focused.xml` |
| Consumer/adjacent77 | passed, exit0, failures/errors/skips/exclusions0 | `/private/tmp/liss0583-phase2-consumer-adjacent.xml` |
| Root2423, no exclusions | failed:2422passed/1failed, exit1, errors/skips/exclusions0 | `/private/tmp/liss0583-phase2-root.xml` |
| Spec161/161 | passed, exit0 | `/private/tmp/liss0583-phase2-spec.log` |
| Local non-PR sanity10 | failed:9passed, copy smoke failed, aggregate exit1 | `/private/tmp/liss0583-phase2-check-records.jsonl` and individual logs |

Focused start16:14:06.085612JST, duration1.408s; consumer start16:14:07.167357JST,
duration25.156s. XML supplies timestamp/duration/counts. Exact focused/consumer
selectors are the Phase 1 trace commands with phase2 evidence prefix.
Root command: `/usr/local/bin/python3.12 -m pytest tests/ -q
--junitxml=/private/tmp/liss0583-phase2-root.xml`, no ignore/deselect arguments.
Spec: `/usr/local/bin/python3.12 tests/spec_verification/run_all.py`.
Sanity runs all10 non-PR shell steps from current `.github/workflows/ci.yml`,
with explicit Python3.12 and scratch cleanup trap omitted (scratch retained),
via external `/private/tmp/liss0583-phase2-checks.py`. JSONL records commands,
SHA, dirty status and UTC start/end. PR-only traceability not_run; no CI claim.

Baseline scoped comparison: clean6d1b851b review90pass/4structural failures
becomes94pass; all four exact failures resolved, no new focused failure IDs.
Consumer77 remains passing. Previous clean main root evidence has2419passes
and4approved structural deselections; a fresh same-SHA pre-change root was not
rerun here. Historical `/private/tmp/liss0584-merge-root.xml` was read and has
0failures/2419passes; current root adds the four now-passing structural nodes
and has one new blocking failure in0584's readonly source guard. Same runtime
versions, but no fresh pre-change checkout rerun claimed. Root start
16:14:49.500104JST, end16:20:11.331104JST, duration321.831s.

## Findings, routing and structure

1. **Already closed with evidence:** structural ownership, real hook and live
   state requirements now pass unchanged; unrelated AST/byte guards pass.
2. **Human scope/spec disposition required, do not edit now:** root failure
   `tests/test_liss_0584_repair_boundary_red.py::test_existing_f05_owner_and_readonly_dependencies_are_preserved`.
   Its immutable repair-boundary fixture byte-freezes evaluator.py,
   compatibility.py and context.py; all three differ by the approved extraction.
   Other readonly dependencies match. R07 constrained0584's numeric-only repair;
   this is an additional repair-base guard not covered by0583's accepted F08
   three-guard migration (which names0582 tests only). It was missed in the
   pre-implementation guard inventory. Do not rehash, skip or remove it; request
   bounded Scope/Phase 0 design to reconcile its successor protection first.
   No semantic-regression failure was observed in the other2422 root nodes,
   but full Green is false and exhaustive semantics are not established.
3. **Apply only after guard scope is resolved and local commit approved:** copy smoke rejects
   `Uncommitted distributed source: docs/specs/evaluator-static-foreach-elaboration.md`.
   Do not bypass source-clean or weaken its test. Commit the reviewed records
   and implementation as a bounded unit, then rerun every blocking check at the
   actual committed SHA. Full Green/Phase 2 completion is not claimed now.
4. **Out of scope with gap retained:** dynamic/out-of-tree consumer overrides,
   resolved global ownership/cycles and optional numeric budgets remain unknown.

Reviewer reread the actual current successor and source diff from disk, matched
the implementation to accepted clauses and read fresh outputs; no Phase 3
review claimed. Effective route same_context (weaker), host implementation,
empty model IDs; large-change override absent. Dirty-tree review-change JSON
`/private/tmp/liss0583-phase2-routing.json` explicitly reports uncommitted metric
gaps; committed-diff metrics cannot describe the new module yet. Manual physical
measurement: Evaluator1149→1099, successor69, context275→278,
compatibility317→323. New module owns one responsibility; unrelated large
modules are unchanged and are not hidden behind this split's facade.

Applied lessons: accepted guard lifecycle, source ownership/body removal,
private hook identity, public export baseline, sole state owner and status sync.
Existing bounded-repair-guard lesson reapplied to the missed prerequisite guard;
no new operating rule adopted. Next requested approval: **Scope / Phase 0 design
for the0584 repair-boundary guard's bounded migration within0583**; test/spec
changes require later reviewed approval. Local commit/all-blocking rerun follows
only after that resolution, not Phase 3 or delivery. No commit/push/merge
or issue completion performed. See representative trace for resumable state.

After records: relative links and git diff --check pass; lifecycle0entries and
reviewed-test diff empty. Spec161 and local sanity repeated under
`/private/tmp/liss0583-phase2-record-*`: same9pass/1copy-smoke failure.
Targeted prerequisite-guard rerun:5passed/1failed,6nodes, exit1,
errors/skips/exclusions0,0.19s; same readonly failure, other TypeChecker
preservation/mutation checks pass. Evidence
`/private/tmp/liss0583-phase2-prerequisite-guard.xml`. No tests/fixtures edited.
