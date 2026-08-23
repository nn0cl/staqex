# LISS-0448 Phase 1 Red Extension — Correction Trace 02

- Review disposition: accepted in-scope corrections from independent review 02.
- Current phase: Phase 1 Red extension.
- Implementation permission: none.
- Phase 2 approval: not granted.

## Corrections to apply

1. Make `coin_only.sqx` and `mixture_semantics.sqx` part of the bounded Red evidence.
2. Keep direct Coin coverage isolated from Mix coverage.
3. Require branch-arm source spans and source-order anchoring for the ordered branch-rule contract.
4. Extend fingerprint sensitivity with an else/rule-shape mutation.
5. Stage only tests and fixtures for the Red correction commit; do not stage prior production or architecture work.

## Verification

The current direct test harness reports four intended Red failures and four passing contracts. The failures are the missing canonical control/branch fields, missing arm source spans, legacy copy-pattern CX fallback, and unchanged fingerprint. A fresh independent review is required after the bounded test/fixture correction.

## Review 03 disposition

The fresh reviewer confirmed that the Red tests and all three fixtures are self-contained. One accepted documentation/test correction remains: arm source-line expectations must match fixture lines 6 and 7. The canonical IR fields, arm provenance, fail-closed legacy projection, and fingerprint failures remain intentionally Red implementation targets.

## State

`RE_REVIEW` — correction in progress; no Phase 2 transition.
