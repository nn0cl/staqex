# ADR 0226: Canonical name for Static Kernel observation rejection

## Status

Accepted — Adjudicator approved `ADR 0226 Architecture 承認` on 2026-09-16.

## Context

The accepted observation follow-up specification places `tomography` at the
Host/protocol boundary and requires Static Kernel rejection without implicit
measurement or fabricated results. Its normative mapping uses
`OBSERVATION_UNSUPPORTED`, and the active Red test asserts that code.

LISS-0558 was opened to reconcile a proposed
`OBSERVATION_CAPABILITY_UNSUPPORTED` spelling. Repository inspection found no
current catalog or conformance record establishing that spelling as canonical.
The diagnostic catalog currently omits both names, so changing only the test
would make the test the sole authority and would leave the catalog incomplete.

## Decision

Retain `OBSERVATION_UNSUPPORTED` as the canonical Static Kernel diagnostic for
an observation capability that is outside the selected lane. After approval,
the v1 diagnostic catalog and conformance evidence should explicitly register
that code with the existing observation diagnostic family. No alias for
`OBSERVATION_CAPABILITY_UNSUPPORTED` should be added.

This decision is limited to diagnostic naming and catalog ownership. It does
not implement tomography, POVM execution, Host observation DTOs, provider
integration, or QPU support.

## Rationale

- It preserves the currently normative specification and reviewed Red
  assertion.
- It avoids introducing a second spelling without an existing consumer or
  accepted specification.
- The broad capability boundary remains explicit in the diagnostic meaning
  and surrounding observation contract, while the code stays stable and
  machine-checkable.

## Consequences

- LISS-0558 Phase 1 may update the catalog/conformance evidence and reconcile
  the existing Red node without weakening the rejection contract.
- No runtime behavior needs to change if the implementation already emits the
  canonical code.
- A future rename would require a separate migration decision with consumer
  evidence.

## Approval boundary

This proposed ADR does not authorize Phase 1 test changes, catalog edits,
implementation, or diagnostic aliasing.

## Architecture approval result

- `OBSERVATION_UNSUPPORTED` remains the canonical Static Kernel diagnostic.
- The v1 diagnostic catalog and conformance evidence may register that code in
  the existing observation diagnostic family during LISS-0558 Phase 1.
- No alias, tomography implementation, POVM execution, Host DTO, provider
  integration, or QPU support is authorized by this ADR.
