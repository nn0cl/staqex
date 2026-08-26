# Staqex blackboard, boundary, and deployment matrix

## Status

Design intake for WP-0117. This document is not a normative language
specification and does not authorize implementation.

| Stage | Canonical question | Owns | Must preserve | Must reject / not own |
|---|---|---|---|---|
| Blackboard source | What physics is being written? | theory, operators, basis, domains, states, intended transforms, observations | source spelling, physical narrative, attached intent | backend gate lists, provider settings, hidden discretization |
| Parse / AST | What structure was written? | syntax tree and source spans | structural children, provenance, lane markers | semantic policy invented from text patterns |
| Semantic authority | Is the written physics valid? | **Scientific Semantic IR (ADR 0211)**: dimensions, units, state/observable roles, Hermiticity, phase/lane validity | source-derived meaning, diagnostics, exactness, ownership | caller DTOs, soft diagnostics, `physics_ir`, or synthetic authoring as executable authority |
| Consumer projections | How is canonical meaning made usable downstream? | typed projections to simulator, Quantum Semantic IR, Algorithm Plan, and QASM/QPU consumers | provenance, intent, dimensions, type, exactness, stable source identity | `physics_ir` or another projection becoming a parallel authority; lossy lowering without explicit rejection |
| Finite `Realize` | Can a declared finite representation be formed? | basis/grid/truncation, approximation, resource obligations | ideal meaning and realization provenance | implicit resolution, silent approximation, partial artifacts |
| Simulator | Can the declared inspection or realization execute locally? | exact/symbolic inspection **or** an explicit finite `Realize`; deterministic local evaluation and terminal result | State-first semantics, measurement boundary, diagnostics, no hidden finiteization | provider credentials, network policy, source rewriting, implicit grid/steps/gates/qubits |
| QASM/QPU artifact | Can a target profile realize it? | capability validation and executable projection | instruction payload, wires, parameters, provenance | unsupported capability, generic fallback, partial output |
| Host Job | How is execution requested? | provider-neutral lifecycle, attempts, resource policy | source/realization identity and terminal status | Kernel physics policy, provider SDK details |
| Result / observation | What was observed? | immutable result envelope and observation metadata | measurement vs inspect distinction, attempt/provenance | early collapse claims, incomplete success |
| Deployment adapter | Where/how is an accepted artifact delivered? | **Deferred for H1**; future provider-neutral delivery port may own packaging, environment, transport, operational status, retry, and rollback | artifact identity, capability contract, failure reason, no semantic mutation | changing program meaning, inventing physics semantics, partial delivery reported as success |

## Required invariants

1. A source program remains representable even when a target cannot realize it.
2. `Realize` is an explicit finite transition, not a backend side effect.
3. Unsupported realization fails before allocation or artifact emission.
4. Terminal `measure` remains the classical result boundary.
5. `inspect` and other diagnostic views never become hidden measurement.
6. Every executable projection is validated symmetrically against the same
   source/provenance boundary.
7. Deployment adapters consume an accepted artifact and cannot alter its
   semantic payload.

## First bounded acceptance slice: H1

The H1 slice reuses the existing acceptance authority rather than creating a
second package:

- H1-01/H1-02: `docs/specs/staqex-h1-hamiltonian-authoring-direction.md`;
- parser/AST structure: `docs/specs/staqex-h1-2-parser-ast-acceptance.md`;
- operator AST: `docs/specs/staqex-h1-3-operator-ast-acceptance.md`;
- state-transform plan: `docs/specs/staqex-h1-4-state-transform-plan-acceptance.md`;
- control and operation characteristics:
  `docs/specs/staqex-h1-5-control-lane-classification-acceptance.md` and
  `docs/specs/staqex-h1-6-operation-characteristics-acceptance.md`;
- canonical delivery: ADR 0211 and
  `docs/specs/staqex-scientific-semantic-consumer-migration.md`.

For H1-2-03 and H1-3-05, the existing “Physics IR” acceptance wording is a
consumer-facing projection requirement. The source-derived Scientific
Semantic IR remains the authority; the Physics IR node must retain the
canonical source identity, structural children, carrier, parameters, and
provenance. It cannot independently authorize execution.

The implementation contract must dispatch through Scientific Semantic IR,
must not use an H1 early return to bypass canonical projection, and must
reject with a stable code before producing an executable artifact or allocating
target resources.

The first implementation candidate should be limited to:

- indexed operator/Hamiltonian expression;
- typed parameters and units;
- explicit basis/domain declaration;
- Hermiticity and dimensional diagnostics;
- `prepare -> evolve under H -> expect -> measure`;
- one Scientific Semantic IR and typed consumer-projection evidence;
- one exact/symbolic inspection path with no finite allocation;
- one explicit finite `Realize` path, including method/order/steps or equivalent
  finite policy, error budget, target, and provenance;
- one fail-closed target capability profile.

H1 does not include deployment delivery. Provider-neutral artifact delivery,
retry, rollback, credentials, network, and provider SDK choices remain a
separate future boundary decision.

For the H1 simulator evidence, exact/symbolic inspection is non-finite,
non-collapsing, and performs no allocation. A numeric simulator result is in
scope only through a source-visible finite `Realize` carrying method/order,
steps or equivalent finite policy, error budget, target, and provenance.

It excludes provider SDKs, live QPU submission, credentials, deployment
technology selection, general automatic quantization, and a new mandatory
`theory`/`model`/`realize` syntax.

## Verification evidence

- source-to-AST structural tests;
- semantic diagnostic tests with negative cases;
- provenance-preserving Scientific Semantic IR and projection golden tests;
- exact/symbolic inspection versus finite `Realize` tests;
- finite realization rejection before artifact creation or allocation;
- simulator terminal-measurement tests;
- executable projection fingerprint tests covering opcode, wires, parameters,
  source/provenance identity, symmetric expected/actual filtering, and a
  separate terminal `Measure` check. The deterministic fingerprint contract
  is the canonical tuple `(source_node_id, opcode, wires, parameters,
  provenance_digest)` serialized in field order with explicit numeric
  normalization; expected and actual instructions are filtered by the same
  source/provenance boundary. Mutation, legacy-fallback invocation, or
  terminal-Measure mutation must fail closed before artifact emission.
