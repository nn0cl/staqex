# Staqex Product/Tensor Meaning Preservation Specification

| Field | Value |
|---|---|
| Status | **proposed — Architecture Path design intake** |
| Issue | [LISS-0511](../issues/LISS-0511-product-tensor-meaning-preservation.md) |
| WorkPlan | [WP-0128](../work-plans/WP-0128-product-tensor-meaning-preservation.md) |
| Parent | [WP-0113](staqex-semantic-ir-meaning-preservation.md) |
| Authority | ADR 0211; ADR 0212; [Meaning Preservation](staqex-semantic-ir-meaning-preservation.md) |

## [DESIGN CHECK]

- **Scope and expected behavior:** preserve operator-product and tensor-product
  meaning as distinct source-derived semantic structures before simulator or
  QPU projection.
- **Specifications and files inspected:** the parent meaning-preservation
  specification, ADR 0211/0212, the v1 operator-algebra and multi-register
  specifications, existing `mixture_and_product.sqx` and non-unitary-product
  fixtures, and current product/tensor regression suites.
- **Component boundaries:** the front end retains source grouping and operand
  identity; Scientific Semantic IR owns product/tensor meaning; simulator and
  inspection consume typed projections; finite/QPU projection may reject
  unsupported products. No adapter or provider owns this meaning.
- **Applicable constraints:** no silent unitary interpretation, no hidden
  finiteization, explicit `Realize`, source-order tensor factors, dimension and
  carrier closure, provenance preservation, and atomic no-artifact rejection.
- **Decisions and ambiguities:** semantic node names are design candidates only;
  no production type or syntax is selected here. Operator multiplication,
  tensor product, and non-unitary mathematical products must not be merged into
  one generic executable gate path. Associativity remains source-grouping
  dependent until an accepted normalization contract exists.
- **Included and omitted context:** included canonical IR, AST/HIR retention,
  existing product/tensor semantics, and target rejection behavior. Omitted
  provider SDKs, live QPU execution, numerical approximation, solver work,
  syntax redesign, and tensor-network storage selection.
- **Task routing:** Architecture Path design review followed by a bounded
  Phase 1 Red fixture/test batch; no production implementation in Phase 1.
- **Input/output evidence contract:** inputs are named repository artifacts and
  real `.sqx` source. Outputs are an authority/disposition matrix, acceptance
  fixtures, structural assertions, and no-artifact rejection evidence. Test
  output cannot promote a compatibility DTO to semantic authority.
- **Verification plan:** source reachability, parser/AST/HIR retention,
  canonical-node identity, operand order/grouping, carrier/dimension closure,
  provenance, exactness, simulator inspection, and fail-closed finite/QPU
  projection checks. Run focused tests, spec verification, and `git diff --check`.

## Normative design direction

The canonical semantic result must distinguish at least these meanings:

1. **Operator product:** ordered or explicitly grouped operator operands,
   including scalar/operator multiplication where the carrier remains valid.
2. **Tensor product:** ordered factors with explicit factor boundaries, carrier
   dimensions, and source-order provenance.
3. **Non-unitary mathematical product:** a valid ideal mathematical meaning
   that is inspectable but is not implicitly converted into a unitary circuit.

The semantic projection must retain the source node identity of every operand,
the grouping represented by the source, the resolved carrier/state kind,
dimensions, exactness, and provenance. A consumer may normalize only under an
accepted equivalence contract; output text or numerical coincidence is not
evidence of meaning preservation.

## Acceptance scenarios

- A real `.sqx` source containing an operator product produces a structural
  product meaning, not a generic string or caller-injected DTO.
- A real tensor expression preserves factor order, factor identity, and total
  dimension; swapping factors changes the semantic identity unless an explicit
  equivalence contract says otherwise.
- Nested products preserve source grouping and do not flatten across tensor or
  scalar boundaries without a recorded normalization rule.
- A non-unitary product remains inspectable as ideal meaning and is rejected
  atomically at an unsupported finite/QPU boundary.
- Missing finite realization does not erase the semantic result, allocate a
  circuit, or emit partial QASM.
- Every accepted projection carries source node IDs and provenance for the
  product, each operand, and each tensor factor.

## Phase 1 Red scope

Phase 1 may add only:

- `tests/fixtures/semantic_meaning/product_tensor.sqx`;
- `tests/test_liss_0511_product_tensor_meaning_red.py`;
- this Spec, the Issue, the Work Plan, and review/trace records.

Phase 1 must not add semantic production types, alter lowering, delete legacy
paths, select a tensor backend, install a provider SDK, or emit a new QPU
artifact. The Red batch must cover product/tensor distinction, source grouping,
factor order, dimensions/carriers, provenance, and atomic unsupported
projection.

## Explicit non-goals and stop conditions

- No gate synthesis, numerical approximation, tensor-network engine, provider,
  live QPU, AWS, Rust, solver, or syntax change.
- Stop for ADR/architecture review if preserving the source requires changing
  the Scientific Semantic IR authority, changing `Realize`/`Limit`, selecting
  a new storage representation, or treating a non-unitary product as unitary.

