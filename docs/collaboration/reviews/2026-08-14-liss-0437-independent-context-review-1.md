# LISS-0437 independent context review 1

## Review metadata

- Date: 2026-08-14
- Reviewer: independent subagent, fresh context (`fork_context: false`)
- Scope: ADR 0209, explicit-evolution Spec, WP-0100, LISS-0437, S02, and
  current parser/AST/type/runtime/QPU implementation
- Requested decision: whether the plan was ready to create Phase 1 Red tests
- Verdict: **Not ready before correction**

## Meta-review lenses applied

The review used all nine lenses in
`docs/collaboration/independent-review-perspectives.md`: contract
completeness; architecture boundaries; source-to-domain fidelity; type,
dimension, and validity closure; State/physics safety; realization and
fail-closed behavior; migration/regression safety; phase/approval discipline;
and evidence/context hygiene.

## Findings

| Priority | Finding | Required correction |
|---|---|---|
| P0 | The acceptance contract left grammar, migration, `Limit`, IR, and realization behavior open while the Spec was marked accepted. | Freeze observable contracts before Red; defer internal IR and target resource assertions. |
| P0 | Current `EvolveExpr` has no explicit-transform mode. | Specify a discriminated mode separate from `times` and Hamiltonian forms. |
| P0 | `Operator * State` and `exp(Operator)` cross separate AST domains. | Treat them as dedicated semantic capabilities, not parser-token additions. |
| P1 | Dimensions and validity were incomplete. | Freeze dimensionless exponent, real `hbar`, identity/zero, Hermiticity, and non-unitary target behavior. |
| P1 | QPU realization was underspecified. | Require target-neutral exact/approximate status, policy, resources, and fail-closed rejection with no partial circuit. |
| P1 | Phase 1 scope was too broad. | Limit Red to syntax, diagnostics, source preservation, mode separation, and physics protections. |
| P1 | S02 migration and the `times N` distinction needed an explicit corpus plan. | Preserve `trace_out(psi_0)`, real units, terminal measurement, and leave discrete `times` examples unchanged. |

## Finding-to-lens mapping

- Acceptance and approval findings: lenses 1 and 8
- AST, semantic, and dimensional findings: lenses 2, 3, and 4
- Physics and QPU findings: lenses 5 and 6
- Migration and corpus findings: lens 7
- Independent-context and evidence handling: lens 9

## Reviewer perspective to retain

Reviewers must test whether the source still denotes the blackboard physics,
whether execution boundaries are distinct from physics construction, whether
the AST/semantic boundary can represent the proposed spelling, and whether a
target rejection is honest rather than an adapter-side rewrite. Phase gates
must not be inferred from an architecture approval.

## Resolution

The Spec, ADR, WP, and Issue were revised after this review. The next review
must verify that the frozen contract is internally consistent and that Red
tests do not assert later implementation details.

## Review 2 follow-up

The second fresh-context review initially returned **Not ready** with three
blocking findings: the WP still included S02 numerical equivalence in Red,
dimension behavior was not sufficiently test-frozen, and the migration
diagnostic lacked explicit compile-error/fail-closed semantics. These were
corrected by removing numerical equivalence from Red, specifying compatible
`Operator * State<T>` domains and operator-power checks, and defining the
migration diagnostic as a compile error with no executable or partial target
artifact.

## Review 3 (final)

- Verdict: **Ready for Phase 1 Red test creation**
- Reviewer: independent fresh context, no file edits
- Result: explicit-mode separation, dimensional/source contract, `Limit`
  policy, fail-closed migration diagnostic, S02 fixture boundary, and Red
  scope exclusions were accepted. The missing phase approval record was then
  supplied from the user's explicit instruction to create Red tests after
  review.
