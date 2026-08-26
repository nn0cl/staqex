# ADR 0213: Canonical Mixture Branch Meaning and QPU Boundary

## Status

Accepted — user/Adjudicator approval 2026-08-23.

## Context

The LISS-0448 review showed that a generic source visitor can retain a
`WhenExpr` and its descendants while still losing the blackboard meaning of
the branch pattern, `else` arm, control identity, and mixture rule. The legacy
QASM lowerer can also recognize a copy-shaped `WhenExpr` and emit `CX`, which
is not a meaning-preserving realization of an arbitrary `Coin`/`Mix` mixture.

The project requires the source to preserve physicist meaning first and keep
finite QPU realization explicit. Passing stale Bell-style QASM expectations is
not evidence that a mixture has a unitary QPU realization.

## Decision

1. The canonical Scientific Semantic IR must retain the source-owned branch
   structure needed to reconstruct the blackboard meaning of `Coin`/`Mix`:
   control source identity, ordered branch identities, pattern/else markers,
   declared branch or mixture rule, and provenance for each relation.
   The bounded record shape is `control_source_node_id` plus ordered immutable
   `branch_rules`; each rule contains `pattern`, `is_else`, and
   `source_node_id`, with its source span retained by the corresponding arm
   node.
2. The canonical semantic fingerprint must change when any accepted branch
   pattern, control identity, or mixture rule changes.
3. The public static QASM path may emit instructions only from a
   meaning-preserving finite canonical projection. Unsupported `Coin`/`Mix`
   remains an atomic capability rejection with the accepted code, reason, and
   source/branch provenance.
4. No generic `WhenExpr`/`Mix` path may silently lower to `CX`, H+CX, or another
   unitary pattern. A future controlled-unitary surface requires its own
   explicit source contract and acceptance Spec; it is not inferred from
   mixture syntax.
5. The QPU capability rejection contract is the normative companion contract
   for deterministic codes, provenance, pre-allocation safety, and empty
   target artifacts. It is accepted for this boundary under ADR 0213 and ADRs
   0210/0211.
6. Existing AST lowerers are not semantic authorities. Until their callers
   are inventoried and migrated, any `Coin`/`Mix` path must fail closed; the
   path may not preserve a compatibility fallback that emits a unitary.

## Consequences

Positive:

- Physicists can inspect source-derived branch meaning without reconstructing
  it from target gates.
- A QPU rejection clearly means “no accepted finite realization here,” not
  “the language construct is invalid.”
- Semantic fingerprinting and provenance expose branch changes and prevent
  stale fallback paths from becoming hidden authorities.

Negative:

- The canonical IR needs a structured branch-rule record rather than a generic
  descendant tuple.
- Direct legacy lowerer callers require an inventory and migration/retirement
  plan before the old path can be removed.
- The next implementation slice must restart at Phase 1 Red for the expanded
  branch-preservation contract.

## Enforcement

Code review must reject:

- a `WhenExpr` IR that omits accepted pattern/else/control/rule meaning;
- a semantic fingerprint that remains unchanged after a branch-rule change;
- a `Coin`/`Mix` QPU fallback that emits unitary gates without an explicit,
  meaning-preserving realization;
- a completion claim that relies only on passing stale target expectations;
- a legacy-path disposition that does not name migrate, replace, retire, or
  fail-closed behavior.

## Follow-up

- LISS-0448/WP-0111: Phase 1 Red extension for structured branch meaning and
  legacy fail-closed behavior.
- LISS-0451/WP-0114: accepted rejection-contract companion and provenance
  matrix.
