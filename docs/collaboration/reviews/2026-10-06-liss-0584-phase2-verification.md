# LISS-0584 Phase 2 verification / unresolved delivery boundary

Current update2026-10-06: human `はい。` approves local A/B/C and0583 carrier.
A=a14ab3af, B=14973d84; C/head checks pending. Dirty evidence/failed sanity
below are historical. Final SHA evidence under `/private/tmp/liss0584-committed-*`.

## Review Target

- Canonical: [R01–R07](../../specs/opaque-foreach-wire-arithmetic-repair.md),
  [Issue/AIP-0584-001](../../issues/LISS-0584-opaque-foreach-wire-arithmetic-repair.md),
  [accepted tests](2026-10-05-liss-0584-phase1-review.md).
- Current phase: Feature Path / phase-2-green; focused Green, all-blocking gap.
- Authority: human `LISS-0584 Phase 2 Green／implementation approval（実装承認）`
  on2026-10-06; minimal implementation only.
- Requested decision: reviewed dependency/test-carrier/document separation and
  commit permission. Not a Phase 3 request or implicit merge permission.
- Implementation allowed: approved numeric repair only. Post-review yes; batch N/A.

## Change and Requirement Mapping

Only production change: `compiler/staqex/typecheck.py`,12 added lines in
`_infer_binop`. Infer operands once, left then right; reject five numeric
operators when either inferred kind is Wire, append existing hard code at
binary span, return the Wire operand as recovery type. No name/payload check,
no global assignment change or additional mutable state.

R01/R02: kind guard and Wire recovery preserve nested/alias rejection.
R03: existing hard diagnostic and explicit opaque-element numeric message.
R04/R05: non-Wire branches untouched, positive QASM/numeric suites pass.
R06: foreach env/binding code unchanged and identity tests pass.
R07: boundary/consumer/capture guards pass; all-blocking sanity is not passing.
No reviewed test/assertion/fixture, lifecycle exclusion or frozen baseline change.

## Environment / Evidence

Cwd `/Users/nn0cl/Documents/git/qpex`; macOS27.0.1 arm64, Python3.12.6
`/usr/local/bin/python3.12`, pytest9.0.3. HEAD/base
`a287be51da358eed195f836afa21b07286128940`, branch
`codex/liss-0584-opaque-wire-arithmetic-phase0`; dirty pre-existing0583/new584
tests/docs plus the new guard. Not final committed evidence.
Production SHA256: `917279f48ecb0ff4be1cdce6728b2046d1931bb5b3fc71aa76bb05f1ce58b0ca`.
Root start/end:2026-10-06T01:50:20.137133+09:00 to
2026-10-06T01:55:43.294133+09:00. Spec runner did not emit timestamps/duration;
these are unrecorded, not inferred from neighboring runs.

| Scope | Result | Evidence outside tree |
|---|---|---|
| Focused | 48 passed,0 errors/skips,exit0,0.587s; 01:50:18.094930–01:50:18.681930JST | `/private/tmp/liss0584-phase2-focused.xml` |
| Consumer/adjacent | 74 passed,0 errors/skips,exit0,25.938s; 01:50:18.909607–01:50:44.847607JST | `/private/tmp/liss0584-phase2-adjacent.xml` |
| Reviewer focused rerun | 48 passed,0 errors/skips,exit0,0.358s; 01:51:55.858832–01:51:56.216832JST | `/private/tmp/liss0584-phase2-review.xml` |
| Root, lifecycle-aware | 2419 passed,4 deselected,0 failures/errors/skips,exit0,323.157s | `/private/tmp/liss0584-phase2-root.xml` |
| Spec | 161/161 passed,exit0 | `/private/tmp/liss0584-phase2-spec.log` |
| Repository sanity | failed:9 checks pass,copy smoke fails;exit1;01:51:01.465057–01:51:02.441107JST | `/private/tmp/liss0584-phase2-sanity.log` |

Focused selectors and consumer74 command are exactly the Phase 1 commands in
[trace](../traces/2026-10-05-liss-0584-opaque-wire-arithmetic-repair.md), with
Phase 2 XML paths above. Root: `python3.12 -m pytest tests/ -q` plus the four
`--deselect` arguments produced by `scripts/check-test-lifecycle.py
--as-of 2026-10-06 --pytest-ignore-args`; no added exclusions. Spec:
`/usr/local/bin/python3.12 tests/spec_verification/run_all.py`.
Sanity: execute all10 non-PR-only `repository-sanity` shell steps from current
`.github/workflows/ci.yml`, preserving their commands, with explicit Python3.12;
omit only scratch-directory cleanup trap, retain scratch for inspection.
PR-only traceability not_run (no PR/final SHA); not a local CI-success claim.

Comparison: all24 Phase 1 failures resolved, including original unchanged F05.
Consumer74 remains passing. No comparable whole-root pre-guard baseline was run:
whole-root failure delta unassessed, not a fabricated zero-regression claim.
Sanity rejects `docs/specs/evaluator-static-foreach-elaboration.md` because it
was already untracked before this implementation; source-clean guard reads Git
status, not TypeChecker. Its failure is not waived as pre-existing.

## Same-Context Review / Structure Disposition

Switched to reviewer; reread accepted spec, current source diff, accepted tests,
boundary fixture and source-clean implementation from disk; reran focused48.
No further source implementation during review. Isolation same_context, weaker
than separate_context; host implementation, empty model IDs. No enabled
large-change override or quantitative structure settings.

`review-change.py --base a287be51 --head HEAD` reports dirty-tree unknown and
zero committed changes (not zero actual changes); normal same_context routing.
Measured real dirty source:4678→4690 physical lines; `_infer_binop`293→305.
Disposition: retain accepted guard-only fix; broad TypeChecker decomposition
is outside this repair. Existing large body is not disguised by a facade, and
this work claims no responsibility split. Dynamic/global graph not exhaustively
measured; no new dependency/import/cycle introduced by the12-line guard.

- Missing-wire guard: closed by48 focused tests and exact diff inspection.
- Nested recovery: returns actual Wire operand, never dispatches into ordinary
  numeric promotion; alias/env neighbors preserved.
- Reviewer cannot conclude full Green: copy smoke fails. Keep Phase 2 open.
- Reviewed-test protection: frozen fixture and original F05 hashes unchanged;
  no assertion relaxation, new skip/xfail or F05 exclusion.
- Commit/dependency gap: original adopted0583 test/behavior fixture and spec
  remain uncommitted. Arrange reviewed test-carrier/document dependency or
  agreed separation with human authorization; do not stage all dirty files,
  remove protected docs, amend hashes, or bypass clean-source check.

## Next Safe Action / Decision

Human `はい。整理して` authorizes organizing the
[A/B/C scope](2026-10-06-liss-0584-commit-scope.md) on2026-10-06, not actual commits.
Both uncommitted specs must be committed before source-clean smoke passes.
Next: human carrier/guard disposition and explicit local commit permission, then rerun
all blocking checks at the resulting SHA; only then consider separate Phase 3
approval. No final verification, push, PR or merge authorization inferred.
Do not mark Issue/WP done or Phase 2 fully Green while sanity fails.

- [ ] Dependency-separation/commit scope approved
- [ ] Approved with comments
- [ ] Rejected
