# LISS-0446 / WP-0109 Design Review 01

| Field | Value |
|---|---|
| Trigger | User-approved design investigation and proposed Spec/WP review |
| Context boundary | Independent read-only reviewer; no edits, approval, or implementation |
| Result | **NOT READY** |

## Findings and disposition

| Priority | Finding | Disposition | Correction |
|---|---|---|---|
| P1 | State/Measure/Limit/Realize/rejection behavior was described abstractly rather than as observable cases. | accepted | Added an acceptance matrix covering terminal measurement, State provenance, bare Limit, explicit Realize, capability rejection, and artifact absence. |
| P1 | Compile-once/no-rebuild was not fixed as call-count and object-identity evidence. | accepted | Added call-count/object-identity requirements for every included facade and source/path/CLI flow. |
| P1 | Dynamic QASM and CH0 subset emitters were absent from the inventory. | accepted | Added explicit inventory exclusions with separate ownership/subset contracts. |
| P2 | Unit-only precedence, delegation, wrapper identity, and mismatched unit/IR pairing were underspecified. | accepted | Added explicit delegation cases and a Phase 1 Red contract requiring deterministic rejection or pairing evidence for mixed sources. |
| P2 | Fallback retirement versus API propagation boundary was ambiguous. | accepted | Fixed Phase 2 to propagation only; unrelated fallback behavior remains excluded. |
| P2 | Phase 3 exit evidence was broad. | accepted | Added compatibility-caller matrix, no-cache, regression, and independent-review evidence requirements. |

## Reusable perspectives promoted

- Public entry inventories must include explicit exclusions for every output
  family, not only the main static path.
- Canonical ownership must be tested with call counts and object identity.
- Mixed source/projection pairs require an explicit contract; silent rebuild is
  not a safe compatibility behavior.

## Next review condition

Freshly review the corrected Spec/WP. Phase 1 Red remains unstarted until the
corrected design is READY and separately approved.
