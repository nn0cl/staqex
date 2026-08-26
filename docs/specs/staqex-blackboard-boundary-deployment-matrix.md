# Staqex blackboard, boundary, and deployment matrix

## Status

Design intake for WP-0117. This document is not a normative language
specification and does not authorize implementation.

| Stage | Canonical question | Owns | Must preserve | Must reject / not own |
|---|---|---|---|---|
| Blackboard source | What physics is being written? | theory, operators, basis, domains, states, intended transforms, observations | source spelling, physical narrative, attached intent | backend gate lists, provider settings, hidden discretization |
| Parse / AST | What structure was written? | syntax tree and source spans | structural children, provenance, lane markers | semantic policy invented from text patterns |
| Semantic authority | Is the written physics valid? | dimensions, units, state/observable roles, Hermiticity, phase/lane validity | meaning, diagnostics, exactness, ownership | caller DTOs or soft diagnostics as executable authority |
| Physics IR | What canonical meaning is projected? | symbolic operators, state transforms, observation nodes | provenance, intent, dimensions, type, exactness | lossy lowering without explicit rejection |
| Finite `Realize` | Can a declared finite representation be formed? | basis/grid/truncation, approximation, resource obligations | ideal meaning and realization provenance | implicit resolution, silent approximation, partial artifacts |
| Simulator | Can the declared realization execute locally? | deterministic local evaluation and terminal result | State-first semantics, measurement boundary, diagnostics | provider credentials, network policy, source rewriting |
| QASM/QPU artifact | Can a target profile realize it? | capability validation and executable projection | instruction payload, wires, parameters, provenance | unsupported capability, generic fallback, partial output |
| Host Job | How is execution requested? | provider-neutral lifecycle, attempts, resource policy | source/realization identity and terminal status | Kernel physics policy, provider SDK details |
| Result / observation | What was observed? | immutable result envelope and observation metadata | measurement vs inspect distinction, attempt/provenance | early collapse claims, incomplete success |
| Deployment adapter | Where/how is the artifact delivered? | packaging, environment, provider transport, operational status | artifact identity, capability contract, failure reason | changing program meaning or inventing physics semantics |

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

The first implementation candidate should be limited to:

- indexed operator/Hamiltonian expression;
- typed parameters and units;
- explicit basis/domain declaration;
- Hermiticity and dimensional diagnostics;
- `prepare -> evolve under H -> expect -> measure`;
- symbolic/operator IR evidence;
- one local simulator realization;
- one fail-closed target capability profile.

It excludes provider SDKs, live QPU submission, credentials, deployment
technology selection, general automatic quantization, and a new mandatory
`theory`/`model`/`realize` syntax.

## Verification evidence

- source-to-AST structural tests;
- semantic diagnostic tests with negative cases;
- provenance-preserving IR golden tests;
- finite realization rejection before artifact creation;
- simulator terminal-measurement tests;
- executable projection fingerprint tests;
- Host/deployment adapter contract tests with fake ports only.
