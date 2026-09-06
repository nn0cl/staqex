# WP-0117: Blackboard, boundary, and deployment reorganization

## Status

**Complete — Phase 3 reviewed**

## [DESIGN CHECK]

- Scope and expected behavior: Reorganize the current design around three
  explicit layers: physicist-first blackboard meaning, semantic/realization
  boundaries, and Host/deployment delivery. Preserve the accepted language
  axioms, terminal `measure`, explicit `Realize`, provenance, and fail-closed
  capability rejection.
- Specifications and files inspected: `AGENTS.md`,
  `docs/architecture/adjudicator-language-vision.md`,
  `docs/architecture/physicist-minimal-dialect.md`,
  `docs/architecture/staqex-democratized-language-direction.md`,
  `docs/architecture/staqex-runtime-execution-model.md`, ADR 0210, ADR 0211,
  ADR 0212, ADR 0213, the H1-01–H1-06 acceptance specifications, and
  `docs/specs/staqex-scientific-semantic-consumer-migration.md`,
  `docs/architecture/open-work-register.md`,
  `docs/specs/staqex-unmerged-branch-asset-reassessment.md`, WP-0091,
  WP-0092, and PR #574 (`e87937e`).
- Component boundaries, ports/adapters, and VO/DTO candidates when
  applicable: `BlackboardMeaning`, `RealizePlan`, `CapabilityProfile`,
  `ExecutionArtifact`, `JobRequest`, and `JobResult` are design-level names
  only. They must not become implementation types until their owning boundary
  and acceptance contract are approved.
- Applicable constraints: source must denote the same physics as the
  blackboard; machine convenience cannot reshape the source; Kernel, Host,
  simulator, QASM, provider, and deployment concerns remain separate; no
  provider SDK or live QPU technology is selected here.
- Decisions, assumptions, and unresolved ambiguities: PR #574 is treated as a
  source of candidate assets, not as an authority or merge base. Candidate
  H1 names (`theory`, `model`, `experiment`, `realize`, `quantize`, and
  `finiteize`) remain proposals unless an existing accepted specification
  already covers them. The meaning and scope of “deployment” must remain a
  Host/delivery concern, not a new Kernel language layer.
- Included and omitted AI context: included the accepted vision, minimal
  dialect, realization and boundary specifications, open-work register, and
  PR #574 inventory. Omitted provider SDKs, credentials, private data, full
  historical ADR bodies, and unrelated source directories.
- Task routing: strong-reasoning architecture analysis for boundary and
  authority decisions; deterministic Git inventory, link checks, and tests
  for evidence.
- Input/output evidence contract when AI output is involved: inputs are named
  repository artifacts and deterministic Git evidence; outputs are a
  reviewable disposition table, boundary matrix, and acceptance plan. No
  generated summary becomes normative without an accepted Spec or ADR.
- Independent review lenses selected and why: contract completeness,
  architecture/boundary integrity, source-to-domain fidelity, state/physics
  safety, realization fail-closed behavior, migration safety, canonical
  authority, and executable projection integrity.
- Verification plan: validate every PR #574 commit disposition, maintain
  source/provenance links, run `git diff --check`, link/reference checks, and
  the existing deterministic specification suites only after implementation
  slices receive their own phase approval.

## Three-layer target model

```text
Blackboard meaning
  theory / operator / basis / state / observe / measure
        |
        v
Semantic and realization boundary
  AST -> Scientific Semantic IR (canonical authority)
       -> typed consumer projections -> explicit Realize plan
        |
        v
Execution and deployment boundary
  capability profile -> artifact -> Host Job -> Result -> delivery adapter
```

The arrows are contracts, not permission to add a new syntax or backend.
Every projection must preserve source provenance, physics intent, dimensions,
exactness, lane, and rejection semantics, or reject the projection before
artifact emission.

## Ordered design batch

1. Complete the PR #574 asset disposition and duplicate/overlap evidence.
2. Freeze the blackboard-to-boundary vocabulary and ownership matrix around
   ADR 0211's Scientific Semantic IR authority.
3. Map the H1 slice to the existing H1-01 through H1-06 specifications and
   canonical-dispatch/no-early-return contract; do not create a second H1
   acceptance authority.
4. Define the exact/symbolic inspection versus finite `Realize` contract.
5. Keep deployment explicitly deferred for H1 unless a future provider-neutral
   delivery-port contract is separately accepted.
6. Request independent read-only review and record dispositions.
7. Request separate Phase 1 approval before creating Red tests.

## Stop conditions

- A proposal changes accepted language meaning or removes an axiom.
- A new syntax, IR authority, provider, deployment technology, or persistence
  convention is required without an ADR and typed approval.
- A projection cannot preserve source meaning or executable payload
  provenance.
- A conflict can only be resolved by choosing between competing physics
  readings rather than by applying an accepted contract.

## Approval state

- Scope approval: granted by user on 2026-08-26.
- Architecture approval: granted by user on 2026-08-26 for this design batch.
- Phase 1 approval: granted by user on 2026-08-26 for failing tests only.
- Phase 2 approval: granted by user on 2026-08-26 for the reviewed Red slice.
- Implementation approval: granted for this bounded Phase 2 slice only.
- Phase 3 approval: granted by user on 2026-08-26 for refactoring only.
- Post-review: completed; latest independent review is `COMPLETE` / `READY`.

## Phase 1 execution record

- Typed approval: user message `承認`, 2026-08-26.
- Allowed operation: add failing acceptance tests only.
- Test file: `tests/test_blackboard_boundary_projection_red.py`.
- Contract under test: canonical executable projection fingerprinting for
  Unicode NFC normalization, finite numeric values, ordered instruction lists,
  and duplicate preservation.
- Forbidden in this phase: production serializer changes, fallback behavior,
  implementation, deployment work, provider selection, and merge actions.
- Expected Red state: the current JSON-based fingerprint does not yet enforce
  NFC normalization or rejection of non-finite numeric values.

## Phase 2 execution record

- Typed approval: user message `承認`, 2026-08-26.
- Allowed operation: minimum production implementation required by the Red
  fingerprint tests; no unrelated semantic or deployment changes.
- Implementation: `compiler/staqex/qpu_ir.py` now uses a tagged canonical byte
  serializer with big-endian u64 lengths, UTF-8/NFC strings, recursive arrays,
  finite IEEE-754 numbers, and ordered provenance digest inputs.
- Verification: direct smoke checks passed for NFC normalization, non-finite
  rejection, instruction order, and duplicate preservation; `py_compile` and
  `git diff --check` passed. The focused regression test passes (`3 passed`).
- Test changes: reviewed Phase 1 tests were not modified.

## Phase 3 closeout

- Typed approval: user message `承認`, 2026-08-26.
- Refactor scope: split canonical float, sequence, and mapping encoding into
  named helpers without changing the fingerprint byte contract or assertions.
- Verification: `py_compile`, direct fingerprint smoke checks, and
  `git diff --check` passed. Repository checks also passed: coverage/Open
  Topics consistency, 20 execution-batch review records, and spec
  verification 161/161 (100%). The focused blackboard-boundary regression
  test passes (`3 passed`).
- Reviewer empathy summary: the serializer's type dispatch is now easier to
  scan, finite-number policy is isolated, and recursive collection handling is
  explicit. The remaining review focus is the exact serialization contract
  and terminal Measure boundary; no deployment or provider behavior was added.
- Remaining risk: the full repository-wide pytest suite was not rerun in this
  closeout; provider SDK installation, credentials, and live QPU execution
  remain explicitly out of scope.
- Process review: no operating-contract deviation or operational problem
  found.
- Status: `complete`; local implementation and design closeout are complete.
