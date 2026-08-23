# LISS-0448 Phase 1 Red Design Review 02

| Field | Value |
|---|---|
| Trigger | Fresh re-review after accepted Review 01 corrections |
| Independent context | Rawls, fresh read-only context `01a024f5-5594-78b3-b118-507f42d0dafc` |
| Scope | LISS-0448 Phase 1 Red tests, conformance labels, and evidence |
| Verdict | NOT READY; two small in-scope test/documentation corrections |
| Files changed by reviewer | None |

## Findings and disposition

| Priority | Finding | Disposition | Correction |
|---|---|---|---|
| P1 | The focused rejection test did not assert `compiled.qpu_ir["instructions"] == ()`. | accepted | Add the explicit QPU IR instruction-envelope assertion. |
| P2 | SV-11 case descriptions still said valid QASM and `Coin→H, when-copy→CX, Measure` even though executable assertions rejected the fallback. | accepted | Rename the descriptions to explicit capability rejection. |
| P3 | Branch relation, child, role, and provenance assertions were appropriate and parser-reachable. | accepted as confirmed | No change required. |

## Evidence and reusable perspectives

- Focused pytest: 3 failures as expected.
- Spec verification: 158/161; no production implementation changed.
- `git diff --check`: passed.
- Reusable perspectives: exact artifact-envelope pinning, stale conformance
  label hygiene, and source-derived semantic authority over AST fallback.

## Terminal state

Not terminal. After the accepted corrections, a fresh independent re-review is
required. This review does not approve Phase 2 or implementation.
