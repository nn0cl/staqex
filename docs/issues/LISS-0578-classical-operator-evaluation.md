# LISS-0578: Classical Operator-expression evaluation decomposition

## Metadata

- Local issue ID: LISS-0578
- GitHub issue: none
- Status: in_progress — Phase 3 final review accepted; final commit verification pending
- Phase: phase-3-refactor
- Type: Architecture Path structural decomposition
- Priority: normal
- Initial planning size: M
- Current planning size: M
- Reclassification reason: none
- Owner/agent: Codex
- Related branch: `codex/liss-0578-classical-op-eval`

## Summary

Extract the classical evaluation of Operator-DSL expression ASTs and binders
from `runtime/evaluator.py`, preserving existing results, errors,
short-circuiting, and private consumer behavior. The Phase 2 implementation is
present; repository-wide CI readiness still has a baseline snapshot
disposition pending.

## Acceptance Notes

- The successor owns `_eval_op_expr_classical` and
  `_eval_classical_op_binder` behavior, including their mutual recursion.
- `_eval_set_comprehension` remains a separate binding/runtime operation; its
  conditions continue to use the classical expression evaluator through a
  narrow explicit callback or an equally clear approved boundary.
- `Evaluator` remains the owner of mutable runtime state. Classical scalar,
  operator-array lookup, and assignment lookup are supplied by explicit
  context callbacks; the successor must not import or instantiate Evaluator.
- Preserve `IndexDomain`/`RevDomain` handling, inclusive range semantics,
  guarded and nested binders, empty-domain identities, `ForAll` short circuit,
  operator/Pauli rejection, indexing failures, supported operators, and exact
  user-visible diagnostics.
- Inventory AST dispatch, private test consumers, `binding.py` dispatch,
  `operators.py` set-comprehension lookup, and dynamic compatibility hooks
  before Phase 1 Red. Do not infer that `rg`-visible runtime calls are the
  complete consumer set.
- No new DTO, port, provider, QPU behavior, parser/typechecker change, or
  Semantic IR authority is introduced.
- Target successor structure budget: below 400 physical lines, subject to the
  repository source-code-quality policy and measured implementation bodies.

## Dependencies

- Parent: WP-0171
- Depends on: WP-0170 / LISS-0577 (done on the parent successor branch)
- Blocks: none
- Related: WP-0167, WP-0168, LISS-0577

## Adjudicator Decision Points

- Phase 1 Red approval recorded: `WP-0171 / LISS-0578 Phase 1 Red 承認`
  (2026-09-24). Only the issue-owned structural test and active-Red metadata
  are authorized; production implementation is not.
- Phase 1 Red test review is required before Phase 2.
- Phase 1 Red test review accepted by the Adjudicator on 2026-09-24 as
  `WP-0171 / LISS-0578 Phase 1 Red テストレビュー承認`. This accepts only the
  corrected failing-test contract; it does not authorize production changes.
- Test review on 2026-09-24 was not accepted. Review Summary:
  `docs/collaboration/reviews/2026-09-24-liss-0578-phase1-red-review.md`.
  Correct the weak compatibility assertion, complete the `classical.py`
  consumer inventory, and include Operator-resolution characterization before
  resubmitting for review. The Adjudicator approved this bounded correction
  on 2026-09-24; the corrected suite now checks exact installer AST mappings,
  installer invocation, and live hook identity, and the named consumer
  characterization includes LISS-0430. The correction review packet is
  `docs/collaboration/reviews/2026-09-24-liss-0578-phase1-red-correction-review.md`.
- Phase 2 Green/Implementation approval was granted on 2026-09-24 as
  `WP-0171 / LISS-0578 Phase 2 Green / Implementation 承認`. The successor
  module and compatibility hooks are implemented; 2,260 root tests and
  161/161 spec checks pass. The Adjudicator separately approved the
  verification-baseline snapshot update scope on 2026-09-24. The generated
  `docs/testing/refactor-baseline.json` now includes the already-public
  `MutableMapping` symbol and byte-compares with a fresh capture. Phase 3
  Refactor approval was granted on 2026-09-24 as
  `WP-0171 / LISS-0578 Phase 3 Refactor 承認`. The successor was reviewed and
  retained without extra abstraction; the same-context review packet is
  `docs/collaboration/reviews/2026-09-24-liss-0578-phase3-review.md`. All
  2,260 root tests, 31 focused tests, and 161 spec checks pass on this dirty
  worktree. Final-commit verification and GitHub CI remain pending.
- Adjudicator accepted the Phase 3 final review on 2026-09-24 as
  `WP-0171 / LISS-0578 Phase 3 最終レビュー 承認`. This records human acceptance
  of the review result; it does not claim a final commit, GitHub CI, or
  post-commit blocking-suite run. Issue closure and process review remain
  pending those completion steps.
- Operator projection is excluded from this issue. Its distinct `Joint`
  transformation, Hamiltonian compilation, and `calls.py` context boundary
  warrant a separate successor investigation and separate scope approval.

## Context

- Included: classical Operator AST evaluation and binder folding; set
  comprehension as a consumer; Evaluator context callbacks; compatibility and
  private consumer inventory.
- Omitted: `_project_onto_operator` implementation, generic Operator lowering,
  parser/typechecker, other evaluator families, QPU/provider delivery.
- Assumptions: the approved 2026-09-24 source baseline is the starting point;
  observed private hooks may have consumers outside direct runtime calls.

## AI Planning Records

### AIP-0578-001

- Status: accepted
- Created by:
  - Agent/environment: Codex desktop, isolated local worktree
  - Model as displayed: N/A
  - Reasoning setting as displayed: N/A
  - N/A reason: not displayed by the host
- Created at: 2026-09-24
- Planning size: M
- Intended execution route: host implementation; same-context review if a
  review packet is required, per live routing
- Intended scope: one classical Operator-expression evaluation successor,
  characterization/structure tests, and consumer compatibility
- Estimated token range: 8,000–15,000
- Estimated token midpoint: 11,500
- Token metric: planning/execution context tokens, estimate only
- Estimation basis: two mutually recursive functions, compatibility wiring,
  characterization and structural tests, plus focused and blocking
  verification; no unrelated module rewrite
- Assumptions: existing test fixtures can characterize the accepted behavior;
  no new architecture or technology decision is needed
- Confidence: medium
- Revises: none
- Revision reason: none
- Superseded by: none

## References

- `docs/specs/staqex-core-module-decomposition.md`
- `compiler/staqex/runtime/evaluator.py`
- `compiler/staqex/runtime/evaluation/binding.py`
- `compiler/staqex/runtime/evaluation/operators.py`
- `compiler/staqex/runtime/evaluation/context.py`
- `compiler/staqex/runtime/evaluation/compatibility.py`

## Work Notes

- Phase 0 design and consumer boundary were accepted by the Adjudicator on
  2026-09-24. Phase 1 Red was separately approved on 2026-09-24; see the
  representative trace dated 2026-09-24.
- Projection is explicitly a separate candidate, not part of LISS-0578.
- Applicable process lessons: `private-consumer-inventory` and
  `decomposition-callback-boundary` require direct, dynamic-hook, and
  underscore-prefixed consumer checks; `evaluator-state-ownership` keeps
  mutable maps in Evaluator; `decomposition-source-ownership` requires
  successor ownership and duplicate-body absence checks; `refactor-branch-preservation`
  requires exact declared-suite verification on the final branch.

## Verification

- Phase 0 used read-only static source and consumer inspection.
- Phase 1 correction expanded the structural suite to five contracts: four
  intended structural Red failures and one passing installer-invocation
  assertion. Existing LISS-0424/0427/0428/0429/0430 suites are retained as
  positive behavior characterization and run separately. The corrected
  Phase 1 Red review was accepted by the Adjudicator on 2026-09-24.
- Phase 2 moved both evaluator algorithms to the successor module, installed
  both hooks through the accepted compatibility installer, and removed the
  duplicate bodies from Evaluator. Full root pytest passed (2,260 tests), and
  spec verification passed 161/161 when run from a writable temporary cwd.
  Following separate scope approval, the refactor-baseline snapshot was
  synchronized and a fresh capture byte-compared successfully. The full root
  suite was run before this snapshot-only change; it was not repeated because
  no source or test behavior changed. GitHub-hosted CI and final-commit
  verification remain unassessed. See the verification record in the trace.
- Phase 3 review confirmed successor ownership, compatibility-hook identity,
  live Evaluator state ownership, and named runtime consumers. No code or
  assertion changes were warranted. `classical_operator_eval.py` is 147 lines
  and `evaluator.py` is 1,477 lines. Aggregate automatic change measurement
  reports unknown because the tree is dirty and contains untracked artifacts;
  the same-context review packet records this limitation. Final Adjudicator
  review remains required.

## Process Review

- Outcome: not yet
- Lesson written: not applicable
- Template-feedback path: none
