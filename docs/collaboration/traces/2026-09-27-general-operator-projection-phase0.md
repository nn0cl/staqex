# Trace: General Operator projection successor — Phase 0

## Request

- Date: 2026-09-27
- User request: Investigate/design the successor boundary for general Operator
  projection under Architecture Path Phase 0 scope approval.
- Current phase: Phase 2 committed and verified; separate Phase 3 approval is
  the next gate
- Canonical issue or work plan: LISS-0579 / WP-0172
- AI planning record: AIP-0579-001 (proposed)

## Context Ledger

- Included: `evaluator.py` projection method; call dispatcher/context; execution
  and observation context initialization; LISS-0431/0432; LISS-0578 exclusion;
  LISS-0430/0431 tests; architecture, source-quality, routing and process rules;
  applicable process lessons.
- Omitted: unrelated evaluator families, parser/typechecker, QPU/provider
  adapters, external AI, private user/business data.
- Assumptions: Phase 0 scope approval authorizes source/design artifacts only;
  no implementation or tests are authorized.
- Open decisions: accept/revise proposed ownership contract; separately decide
  whether any semantic changes to diagonal projection should be filed outside
  this structural successor.

## Routing

- Model/assistant/tool: host agent plus deterministic repository search/read.
- Reason: Architecture scope and source ownership are local; no external model
  or provider is needed. Review isolation is `same_context`; implementation is
  `host` per live routing, without granting implementation approval.
- Privacy constraints: public repository docs and local source only; no secrets
  or private data included.

## AI Execution Records

### Attempt 1

- Agent: Codex
- Environment: Codex desktop, local checkout
- Model as displayed: N/A
- Reasoning setting as displayed: N/A
- Estimated token range: 8,000–14,000 (planning record; not actual usage)
- Estimated token midpoint: 11,000
- Actual tokens: N/A
- Token metric: N/A
- Token source: N/A
- Token attribution boundary: N/A
- Actual token unavailable reason: host did not expose token accounting
- Estimate variance: N/A
- Variance reason: not measured
- Scope: Phase 0 source/spec/test inventory and proposal artifacts only
- Result: drafted proposed acceptance and ownership boundary; no tests or
  implementation run or changed
- Attempt boundary: initial cohesive Phase 0 investigation
- Notes: dedicated branch created from current `main`; a separate prior local
  documentation branch was preserved untouched.

### Attempt 2 — Phase 1 Red

- Agent: Codex
- Environment: Codex desktop, local checkout
- Model as displayed: N/A
- Reasoning setting as displayed: N/A
- Estimated token range: N/A
- Estimated token midpoint: N/A
- Actual tokens: N/A
- Token metric: N/A
- Token source: N/A
- Token attribution boundary: N/A
- Actual token unavailable reason: host did not expose token accounting
- Estimate variance: N/A
- Variance reason: N/A
- Scope: test-only Phase 1 Red plus active-Red registration
- Result: focused structural suite has five expected failures and two passing
  behavior characterizations; adjacent suites and lifecycle validation pass.
- Attempt boundary: one cohesive Phase 1 run; the first off-diagonal fixture
  failed at the tuple-coordinate precondition, was corrected to the
  Sigma-generated tuple-state form, and rerun before review.
- Notes: no production code or existing assertions were changed.

### Attempt 3 — Phase 2 Green

- Agent: Codex
- Environment: Codex desktop, local checkout
- Model as displayed: N/A
- Reasoning setting as displayed: N/A
- Estimated token range: N/A
- Estimated token midpoint: N/A
- Actual tokens: N/A
- Token metric: N/A
- Token source: N/A
- Token attribution boundary: N/A
- Actual token unavailable reason: host did not expose token accounting
- Estimate variance: N/A
- Variance reason: N/A
- Scope: minimum successor implementation and compatibility wiring; reviewed
  tests unchanged
- Result: focused/adjacent 27 passed; root 2,267 passed; spec verification
  161/161 passed on the then-current suite. Later spec reconciliation found
  required characterization gaps, so these results do not establish accepted
  Phase 2 Green.
- Attempt boundary: one cohesive Green execution; import syntax was corrected
  after an initial collection failure, then focused and full suites reran.
- Notes: full root suite ran 318.90s on Python 3.14.6/pytest 9.1.1. Template
  copy smoke is pending a committed tree because the distributor rejects
  uncommitted specs.

### Attempt 4 — Phase 1 Red contract correction

- Agent: Codex; routing: host implementation and same-context review per live
  routing; separate-context review was not configured.
- Environment: Codex desktop, local checkout; Python 3.14.6, pytest 9.1.1,
  macOS arm64.
- Scope: tests only for unknown Operator, empty output, copied phase maps,
  coalescing, and cache reuse. Existing assertions and production files remain
  unchanged.
- Result: focused LISS-0579 suite **11 passed**; combined with LISS-0431,
  LISS-0430, and LISS-0566-C **31 passed**; lifecycle has zero active-Red
  entries; py_compile and `git diff --check` passed.
- Tested HEAD: `d3b3225109cfe5471d8811854baf6d92d5ca6a8e`; dirty worktree with
  earlier Phase 2 implementation and this correction present. This is focused
  correction evidence, not fresh all-blocking Phase 2 evidence.
- Review disposition: same-context test review found no blocker; weaker than
  separate-context review. The Adjudicator approved the corrected suite on
  2026-09-27; this approved suite was used in the following Phase 2 rerun.

### Attempt 5 — Phase 2 verification after corrected test review

- Approval: corrected Phase 1 suite accepted by the Adjudicator on 2026-09-27;
  earlier Phase 2 implementation approval remains the implementation authority.
- Tested implementation commit/tree:
  `98026263419b86982e8c9e28dc0675b01a9ee465`, clean tree before the final
  evidence-documentation commit.
- Environment: macOS arm64; Python 3.14.6; pytest 9.1.1; `.venv`.
- Focused and adjacent: LISS-0579 + LISS-0431 + LISS-0430 + LISS-0566-C,
  **31 passed**.
- Root suite: `./.venv/bin/python -m pytest tests/ -q`, **2,271 passed** in
  320.17s. Compared with the prior 2,267 pass run, the four new approved tests
  account for the increase; no failures or collection errors were reported.
- Other checks: specification verification **161/161**; document lifecycle,
  coverage-ledger, active-Red lifecycle (0 entries), execution-batch (20),
  shell syntax, baseline comparison, `py_compile`, and `git diff --check` pass.
- Repository CI checks including template-copy smoke passed on the implementation
  commit. A subsequent documentation-only commit records this outcome; its
  final blocking verification is reported in the handoff.

## Cost / Reasoning Control

- Operating path: Architecture Path / Phase 0
- Files read: design/process skills, runtime-routing and architecture policies,
  LISS-0431/0432/0578, WP-0171, projection source/context/call/setup, Joint,
  focused tests and process lesson log.
- Context intentionally omitted: unrelated runtime source families and all
  external provider documentation.
- Deterministic checks used: `rg` inventories, source read, git status/branch
  inspection; no test execution.
- Escalation reason: none
- Avoided LLM work: no external agent/model launched.
- Rework caused by AI output: none known.

## Adjudicator Decisions

- Scope approval: Architecture Path / Phase 0 investigation, 2026-09-27.
- Architecture Path / Phase 0 acceptance: `承認`, 2026-09-27, for the drafted
  state-ownership boundary and behavior-preservation acceptance specification.
- Phase 1 Red approval: `LISS-0579 Phase 1 Red 承認`, 2026-09-27.
- Phase 1 test review: `LISS-0579 Phase 1 Red テストレビュー承認`, 2026-09-27;
  accepted five intended structural failures and two passing runtime cases.
- Phase 2 Green/Implementation: `LISS-0579 Phase 2 Green / Implementation
  承認`, 2026-09-27.
- Phase 1 Red contract correction: `LISS-0579 Phase 1 Red contract correction
  承認`, 2026-09-27; test-only scope.
- Corrected test review: `LISS-0579 Phase 1 Red contract correction
  テストレビュー承認`, 2026-09-27.
- Phase 1 Red contract correction test review: `LISS-0579 Phase 1 Red contract
  correction テストレビュー承認`, 2026-09-27.
- Phase 3 Refactor: not granted.

## Verification

- Commands/checks: source and test consumer searches; manual source/spec
  comparison; `git status` and branch base confirmation.
- Result: Phase 0 static inventory completed. Phase 1 focused suite reports
  5 failed / 2 passed on the expected structural gaps; LISS-0431 reports 4
  passed; LISS-0430 reports 5 passed; active-Red lifecycle passes.
- Tested SHA/tree: `d3b3225109cfe5471d8811854baf6d92d5ca6a8e`, dirty tree.
- Environment: macOS local checkout; Python 3.14.6, pytest 9.1.1, `.venv`.
- Commands: `./.venv/bin/python -m pytest -q
  tests/test_liss_0579_operator_projection_red.py`; corresponding commands for
  LISS-0431 and LISS-0430; `./.venv/bin/python
  scripts/check-test-lifecycle.py --as-of 2026-09-27`.
- Exit/results: new suite exit 1, 5 failed / 2 passed; LISS-0431 exit 0,
  4 passed; LISS-0430 exit 0, 5 passed; lifecycle exit 0, one active entry.
- Phase 2 tested SHA/tree: `d3b3225109cfe5471d8811854baf6d92d5ca6a8e`, dirty
  worktree.
- Phase 2 commands: combined focused suite over LISS-0579, LISS-0431,
  LISS-0430, and LISS-0566-C; `./.venv/bin/python -m pytest tests/ -q`;
  `./.venv/bin/python tests/spec_verification/run_all.py`; document lifecycle,
  coverage ledger, execution-batch, active-Red lifecycle, shell syntax, and
  refactor-baseline capture+cmp commands.
- Phase 2 results: focused/adjacent 27 passed; root 2,267 passed in 318.90s;
  spec 161/161; document/coverage/execution-batch/active-Red checks passed;
  shell syntax and refactor-baseline cmp passed. Pre-commit template-copy
  smoke was blocked by its expected refusal to distribute an uncommitted spec.

## Changed Files

- `docs/issues/LISS-0579-general-operator-projection-successor.md`
- `docs/specs/evaluator-general-operator-projection.md`
- `docs/work-plans/WP-0172-general-operator-projection-successor.md`
- `docs/collaboration/traces/2026-09-27-general-operator-projection-phase0.md`
- `tests/test_liss_0579_operator_projection_red.py`
- `docs/testing/active-red-tests.toml`

## Next Safe Action

- Request separate Phase 3 Refactor approval before starting Phase 3.

## Notes

- The current test named for non-diagonal rejection uses diagonal `Z` terms and
  a scalar basis state, so it currently does not prove the non-diagonal error
  branch. This is recorded as a Phase 1 evidence gap, not fixed in Phase 0.
