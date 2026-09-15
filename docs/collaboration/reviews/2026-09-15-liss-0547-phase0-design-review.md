# LISS-0547 Phase 0 Design Review

- Date: 2026-09-15
- Scope: Parser family decomposition
- Path: Feature Path, Phase 0 design
- Review isolation: `same_context` (per runtime routing)
- Approval received: `LISS-0547 Phase 0 acceptance 承認`

## Review basis

The design was checked against WP-0160, the accepted core decomposition
specification, the language grammar, project conventions, implementation
readiness, testing strategy, the current Parser method/state inventory, and
the process lessons log.

## Accepted design

The approximately 3,669-line Parser is divided into cursor, top-level,
scientific, statements, expressions, operators, and recovery units. Parser
remains the public facade and sole token-cursor/diagnostic owner. Components
receive explicit shared context and never subclass Parser or retain a second
cursor.

Top-level sequencing and recovery remain in Parser orchestration. Expression
and operator precedence remain separate. Scientific parsing reuses shared
grammar callbacks without creating a second AST or semantic authority.

## Acceptance and risk boundaries

- Preserve AST node classes/fields, source spans, token consumption, diagnostic
  code/order, error recovery, Unicode aliases, and nested-scope syntax.
- Do not change grammar, AST schema, parser behavior, or unrelated typechecks.
- Do not add dependencies, provider code, or generic parser utilities.
- Return to Architecture review if cursor ownership or public AST/ParseError
  contracts must change. Return to Feature Path if characterization exposes a
  syntax defect.

## Reviewer empathy summary

A maintainer can locate grammar responsibility by family while tracing every
component back to one token cursor and diagnostic sink. The design makes token
consumption and recovery explicit, avoiding the most dangerous parser split
failure: silently consuming or accepting the wrong token.

## Next approval required

`LISS-0547 Phase 1 Red 承認`
