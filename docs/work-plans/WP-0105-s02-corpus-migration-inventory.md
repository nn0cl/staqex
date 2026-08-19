# WP-0105: S02 and representative-example migration inventory

| Field | Value |
|---|---|
| Status | **complete — independent review READY; inventory closed** |
| Local Issue | [LISS-0442](../issues/LISS-0442-s02-corpus-migration-inventory.md) |
| Specification | [S02 and representative-example migration inventory](../specs/staqex-s02-corpus-migration-inventory.md) |
| Planning size | S/M documentation and evidence slice |
| Implementation permission | **No** |
| Follow-up | [LISS-0443](../issues/LISS-0443-s02-numerical-migration.md) / [WP-0106](WP-0106-s02-numerical-migration.md) |

## [DESIGN CHECK]

- **Scope and expected behavior:** Build a source-grounded inventory before
  opening any example migration or S02 numerical phase.
- **Specifications and files inspected:** S02 acceptance/specification,
  explicit-evolution contracts, LISS-0438/WP-0104 completion records, SV-09,
  S02 source/README/Host code, and focused regression tests.
- **Component boundaries:** Documentation/evidence only; no Kernel, Host,
  adapter, QASM, or benchmark behavior changes.
- **Applicable constraints:** Physicist-first source, explicit evolution,
  terminal measurement, no hidden realization, and approval gates.
- **Independent review lenses:** Contract completeness; source fidelity;
  realization honesty; regression safety; evidence hygiene; phase discipline;
  architecture/boundary integrity; type/dimension/validity closure; and
  state/physics safety.
- **Verification:** direct S02 compile, focused LISS-0437/LISS-0438/LISS-0402/
  LISS-0403 checks, full spec verification, and diff/link inspection.

## Work units

1. **Corpus map:** enumerate official examples, equation-bearing constructs,
   and current compile/run evidence.
2. **Boundary map:** distinguish classical parameters, mathematical binders,
   quantum state/operator transforms, finite realization, and Host control.
3. **S02 preservation map:** record exact local `U_t`, formal `Limit`, explicit
   `Realize`, Host inputs, capability rejection, and fixed-seed baseline.
4. **Gap register:** classify each gap as supported, partial, unsupported, or
   intentional scope; assign P0/P1/P2 and recommend a separate Issue where
   needed.
5. **Independent review preparation:** record selected review lenses and
   evidence; do not treat reviewer readiness as phase approval.

## Phase 0 result

Work units 1–4 are now recorded in the Spec’s “Phase 0 inventory result”:
the 26 SV-09 entrypoints plus one README case are the official runnable
corpus, S02 is a separate
Host-dependent showcase lane, and G-01 through G-06 capture the current
support/partial/unsupported/intentional-scope boundaries. The deterministic
evidence and the pytest-environment limitation are recorded there as well.

The first reviews were `NOT READY`; the final fresh independent review returned
`READY` after the correction loop. The inventory is complete and this WP is
closed. The S02 numerical migration is a separate planned task under
LISS-0443/WP-0106.

## Exits and next gate

This WP exits with a reviewed inventory and no code changes. Provider SDK and
live QPU remain outside the follow-up task and require separate approval.
