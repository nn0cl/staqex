# LISS-0582 public-import repair — Phase 2 verification

## Scope / authorization / state

Accepted [R01–R07](../../specs/evaluator-public-import-compatibility-repair.md),
[Red acceptance](2026-10-05-liss-0582-repair-red-acceptance.md),
LISS-0582 / WP-0174 / AIP-0582-002 (M).
Human `Phase 2 Green／implementation` received 2026-10-05 after the unique
implementation approval request. Phase and implementation approved for this
import-only repair, not Phase 3, final verification or delivery.
Approved scope: ten original-object exports, frozen baseline and ownership.
Implementation allowed yes within Phase 2 only; post-review yes; batch N/A.
This is execution evidence, not a Phase 3 reviewer pass or issue completion.

Design/readiness: accepted tests reviewed and byte-frozen; sole production
owner evaluator facade; no new business logic, VO/DTO, port, adapter, provider,
dependency or ADR. Operating path Feature Path, host implementation;
same_context review setting, empty model IDs, no enabled large-change override
or numeric structure budget. Global/dynamic consumers/cycles remain gaps.

## Exact changes / clause reconciliation

- R01/R02: restore EvolveExpr, Measure, OpAttr, OpBin, OpBinder, OpCall,
  OpIndexed, OpPauli, OpPow through existing ast_nodes facade; replace from
  dataclasses. No wrapper, alias, direct legacy import or `__all__` restriction.
- R03: frozen generator/cases/expected JSON unchanged; real capture/cmp agrees.
- R04: consumer-first imports, legacy error identity and private rational
  behavior exercised by accepted tests; existing consumer regression retained.
- R05: production diff evaluator only, 12 added/1 deleted physical lines:
  imports/comments. Executable AST unchanged against base423c003b; successor,
  orchestration/installer and accepted tests unchanged. No new state/body owner.
- Lifecycle: after 37 focused passes, retire all five exact active-Red entries;
  no exclusion, skip or xfail remains. This metadata change is not test weakening.
- R06: scoped runs separated below. Full root passes provisionally;
  post-commit checks pending; remote CI not_run at repaired head. No full delivery Green claim.
- R07: no push/merge/force/history rewrite or later-source propagation. Later
  feature heads need explicit snapshot-guard disposition and new-SHA evidence.

Physical source lines before/after: evaluator1139/1149, successor181/181,
orchestration154/154, compatibility installer317/317. Only import surface
grew; no executable AST change. Retain existing body structure within this
bounded repair; not a claim of global responsibility decomposition completion.
Numeric budget dispositions not applicable (settings absent), qualitative
ownership checked. Unknown dynamic graph is not permission to widen scope.

## Declared blocking commands and environment

cwd `/Users/nn0cl/Documents/git/qpex`; macOS27.0.1 arm64 / Python3.12.6 /
pytest9.0.3. Baseline423c003b0b39c292731f6a8c7456a0b40cbd03f2.
Accepted-test/docs commit c7c726978de8d8e1228b49982c2caf8987ec4603;
pre-commit results are dirty-tree/provisional, not final-SHA evidence.

- `/usr/local/bin/python3.12 -m pytest tests/ -q --junitxml=PATH`, no exclusions.
- `/usr/local/bin/python3.12 tests/spec_verification/run_all.py`.
- `/usr/local/bin/python3.12 scripts/capture-refactor-baseline.py --cases
  tests/fixtures/liss_0543/baseline-cases.toml --output PATH`, then
  `cmp docs/testing/refactor-baseline.json PATH`.
- Repository sanity: all eleven applicable CI run blocks, using host Python,
  local PR-base/head/branch values and unique external temporary output paths.
  Includes required docs/ADRs, syntax, batches, document/coverage/Red lifecycle,
  baseline, conflict markers, template copy smoke and traceability. No remote
  checkout/setup/permissions simulation or GitHub CI success inferred.
- Focused37, consumer8 and adjacent52 commands are exactly the selections in
  the [trace](../traces/2026-09-29-liss-0582-runtime-plan-eligibility.md).

## Provisional scoped evidence

All errors/skips/exclusions0, failures0. End time = start + recorded duration.

| Scope | Result / exit | Start JST / duration | Evidence |
|---|---|---|---|
| focused repair | 37 pass / 0 | 2026-10-05 11:23:02.350428 / 1.061s | `/private/tmp/liss0582-repair-green-focused.xml` |
| consumer / baseline-generator regression | 8 pass / 0 | 11:23:03.381863 / 0.776s | `/private/tmp/liss0582-repair-green-consumers.xml` |
| adjacent / original ownership | 52 pass / 0 | 11:23:04.412912 / 0.534s | `/private/tmp/liss0582-repair-green-adjacent.xml` |
| spec runner | 161/161, 100%, gate PASS / 0 | tool output; exact pre-commit timing not recorded | execution output; rerun at commit required |
| capture/cmp | three cases, bytes equal / 0+0 | tool output; exact pre-commit timing not recorded | `/private/tmp/liss0582-repair-green-baseline.json` |
| repository sanity | 11 pass / 0 | 11:27:01.887021–11:27:05.823591 | `/private/tmp/liss0582-sanity-sn2gyjzi/results.json` |
| full root | 2322 pass / 0 | 11:24:01.698734 / 320.795s | `/private/tmp/liss0582-repair-green-root.xml` |

All provisional local blocking checks passed. All blocking commands must rerun after
the implementation/status commit; post-commit external logs/XML tied to that
SHA are authoritative, and must be read before reporting final local Green.
Any later documentation commit requires another all-blocking rerun.

Failure comparison: fourteen known import/manifest/route failures resolved by
unchanged focused tests; previously passing23 still pass. Consumer/adjacent
same selections pass. Full local baseline-root comparison unavailable (not run
before repair); old Ubuntu CI root2285 is not an identical local environment.
No complete no-new-failures claim inferred from focused success.

Frozen SHA256s: new test88c949852d81846a5ff28b90a7fd226f25017f0aba69bd0a94a3381e48036a8f;
original test a9be2ddbe1984414c1e5c0244e15735ba2aa6481036e4c7cc07a2b2482058953;
expected JSON1dcc3848030fdf48f3c44ebbe8951853b1698cce2ffd75c713d213e22dc99692.
Generator/cases retain recorded Phase 0 hashes. New evaluator SHA256
7e91c417178f0c49abcef36aaa618b8b6946a4dc0d9325974225e89b0a22c8a5.

Temporary local sanity harness first exited1 because its copied mktemp path
became `/private/private/tmp/...`; this was harness path rewriting, not a
repository failure. Corrected external harness and reran all11 checks; no
repository source/test/CI change to pass it, no failure hidden or excluded.
Generated smoke checkouts/logs retained outside the worktree; no recursive
cleanup or user data deletion. External harness is not shipped application code.

## Next gate

After all declared local checks pass at implementation commit: request
Phase 3 Refactor/review approval (phase). Post-review required yes, batch N/A;
do not execute refactor from Phase 2 permission. Final approval/remote CI,
PR #604 delivery and downstream new-SHA/merge-result evidence remain pending.
