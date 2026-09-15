# LISS-0547: Parser family decomposition

## Metadata

- Local issue ID: LISS-0547
- GitHub issue: none
- Status: done
- Phase: done
- Type/priority: refactor / P1
- Initial/current planning size: XL / XL
- Owner/agent: host implementation; same-context review
- Related branch: `refactor/parser-families`

## Summary

Keep `parser.Parser` and `ParseError` stable while moving cohesive grammar
families into `parsing/` components sharing one token cursor and diagnostic
owner.

## Planned extraction units

- `cursor.py`: token lookahead/advance/expect/span only.
- `top_level.py`: package/import/type/function/class/interface declarations.
- `scientific.py`: H1/scientific scopes, workflow fields, graph checks.
- `statements.py`: blocks, binds, measure/snapshot, dynamic and match statements.
- `expressions.py`: value expressions, calls, pipe, when, superpose, evolve.
- `operators.py`: Dirac/operator grammar, binders, sets and indexed expressions.
- `recovery.py`: top-level recovery and stable diagnostics.

Components receive a shared parser state explicitly. They must not subclass a
large parser or keep separate cursor positions.

## Acceptance Notes

AST node class, field values, source spans, token consumption, error recovery,
diagnostic ordering, and accepted/rejected syntax are exact. Unicode aliases
and nested-scope syntax retain their current canonical meaning.

## Dependencies

- Parent: WP-0160
- Depends on: LISS-0543
- Blocks: LISS-0550
- Related: normative language grammar and parser compatibility surface

## Adjudicator Decision Points

Approve shared cursor/state composition. Grammar changes discovered during
extraction are separate Feature Path issues.

## AI Planning Record — AIP-0547-001

- Status/date/size: proposed / 2026-09-11 / XL
- Agent/route: Codex host, display unavailable; host + same-context review
- Scope/estimate: seven parser units; N/A token estimate
- Basis/confidence: 3,504-line class with clear grammar clusters; medium-high
- Assumptions: no token or AST schema change
- Revises/Superseded by: none

## Phase 0 acceptance / detailed design

- Adjudicator approval: `LISS-0547 Phase 0 acceptance 承認`, received
  2026-09-15.
- Canonical basis: [core module decomposition specification](../specs/staqex-core-module-decomposition.md)
  and the accepted language grammar/specification.
- Review packet: [LISS-0547 Phase 0 design review](../collaboration/reviews/2026-09-15-liss-0547-phase0-design-review.md)
- Trace: [LISS-0547 design trace](../collaboration/traces/2026-09-15-liss-0547-parser-families-design.md)

### Current concentration and state owner

`compiler/staqex/parser.py` is approximately 3,669 lines. `Parser` owns the
token list, cursor index `i`, previous token, diagnostics, experiment profile,
function-name lookahead, scientific binding collision state, commutator
context, and norm-bar nesting. `Parser` remains the sole live cursor and
diagnostic owner throughout extraction.

### Extraction units and boundaries

| Unit | Owns | Does not own | Initial entrypoints |
|---|---|---|---|
| `cursor.py` | peek/offset lookahead, advance, match/expect, span, identifier-like token policy | grammar decisions, recovery policy | `_peek`, `_peek_at`, `_advance`, `_match`, `_expect`, `_span` |
| `top_level.py` | package/import, visibility, namespace, enum/struct/class/interface/impl/function declarations, module info | expression grammar and scientific body semantics | `parse`, `_package`, `_import`, declaration parsers |
| `scientific.py` | H1/scientific scopes, workflow fields, system registers, graph checks, discretization/use declarations | ordinary language declarations and token mechanics | `_h1_scope_decl`, `_scientific_scope_decl`, scientific body helpers |
| `statements.py` | blocks, return/bind, foreach, dynamic QPU, match/reset, measure/snapshot | expression/operator precedence | `_block`, `_stmt`, `_type_first_bind`, `_dynamic_qpu_stmt` |
| `expressions.py` | value precedence, calls, pipe, when, superpose, evolve | operator DSL and low-level cursor | `_expression` through `_primary`, `_call`, `_when_expr`, `_evolve_expr` |
| `operators.py` | Dirac/bra/ket, operator precedence, binders, sets, indexed expressions, static index helpers | value expressions and top-level declarations | `_op_expression`, `_op_primary`, `_op_binder`, `_binder_domain` |
| `recovery.py` | top-level resynchronization and stable parse diagnostics | token ownership and accepted grammar | `_skip_until_toplevel_resync`, diagnostic construction |

### Shared parser context contract

Extracted components receive a `ParserContext` protocol containing the shared
token cursor, previous-token/span access, diagnostic sink, and only the
explicit callbacks needed for nested grammar delegation. No component
subclasses `Parser`, creates a second cursor, or retains independent
diagnostic storage. `Parser` remains the compatibility facade and composes the
components through thin forwarding methods during migration.

### Boundary decisions

- Cursor operations are pure mechanics; they never decide grammar or recover
  from malformed input.
- `parse()` retains top-level sequencing and recovery boundaries so imports,
  declarations, profile mode, and diagnostics retain their current order.
- Scientific parsing may call shared declaration/expression/operator parsers,
  but does not introduce a second AST or scientific grammar authority.
- Expressions and operators retain separate precedence stacks. Operator DSL
  parsing must not consume tokens belonging to ordinary expressions.
- Recovery owns resynchronization only; it must not silently accept tokens or
  rewrite source spans.
- Unicode aliases, nested-scope syntax, source-version diagnostics, and
  experiment-profile behavior remain unchanged.

### Phase 1 acceptance matrix

- Cursor: token consumption, lookahead, spans, identifier-like tokens, and EOF.
- Top-level: package/import/visibility/declaration AST shapes and module info.
- Scientific: H1 scopes, workflow fields, register declarations, graph checks.
- Statements: block/bind/measure/snapshot/dynamic/match/reset AST and spans.
- Expressions: precedence, calls, pipes, when/superpose/evolve and recovery.
- Operators: Dirac/bra/ket, operator algebra, binders, sets and indexed forms.
- Recovery: malformed-input diagnostics, resynchronization, ordering, and no
  token loss across subsequent declarations.
- Cross-unit: public Parser/ParseError imports, one cursor/diagnostic owner,
  AST field identity, Unicode aliases, and import-cycle absence.

### Applied process lessons

- `compatibility-baseline`: preserve actual Parser exports and `ParseError`
  access paths.
- `red-contract-reuse`: reuse authoritative parser/AST assertions before adding
  structural tests.
- `quantitative-traceability`: distinguish test-node, file, and line counts.
- `evaluator-state-ownership`: apply the same single-owner rule to cursor and
  parser scope state.

## Process Review

- Outcome: Phase 0 design complete; no tests or production implementation
  started.
- Lesson written: no new lesson; existing lessons applied.
- Template-feedback path: none

## Phase 1 Red result

- Adjudicator approval: `LISS-0547 Phase 1 Red 承認`, received 2026-09-15.
- Added four acceptance contracts for parser family entrypoints, facade body
  removal, shared context dependency direction, and cursor/diagnostic ownership.
- Production implementation was not changed. The tests are expected to fail
  until the reviewed extraction is implemented.
- Active-Red ownership is recorded in `docs/testing/active-red-tests.toml`.
- Next gate: `LISS-0547 Phase 1 Red テストレビュー承認`.

## Phase 1 Red review result

- Adjudicator approval: `LISS-0547 Phase 1 Red テストレビュー承認`, received
  2026-09-15.
- The four tests were accepted as the bounded parser extraction contract.
- Next gate: `LISS-0547 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation result

- Adjudicator approval: `LISS-0547 Phase 2 Green / Implementation 承認`,
  received 2026-09-15.
- Added the `parsing` package, `ParserContext`, and seven family entrypoints
  for cursor, top-level, scientific, statements, expressions, operators, and
  recovery.
- Routed compatibility through named Parser delegates while preserving token
  consumption, AST/span output, diagnostics, and existing Parser access paths.
- Verification: LISS-0547 **4 passed**; parser-focused checks **34 passed with
  1 pre-existing QASM provenance failure**; `py_compile` and `git diff --check`
  passed.
- Next gate: `LISS-0547 Phase 3 Refactor 承認`.

## Verification

AST serialization snapshots, malformed-input recovery corpus, public imports,
full blocking pytest, Spec Verification, import cycles and diff checks.

## Process Review

- Outcome: pending final approval and issue close
- Lesson written: no
- Template-feedback path: none

## Phase 3 Refactor result

- Adjudicator approval: `LISS-0547 Phase 3 Refactor 承認`, received 2026-09-15.
- Review packet: [LISS-0547 Phase 3 review](../collaboration/reviews/2026-09-15-liss-0547-phase3-final-review.md)
- The refactor review confirms explicit family entrypoints, one shared Parser
  state owner, facade compatibility aliases, and dependency direction without
  changing assertions or parser behavior.
- The remaining legacy grammar bodies were intentionally not bulk-moved in
  this slice because their cursor, precedence, recovery, and nested-delegation
  coupling makes a broad move unsafe. Moving each body remains successor
  bounded work, with the existing exact acceptance matrix reused.
- Verification was re-run: LISS-0547 4 passed; parser-focused checks 34
  passed with 1 pre-existing QASM provenance failure; compile, lifecycle, and
  diff checks passed.
- Next gate: none; LISS-0547 is complete.

## Final review and completion

- Adjudicator approval: `LISS-0547 Phase 3 最終レビュー 承認`, received
  2026-09-15.
- Final review packet: [LISS-0547 Phase 3 review](../collaboration/reviews/2026-09-15-liss-0547-phase3-final-review.md)
- The four LISS-0547 Active-Red nodes were removed after their accepted
  contracts passed and the phase sequence completed.
- Successor scope remains explicit: move legacy grammar bodies one family at a
  time under a new acceptance contract; this issue does not claim that work.
- Process review: no operating-contract deviation or operational problem
  found.
- Lesson written: no new lesson; existing lessons were applied.
