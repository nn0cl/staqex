# Staqex Canonical QASM `Coin`/`Mix` Projection Specification

| Field | Value |
|---|---|
| Status | **Accepted — user approved 2026-08-23; bounded implementation under review** |
| Issue | [LISS-0448](../issues/LISS-0448-canonical-qasm-coin-mix-projection.md) |
| WorkPlan | [WP-0111](../work-plans/WP-0111-canonical-qasm-coin-mix-projection.md) |
| Related authority | [ADR 0211](../architecture/adr/0211-scientific-semantic-core-and-ir-authority.md) |

## [DESIGN CHECK]

- **Scope:** resolve the six SV-10/SV-11 failures caused by the retired AST
  fallback for `Coin`/`Mix` QASM examples.
- **Inspected:** LISS-0446/LISS-0447 artifacts, Scientific Semantic IR,
  QPU IR/QASM emitters, SV-10/SV-11 suites, and PR #557 CI logs.
- **Boundary:** QASM may consume only the compile-owned canonical projection;
  no ordinary AST fallback or hidden finiteization is permitted. An explicitly
  source-declared finite Suzuki/binder policy may use the reviewed compatibility
  lowering path; that path is not an implicit fallback.
- **Review lenses:** physicist-first source meaning, canonical authority,
  projection conservation, capability honesty, atomic rejection, and phase
  discipline.
- **Verification:** first a design review, then Red tests, an approved Green
  implementation, independent review, and full spec verification.

## Design direction

`Coin`/`Mix` must remain representable in the ideal language and Scientific
Semantic IR. The QPU/QASM boundary may reject them only when no explicit,
meaning-preserving finite realization exists. This is not a choice between
removing source meaning and restoring an AST fallback.

An architecture decision is required if adding the canonical semantic form
changes ADR 0211 or the QPU capability model.

## Invariants

1. Source structure and intended quantum meaning remain inspectable.
2. QASM is emitted only from Scientific Semantic IR → QPU IR.
3. Unsupported or incomplete inputs reject before gate allocation.
4. Rejection leaves QASM, gates, instructions, allocation, and partial program
   empty.
5. Provider SDK, live submission, S02 numerical migration, and solver work stay
   excluded.

## Canonical semantic field mapping

The ideal projection must expose this structure before any QPU capability
decision:

| Meaning | Required canonical fields |
|---|---|
| `Coin` | `kind=coin`, `source_node_id`, state role, preparation intent, provenance |
| `Mix` | `kind=mixture`, control/branch relation, child node IDs, branch weights or declared mixture rule, state role, provenance |
| `when` | `kind=branch`, controlling node ID, arm node IDs, branch relation, provenance |

For the accepted bounded slice, the canonical `WhenExpr` record exposes
`control_source_node_id` and ordered immutable `branch_rules`. Each rule
contains `pattern`, `is_else`, and `source_node_id`; the corresponding arm
node retains its source span. The semantic fingerprint includes these fields.

The QPU projection may reject these meanings, but may not replace them with a
unitary operation without an explicit meaning-preserving realization.

## Phase 1 Red cases

- `test_liss_0448_coin_builds_structural_semantic_node`;
- `test_liss_0448_mix_preserves_branch_children_and_provenance`;
- `test_liss_0448_qpu_rejection_preserves_ideal_semantic_result`;
- rejection code `E_QPU_CANONICAL_PROJECTION_UNAVAILABLE` and reason
  `mixture_projection_unavailable`;
- rejection provenance includes the mixture source node, branch child source
  IDs, and source span;
- rejection has empty QASM, QPU instructions, gates, allocation, allocated
  qubits, and partial program;
- SV-10/SV-11 cases `sv10-openqasm-bell`, `sv10-cli-emit-qasm`,
  `sv10-target-qpu-emit`, `sv11-qasm3-syntax`, `sv11-gate-map`, and
  `sv11-cli-openqasm3` assert the same explicit rejection rather than the
  retired H+CX AST fallback;
- fixture: `tests/fixtures/canonical_coin_mix/mixture_semantics.sqx`.

### Given/When/Then

- Given `mixture_semantics.sqx`, when semantic IR is built, then `Coin`/`Mix`
  nodes contain the mapped fields and branch child identities.
- Given the same source, when QPU projection has no finite realization, then
  ideal semantic output remains available and the target artifact envelope is
  empty.

## Acceptance record

- User approved the meaning-preservation direction and separate Spec
  acceptance on 2026-08-23.
- Authority: ADR 0210/0211 and the QPU capability rejection contract.
- This Spec freezes the bounded canonical Coin/Mix meaning and explicit
  finite-QPU rejection boundary. It does not authorize provider integration,
  hidden finiteization, or a unitary fallback.

## Competing-path disposition

- Scientific Semantic IR → canonical QPU projection: **authoritative** for
  public QASM emission.
- `compiler/staqex/backend/qasm/lower.py` AST-pattern lowerer: **retained as a
  compatibility boundary for direct legacy callers**, but it is not a
  semantic authority and its `Coin`/`WhenExpr` paths remain fail-closed with
  no unitary fallback. Future migration may retire this path after its direct
  callers are inventoried and replaced.
