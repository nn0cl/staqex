# LISS-0520 SQXA target-build Phase 2 Green trace

- Date: 2026-09-11 (Asia/Tokyo).
- Scope: provider-neutral `.sqxa` model, writer/reader, fake target builder,
  and Runtime preflight.
- Approval: `Phase 2実装承認`.
- Added `compiler/staqex/sqxa.py`; portable/targeted artifacts preserve common
  identity and provenance while target metadata remains separate.
- Runtime rejects route mismatch, expired capability, and secret-bearing
  artifact cases before provider construction/access. A pre-existing test
  variable typo was corrected without weakening the contract.
- Targeted pytest passed **6 tests**; AST, `git diff --check`, and document
  lifecycle checks passed.
- Out of scope: SDK installation, credentials, network, signing, registry,
  deployment infrastructure, and live QPU submission.
- Next gate: `LISS-0520 Phase 3 approval`.
