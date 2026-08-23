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

### 10. Canonical authority and implementation reality

Check whether a claimed language capability is reachable from real source,
structurally represented, type-checked, connected to a consumer, and used as
an authority rather than merely exposed as an importable DTO, fixture, soft
diagnostic, or caller-injected object. Check parallel AST/IR/evaluator paths,
stringly-typed formula fields, duplicated dispatch, and whether preserving an
existing artifact would create maturity debt. Require an explicit
`migrate`/`replace`/`retire` disposition for each competing representation.

### 11. Projection conservation and authority reachability

Check that every downstream projection identifies its canonical source node and
preserves structural children, provenance, type, dimensions, exactness, role,
and intent, or rejects a lossy conversion. Add negative evidence that legacy
IRs, caller DTOs, soft diagnostics, AST-pattern branches, and synthetic
authoring paths cannot independently create executable meaning. Treat exact or
symbolic simulator inspection as distinct from finite `Realize` and require
the latter for every finite target choice.

### 12. Executable projection integrity

For any canonical projection that can emit executable instructions, validate
both the semantic payload and the downstream instruction payload. A source
node ID alone is insufficient: opcode, wires, parameters, and instruction
provenance must be covered by a deterministic digest or equivalent structural
comparison, and mutation must fail closed before artifact emission. Record
legacy fallback and diagnostic re-lowering separately rather than treating a
canonical metadata field as proof that every consumer has migrated.

## Design-time checklist

Before implementation or review, answer:

- Which lenses apply, and why?
- What contract and failure behavior are frozen?
- Which existing modes, axioms, ports, and examples remain unchanged?
- What realization is in scope, and what is rejected?
- What evidence verifies each claim?
- Which prior review records were consulted?
- Is each claimed capability parser-reachable and consumer-wired, or only
  present as a DTO, fixture, soft projection, or test helper?
- Which representation is the canonical semantic authority, and what happens
  to every competing path at maturity?

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

### 12. Symmetric projection validation

When validating a downstream instruction projection, filter both the expected
canonical operations and actual instructions by the same source/provenance
boundary. Otherwise a validator can either miss mutations or reject unrelated
canonical expansions such as QFT. Validate terminal operations separately so
Measure provenance cannot be changed while the executable fingerprint is
recomputed.

### 13. Public entry inventory and ownership pairing

When a canonical projection is propagated through public facades, inventory
every output family, including dynamic or subset emitters that are explicitly
excluded. For included facades, test compile/build call counts and object
identity, not only output text. Define the behavior for a caller-supplied
source object paired with a projection from another source; never repair a
mixed pair by silently rebuilding or caching canonical meaning.
