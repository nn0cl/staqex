# WP-0105: S02 and representative-example migration inventory

| Field | Value |
|---|---|
| Status | **Phase 0 in progress — investigation only** |
| Local Issue | [LISS-0442](../issues/LISS-0442-s02-corpus-migration-inventory.md) |
| Specification | [S02 and representative-example migration inventory](../specs/staqex-s02-corpus-migration-inventory.md) |
| Planning size | S/M documentation and evidence slice |
| Implementation permission | **No** |

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
  realization honesty; regression safety; evidence hygiene; phase discipline.
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

## Exits and next gate

Phase 0 exits with a reviewed inventory and no code changes. A future Phase 1
Red request must name its Issue, accepted scenarios, allowed paths, exclusions,
and whether it concerns example migration, compiler semantics, or numerical
behavior. S02 numerical migration, Provider SDK, and live QPU remain separate
approval gates.

