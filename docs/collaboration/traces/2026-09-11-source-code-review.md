# AI Work Trace — repository source-code review

## Request

- Date: 2026-09-11
- User request: perform a detailed source-code review, organize findings by
  viewpoint, document the result, and prioritize future corrections.
- Current phase: review-only design/evidence pass
- Canonical issue or work plan: none; repository-wide review requested directly
- AI planning record: this trace
- Planning size: L (repository-wide review; no implementation slice)

## Context Ledger

- Included: Python compiler/runtime/adapters, CI, tests, executable examples,
  README surfaces, and directly governing specifications/issues/work plans.
- Omitted: provider network, credentials, live QPU, cloud deployment, and Rust
  reimplementation.
- Assumptions: current `main` and repository artifacts are authoritative;
  `*_red.py` names do not prove that tests remain intentionally Red.
- Open decisions: public S02 assay record DTO; active-Red lifecycle metadata;
  `.sqxa` envelope authority and version policy.

## Routing

- Model/assistant/tool: host Codex agent; shell/static inspection and local test
  execution.
- Reason: `runtime-routing.toml` selects same-context review and host execution.
- Privacy constraints: local repository only; no provider or network access.

## AI Execution Records

### Attempt 1

- Agent: Codex reviewer role
- Environment: local macOS workspace, Python virtual environment
- Model as displayed: not recorded by repository runtime
- Reasoning setting as displayed: not recorded by repository runtime
- Estimated token range: unavailable
- Estimated token midpoint: unavailable
- Actual tokens: unavailable
- Token metric: unavailable
- Token source: unavailable
- Token attribution boundary: this repository-wide review turn
- Actual token unavailable reason: host does not expose a compatible per-attempt
  token metric to repository artifacts
- Estimate variance: unavailable
- Variance reason: unavailable
- Scope: code, tests, CI, contracts, and documentation consistency
- Result: eight prioritized findings; four blocking fail-closed/regression
  claims; no production-code modification
- Attempt boundary: starts with repository-state recovery and ends with review
  document verification
- Notes: same-context review is weaker than separate-context review

## Cost / Reasoning Control

- Operating path: Feature Path review-only intake
- Files read: targeted high-risk modules and their accepted contracts, plus CI,
  README surfaces, test inventory, and review/process templates
- Context intentionally omitted: historical issue prose unrelated to observed
  failures; provider SDK internals; live-QPU evidence
- Deterministic checks used: CI-equivalent pytest, full pytest, Spec Verification,
  compileall, document lifecycle, coverage-ledger consistency, diff check, and
  two minimal reproduction scripts
- Escalation reason: none for review; branch creation required repository git
  metadata permission
- Avoided LLM work: file/test counts and failures were obtained mechanically
- Rework caused by AI output: none

## Adjudicator Decisions

- User authorized creation, commit, push, and merge of the review result.
- No implementation approval for the recommended repair work is inferred.

## Verification

- `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q --ignore-glob='*_red.py' -k 'not trotter_ising_evolve_qasm and not trotter_rejects_fock_hamiltonian'`
  — 77 passed, 2 deselected.
- `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q --tb=short`
  — 2031 passed, 19 failed in 312.43 seconds.
- `PYTHONPATH=. .venv/bin/python tests/spec_verification/run_all.py`
  — 161/161, gate pass.
- `python -m compileall compiler/staqex` — pass.
- `python3 scripts/check-document-lifecycle.py` — pass before documentation
  edits; rerun required after edits.
- `python3 scripts/check-coverage-ledger-consistency.py` — pass before
  documentation edits; rerun required after edits.
- S02 malformed-evidence reproduction — returned `matched`, NaN gap, negative
  total, and empty snapshot identity.
- `.sqxa` tampered-manifest reproduction — unsupported version and
  contradictory kind/identity loaded successfully.

## Changed Files

- `docs/collaboration/reviews/2026-09-11-source-code-review.md`
- `docs/collaboration/traces/2026-09-11-source-code-review.md`
- `docs/collaboration/process-lessons-log.md`

## Next Safe Action

Request Phase 0 acceptance for WP-A (regression-authority restoration), then
write the acceptance specification and Red tests/CI lifecycle checks before
implementation.

## Notes

The review intentionally distinguishes a failing test from a proven production
defect. CR-002, CR-003, and CR-004 were independently reproduced from current
source; the remaining full-suite failures require contract-by-contract triage.
