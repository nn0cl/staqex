# LISS-0437 Phase 3 Red review loop — ABORT 2

## Trigger

User resumed the review/correction loop after the prior ABORT. A fresh
independent review was performed against the current Red suite.

## Resolved findings

- Common `*_or_null` provenance names are now used consistently.
- The Red runner collects assertion and unexpected exceptions for all five
  tests.
- S02 canonical `exp` and optional expanded `Limit` wording is aligned.
- S02 source-fidelity elements and baseline checks are present.

## Unresolved finding requiring a design decision

The P10 budget test must use a supported binder with a valid register mapping,
but the accepted target-profile contract does not yet define how a test or
implementation supplies that mapping. The current profile surface has no
stable mapping field. Using a guessed field would introduce a new API and
architecture decision; using a binder without mapping conflates budget failure
with capability failure.

The reviewer also identified remaining overly specific Limit provenance value
assertions. Removing them is design-preserving; defining the supported binder
mapping API is not determinable from the current Spec/ADR/WP.

## Disposition

- Status: **ABORT**
- Reason: user/Adjudicator decision is required for the target-profile mapping
  contract before the P10 Red test can be made authoritative.
- Green implementation: not started
- Phase approval: unchanged; no Phase 3 Green approval exists

## Required decision to resume

Choose whether the binder-capability witness is supplied by:

1. a new typed `register_mapping` field on the target profile;
2. an existing provider-neutral mapping port/DTO extended for this scope; or
3. a different already-approved contract.

No option is assumed by this record.
