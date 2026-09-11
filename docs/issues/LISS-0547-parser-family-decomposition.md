# LISS-0547: Parser family decomposition

## Metadata

- Local issue ID: LISS-0547
- GitHub issue: none
- Status/phase: proposed / phase-0-design
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

## Verification

AST serialization snapshots, malformed-input recovery corpus, public imports,
full blocking pytest, Spec Verification, import cycles and diff checks.

## Process Review

- Outcome: not yet
- Lesson written: no
- Template-feedback path: none
