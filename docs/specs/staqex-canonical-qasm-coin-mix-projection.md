# Staqex Canonical QASM `Coin`/`Mix` Projection Specification

| Field | Value |
|---|---|
| Status | **proposed** |
| Issue | [LISS-0448](../issues/LISS-0448-canonical-qasm-coin-mix-projection.md) |
| WorkPlan | [WP-0111](../work-plans/WP-0111-canonical-qasm-coin-mix-projection.md) |
| Related authority | [ADR 0211](../architecture/adr/0211-scientific-semantic-core-and-ir-authority.md) |

## [DESIGN CHECK]

- **Scope:** resolve the six SV-10/SV-11 failures caused by the retired AST
  fallback for `Coin`/`Mix` QASM examples.
- **Inspected:** LISS-0446/LISS-0447 artifacts, Scientific Semantic IR,
  QPU IR/QASM emitters, SV-10/SV-11 suites, and PR #557 CI logs.
- **Boundary:** QASM may consume only the compile-owned canonical projection;
  no ordinary AST fallback or hidden finiteization is permitted.
- **Review lenses:** physicist-first source meaning, canonical authority,
  projection conservation, capability honesty, atomic rejection, and phase
  discipline.
- **Verification:** first a design review, then Red tests, an approved Green
  implementation, independent review, and full spec verification.

## Decision required

The Spec remains proposed until one of these is accepted:

| Option | Meaning | Consequence |
|---|---|---|
| A | Add canonical `Coin`/`Mix` projection | Extend Scientific Semantic IR and QPU projection with an explicit, source-owned meaning; preserve no-fallback rule |
| B | Declare this subset unsupported | Update SV-10/SV-11 to assert explicit capability rejection and empty artifacts; no semantic extension |

The implementation agent must not choose A or B silently. Option A requires an
architecture decision if the projection changes ADR 0211 or QPU capability
semantics. Option B requires acceptance that the existing conformance promise
is narrowed.

## Invariants for either option

1. Source structure and intended quantum meaning remain inspectable.
2. QASM is emitted only from Scientific Semantic IR → QPU IR.
3. Unsupported or incomplete inputs reject before gate allocation.
4. Rejection leaves QASM, gates, instructions, allocation, and partial program
   empty.
5. Provider SDK, live submission, S02 numerical migration, and solver work stay
   excluded.
