# Local semantic backlog detailed design review

## Review target

- **Artifacts:**
  - [Scientific Semantic Core Spec](../../specs/staqex-scientific-semantic-core.md)
  - [Meaning Preservation Spec](../../specs/staqex-semantic-ir-meaning-preservation.md)
  - [Real-QPU readiness Spec](../../specs/staqex-real-qpu-readiness-acceptance.md)
  - [Quantum mental-model Spec](../../specs/staqex-v1-quantum-mental-model-follow-up.md)
  - WP-0107, WP-0113, WP-0120, WP-0092 and LISS-0476–0483
- **Current phase:** Phase 0 design complete; no implementation phase started
- **Requested approval:** review the detailed design and authorize selected
  Issue-level Phase 1 Red work
- **Approval type:** architecture/specification and typed Phase 1 approval,
  separately per Issue
- **Implementation allowed:** no Phase 2 implementation permission
- **Post-review required:** independent review after each Phase 1 Red; Phase 2
  requires a separate implementation approval

## Design decisions made

1. `symbolic_ir` migration and AST/DTO retirement are separate WP-0107 slices.
2. Interference/phase/branch meaning is a semantic-only WP-0113 slice.
3. WP-0120 owns only source-family readiness classification; completed family
   slices are not reopened and unsupported rows may close as explicit defer.
4. WP-0092 separates lexicon, observation types, IR mapping, and conformance;
   no new grammar or public type is implemented by this design review.
5. All slices preserve canonical source identity, provenance, exactness,
   dimensions, `State<T>`, terminal `measure`, explicit `Realize`, and
   fail-closed no-artifact behavior.

## Decisions still requiring Adjudicator/ADR judgment

- whether any public compatibility signature may change during 0476/0477;
- whether the residual 0478 family needs a numerical approximation or new
  semantic node family;
- which 0479 source-family row, if any, should enter Phase 1 first;
- whether 0480/0481 introduce normative grammar/public types, and therefore
  whether ADR 0189/0190 or a new ADR must be amended.

## Verification

- New Issue IDs 0476–0483 are unused and linked to their owning WP/Spec.
- `git diff --check` passes.
- No production code, tests, provider SDK, credentials, or network access was
  changed or used.

## Decision

- [ ] Approve the detailed design as written
- [ ] Approve selected Issue(s) for Phase 1 Red
- [ ] Approve with comments
- [ ] Needs ADR / further design
