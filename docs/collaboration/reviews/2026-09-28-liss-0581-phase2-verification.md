# LISS-0581 Phase 2 Verification Record

## Scope and status

- Scope: approved LISS-0581 Phase 2 Green/Implementation; pure liveness
  extraction and compatibility wiring only.
- Status: passed on dirty worktree; provisional until final-commit rerun.
- Approval: `WP-0174 / LISS-0581 Phase 2 Green / Implementation 承認`,
  2026-09-28.
- Tested SHA: `83c93a524c7c90710ed965d231ffe85b20dc3163`; source and test
  changes were uncommitted, so this is a dirty-tree result, not a claim about
  that commit alone.
- Baseline SHA: same HEAD. A clean-baseline all-blocking run was not performed;
  comparable baseline failure-ID analysis is unavailable.
- Environment: local macOS host; Python 3.14.6 via `.venv`. Exact OS build and
  dependency lock/runtime inventory were not recorded. No environment secrets
  were captured.
- Execution timestamp: 2026-09-28; precise start/end wall-clock timestamps
  were not retained.

## Results

| Class | Command | Result |
|---|---|---|
| Focused and adjacent | `.venv/bin/pytest -q tests/test_liss_0581_evaluator_coordinate_liveness_red.py tests/test_trace_out_gc_fn_scope_red.py tests/test_bare_block_trace_out_red.py tests/test_evolve_trace_out_gc_red.py tests/test_interprocedural_trace_out_red.py tests/test_liss_0561_evaluator_observation_dynamic_red.py tests/test_liss_0572_frames_constructors_assignments_red.py tests/test_liss_0573_pipes_successor_red.py` | Passed: 41 tests, 0 failures/errors; 0.34s |
| All blocking tests | `.venv/bin/pytest tests/ -q` | Passed: 2,280 tests, 0 failures/errors; 317.29s (5m17s) |
| Spec verification | `python3 tests/spec_verification/run_all.py` | Passed: 161/161 (100%) |
| Document lifecycle | `python3 scripts/check-document-lifecycle.py --root .` | Passed; 1 register |
| Active-Red lifecycle | `python3 scripts/check-test-lifecycle.py --root .` | Passed: `ACTIVE_RED_LIFECYCLE_OK entries=0` |
| Coverage ledger | `python3 scripts/check-coverage-ledger-consistency.py` | Passed |
| CI shell syntax | `bash -n` over the shell scripts declared by repository CI | Passed |
| Refactor baseline | `scripts/capture-refactor-baseline.py` compared with `docs/testing/refactor-baseline.json` | Passed: 3 cases |
| Whitespace/conflict check | `git diff --check` | Passed |

The initial focused collection during implementation found an indentation
error in `frames.py`; it was corrected before the final focused and root runs.
It is not an unresolved test failure. No final-commit rerun has occurred.

## Consumer and compatibility evidence

- The Phase 0 inventory recorded private Evaluator hook consumers across
  `frames.py`, `pipes.py`, `evolution_ops.py`, `execution.py`, and
  `observation.py`, plus source-inspection tests. `context.py`, `execution.py`,
  `pipes.py`, and `evolution_ops.py` were left unchanged.
- The focused/adjacent command exercised the LISS-0581 owner/delegate checks,
  function-call Trace-Out, bare-block and evolve cleanup, interprocedural
  liveness, observation/dynamic, frame, and pipe consumers.
- The new module owns seven pure liveness/AST functions. Evaluator compatibility
  hooks remain, with runtime identity asserted for AST walker hooks. Frames now
  imports the coordinate helpers directly; observation imports the AST walkers.
- Static discovery cannot prove use by out-of-tree or dynamically loaded
  clients. No such loading mechanism was identified in the approved scope.

## Acceptance-to-change-to-test reconciliation

| Acceptance clause | Change | Evidence |
|---|---|---|
| Pure algorithm ownership without Evaluator state | New `runtime/evaluation/liveness.py`; Evaluator retains delegates | LISS-0581 structural and hook-identity tests; full suite |
| Remove duplicate frame coordinate helpers | `frames.py` imports successor helpers | LISS-0581 ownership tests and LISS-0572 frame suite |
| Share AST walkers without moving deferred-observation behavior | `observation.py` aliases the successor walkers; remaining observation algorithms stay put | LISS-0561 observation/dynamic suite and identity checks |
| Preserve function, block, evolve, and interprocedural Trace-Out behavior | Existing algorithms moved/wired without intended semantic changes | Four Trace-Out suites in focused/adjacent command and full suite |
| Do not alter frozen tests or excluded runtime consumers | Reviewed Red test unchanged after review; excluded consumer files unchanged | Worktree review and focused tests |

## Structure and review limitations

- `evaluator.py` is now 1,283 lines (from 1,307 before extraction); its
  reduction is modest because two algorithms were duplicated in `frames.py`
  and the AST walkers were owned in `observation.py`.
- `liveness.py` is 286 lines. Its free-variable walker body is 131 lines and
  was moved intact; it remains a candidate for separately approved Phase 3
  readability work, not a hidden claim of completed simplification.
- The live runtime-routing file has no `[source_structure]` thresholds and no
  `[review.large_change]` section. No numeric structure-budget compliance or
  independent-review availability claim is made. Same-context review routing
  applies if a review packet is required; this record is verification evidence,
  not a substitute for that review or human phase approval.
- Before Phase 3/closure, inspect ownership behind compatibility hooks and
  perform the policy-required review. Human Phase 3 approval remains separate.

## Final disposition

All declared focused, adjacent, all-blocking, and repository checks passed on
the dirty worktree. There are no current Active Red exclusions. Baseline
failure comparison is unavailable because no comparable clean-baseline suite
was run. This establishes working-tree Phase 2 Green, not final completion.
After final commit, rerun every blocking suite against that exact SHA as
required by `docs/collaboration/verification-policy.md`. LISS-0581 remains
active; Phase 3 Refactor approval is the next gate.
