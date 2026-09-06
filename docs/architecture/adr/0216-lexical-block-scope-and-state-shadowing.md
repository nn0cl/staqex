# ADR 0216: Lexical Block Scope and State Shadowing

## Status

Accepted — user direction recorded 2026-09-05; implementation follows a
separate AT-TDD phase gate.

## Context

Staqex source should retain compact blackboard expressions and should not force
an author to move nested mathematics into helper functions or separate files.
Scientific names such as `psi` must therefore be resolved from explicit source
scope rather than classified globally. `State<T>` also remains linear, so a
name shadow does not permit reuse of the outer state binding.

## Dependency Adoption Evidence

Not applicable. This decision selects no dependency or provider.

## Decision

1. A brace block `{ ... }` creates a lexical scope. Function, method, loop,
   and expression blocks use the same rule.
2. A reference resolves to the nearest declaration visible in its lexical
   scope. An inner declaration may shadow an outer declaration, including when
   the types differ.
3. Two declarations with the same name in one lexical scope are rejected with
   a duplicate-declaration diagnostic.
4. A shadow creates a distinct binding identity. `State<T>` linearity is
   checked per binding identity; shadowing neither consumes nor revives the
   outer state.
5. When an inner scope ends, the outer binding becomes visible again. An outer
   state that was not consumed remains available according to the ordinary
   linearity rules.
6. Scientific display metadata is derived from the resolved typed declaration;
   `psi`, `phi`, and `rho` are not globally reserved words.

## Consequences

Positive:

- Physicists can write nested equations directly in one source file.
- Scope makes same-name references deterministic and reviewable.
- Scientific aliases do not create a second semantic dialect.
- State linearity remains enforceable despite shadowing.

Negative:

- The compiler must carry lexical binding identities through nested blocks.
- Diagnostics need both the shadowing declaration and the hidden declaration
  source locations.

## Enforcement

Code review should reject:

- global classification of `psi`, `phi`, or `rho` without scope resolution;
- silent same-scope redeclaration;
- treating an inner state shadow as reuse of the outer state;
- requiring nested mathematical expressions to be extracted into functions;
- metadata that reports a name without its resolved declaration identity.

## Follow-up

Create a local Issue for parser/type-checker lexical binding support. Phase 1
must cover inner State shadowing, cross-type shadowing, same-scope duplicate
rejection, restoration of the outer binding, and linear consumption per binding.
