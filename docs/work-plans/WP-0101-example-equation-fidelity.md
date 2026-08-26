# WP-0101: example equation fidelity and compile readiness

| Field | Value |
|---|---|
| Status | **complete — PR #553 / independently reviewed READY (2026-08-17)** |
| Purpose | Ensure official examples let a researcher write/read the blackboard equation naturally and let a programmer recover operators, parameters, approximation policy, and semantic boundaries from source. |
| Local Issue | [LISS-0439](../issues/LISS-0439-example-equation-fidelity.md) |
| Related Issue | [LISS-0437](../issues/LISS-0437-explicit-evolution-surface.md) |
| Completion | **complete — PR #553** |
| Specification | [Staqex explicit evolution surface](../specs/staqex-explicit-evolution-surface.md) |
| ADR boundary | [ADR 0210](../architecture/adr/0210-formal-limit-finite-realization-policy.md) |
| Branch | `codex/wp-0100-explicit-evolution-surface` |
| Scope approval | User approval recorded 2026-08-17 |

## [DESIGN CHECK]

- **Scope and expected behavior:** Correct approved examples so equation
  structure, operator names, parameters, approximation claims, and semantic
  boundaries are source-visible and compile under the current grammar.
- **Specifications and files inspected:** `AGENTS.md`, example catalog,
  WP-0100, LISS-0437, explicit evolution Spec, ADR 0210, B08 README,
  current example sources, and focused compiler checks.
- **Component boundaries:** Example source and documentation only, except the
  existing parser/import behavior is consumed as-is. No compiler policy is
  moved into examples and no adapter behavior is changed.
- **Applicable constraints:** Physicist-first source; no hidden
  `Limit`-to-`exp` conversion; explicit `Realize` only when a finite QPU
  example is intentionally introduced; terminal measurement; existing
  `Evolve()`/`until` grammar; preserve user changes.
- **Decisions:** Use the smallest design-preserving correction. Where an
  example claims Suzuki but executes `exp`, either make the approximation
  explicit or revise the claim to exact propagator semantics. This bounded
  batch chooses comment/source alignment unless an explicit finite example is
  separately added.
- **Included context:** B08, S01 day2/fuel/route, A02/A04/A05/A07/A11, and
  related equation-bearing examples and modules; all example checks.
- **Excluded context:** S02 numerical migration, live QPU submit, provider
  SDK/credentials/network, broad unrelated example redesign, compiler
  architecture changes, and destructive cleanup. Pre-existing user changes
  under S02 are preserved and are not part of this batch.
- **Verification:** `check` for all runnable example entrypoints and package
  roots (module files are verified through their importing main); focused
  `run`/`emit-qasm` for changed examples where applicable; existing
  evolution/Realize regression; import and parser checks; `git diff --check`;
  independent review.

## Approved correction units

1. Align Suzuki claims with actual operations; remove stale unused claims or
   make a finite policy source-visible without implicit conversion.
2. Correct the current `until` syntax in S01 fuel example.
3. Correct A11 relative imports so all example sources are checkable.
4. Make QAOA layer count, Lindblad coefficients, walk-shift semantics, and
   RouteBoard/phase relation explicit in names/comments/source structure.
5. Do not add a finite QPU example unless it uses explicit
   `Realize(source, method, order, steps, error_budget)`.

## Acceptance conditions

- No changed example claims an approximation that is not represented by its
  executable source or clearly labels the example as exact propagator syntax.
- All runnable example entrypoints and package import graphs pass `check`,
  or any remaining failure is explicitly documented as outside this Issue
  with evidence. Library `.sqx` files are not standalone programs.
- Changed examples preserve the same physical intent and terminal State
  boundary.
- No direct `Limit` is introduced; no implicit finiteization is introduced.
- This batch introduces no S02, live QPU, or provider SDK changes; pre-existing
  S02 worktree changes remain outside the batch.
- Independent review reaches `READY` and records reusable perspectives.
