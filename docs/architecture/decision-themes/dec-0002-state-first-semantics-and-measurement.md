# DEC-0002: State-first semantics and measurement

## Status

**Accepted current surface — ADR 0189**

## Current rules

- Mid-program values remain `State<T>`; classical collapse occurs only at
  terminal `measure`.
- `when` preserves all worldlines and replaces classical `if` branching.
- Failure is represented as a state/worldline outcome, not an exception path.
- `inspect` and `snapshot` are non-destructive diagnostics and must not
  collapse a state.
- `project`, `map`, `interfer`, `evolve`, and `trace_out` operate within the
  accepted state semantics; unsupported or non-unitary operations reject
  explicitly.
- Observation is a first-class semantic family: `expect`, `project`,
  `inspect`, `trace_out`, terminal `measure`, and Host/protocol `tomography`
  have distinct collapse and result contracts.
- Semantic expressibility is separate from target executability. A target may
  reject an observation explicitly, but may not replace it with a silent
  collapse or classical fake.
- The finite Joint/limited density Kernel is a first implementation of the
  state semantics, not the complete Hilbert-space or observable-calculus
  horizon.
- Linear uncompute checks use the physical amplitude tolerance `1e-12`.
- The language surface is governed by the language axioms and normative
  specification, not by a backend's implementation convenience.
- `&&`/`||` are total-pushforward Boolean operators, not classical
  short-circuit: both operands are always evaluated, in every Joint
  world, combined via the ordinary truth table — the same pushforward
  shape every other `State<T>` binary operator already uses. `!`
  (logical NOT) remains undecided. This applies only to general-
  expression `&&`/`||`; the Operator-DSL's own binder-guard `&&`/`||`
  (`sum(...) where ...`) is a separate, unaffected compile-time
  predicate over index combinations, not a runtime value operator
  ([ADR 0196](../adr/0196-boolean-total-pushforward-logical-operators.md)).

See [language axioms](../staqex-language-axioms.md), the
[language specification](../../specs/staqex-language-specification.md), and
[physicist-first vision](../adjudicator-language-vision.md). The direction is
defined by [ADR 0189](../adr/0189-quantum-mental-model-and-observation-contract.md).

## Source boundary

- Source tag: `docs/pre-canonicalization-2026-08-03`
- Source commit: `8663ba72295964069ac275b93c350e762a0844d8`
- Source ADRs: ADR 0013, ADR 0014, ADR 0016, ADR 0018, ADR 0020, ADR 0021, ADR 0025, ADR 0026, ADR 0027, ADR 0030, ADR 0034, ADR 0038, ADR 0039, ADR 0040, ADR 0044, ADR 0045, ADR 0052, ADR 0060, ADR 0064, ADR 0075, ADR 0087, ADR 0088, ADR 0089, ADR 0102, ADR 0107, ADR 0114, ADR 0115, ADR 0117, ADR 0120, ADR 0122, ADR 0123, ADR 0167, ADR 0168, ADR 0173
- Recovery command: `git show <source_tag>:<source_path>`

## Acceptance gate

The source set has been reviewed for duplicate, superseded, unique, and
unresolved decisions. This document is the current thematic reading surface;
the listed ADRs are archived source records.
