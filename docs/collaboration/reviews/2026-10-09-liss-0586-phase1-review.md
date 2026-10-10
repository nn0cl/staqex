# LISS-0586 Phase 1 Red same-context test review

## Outcome / approval boundary

Human acceptance2026-10-09:
`Phase 1 Red テストレビュー／acceptance承認（H04の扱いを含む）`.
Unchanged tests and R1/H04 disposition accepted. Next requested approval:
Phase2 Green/implementation (phase and implementation); implementation allowed:no
until that separate approval. Approved scope remains H01–H09 only. Post-review
required:yes, fresh focused/consumer/adjacent/all-blocking verification followed
by separately approved Phase3/final/delivery gates. No commit authority inferred.
The pending wording below records the earlier agent-review boundary.

Agent test review passed on unchanged test bytes2026-10-09. No blocking test
finding. Human test acceptance, including H04's explicitly unreachable
name-only-error disposition, remains separate and pending. Phase2 implementation
permission:no. No commit/push/delivery authorization.

- User selected Phase1 Red test review / acceptance; reviewer execution performed.
- Approved scope: accepted H01–H09 tests and bounded test-only guard integration.
- Next requested approval type: Phase1 test acceptance, unchanged tests plus H04
  disposition; subsequent Green/implementation requires another explicit approval.
- Post-review required:yes. Execution batch:none.
- Isolation:same_context, weaker than separate_context; no optional model ID set.
  Reviewer re-read disk artifacts and reran verification; authorship reasoning
  was not treated as evidence.

## Sources re-read and reconciliation

- [Accepted specification](../../specs/evaluator-host-coefficient-resolution-successor.md).
- [Execution / complete H01–H09 node matrix and hashes](2026-10-09-liss-0586-phase1-execution.md).
- Three0586suites,0586projection, original42-line fixture, shared0583projection,
  bounded0583/0585fixture-copy diffs, readonly0584guard.
- Current evaluator resolver, scientific-input provenance/name checks,
  implementation-readiness and review/routing/verification policies.
- Applicable lessons: shape invariance, bounded guard lifecycle, clause
  reconciliation, exact hook identity, state ownership, compatibility baseline.
  Applied by exact projections, real fixture probes and unchanged frozen
  artifacts. AST-walker/provider semantic redesign excluded with reason: no
  such production behavior is changed in this phase.

H01–H07 cover the observable early return/read ordering/cache/dtype/error/
provenance/merger/live-execution contracts. H08 names the required structural
ownership/identity gaps and exercises a cold actual consumer. H09 covers exact
positive/negative shapes and retained protections, not generic method ignores.
The execution node matrix remains applicable unchanged; all listed subcases
reconciled, with the H04 disposition explicitly recorded below.

## Findings and dispositions

| Finding / failure scenario examined | Disposition and evidence |
|---|---|
| R1 — blank key could be mistaken for a reachable CoefficientTensor NAME_ERROR | Already explained with source evidence: InputProvenance rejects input_id while evaluating the constructor argument, before the tensor constructor executes. The real blank-key test asserts provenance error and cause. Recommend accepting the unreachable name-only subcase; human disposition pending, no semantic/assertion change |
| R2 — dedented source could restore a different historical AST literal | Closed with independent Git comparison: reviewer probe reads the original method from a661fb17 and compares full AST with restored immutable fixture. Equality true, including restored multiline docstring. Original fixture hash unchanged |
| R3 — two pre/post labels could copy the same checkout shape | Closed: assertions distinguish method/setup/file presence before real copies in the4Host×Tensor cases. Independent future-root probe also calls old0585's actual test setup for both `unextracted` and `tensor-extracted`, and old0583's retained-body mutation test; all pass |
| R4 — projections could weaken other exports/bodies/state/hooks | Closed for scoped protections: only exact Host import/setup/mapping is removed, old method restored at its position, old Tensor/foreach projections and assertions remain. Mutations reject wrong/duplicate wiring, old duplicate body, algorithm/context/error/import/export changes, missing successor and all five frozen byte paths |

No finding was waived because the reviewer authored the tests. Tests and fixture
bytes were not edited during review. Projections do not themselves prove an
installed implementation exists: separate blocking ownership/runtime identity
tests do, and intentionally remain Red. Real runtime acceptance is still
subject to later Green and final all-blocking checks.

## Fresh deterministic results

Tested HEAD:a661fb1778e97eda3d35fd1615fd8928c031f062 plus uncommitted test/docs
changes, dedicated branch `codex/liss-0586-host-coefficient-phase0`.
Cwd `/Users/nn0cl/Documents/git/qpex`; local macOS arm64,
Python `/usr/local/bin/python3.12`3.12.6 / pytest9.0.3.
Evidence directory `/private/tmp/liss-0586-review.AQUy88`.

| Scope | Fresh result | Exit / log |
|---|---|---|
| New focused3suites |56passed /4expected structural Red,3.39s |1 /focused.log |
| Inherited guards + existing consumer/adjacent11suites |94passed,7.88s |0 /regression.log |
| Independent full original Git AST and actual future-root inherited setups |AST equal; both Tensor setups and foreach old-body mutation passed |0 /probe.log, probe.py |

Commands are the exact focused and regression suite lists in the execution
packet, using Python3.12 pytest; regression combines its3inherited+8consumer
lists. Probe is reviewer-only, external to the worktree, and touches only its
temporary synthetic root. Logs captured pipefail+tee. No collection errors,
skips or exclusions. Exact start/end timestamps not captured: these are scoped
Phase1 review evidence, not final verification-policy completion evidence.
Compared to the author execution, same56pass/4node failure IDs and same94
regression passes. No resolved/new failure IDs in this compared selection;
whole-root failures unassessed. All four failures are only ownership-suite
nodes listed in focused.log, not fixture/setup failures or independent defects.

Production/baseline/old immutable fixtures unchanged: `git diff --exit-code`
exit0. SHA256 of all four new test/helper artifacts matches execution packet.
Original assertions remain; no broad ignore/xfail/lifecycle change. ActiveRed0.
Root/spec/all applicable sanity not_run in this test review; no full Green.

## Routing / structure / remaining limits

`review-change.py --root . --base a661fb17 --head HEAD` reports dirty tree
unknown because committed diff has0files/lines; those zeros do not measure this
uncommitted review. No enabled large_change settings or numeric source_structure
settings exist, so effective configured review remains same_context, status
normal. Unknown dynamic consumers/graph/cycles are gaps, not zero estimates.

Actual new physical sizes: behavior234, ownership52, migration216, helper128,
fixture42. Cohesive tests separated by behavior, ownership and transition; no
production bridge generated. Existing production owner sizes and qualitative
guardrails remain in accepted spec; no numerical budget exception inferred.
Full public-export compatibility is supported by unchanged AST import guards,
but cold smoke samples actual consumer imports rather than claiming exhaustive
external coverage. Require actual successor syntax/import/cycle audit, consumer
smoke, adjacent and all-blocking suites after the final implementation commit.

## Handoff / next gate

Changed this review: this packet, Issue/spec/WP/trace status synchronization and
process-lessons-log application note only. No test/source edits or commit.
Included direct contract/tests/evidence; omitted Rust/rank6/providers/secrets.
Human approval is separate from same-context pass and automated results.
Next: explicitly accept unchanged Phase1 tests and the R1/H04 unreachable
disposition, then separately authorize Phase2 Green/implementation. Until then
do not implement. Resume via representative trace and execution hashes.
