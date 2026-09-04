# AI work trace: LISS-0492 `run_unit()` complete removal design

- Date: 2026-09-01
- User target: complete removal of the evaluator `run_unit()` API.
- Current phase: architecture design; implementation permission not granted.
- Canonical issue: `docs/issues/LISS-0492-evaluator-run-unit-complete-removal.md`.
- Included context: LISS-0491, evaluator, pipeline, host/run/CLI, all direct
  caller classes, WP-0107, and the consumer-migration Spec.
- Omitted: provider/QPU/AWS, Rust, solver, release/version policy, and
  unrelated language features.
- Design decision: migrate tests and verification suites in bounded families,
  then remove the public API only after canonical-only and no-reference gates.
- Applicable lessons: preserve authority/source evidence; keep compatibility
  explicit and non-authoritative; synchronize status at closure.
- Next gate: Architecture approval, then a separately approved Phase 1 Red
  removal-guard test batch.
- Phase 1 result: added the fixed removal contract; verification produced 2
  failures and 2 passes with no collection errors. The public API remains and
  131 executable test/spec-verification references require migration.
- Phase 1 review: same-context review accepted the Red contract; see
  `docs/collaboration/reviews/2026-09-01-liss-0492-phase1-review.md`.
- Next gate: separately approved Phase 2 Green caller migration.
- Phase 2-A result: added the shared canonical execution helper and migrated
  SV-07/SV-08 (nine calls); full Spec Verification passed 161/161 (100%).
- Phase 2-A review: same-context review accepted the bounded batch; see
  `docs/collaboration/reviews/2026-09-01-liss-0492-phase2a-review.md`.
- Remaining: feature/regression and other specification-verification caller
  families, then the public API removal gate.
- Phase 2-B result: migrated the remaining 15 verification suites (17 calls);
  suite references are now zero and full Spec Verification remains 161/161
  (100%). The remaining executable inventory is 103 feature/regression calls.
- Phase 2-B review: same-context review accepted the bounded batch; see
  `docs/collaboration/reviews/2026-09-01-liss-0492-phase2b-review.md`.
- Next gate: continuation approval for LISS-0492-C feature/regression migration.
- Phase 2-C result: migrated 48 unit/runtime/display tests to the canonical
  helper; targeted verification passed 48/48. Remaining executable feature
  references are 73 in operator, dynamic, and structured families.
- Phase 2-C review: same-context review accepted the bounded batch; see
  `docs/collaboration/reviews/2026-09-01-liss-0492-phase2c-review.md`.
- Next gate: continuation approval for the next feature-family batch.
- Phase 2-C operator batch result: migrated 42 calls across 12 operator /
  expression modules; targeted verification passed 56/56. Remaining feature
  references are 31 in ports, dynamic, evolve/binder, and examples.
- Operator batch review: same-context review accepted the bounded migration;
  see `docs/collaboration/reviews/2026-09-01-liss-0492-phase2d-review.md`.
- Next gate: continuation approval for the remaining 31-call family.
- Final feature migration result: migrated the remaining 31 calls across
  ports, dynamic/evolve, binder, and example tests; targeted verification
  passed 65/65. Non-contract executable references are now zero.
- Final migration review: same-context review accepted the bounded batch; see
  `docs/collaboration/reviews/2026-09-01-liss-0492-phase2e-review.md`.
- The removal guard now has only one expected failure: the public
  `Evaluator.run_unit` attribute still exists. Next gate is explicit
  LISS-0492-D API-removal implementation approval.
- LISS-0492-D result: removed public `Evaluator.run_unit()` and compatibility
  metadata; API-related regression passed 19/19 and Spec Verification passed
  161/161. Full pytest passed 1823 with 10 unrelated failures.
- Final review: same-context review accepted the removal; see
  `docs/collaboration/reviews/2026-09-01-liss-0492-phase3-review.md`.
- Process review: no operating-contract deviation or operational problem found.
- Next safe action: treat evaluator internal AST mechanics as a new separately
  approved task; do not reopen this completed Issue implicitly.
