# AI work trace: llm-project-template sync

## Request

- Date: 2026-09-17
- User request: 最新の`llm-project-template`を取り込み、プロジェクト運用規約を更新する。
- Current phase: Architecture Path / template synchronization
- Canonical issue or work plan: template update propagation; no application Issue
- AI planning record: N/A

## Context Ledger

- Included: template revision `54bb6a2565703bfcaf28fe0304a9d45b70c0d6bc`, qpex
  contract files, project conventions, sync scripts, lifecycle checks.
- Omitted: application source, scientific specifications, target-domain history,
  secrets, and template maintenance Issues/reviews excluded by the sync policy.
- Assumptions: qpex's project facts remain authoritative in
  `docs/collaboration/project-conventions.md`; template-owned process files may
  be updated from the selected local template checkout.
- Open decisions: Adjudicator review is required before merging contract-file
  changes; no provider, language, or domain decision is introduced.

## Routing

- Model/assistant/tool: host assistant, deterministic sync script, shell checks.
- Reason: template synchronization is repository/process work; no LLM provider
  or application runtime dependency is needed.
- Privacy constraints: no private data or credentials were copied.

## AI Execution Records

### Attempt 1

- Agent: Codex host
- Environment: qpex shared local worktree
- Model as displayed: N/A
- Reasoning setting as displayed: N/A
- Estimated token range: N/A
- Estimated token midpoint: N/A
- Actual tokens: N/A
- Token metric: N/A
- Token source: unavailable
- Token attribution boundary: N/A
- Actual token unavailable reason: host does not expose task token metrics
- Estimate variance: N/A
- Variance reason: N/A
- Scope: inspect template and qpex, dry-run sync, apply template-owned files
- Result: template files applied; the older target sync script reported a syntax
  error after the application. The resulting diff was inspected and the target
  script was confirmed syntactically valid after the template copy.
- Attempt boundary: first sync attempt ended at the script syntax error
- Notes: `.DS_Store` paths were intentionally excluded through
  `.collaboration-template-ignore`; project conventions were not overwritten.

## Cost / Reasoning Control

- Operating path: Architecture Path
- Files read: AGENTS, template AGENTS, adoption guide, prompt change control,
  process lessons, project conventions, sync scripts, verification policy, ADR 0019.
- Context intentionally omitted: application implementation and private data.
- Deterministic checks used: `bash -n` on sync scripts, document lifecycle,
  execution-batch validation, and `git diff --check`.
- Escalation reason: Git writes and template synchronization required outside
  sandbox permissions.
- Avoided LLM work: no generated application code or speculative refactor.
- Rework caused by AI output: none; the sync script's pre-existing syntax issue
  was recorded as an operational gap.

## Adjudicator Decisions

- User authorized the latest local template to be incorporated.
- Contract-file merge still requires explicit Adjudicator review under the
  prompt/instruction change-control policy.

## Verification

- Commands/checks: `bash -n scripts/update-ai-collaboration-files.sh
  scripts/copy-ai-collaboration-files.sh scripts/configure-ai-collaboration.sh
  scripts/init-llm-context.sh`; `scripts/check-document-lifecycle.py`;
  `scripts/check-execution-batch-reviews.py`; `git diff --check`.
- Result: all checks passed; 20 execution-batch records validated and document
  lifecycle passed.

## Parity Correction

- The post-sync contract comparison found one remaining mismatch in
  `.grok/rules/01-quickstart.md`.
- Its approval wording and session-entry condition were aligned with the
  latest template revision `54bb6a2565703bfcaf28fe0304a9d45b70c0d6bc`.
- The correction is limited to that contract file; no project facts or
  application source were changed.

## CI Follow-up

- PR validation exposed five template-owned helper scripts referenced by the
  synchronized CI workflow but absent from the target tree.
- The exact files from the adopted template were restored:
  `scripts/review-change.py`, `scripts/run-regression-tests.py`,
  `scripts/lib/source-clean.sh`, `scripts/lib/review_policy.py`, and
  `scripts/lib/change_metrics.py`.
- This is a template synchronization completeness fix, not application logic.

## Changed Files

- Template-owned collaboration and contract files reported by the sync
  summary, plus four new verification/quality files.
- `.collaboration-template-ignore` for repository metadata files.
- This trace.
- `docs/collaboration/project-conventions.md` was intentionally unchanged.

## Next Safe Action

Review the contract-file parity and template sync diff, then obtain explicit
Adjudicator approval before merging the dedicated sync branch into `main`.

## Notes

The template revision adds focused/all-blocking verification, consumer smoke
and structure-budget guidance, conditional review routing, and associated
quality evidence. It does not authorize application implementation or change
Staqex's domain boundaries.
