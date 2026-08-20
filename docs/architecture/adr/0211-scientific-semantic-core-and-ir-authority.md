# ADR 0211: Scientific Semantic Core and IR authority

## Status

Architecture-approved by user 2026-08-19; independent design review required
before implementation or Phase 1.

## Context

Staqex currently has several representations that overlap in purpose but do
not have equal authority: the operational AST and `OpExpr` path, `symbolic_ir`,
`physics_ir`, `physics_equation` DTOs, HIR, Quantum Semantic IR, and Algorithm
Plan IR. The Physics IR pipeline is a soft projection, while `EquationNode`
can be supplied by callers and stores sides/coefficient expressions as
strings. The evaluator also contains repeated source-shape-specific dispatch.

This means that a construct can appear supported in a DTO or golden test while
not being expressible from `.sqx` source or connected to execution semantics.
Keeping these structures merely because they already exist would create a
long-term semantic authority and migration debt.

## Decision

Staqex will establish one authoritative, source-derived Scientific Semantic
IR between typed source/HIR and consumer-specific projections.

The Scientific Semantic IR will:

1. be built from parsed source, never only injected by callers;
2. represent expressions and equations structurally, never as opaque formula
   strings in semantic nodes;
3. retain source provenance, type, dimensions/units, phase, exactness, and
   attached intent;
4. distinguish classical expression, mathematical relation, quantum state or
   operator, evolution relation, simulator evaluation, and finite realization;
5. reject invalid cross-role conversions explicitly;
6. feed simulator and quantum-semantic consumers through typed projections;
7. feed `Realize` and Algorithm Plan only after source meaning is complete;
8. allow existing Physics IR, Symbolic IR, and Equation DTO paths to be
   migrated, rewritten, or retired based on conformance, not compatibility
   preference.

The source remains physicist-first and ASCII-canonical under ADR 0191. The
semantic IR is not a new user-visible namespace or class hierarchy. Namespace
and entry-point rules from LISS-0440 remain unchanged. `State<T>` and terminal
`measure` remain governed by the existing state axioms. `Realize` remains the

### Boundary contracts made explicit by review

- Semantic roles are internal IR/type-system classifications. They are not
  user-facing `Classical`, `Quantum`, `Simulator`, or `Realization` namespace
  or class containers; existing meanings of `namespace` and `class` remain.
- An exact or symbolic simulator projection may inspect a formal expression or
  evolution without creating a finite target artifact. Any approximation that
  chooses finite steps, gates, qubits, or a backend target is a `Realize`
  operation and must obey ADR 0210. A simulator must not perform hidden
  finiteization as an implementation convenience.
- Every semantic node has a stable source node identity. Projections must
  preserve identity, structural children, role, type/dimension validity,
  exactness, intent, and realization provenance. A projection may omit only
  fields declared non-semantic by its contract; otherwise it rejects as lossy.
- The canonical authority is closed only when a real source-derived path owns
  meaning and consumers cannot independently establish executable meaning from
  AST shape, caller DTOs, soft diagnostics, or alternate synthetic authoring
  paths.
- Exact/symbolic simulator inspection returns only a `SemanticInspectionResult`
  canonical semantic projection in this Issue; it does not evaluate or return
  an exact numeric/symbolic value. It performs no finite allocation or collapse.
  Approximate
  numerical evaluation, discretization, gate selection, qubit allocation, and
  backend targeting require explicit source-visible `Realize`.
- Static terminal `measure` remains the only ordinary source-level collapse to
  a classical result. Existing dynamic-lane mid-circuit measurement is modeled
  in the same canonical IR with a distinct dynamic-measurement lane/role; it
  does not authorize implicit static-lane collapse or finiteization. Its
  existing downstream execution contract is not expanded by LISS-0444.

## Consequences

Positive consequences:

- source, blackboard meaning, simulator behavior, and finite realization can be
  compared through one provenance chain;
- unsupported composition can be rejected at the semantic boundary rather than
  hidden in evaluator or adapter code;
- obsolete DTOs and parallel IRs can be removed instead of becoming permanent
  compatibility dialects.

Costs and risks:

- this is an architecture-level change and may require broad migration;
- existing tests that construct DTOs directly may need replacement with source
  and semantic-IR acceptance tests;
- evaluator responsibilities must be split after the semantic contract is
  stable.

## Rejected alternatives

- **Add more DTOs beside the current models:** preserves the authority split.
- **Keep `EquationNode` string fields as an interim semantic model:** cannot
  prove structure, typing, dimensions, or source fidelity.
- **Make Physics IR authoritative without source integration:** retains the
  current soft/injected boundary and does not make equations a language feature.
- **Create `Classical`/`Quantum` namespaces or classes:** confuses program
  organization with semantic role and shifts physics into nominal containers.

## Review requirement

An independent reviewer must audit the implementation evidence, not only the
documents. The request must explicitly ask whether each claimed capability is
parser-reachable, structurally represented, type-checked, connected to its
consumer, and safe to retire or migrate. A review that accepts DTO existence,
golden fixtures, or soft diagnostics as proof of language support is
insufficient.
