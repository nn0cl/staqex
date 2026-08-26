# DEC-0003: Language surface and physicist-first DX

## Status

**Accepted current surface — ADR 0189**

## Current rules

- Ideal blackboard form and physicist mental models take priority over
  machine-convenient syntax. Source must denote the same physics as the
  blackboard (including intentional expansion / rewrite / combination);
  realization failure is fail-closed, not a license to reshape chalk
  ([vision §2.2](../adjudicator-language-vision.md)).
- The active surface uses `when`, `state`, `evolve`, `measure`, `fn`, `pub`,
  `namespace`, `enum`, `struct`, and `class`; legacy `if`, `null`, and
  exception-style control are not part of the language.
- Modules and visibility are explicit. `struct` is value-oriented, `class` is
  reference-oriented, and methods use `this` with explicit initialization.
- Type-First declarations and source-friendly quantum notation are preserved
  when they clarify the physics.
- The language provides a contextual scientific lexicon with stable ASCII
  aliases for common symbols such as `psi`/`ψ`, `phi`/`φ`, and `rho`/`ρ`;
  these names are not hidden classical values or an unrestricted global
  reservation of every Greek letter.
- Quantum state composition must not inherit classical branch semantics. The
  current `when` spelling remains a compatibility form, while `superpose` is
  the proposed canonical future spelling pending surface specification and
  migration design.
- Examples are contract-bearing documentation and must not present a
  beautiful equation as a broken DSL workaround.

See [language vocabulary](../staqex-syntax-vocabulary.md),
[physicist × DX harmony](../physicist-dx-harmony.md), and the
[language specification](../../specs/staqex-language-specification.md). The
direction is defined by [ADR 0189](../adr/0189-quantum-mental-model-and-observation-contract.md).

## Source boundary

- Source tag: `docs/pre-canonicalization-2026-08-03`
- Source commit: `8663ba72295964069ac275b93c350e762a0844d8`
- Source ADRs: ADR 0017, ADR 0023, ADR 0024, ADR 0035, ADR 0053, ADR 0054, ADR 0055, ADR 0056, ADR 0057, ADR 0058, ADR 0066, ADR 0067, ADR 0068, ADR 0095, ADR 0106, ADR 0165, ADR 0175, ADR 0176, ADR 0177, ADR 0178, ADR 0179, ADR 0182, ADR 0183, ADR 0184
- Recovery command: `git show <source_tag>:<source_path>`

## Acceptance gate

The source set has been reviewed for duplicate, superseded, unique, and
unresolved decisions. This document is the current thematic reading surface;
the listed ADRs are archived source records.
