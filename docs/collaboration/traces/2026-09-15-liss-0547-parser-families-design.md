# LISS-0547 Parser family decomposition trace

- Date: 2026-09-15
- Issue/WP: LISS-0547 / WP-0160
- Path: Feature Path
- Phase: Phase 0 design
- Route: host implementation; same-context review

## Phase 0

- Approval received: `LISS-0547 Phase 0 acceptance 承認`.
- Current evidence: approximately 3,669 lines; `parse` approximately 246
  lines; `_primary` approximately 212 lines; cursor, diagnostics, scientific
  mode, and recovery state are concentrated in Parser.
- Design decision: seven cohesive units—cursor, top-level, scientific,
  statements, expressions, operators, and recovery—with one shared context.
- Boundary decision: Parser remains the public facade and sole cursor/diagnostic
  owner; no grammar, AST, span, or recovery behavior changes.
- Applied lessons: compatibility-baseline, red-contract-reuse,
  quantitative-traceability, and evaluator-state-ownership.
- Phase 1 acceptance matrix and ambiguity boundaries are recorded in the Issue.

## Next Safe Action

Request `LISS-0547 Phase 1 Red 承認`.

### Phase 1 Red

- Approval received: `LISS-0547 Phase 1 Red 承認`, 2026-09-15.
- Added four bounded tests covering family entrypoints, facade body removal,
  shared context direction, and cursor/diagnostic callbacks.
- No production implementation changed; active-Red nodes are issue-owned.

## Next Safe Action

Request `LISS-0547 Phase 1 Red テストレビュー承認`.

### Phase 1 Red review

- Approval received: `LISS-0547 Phase 1 Red テストレビュー承認`, 2026-09-15.
- The four bounded parser tests were accepted.

### Phase 2 Green

- Approval received: `LISS-0547 Phase 2 Green / Implementation 承認`,
  2026-09-15.
- Added seven family entrypoints and the shared ParserContext; compatibility
  delegates preserve existing parser behavior and access paths.
- Verification: LISS-0547 **4 passed**, parser-focused checks **34 passed with
  1 pre-existing QASM provenance failure**, and static checks passed.

## Next Safe Action

Request `LISS-0547 Phase 3 Refactor 承認`.

### Phase 3 Refactor

- Approval received: `LISS-0547 Phase 3 Refactor 承認`, 2026-09-15.
- Same-context review re-read the canonical specification, issue, parser
  facade, seven family modules, tests, and lifecycle ledger.
- Review result: family entrypoints and shared state ownership are explicit;
  family modules do not import the facade; compatibility aliases preserve
  existing access paths. No behavior or assertion change was found.
- Bounded disposition: retain named legacy bodies temporarily because a broad
  move would cross cursor, precedence, recovery, and nested-delegation
  boundaries. Record one-family-at-a-time body migration as successor scope.
- Verification: structural tests 4 passed; parser-focused checks 34 passed
  with 1 pre-existing QASM provenance failure; compile, lifecycle, and diff
  checks passed.

## Next Safe Action

Request `LISS-0547 Phase 3 最終レビュー 承認`.

### Final review and completion

- Approval received: `LISS-0547 Phase 3 最終レビュー 承認`, 2026-09-15.
- LISS-0547 is complete; its four Active-Red nodes were removed from the
  lifecycle ledger.
- Process review: no operating-contract deviation or operational problem
  found. No new process lesson was required.
- Successor scope: migrate the remaining legacy grammar bodies one family at
  a time with exact parser acceptance evidence.
