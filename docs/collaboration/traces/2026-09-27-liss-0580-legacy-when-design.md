# AI work trace: LISS-0580 legacy `when` binding design

## Request

- Date: 2026-09-27
- User request: audit old `when` consumers and canonical execution relation;
  propose retain/extract/retire, with file splitting allowed.
- Current phase: final review approved; commit and committed-SHA verification
  pending.
- Canonical issue or work plan: LISS-0580 / WP-0173
- AI planning record: AIP-0580-001

## Context Ledger

- Included: ADR 0213, ADR 0227, LISS-0495, canonical consumer migration
  specification, orchestration, legacy execution, binding dispatcher,
  compatibility wiring, evaluator context, and directly relevant tests.
- Omitted: provider/QPU routes, unrelated evaluator families, and the full
  scientific-semantic implementation not needed to decide this boundary.
- Assumptions: accepted behavior is preserved; the proposed successor is a
  structural extraction only.
- Open decisions: Phase 0 reviewer must accept the exact fallback fixture and
  clause-to-test mapping; helper extraction remains conditional on consumer
  inventory.

## Routing

- Model/assistant/tool: host agent; deterministic `rg`, Git inspection, and
  source review. Model and reasoning setting were not surfaced.
- Reason: bounded cross-module architecture audit and design.
- Privacy constraints: public repository artifacts and local source only; no
  secrets or external/private data included.

## AI Execution Records

### Attempt 1

- Agent: Codex host agent
- Environment: local qpex repository, macOS workspace
- Model as displayed: N/A
- Reasoning setting as displayed: N/A
- Estimated token range: 7,000–12,000
- Estimated token midpoint: 9,500
- Actual tokens: N/A
- Token metric: N/A
- Token source: N/A
- Token attribution boundary: N/A
- Actual token unavailable reason: host does not expose token telemetry
- Estimate variance: N/A
- Variance reason: N/A
- Scope: audit and propose disposition, then record accepted module boundary
  and Phase 0 design artifacts; no tests or production implementation.
- Result: found canonical fallback reaches `_bind_when` when deferred
  eligibility fails; recommended retain-and-extract. ADR 0227 records the
  Adjudicator's architecture approval. Phase 0 acceptance was subsequently
  approved on 2026-09-27.
- Attempt boundary: completed after design artifact review and deterministic
  read-only checks.
- Notes: initial design branch `docs/liss-0580-legacy-when-binding`; test work
  continued on `test/liss-0580-legacy-when-binding-red`.

### Attempt 2

- Agent: Codex host agent
- Environment: local qpex repository, macOS 27.0.0 arm64, Python 3.14.6
- Model as displayed: N/A
- Reasoning setting as displayed: N/A
- Estimated token range: 4,000–8,000
- Estimated token midpoint: 6,000
- Actual tokens: N/A
- Token metric: N/A
- Token source: N/A
- Token attribution boundary: N/A
- Actual token unavailable reason: host does not expose token telemetry
- Estimate variance: N/A
- Variance reason: N/A
- Scope: execute approved Phase 1 Red only; add structural contracts and
  canonical fallback characterization; synchronize phase records.
- Result: focused suite reports three expected structural failures and one
  passing characterization; existing consumer suites pass. The initial test
  fixture incorrectly reused the same state across `Inspect` and `Measure`;
  it was corrected to the established `expect` then `Inspect` pattern and
  rerun successfully.
- Attempt boundary: Phase 1 tests and lifecycle record complete; implementation
  withheld pending separate test review and Phase 2 approval.
- Notes: no production source changed.

### Attempt 3 — Phase 1 Red test review

- Role: same-context reviewer, not implementer.
- Reviewed from disk: accepted LISS-0580 specification, ADR 0227, Phase 1
  test, active-Red manifest, runtime routing, verification policy, and the
  relevant orchestration call sites.
- Finding: the passing host-path characterization observes legacy body and
  binder calls but does not assert that a canonical `control_mixture` plan
  selected its legacy fallback. Other orchestration families can also reach
  the legacy body.
- Disposition: blocking; add a decisive family/fallback assertion and repeat
  review. No implementation performed.
- Verification rerun: focused **3 failed, 1 passed**; adjacent combined **3
  expected failures, 12 passed**; active-Red lifecycle check passed.
- Review summary:
  `docs/collaboration/reviews/2026-09-27-liss-0580-phase1-red-review.md`.
- Isolation: `same_context`, weaker than separate-context review.

### Attempt 4 — Phase 1 Red review correction and re-review

- Correction: the characterization now wraps `execute_control_mixture_plan`,
  asserts the canonical plan family, verifies all in-executor deferred
  eligibility observations are false, and confirms the same executor call
  enters the legacy body. It still verifies `_bind_when` through Host.
- Test fixture iteration: the first observer assumed an instance method;
  runtime inspection showed `_main_deferred_eligible` is a staticmethod. The
  observer was corrected accordingly. A second draft assumed one invocation;
  assertions now express false eligibility rather than depending on incidental
  call count.
- Re-review from disk found no remaining test-contract blocker.
- Verification: focused **3 expected failures, 1 pass**; adjacent combined
  **3 expected failures, 12 passes**; lifecycle, compile, and diff checks
  passed.
- Same-context reviewer disposition: request Adjudicator acceptance; no
  implementation authorization.

### Attempt 5 — Phase 2 Green implementation

- Approval: `LISS-0580 Phase 2 Green / Implementation 承認`, Adjudicator,
  2026-09-27.
- Scope: extract the accepted legacy `when` binding family and its private
  control-mass/pattern helpers behind the existing compatibility hook; no
  semantic changes.
- Consumer inventory: repository-wide Python search found dispatch through
  `evaluation.binding` and the Protocol callback; helper consumers were
  limited to the moved family and reviewed tests. No other private production
  imports or monkeypatch consumers were found.
- Result: implementation is owned by the successor functions; mutable maps
  and enum runtime type remain on the live Evaluator context. Compatibility
  setup installs the exact successor callable as `_bind_when`.
- Verification: focused plus adjacent consumers **15 passed**; all **2,275**
  collected pytest cases passed across an initial 863-pass run, a standalone
  long benchmark test (1 pass), and a continuation run (1,411 pass). Lifecycle,
  compilation, coverage-ledger consistency, and whitespace checks passed.
- Environment/evidence: base SHA
  `98d71df0f553bc3c0b8173d7aeb2310fa40c7184`, dirty tree; macOS 27.0.0 arm64,
  Python 3.14.6, pytest 9.1.1. Ruff unavailable. No complete baseline suite
  comparison exists.
- Structure: successor 140 physical lines; evaluator facade 1,305 lines; no
  numeric `[source_structure]` budget is configured.
- Boundary: Phase 2 Green done. No Phase 3 refactor or commit performed.
  Separate Phase 3 approval was received after Phase 2 verification.

## Cost / Reasoning Control

- Operating path: Architecture Path for the disposition audit; subsequent
  bounded implementation, if approved, follows Feature Path phases.
- Files read: runtime and collaboration policies, evaluator orchestration and
  binder code, `EvaluatorContext`, ADR 0213, LISS-0495, canonical migration
  spec, related tests, and local planning templates.
- Context intentionally omitted: unrelated language families, provider
  integrations, and unrelated large files.
- Deterministic checks used: symbol/call-site searches, branch and clean-tree
  checks; no tests run because this is design-only.
- Escalation reason: determining whether a private runtime path is still
  reachable through a canonical execution fallback.
- Avoided LLM work: no external research or generated runtime behavior.
- Rework caused by AI output: none observed.

## Adjudicator Decisions

- Architecture approval for retaining and extracting legacy `when` binding:
  approved 2026-09-27.
- Phase 0 acceptance: approved 2026-09-27; specification accepted.
- Phase 1 Red: approved 2026-09-27; same-context test review found no
  remaining blockers after correction; Adjudicator accepted the test review
  on 2026-09-27.
- Phase 2 Green/Implementation: approved and executed 2026-09-27; all
  collected pytest cases passed across segmented runs.
- Phase 3 Refactor: approved and executed 2026-09-27; same-context review found
  no blocker. Final Adjudicator review and committed-SHA verification remain.

## Verification

- Commands/checks: focused and adjacent pytest suites, active-Red lifecycle
  check, test `py_compile`, `git diff --check`; Ruff availability check.
- Result: 3 expected structural failures and 1 passing canonical fallback
  characterization; existing consumers 11 passed; combined 3 expected
  failures, 12 passed. Lifecycle, compile, and whitespace checks passed; Ruff
  was unavailable. Evidence base SHA
  `98d71df0f553bc3c0b8173d7aeb2310fa40c7184`, dirty working tree.

## Changed Files

- `docs/architecture/adr/0227-legacy-when-binding-module-boundary.md`
- `docs/specs/evaluator-legacy-when-binding.md`
- `docs/issues/LISS-0580-legacy-when-binding-extraction.md`
- `docs/work-plans/WP-0173-legacy-when-binding-extraction.md`
- `docs/collaboration/traces/2026-09-27-liss-0580-legacy-when-design.md`
- `docs/collaboration/reviews/2026-09-27-liss-0580-phase1-red-review.md`
- `docs/collaboration/process-lessons-log.md`
- `tests/test_liss_0580_legacy_when_binding_red.py`
- `docs/testing/active-red-tests.toml`

### Attempt 6 — Phase 3 Refactor and review

- Approval: `LISS-0580 Phase 3 Refactor 承認`, Adjudicator, 2026-09-27.
- Scope: reviewer-empathy and readability inspection only; no semantic,
  assertion, or unrelated Evaluator changes.
- Finding: the 140-line successor already has clear single-purpose helpers and
  keeping its explicit two-pass arm selection makes the non-else-before-else
  precedence easy to verify. Added one comment stating that invariant; no
  helper extraction or algorithm rewrite was justified.
- Consumer inventory: repeated repository-wide Python search found production
  dispatch through `binding.py`, the protocol callback, compatibility
  installation/live hook, and approved tests; no additional private helper
  consumers found.
- Verification: focused and adjacent consumers **15 passed**; full CI
  blocking suite `.venv/bin/python -m pytest tests/ -q`: **2,275 passed in
  314.44s**. Lifecycle, coverage-ledger consistency, and whitespace checks
  passed. Ruff is unavailable.
- Evidence: base SHA `98d71df0f553bc3c0b8173d7aeb2310fa40c7184`, dirty tree;
  macOS 27.0.0 arm64, Python 3.14.6, pytest 9.1.1. This is not final-commit
  evidence. No baseline rerun was made; Phase 2 evidence is documented above.
- Structure/routing: successor 141 lines, compatibility 289, evaluator 1,305;
  no numeric structure budget or enabled large-change override. Workspace
  inventory is 13 changed files including earlier phase artifacts (4 modified,
  9 untracked; manually counted 1,379 additions and 102 deletions). The
  `review-change.py` Git-ref report cannot model this dirty/untracked snapshot.
- Reviewer empathy: the branch/else precedence is now immediately explained
  at the point of selection; state ownership and compatibility wiring remain
  straightforward to trace. No additional refactor is recommended within this
  issue.
- Same-context review disposition: no blocker. Same-context is weaker than
  separate-context review. Adjudicator approved the final review on
  2026-09-27; committed-SHA rerun remains required.

## Next Safe Action

Adjudicator approved the Phase 3 final review on 2026-09-27. Commit when
authorized, then rerun every blocking suite on that final commit before closing
the Issue or WP.
