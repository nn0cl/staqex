# Independent Review Perspectives Ledger

This is the reusable meta-record for independent-context reviews. It records
which questions reviewers use, not only what one Issue's reviewer found.
Design and implementation work must consult it before requesting review.

## Review lenses

### 1. Contract and acceptance completeness

Check observable behavior, diagnostics, failure behavior, migration rules, and
out-of-scope behavior. Open decisions must be explicit ambiguity boundaries.

### 2. Architecture and boundary integrity

Check parser, AST, semantic, use-case, port, adapter, runtime, and delivery
boundaries. Adapters must not invent business or physics policy. New
architecture decisions require an ADR.

### 3. Source-to-domain fidelity

For Staqex, check that source denotes the same physics and blackboard
reasoning, including intentional expansion and rewrite. Machine convenience
must not force a dialect shift.

### 4. Type, dimension, and validity closure

Check operand domains, dimensions, units, identity/zero cases, invalid and
non-unitary cases, precedence, composition, and stable diagnostics.

### 5. State and physics safety

Check Never Leave the State, terminal measurement, no-cloning/linear-use,
early-collapse prohibitions, classical-control restrictions, ownership, and
trace/discard obligations across all traversals.

### 6. Realization and fail-closed behavior

Check separation between source meaning and simulator/QPU realization. Exact
versus approximate status, policy, resources, capability limits, and rejection
must be explicit. Unsupported lowering must not emit partial artifacts or
silently rewrite source meaning.

### 7. Migration and regression safety

Check compatibility period, migration order, corpus inventory, unchanged
neighboring modes, baseline comparisons, and rollback/failure behavior.

### 8. Phase and approval discipline

Check requested phase, allowed paths, implementation permission, post-review
requirement, and stopping condition. A reviewer may say “ready” but cannot
grant typed human approval.

### 9. Evidence and context hygiene

Check minimal included context, omitted context, path-based evidence,
deterministic checks, and that hidden chain-of-thought is neither requested
nor recorded.

## Design-time checklist

Before implementation or review, answer:

- Which lenses apply, and why?
- What contract and failure behavior are frozen?
- Which existing modes, axioms, ports, and examples remain unchanged?
- What realization is in scope, and what is rejected?
- What evidence verifies each claim?
- Which prior review records were consulted?

## Update rule

Every independent review record maps findings to these lenses and records any
new recurring concern. Promote recurring concerns into this ledger. The
Issue-specific review remains historical evidence; this document is the
cross-Issue reusable guidance.

## Evidence standard

Each finding must identify the artifact, file path, line or section when
available, and the deterministic or document evidence supporting the finding.
Each correction must identify the changed artifact and the verification that
the finding is resolved. A readiness verdict without this evidence is
incomplete.
