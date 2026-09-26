# LISS-0579: General Operator projection successor boundary

## Metadata

- Local issue ID: LISS-0579
- GitHub issue: none
- Status: ready
- Phase: phase-3-refactor
- Type: Architecture Path structural decomposition
- Priority: normal
- Initial planning size: M
- Current planning size: M
- Reclassification reason: none
- Owner/agent: Codex
- Related branch: `codex/liss-0579-operator-projection-successor`

## Summary

Investigate and specify a behavior-preserving successor boundary for
`Evaluator._project_onto_operator`, which compiles a named Operator and
transforms a `Joint` for the `project ψ onto P` call path. This Phase 0 design
does not authorize semantic changes; implementation remains separately gated.

## Design Note

- Target behavior: Preserve the current general-Operator projection behavior
  and diagnostics while moving the cohesive compile/eligibility/Joint
  transformation responsibility out of the oversized Evaluator facade.
- Requested phase: Phase 2 Green/Implementation verification after accepted
  Phase 1 correction.
- Proposed next phase: complete commit-level blocking verification, then seek
  separate Phase 3 Refactor approval.
- Adjudicator decision needed: Phase 3 approval remains separate and is not
  requested until commit-level verification is complete.
  Any semantic expansion remains a separate issue/spec and decision.
- Requested approval type: Phase 2 verification. Existing Phase 2
  implementation approval and corrected Phase 1 test-review approval do not
  authorize Phase 3.
- Approved scope: `Architecture Path / Phase 0 scope approval / general
  Operator projection successor investigation` (2026-09-27).
- Implementation allowed: missing tests only after explicit correction
  approval; no production changes in that correction. Phase 2 permission was
  received 2026-09-27.
- Post-review required: yes, after Phase 3 and before closing the Issue.

## Scope and Candidate Boundary

Candidate responsibility is the current 74-line
`Evaluator._project_onto_operator` body in `compiler/staqex/runtime/evaluator.py`.
It reads an Operator by name, memoizes its compiled Hamiltonian matrix,
rejects off-diagonal matrices, maps tuple coordinates to big-endian indices,
scales amplitudes, builds `World` values, coalesces them, and returns a
`Joint`. Its only runtime call is `evaluation/calls.py`; its private callback
is declared in `evaluation/context.py`.

Accepted successor boundary: a narrowly named module-local operation in
`runtime/evaluation/operator_projection.py`, with Evaluator remaining the sole
owner of `operators` and `_compiled_operator_cache`. The facade compatibility
hook remains installed through `evaluation/compatibility.py` only if consumer
inventory confirms a retained private entrypoint is needed. This is the
accepted Phase 0 architecture; implementation details remain bounded by the
acceptance contract below.

Candidate dependencies are `hamiltonian.compile_hamiltonian`, `Joint`,
`World`, `_coalesce`, `EPS`, the live operator mapping, and the evaluator-owned
compiled-matrix cache. No external port/adapter, parser/typechecker change,
QPU/provider behavior, new DTO, or new semantic authority is proposed.

## Accepted Phase 0 Boundary and Acceptance Notes

### Behavior-preservation contract

1. A source `project ψ onto P` with `P` resolving to an Operator continues to
   use the existing operator environment and tuple-valued coordinate path.
2. Operator compilation remains keyed by `(operator_name, tuple_width)` and
   cached for the lifetime currently established by execution context setup;
   the implementation must not move, widen, or extend cache lifetime without
   a separate decision.
3. A matrix with an off-diagonal entry above `EPS` is rejected using the
   established user-facing diagnostic. The accepted scope remains
   diagonal-only.
4. Each tuple-valued world's basis index uses the existing big-endian
   convention. The output amplitude is the input amplitude multiplied by the
   complex square root of the real diagonal entry, with the existing `EPS`
   pruning behavior; this operation does not renormalize.
5. Worlds lacking a tuple-valued target coordinate are skipped as today;
   empty output returns `Joint.empty()`. Retained worlds copy assignment and
   coordinate-phase mappings, and output worlds are coalesced as today.
6. Unknown Operator and absence of any tuple-valued source coordinate retain
   their established diagnostics. No incidental exception or error boundary is
   intentionally changed in this structural successor.
7. Basis-label projection, `feasible(...)`, normalization, Hamiltonian
   evolution, and other Operator lowering behavior remain outside this scope.

### Explicit non-goals and semantic traps

- Do not call all diagonal Operators projectors or add idempotence,
  Hermiticity, nonnegative-spectrum, or 0/1-eigenvalue validation. Current
  code only checks diagonality and applies its existing numeric transform.
- Do not add non-diagonal/Lüders projection, partial trace, density-matrix
  support, renormalization, or a new public syntax/API.
- The existing LISS-0431 test named
  `test_project_onto_general_operator_rejects_non_diagonal` is not a valid
  positive proof of the off-diagonal rejection branch: its `H` is diagonal,
  and its scalar `|0>` coordinate fails the tuple-coordinate precondition.
  Phase 1 must repair the evidence with an actually non-diagonal Operator and
  a tuple-valued target coordinate while retaining independent tuple-shape
  rejection coverage.

## Consumer and State Inventory

- `evaluation/calls.py::bind_call`: sole in-tree runtime invocation found; it
  dispatches Operator variables to `context._project_onto_operator`.
- `evaluation/context.py::EvaluatorContext`: declares the private callback.
- `evaluation/compatibility.py`: dynamically installs extracted successor
  hooks for other families; no projection hook currently exists. Phase 1 must
  inspect full installer AST/setup and actual runtime identity if a new hook is
  introduced.
- `evaluation/execution.py::_prepare_execution_context`: initializes the
  Operator environment and `_compiled_operator_cache`; `GridHamiltonianRef`
  aliases may be present in that map and should be explicitly rejected or
  otherwise handled only if existing execution proves relevant.
- `evaluation/observation.py::_prepare_first_family_context`: separately
  initializes/reset these maps for State/Measure execution. Preserve this
  lifecycle; do not consolidate state setup as incidental scope.
- Tests: direct semantic characterization is in
  `tests/test_liss_0431_project_no_implicit_renorm_red.py`; adjacent operator
  construction/semantics include LISS-0430 and LISS-0566 Unit C tests.
  Static search found no Python test importing `_project_onto_operator`
  directly. Phase 1 must still inventory dynamic/private consumers, direct
  imports, active-Red declarations, and test discovery.

## Applicable Process Lessons

- `evaluator-state-ownership`: apply; retain operator maps and cache ownership
  in Evaluator and pass narrow explicit state access, never a second store.
- `decomposition-callback-boundary`: apply; inventory callback and hidden
  consumers before selecting whether the private facade hook remains.
- `private-consumer-inventory`: apply; search underscore imports, runtime
  identity checks, compatibility installers, and tests before body removal.
- `decomposition-source-ownership`: apply in Phase 1/2; require successor
  algorithm ownership and actual removal of the Evaluator body, not just a
  forwarding facade test.
- `red-contract-scope`: apply; separate structural Red failures from existing
  positive characterization, and correct the invalid non-diagonal fixture
  without weakening its independent coordinate-shape contract.
- `refactor-branch-preservation`: apply in Phase 3; inspect the complete
  transformed method/control flow and run named spec/consumer suites on the
  final commit.
- `status-drift`: apply at each gate; synchronize this spec, issue, plan, and
  trace together when statuses change.
- `compatibility-hook-identity-contract`: apply if any dynamic compatibility
  hook is added; assert exact installer mapping, setup invocation, and runtime
  callable identity.

## Open Decisions / Ambiguity Boundaries

1. Exact successor function inputs: whole context, narrow Protocol, or explicit
   operator/cache mappings. Recommendation is a narrow explicit contract that
   leaves the mutable maps owned by Evaluator; implementation-readiness review
   must confirm the least broad form against consumers.
2. Whether the compatibility callback should remain on `EvaluatorContext` or
   be replaced by a direct successor import at the call dispatcher. Keep the
   established callback unless inventory demonstrates it can safely retire;
   do not widen the shared protocol speculatively.
3. Cache invalidation and operator rebinding are not independently specified
   here. LISS-0432 says the operator environment does not rebind mid-run; prove
   that invariant for the affected execution lane before relying on it. Do not
   change cache key/lifetime in this work.
4. Current numerical edge behavior for negative/complex diagonal values,
   malformed tuple widths/bits, and dimension mismatch is not a new semantic
   design target. Preserve observed behavior in the decomposition; route any
   discovered unsafe or surprising behavior to a separate issue for a typed
   decision.
5. Routing file has no `[source_structure]` section. Module size thresholds
   and resolved dependency/cycle measurements are therefore not available as
   configured evidence. Do not claim quantitative budget compliance; the
   later review must measure the successor and its full implementation body,
   record the gap, and propose a disposition under source-code-quality.

## Phase 1 Evidence Plan

- Structural contracts: successor owns the transformation; the facade body is
  absent; state remains evaluator-owned; call dispatch and any compatibility
  wiring resolve to the intended successor.
- Positive behavior: current hand-computed unnormalized LISS-0430/0431 path,
  multiple tuple widths/cache reuse if reachable in one evaluator, amplitude
  and coordinate-phase preservation, coalescing, empty-result behavior.
- Negative behavior: genuinely off-diagonal Operator with tuple coordinate;
  missing/unknown Operator; no tuple coordinate; malformed dimension/shape
  cases only to characterize established behavior (not to invent new errors).
- Named consumers: LISS-0430 projector-sum construction, LISS-0431 projection
  and explicit norm division, call dispatcher, compatibility identity if
  introduced, and adjacent Operator regressions.
- No tests have been run or added in Phase 0.

## Phase 1 Red Record

- Approval: `LISS-0579 Phase 1 Red 承認` received 2026-09-27. Scope is tests
  and active-Red registration only; production code remains unchanged.
- Added `tests/test_liss_0579_operator_projection_red.py` with five structural
  ownership/hook contracts and two runtime characterizations.
- Focused result after fixture correction: **5 failed, 2 passed**. The five
  intended failures are successor ownership, facade-body retirement,
  compatibility mapping, installer invocation, and live hook identity. Both
  behavior cases passed: genuine non-diagonal rejection and independent scalar
  coordinate rejection.
- The first run exposed an invalid fixture (`|00>` followed a non-tuple
  runtime path); replaced it with the established `Sigma`-generated tuple
  state, without weakening the intended non-diagonal assertion. The rerun
  reached and confirmed the specified diagonal-only diagnostic.
- Existing characterization: LISS-0431 **4 passed**; adjacent LISS-0430
  **5 passed**. `scripts/check-test-lifecycle.py --as-of 2026-09-27` passed with
  one active-Red entry.
- No production source was changed. Focused and adjacent suites are local
  evidence only; all-blocking suites were not run in Phase 1.
- Test review: `LISS-0579 Phase 1 Red テストレビュー承認` received
  2026-09-27. The five intended structural failures and two runtime
  characterization nodes are accepted; no test correction was requested.
- Subsequent spec reconciliation found five required details not explicitly
  asserted: unknown Operator, empty output, copied phase metadata, coalescing,
  and cache reuse. The Adjudicator approved a bounded Phase 1 test-only
  correction on 2026-09-27; prior assertions and production code remain
  unchanged.
- Added four focused tests covering those five details (phase-copy and
  coalescing share one test). Same-context review found no blocking issue;
  `LISS-0579 Phase 1 Red contract correction テストレビュー承認` was received
  2026-09-27. Because Phase 2 implementation is present in the dirty worktree,
  this correction run is not claimed as a fresh structural Red.
- Correction review is accepted; Phase 2 verification against the corrected
  suite is recorded below.

## Phase 2 Green Record

- Approval: `LISS-0579 Phase 2 Green / Implementation 承認` received
  2026-09-27. Existing reviewed tests were not edited.
- Moved the projection algorithm into
  `runtime/evaluation/operator_projection.py`, using a narrow Protocol for the
  evaluator-owned Operator environment and matrix cache. The Evaluator remains
  the sole owner of both maps.
- Added `install_operator_projection_compatibility` to install the exact
  successor function under the existing private callback; evaluator setup
  invokes it. Removed the old method body from the facade.
- Preserved matrix cache key/lifetime, diagonal-only check and diagnostic,
  big-endian indexing, EPS pruning, unnormalized amplitude scaling, copied
  world maps, and coalescing.
- Focused consumer/adjacent result: LISS-0579 + LISS-0431 + LISS-0430 +
  LISS-0566 Unit C: **27 passed**.
- All root tests: **2,267 passed**. Spec verification: **161/161**.
- Repository checks passed: active-Red lifecycle (0 entries), document
  lifecycle, coverage-ledger consistency, 20 execution-batch records, shell
  syntax, refactor baseline byte comparison, and conflict-marker search.
- Template-copy smoke was attempted before commit and correctly refused to
  distribute the uncommitted accepted spec; it must be rerun from the committed
  tree.
- Structure: new successor is 93 lines; `evaluator.py` decreased from 1,477
  to 1,404 lines. No `[source_structure]` budget is configured, so this is a
  measurement, not a configured-budget compliance claim.
- Phase 2 worktree verification ran on `d3b3225109cfe5471d8811854baf6d92d5ca6a8e`
  with uncommitted changes. One initial collection attempt exposed an invalid
  multi-line import alias (177 collection errors); the syntax was corrected,
  py_compile and focused suites passed, and the full root suite was rerun to
  completion.
- Acceptance note: later reconciliation against the specification found
  missing explicit characterization for unknown Operator, empty output, copied
  phase metadata, coalescing, and cache reuse. The passing results above do not
  close Phase 2 until the contract correction is reviewed and verification is
  rerun.
- After corrected test-review approval, Phase 2 was committed as
  `98026263419b86982e8c9e28dc0675b01a9ee465`. On that clean commit, focused and
  adjacent suites passed (**31 passed**), root pytest passed (**2,271 passed**),
  spec verification passed **161/161**, and repository checks including the
  template-copy smoke passed. This is Phase 2 evidence only; Phase 3 remains
  separately gated.

## Verification and Routing

- Phase 0: read-only source/spec/test inventory; no test execution.
- Phase 1 after approval: focused structural suite separately reported from
  passing characterization and adjacent consumer suites.
- Phase 2 after reviewed Red and implementation approval: focused consumer
  smoke, adjacent Operator regression, full blocking suites and specification
  verification, with tested SHA/environment; rerun all blocking suites after
  the final commit.
- Phase 3 after approval: verify actual successor ownership and structure
  budget disposition, same-context review per runtime routing, consumer smoke,
  adjacent regression, and blocking suites on final SHA.
- Review isolation: `same_context`; implementation isolation: `host`; models
  are unspecified and capability-class routing applies.
- AI planning record: AIP-0579-001 (proposed; Architecture Path, M).

## Dependencies

- Parent: WP-0172
- Depends on: WP-0171 / LISS-0578 (merged in PR #600)
- Blocks: none
- Related: LISS-0430, LISS-0431, LISS-0432, LISS-0566 Unit C, LISS-0578

## References

- `docs/specs/evaluator-classical-operator-evaluation.md`
- `docs/specs/staqex-core-module-decomposition.md`
- `docs/issues/LISS-0431-project-explicit-renorm.md`
- `docs/issues/LISS-0432-retire-feasible-and-host-bool-arrays.md`
- `compiler/staqex/runtime/evaluator.py`
- `compiler/staqex/runtime/evaluation/calls.py`
- `compiler/staqex/runtime/evaluation/context.py`
- `compiler/staqex/runtime/evaluation/execution.py`
- `compiler/staqex/runtime/evaluation/observation.py`
- `tests/test_liss_0431_project_no_implicit_renorm_red.py`

## Adjudicator Decision Points

- Scope approval received 2026-09-27 for investigation/design only.
- `承認` received 2026-09-27 for the proposed Phase 0 boundary and acceptance
  specification. Architecture/Phase 0 accepted; no implementation permission.
- `LISS-0579 Phase 1 Red 承認` received 2026-09-27.
- `LISS-0579 Phase 1 Red テストレビュー承認` received 2026-09-27.
- `LISS-0579 Phase 2 Green / Implementation 承認` received 2026-09-27.
- `LISS-0579 Phase 1 Red contract correction 承認` received 2026-09-27 for
  tests only.
- `LISS-0579 Phase 1 Red contract correction テストレビュー承認` received
  2026-09-27. Commit `98026263419b86982e8c9e28dc0675b01a9ee465` passed the
  root suite and declared repository checks. Phase 3 is not yet authorized.
