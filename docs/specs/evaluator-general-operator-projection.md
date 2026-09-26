# General Operator Projection Successor — Draft Acceptance Specification

| Field | Value |
|---|---|
| Status | Accepted — Architecture Path Phase 0, 2026-09-27 |
| Scope | WP-0172 / LISS-0579 |
| Source authority | `docs/issues/LISS-0431-project-explicit-renorm.md`; current runtime behavior |
| Architecture approval | User `承認`, 2026-09-27 |
| Implementation permission | Phase 2 Green/Implementation approved 2026-09-27; Phase 2 acceptance withheld pending Phase 1 test-contract correction; Phase 3 unapproved |

## Purpose

Define a behavior-preserving decomposition of the general-Operator target of
`project`, currently implemented by `Evaluator._project_onto_operator`. This
specification does not redefine what a mathematical projector is and does not
expand the language's supported projection semantics.

## Existing Behavior to Preserve

Given a call dispatched as `project ψ onto P`, where `P` resolves in the
Evaluator's Operator environment:

1. The runtime requires at least one tuple-valued assignment for the source
coordinate and infers the register width from that tuple.
2. It compiles the Operator expression to a Hamiltonian matrix and memoizes
   that matrix by `(operator_name, width)` in the evaluator-owned cache.
3. It rejects the matrix if any off-diagonal element has magnitude greater
   than `EPS`.
4. For each world whose source coordinate is a tuple, it computes its
   big-endian basis index. A diagonal real component `d <= EPS` is omitted;
   otherwise the world's amplitude is multiplied by `sqrt(d)` using complex
   square root semantics. Results whose squared amplitude is `<= EPS` are
   omitted.
5. Retained worlds preserve assignment and coordinate-phase values by copy,
   then are coalesced. No retained worlds yields `Joint.empty()`.
6. Projection does not implicitly normalize. Explicit normalization remains
   source-level behavior described by LISS-0431.

This is a preservation contract, including established failure boundaries;
it is not an endorsement of every numerical edge case as a desirable future
language rule.

## EARS Scenarios

### Supported diagonal Operator projection

- WHEN a source program projects a tuple-valued State onto a named diagonal
  Operator
- THEN the runtime returns the same unnormalized Joint amplitudes, support,
  coordinate phases, and coalescing as the current implementation.

### Explicit normalization

- WHEN the source explicitly divides the projection by its norm
- THEN normalization occurs only through that explicit source expression;
  projection itself does not normalize.

### Non-diagonal Operator rejection

- WHEN a tuple-valued source coordinate is projected onto an Operator whose
  compiled matrix has an off-diagonal entry with magnitude greater than EPS
- THEN the existing diagonal-only diagnostic is raised.

### Unknown Operator and coordinate shape

- WHEN the requested Operator is absent from the live Operator environment
- THEN the established unknown-Operator diagnostic is raised.
- WHEN no tuple-valued source coordinate is available
- THEN the established tuple-coordinate diagnostic is raised.

### Empty and pruned results

- WHEN all worlds are removed by the existing diagonal/amplitude thresholds
- THEN the result is `Joint.empty()`; otherwise retained worlds are copied and
  coalesced without changing their phase mappings.

## Accepted Ownership and Dependency Boundary

- `Evaluator` remains the sole owner of mutable runtime maps, specifically the
  Operator environment and compiled-matrix cache.
- A successor under `runtime/evaluation/` owns the projection algorithm and
  depends only on explicit live inputs/callbacks, `compile_hamiltonian`, and
  `Joint` value operations. It must not instantiate/import `Evaluator` or
  construct a second state store.
- `evaluation/calls.py` remains the language call dispatcher; it delegates the
  Operator case and retains basis-label projection behavior.
- The private compatibility hook is retained only if actual consumer
  inventory shows it is needed. If retained, the installer mapping, setup
  invocation, and runtime callable identity are testable contracts.
- No external port, adapter, provider, Semantic IR authority, QPU lowering, or
  public language surface is added.

## Explicit Exclusions

- General non-diagonal/Lüders projection.
- New validation that a diagonal Operator is Hermitian, idempotent, positive,
  or has only zero/one eigenvalues.
- Changing complex/negative diagonal handling, `EPS`, malformed-coordinate
  errors, cache lifetime/key, or Operator rebinding semantics.
- Basis projection, `feasible(...)`, Hamiltonian evolution, and generic
  Operator lowering.

Any discovered defect or desire to change these semantics requires a separate
issue and explicit Adjudicator decision; it must not be smuggled into this
structural refactor.

## Phase 1 Red Tests and Evidence

Separate structural ownership failures from passing behavioral
characterizations. At minimum, inventory and test:

- direct, private, and dynamic consumers of the method and cache;
- exact successor ownership and actual removal of the old method body;
- single state ownership and compatibility hook identity, if applicable;
- valid diagonal projection against hand-computed amplitudes and explicit
  normalization;
- non-diagonal rejection using a genuinely off-diagonal Operator and a
  tuple-valued source (the current LISS-0431 test does not establish this);
- unknown Operator, missing tuple-coordinate, empty output, copied phase data,
  coalescing, and cache reuse only where reachable through accepted runtime
  paths;
- LISS-0430 Operator construction and adjacent Operator execution regressions.

Phase 0 architecture and this acceptance boundary were accepted by the
Adjudicator on 2026-09-27. Phase 1 Red was separately approved, and the
issue-owned suite's five structural Red failures and two passing runtime
characterizations were accepted in the test review on 2026-09-27. Phase 2
Green/Implementation was approved on 2026-09-27 and implemented without
changing the reviewed tests. A subsequent reconciliation identified missing
explicit characterization for unknown Operator, empty output, copied phase
metadata, coalescing, and cache reuse. Thus prior passing results do not close
Phase 2 acceptance. Phase 1 contract correction and test review are required
before Phase 2 is re-verified; Phase 3 remains unapproved. The Adjudicator
approved the bounded test-only correction on 2026-09-27. Four added runtime
tests now cover those five details (phase-copy and coalescing share a test).
The corrected suite passed review (`LISS-0579 Phase 1 Red contract correction
テストレビュー承認`, 2026-09-27). Phase 2 commit
`98026263419b86982e8c9e28dc0675b01a9ee465` passed focused/adjacent tests
(31), root pytest (2,271), spec verification (161/161), and repository checks
including template-copy smoke. Phase 3 remains unapproved.
