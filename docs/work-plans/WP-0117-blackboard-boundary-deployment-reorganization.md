# WP-0117: Blackboard, boundary, and deployment reorganization

## Status

**Design intake — Architecture approved; implementation not approved**

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
  `docs/architecture/staqex-runtime-execution-model.md`,
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
  AST -> semantic authority -> Physics IR -> explicit Realize plan
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
2. Freeze the blackboard-to-boundary vocabulary and ownership matrix.
3. Write the H1 acceptance package for the smallest source-preserving slice.
4. Define the realization/deployment contract without selecting a provider.
5. Request independent read-only review and record dispositions.
6. Request separate Phase 1 approval before creating Red tests.

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
- Phase 1 approval: not granted.
- Implementation approval: not granted.
- Post-review: required before Phase 1.
