# LISS-0587 Phase1 Red review

## Review target and authority

- Result:agent review passed for Phase1 Red; human test acceptance approved2026-10-12.
- Scope:accepted P01–P09 test inventory and bounded guard transition only.
- Current phase:phase-1-red, reviewer role; no production or test edits here.
- Approved:Scope/Phase0, dedicated Issue/spec and guard policy, Phase1 execution.
- Human approval received:`LISS-0587 Phase 1 Red テストレビュー／acceptance承認`,2026-10-12.
- Requested next approval:Phase2 Green/implementation, separately.
- Implementation allowed:no. Post-review human Red acceptance satisfied; later
  Phase2 implementation approval and actual-SHA all-blocking verification separate.
- Execution batch:not applicable.
- Isolation:same_context, weaker than separate_context; host model identifiers
  empty. No independent-context reviewer or model switch claimed.

## Canonical and evidence documents re-read

- [Accepted P01–P09](../../specs/evaluator-partial-filling-successor.md)
- [Issue and clause/node inventory](../../issues/LISS-0587-evaluator-partial-filling-successor.md)
- [Trace/handoff](../traces/2026-10-12-liss-0587-partial-filling.md)
- New partial behavior, ownership and guard-migration tests; exact projection
  helper and immutable source/readonly fixtures; all four existing carrier diffs.
- readiness, runtime-routing TOML/policy, source-code-quality, verification
  policy, same-context procedure and process-lessons; execution result/root log.
- Canonical Register:not a new rule/navigation topic; accepted spec is the
  agreement owner. This review does not change clauses or introduce an ADR.

## Findings and dispositions

| Finding / failure scenario | Disposition / evidence |
| --- | --- |
| R1: fixture/hash can agree with itself while misrepresenting old class/body | Closed:independent probe compares complete original class and static method AST, including docstrings/decorators, with Git b5ad7402, and verifies all22 readonly hashes against Git |
| R2: pre/post labels may exercise the same shape or omit successor from copies | Closed:new tests explicitly construct/assert both shapes; independent probe runs unchanged0583/0584/0585/0586 suites on a true post-partial dependency root,89 passed |
| R3: missing successor, wrong static hook, duplicate body/class/import, changed fields/decorator/module/algorithm or extra state can bypass guard | Closed:new27-case guard suite exercises real repair guard, approved positives and mutation rejection; no old hash/assertion/exclusion changes |
| R4: AST forward shape is not successful runtime import/serialization after extraction | Out of current phase:actual new-owner cold-import/identity test is Red; retained old-class pickle behavior passes. Must pass real moved imports and legacy/new pickle in Green, not a waiver |
| R5: dirty committed-diff metrics and incomplete dynamic graph can be mistaken for zero change | Gap retained:review-change reports dirty-tree unknown; its zero committed diff does not describe this work. No enabled large_change override; normal same_context route confirmed by tool, not downgraded because measurements are missing |
| R6: ownership-suite docstring calls four nodes independent gaps | Nonblocking reporting clarification:four contract nodes but two observed root causes (missing successor and retained old bodies); reviewed packet/Issue explicitly distinguish these. No test assertions changed |

No unresolved acceptance-inventory or guard-safety blocker found for Phase1.
Human Red acceptance is satisfied; separate implementation authority remains the gate to Phase2.

## Specification mapping and existing behavior

- P01–P04:3 order/nonmutation cases, repeated stepwise case,2 exact-fill span
  cases,6 invalid-arity cases; real retained hook, no successor stand-in import.
- P05:seven original suites,16 cases, byte-pinned and rerun. Covers one-hole
  pipe, repeated fills, multi-hole tuple pipe, fusion, Float indexing and move/errors.
- P06:legacy pickle fixture, current roundtrip/dataclass mutability and static
  class/instance invocation; moved-owner identity remains intentionally Red.
- P07:exact class/function AST and restricted imports, absent old class/body,
  two cold import orders. Three nodes currently stop at missing successor,
  not a collection error; successful runtime execution is not yet evidence.
- P08:two unaffected Evaluator AST/import checks and22-file immutable manifest.
  Context/calls/binding/pipes/scientific dependencies and source meaning protected.
- P09:27 real-guard tests, including historical restoration and persistent byte
  mutations. New restoration limited to exact partial class/body/static mapping.
- Four modified existing test carriers:0583 projection;0584 live-successor
  guard;0583 and0585 copy fixtures. Existing assertions and old fixtures retained.
  No new production module, weakened assertion, active-Red exclusion or moved failure.

## Verification, environment and gaps

- Tested HEAD/base:b5ad7402c184a3a79440271e02dd423c53d8bc36, dirty uncommitted
  tests/docs; macOS27.0.1 arm64 / CPython3.12.6 / pytest9.0.3.
- Reviewer focused rerun:44 passed/same4 intended Red,2.43s, exit1.
- Reviewer forward-root probe:89 passed5.81s, exit0; UTC boundaries in probe.log.
- Reviewer inherited/adjacent rerun:159 passed7.34s, exit0,
  in external inherited-adjacent.log. Totals overlap; do not add them.
- All11 reviewed test/helper/fixture hashes unchanged at closeout;
  document/test lifecycle, coverage consistency and diff checks passed.
- Execution whole root:2617 passed/same4 Red341.84s; spec161/161 PASS.
  These logs were reread, not rerun in review. Reviewed test bytes unchanged.
  No clean final-commit/full-Green claim. Root intentionally fails; no exclusions.
- Full same-environment base root comparison unavailable; per-command execution
  UTC boundaries unavailable for old run; spec skip count not independently reported.
- Dynamic/external consumers, full resolved dependency graph and cycles remain
  unproved. Cold-import moved owner remains unassessed until Green.
- Structure:new helper123 lines, behavior107, ownership77, guard tests131;
  existing Evaluator1014 unchanged, retained outside this slice with WP-0174 owner.
  No numeric live structure budgets; qualitative responsibility review applied.
  Dirty/untracked aggregate changed-line/module metrics unknown, not zero.
- Evidence:`/private/tmp/liss-0587-red-review.bByRNw/` contains probe.py/log,
  focused.log, inherited-adjacent.log, routing.json and reviewed-tests.sha256.
  Earlier root/spec evidence:`/private/tmp/liss-0587-red.L9zKc8/`.

## Next gate

Human accepted these exact test/fixture bytes2026-10-12, then separately approved
Phase2 Green/implementation. This packet preserves the Phase1 review boundary;
current implementation/next gate are in the [Phase2 record](2026-10-12-liss-0587-phase2-verification.md).
Acceptance synchronization is documentation only;
no implementation, local commit, push, PR or delivery performed by this review.
