# LISS-0457: Meaning-family QPU readiness matrix

| Field | Value |
|---|---|
| Status | **done — Product/Tensor bounded slice complete; other families deferred** |
| Phase | phase-3-refactor |
| Type | semantic contract |
| Priority | P1 |
| Initial size | XL |
| Current size | XL |
| Owner | semantic/physics boundary |
| Parent | WP-0119; WP-0120; WP-0113 |
| Depends on | LISS-0455 |
| Blocks | LISS-0458, LISS-0459 |
| Branch | `codex/liss-0457-meaning-family-qpu-readiness` |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0457--meaning-family-readiness) |

| Scope approval | User approved LISS-0456/LISS-0457 design scope, 2026-08-27 |
| Implementation permission | Phase 3 refactor — Product/Tensor slice only |
| Post-review requirement | CI pytest and human merge review; other family slices remain separately gated |

For product/tensor, continuous/open-system, and measurement families, define
source meaning, Scientific Semantic IR representation, finite realization,
QPU capability rejection, and observable provenance. Each family is a separate
contract; Coin/Mix completion must not imply broader support. Produce either an
accepted specification or an explicit deferred disposition.
## Design detail

**In:** separate matrices for product/tensor, continuous/open-system, and
measurement; source meaning, semantic node, finite realization, capability
rejection, provenance, and evidence requirements. **Out:** universalizing
Coin/Mix, choosing numerical methods/providers, or implementing all families in
one batch.

**Acceptance:** each family has a source example, typed semantic role, finite
boundary, target status, and explicit rejection/deferral reason; lossy
projection preserves inspectable source meaning; terminal and dynamic
measurement remain distinct contracts.

## Phase 0 disposition matrix

| Family | Source evidence | Semantic role to preserve | Finite/QPU status | Required rejection or deferral | Decision owner |
|---|---|---|---|---|---|
| Product/tensor | [`mixture_and_product.sqx`](../../tests/fixtures/semantic_meaning/mixture_and_product.sqx); [`non_unitary_product.sqx`](../../tests/fixtures/capability_rejection/non_unitary_product.sqx) | product/tensor structure, operand identity, dimensions, and mixture-vs-unitary meaning | Limited to already accepted finite projections; generic/non-unitary product is not QPU-ready | `E_QPU_UNSUPPORTED_CAPABILITY` / `non_unitary_target`, or explicit family deferral; never rewrite as a unitary | semantic/physics boundary + Adjudicator |
| Continuous/open-system | [`main_open_systems.sqx`](../../examples/basics/B12_open_systems/main_open_systems.sqx); [continuous discretization spec](../specs/staqex-continuous-discretization.md); [density/CPTP/Lindblad spec](../specs/staqex-density-cptp-lindblad.md) | continuous domain, density state/channel/evolution, discretization contract, and approximation provenance | CPU/simulator contract exists; provider/QPU lowering is deferred | `DISCRETIZATION_REQUIRED_ERROR`, unsupported realization, or explicit defer; no hidden resolution, integrator, or provider mapping | semantic/physics boundary + Adjudicator |
| Measurement | [`dynamic_measurement.sqx`](../../tests/fixtures/semantic_core/dynamic_measurement.sqx); terminal-measure and dynamic-lane specifications | terminal collapse, dynamic measurement/feed-forward, result identity, and lane distinction | Static terminal measurement follows the shipped contract; dynamic support is target-profile dependent; general POVM/tomography remain deferred | `E_QPU_UNSUPPORTED_CAPABILITY` for unsupported dynamic target; no static early collapse or POVM/tomography implication | measurement/Host boundary + Adjudicator |

This matrix is a Phase 0 classification artifact, not a claim that every
listed source example is QPU-executable. A family can enter Phase 1 Red only
for the row-level negative/identity tests whose source, role, target status,
and rejection/defer evidence are present. New numerical methods, public types,
or provider capabilities require a separate ADR and approval.

**Phase/evidence:** Phase 0 research/spec per family; Phase 1 Red matrix and
negative tests; Phase 2/3 only for one separately approved family. Deliverables
are the family matrix, fixtures, ADR/spec decisions, and independent review.
Planning record: `AIP-LISS-0457-2026-08-27-001` (XL; N/A model metrics).

**Stop:** analogy-based generalization, hidden discretization, or changing
Scientific Semantic IR authority requires a new ADR.

### Acceptance-spec review disposition

- Product/tensor: limited to existing finite projections; generic and
  non-unitary product remains explicit rejection/defer.
- Continuous/open-system: CPU/simulator evidence is accepted as the current
  boundary; numerical QPU realization remains deferred with no hidden
  discretization.
- Measurement: shipped terminal/dynamic contracts are distinct; unsupported
  target capability and general POVM/tomography remain explicit boundaries.
- Review result: **READY FOR PHASE 1 RED SCOPE REVIEW**. No implementation,
  new public type, numerical method, provider, or real-QPU action is approved.

## Phase 1 Red artifact

Added [`test_liss_0457_meaning_family_readiness_red.py`](../../tests/test_liss_0457_meaning_family_readiness_red.py).
The four acceptance tests cover non-unitary product rejection, continuous /
open-system deferral without hidden discretization, unsupported dynamic
measurement rejection, and unknown-family fail-closed behavior. They use the
existing source fixtures and describe the future classifier contract only;
production code, fixtures, providers, credentials, and network behavior were
not changed.

Red evidence: the first three family tests reach the intentionally missing
`compiler.staqex.meaning_family_readiness` module under a pytest-independent
harness, producing the expected `ModuleNotFoundError`. Local pytest is not
installed, so the full pytest invocation remains a CI/venv check.

Phase 1 exit: **TESTS REVIEWED; READY FOR PHASE 2 GREEN APPROVAL**.

## Phase 2 Green: Product/Tensor slice

Added [`meaning_family_readiness.py`](../../compiler/staqex/meaning_family_readiness.py).
The implementation recognizes the reviewed scalar-product boundary and returns
an immutable, provider-neutral rejection decision with the source identity,
`E_QPU_UNSUPPORTED_CAPABILITY`, `non_unitary_target`, no artifact/QASM, and an
explicit prohibition on unitary rewriting. Unknown input fails closed with
`ValueError`.

Continuous/open-system and Measurement remain intentionally unimplemented in
this slice and therefore remain failing Red cases. The reviewed Red test file
was not changed.

Phase 2 verification: the direct Product/Tensor harness and unknown-family
fail-closed check pass; Python 3.14 `py_compile` and `git diff --check` pass.
Local pytest remains unavailable because pytest is not installed.

Phase 2 exit: **CORRECTED AND REVIEWED; READY FOR PHASE 3 REVIEW APPROVAL**.
The classifier now consumes the source-derived Scientific Semantic IR
`meaning_kind` and child node structure rather than raw source text.

## Phase 3 refactor and closeout

Extracted the Product/Tensor rejection decision construction into a dedicated
helper and formatted the IR traversal for reviewability. Assertions and
behavior are unchanged; the Red tests remain unchanged. Continuous/open-system
and Measurement remain deferred and are not implied by this completion.

Verification: Product Green direct harness, Python 3.14 `py_compile`, and
`git diff --check` pass. Local pytest is unavailable because pytest is not
installed; CI pytest and human merge review remain required.

Process review: no operating-contract deviation or operational problem found.

Phase 3 exit: **DONE for the bounded Product/Tensor slice**.
