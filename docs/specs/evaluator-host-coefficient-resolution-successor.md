# Evaluator Host coefficient-array resolution successor

| Field | Value |
|---|---|
| Status | accepted — dedicated H01–H09 / bounded guard transition / Phase 0 accepted 2026-10-09 |
| Owner | LISS-0586 / WP-0174 rank 5 |
| Path | Architecture Path Phase 0; later Feature Path phases separately gated |
| Implementation permission | yes — Phase2 minimal H01–H09 extraction approved; no Phase3/commit/delivery |
| Baseline | a661fb1778e97eda3d35fd1615fd8928c031f062 |

Human `LISS-0586 専用Issue/spec H01–H09・限定guard移行方針とPhase 0 acceptance`
accepts this specification unchanged. Phase 1 execution remains separately
gated; acceptance does not authorize test/guard edits, implementation or delivery.

Subsequent human Phase1 Red execution approval2026-10-09 authorizes only the
accepted tests/limited guard migration. [Execution entry](../collaboration/reviews/2026-10-09-liss-0586-phase1-execution.md)
reports56pass/4structural Red and unchanged inherited contracts. Test acceptance
and H04 unreachable-name disposition pending; implementation still prohibited.

[Phase1 agent test review](../collaboration/reviews/2026-10-09-liss-0586-phase1-review.md)
subsequently passed on unchanged tests. Human test acceptance / H04 disposition
still pending; an agent pass does not grant Green/implementation permission.

## Goal and boundary

Human local-commit / actual-SHA all-blocking verification approval separately
granted via `LISS-0586 ローカルコミット／実SHAで全blocking再検証承認`.
No contract/test changes authorized. Result pending at this record commit;
actual evidence is linked by the Phase2 packet. Subsequent Phase3 and delivery
remain separately gated. Earlier commit-pending statements are historical.

Latest: human `LISS-0586 Phase 2 Green／implementation承認` separately approves
the minimal accepted move. Implemented successor and exact hook without test
changes. [Phase2 provisional verification](../collaboration/reviews/2026-10-09-liss-0586-phase2-verification.md)
records passing focused/consumer/adjacent/spec checks and source-clean blocking
failure; committed-SHA all-blocking verification remains required. H01–H09
unchanged, no Phase3/commit/delivery authority. Earlier permission-pending notes
below are historical.

Human `Phase 1 Red テストレビュー／acceptance承認（H04の扱いを含む）`
on2026-10-09 accepts the unchanged reviewed Phase1 tests and H04 disposition:
in this resolver, blank keys with non-None values fail provenance validation
before tensor name validation. The name-only error is unreachable through this
unchanged path, not permission to delete the direct-constructor validator.
H01–H09 remain unchanged. Earlier pending-acceptance statements are historical;
Phase2 Green/implementation approval remains separate and pending.

Move only `Evaluator._resolve_host_coefficient_arrays` into
`runtime/evaluation/host_coefficients.py`. This is input-boundary orchestration,
not adapter policy or a new scientific-input model. Preserve the existing
`HostInputPort`, `CoefficientTensor`, `InputProvenance`, finite-binder helpers,
and error types. Existing typed tensors already own scientific validation;
no new array DTO or generic validation framework is proposed.

Accepted entrypoint: `resolve_host_coefficient_arrays(context, unit) -> dict[str, Any]`.
A declaration-only `HostCoefficientContext(Protocol)` in that module exposes
only `host_input: HostInputPort | None`. It retains no context or mutable data.
This avoids enlarging or changing the byte-protected `EvaluatorContext`.
The context's live port is read at invocation time, not cached in a service.

`compatibility.py` installs exactly
`Evaluator._resolve_host_coefficient_arrays = resolve_host_coefficient_arrays`
via `install_host_coefficient_compatibility`; evaluator setup imports that
installer under a private alias and invokes it once. The original class body
is removed; no duplicate body or wrapper algorithm remains. Execution continues
through the existing private hook. No public evaluator import is removed.
New successor imports use shared AST/error/port modules, never evaluator.

## Acceptance requirements and minimum evidence

| ID | Preserved contract | Required evidence before Green |
|---|---|---|
| H01 | When no valid Host placeholder is declared, return `{}` without reading the port or merging even if Kernel literals exist; unit without main remains unchanged | empty/no-main/literal-only cases, recording port |
| H02 | Read declared keys in placeholder order, once per successfully materialized distinct key; missing keys remain uncached and may be read again for repeated declarations; ignore unrelated adapter entries | recording port: distinct/repeated/missing keys and extra inputs |
| H03 | Validate Float and Bool through existing CoefficientTensor; retain normalized numeric values, exact Bool leaves, nested shapes and fresh invocation results | Float/Bool/nested positives, port replacement between calls, no retained cache |
| H04 | Reject malformed shape, non-real Float, Bool-as-Float, numeric-as-Bool, NaN/Inf, resource overflow and invalid provenance/name through the same scientific validation/error conversion | exact code/message/class/cause cases, with valid neighboring values |
| H05 | Construct provenance `source_formula="HostInputPort", input_id=host_key`; pass declared dtype/shape; use existing merger's arrays and first diagnostic unchanged | capture tensor arguments, real merge result, deterministic ordered diagnostics |
| H06 | Missing port/value fails closed via merger; repeated key with incompatible later shape retains current first-declaration validation and later shape rejection; same-key mixed dtype behavior is not corrected here; port exceptions propagate unchanged | missing/None/repeated-shape/mixed-dtype/raising-port characterizations |
| H07 | Execution resolves arrays before binder lowering, retains evaluator-owned `_resolved_host_arrays`, and supplies arrays to operator resolution; fixed-seed results and neighboring Host-input families unchanged | real canonical execution, 0406/0407 regressions, Bool selection neighbor, failure before lowering |
| H08 | One successor body, narrow declaration-only context, exact private-hook identity and installed setup, no public-import removal or evaluator cycle | AST ownership, cold public/private import smoke, hook identity, statelessness audit |
| H09 | Permit only this reviewed extraction in inherited preservation guards; retain every unaffected AST/byte protection and all historical immutable evidence | real guards on explicitly distinct pre/post shapes; missing/wrong/duplicate wiring, algorithm/state/export mutations and immutable-fixture negatives |

H04 preserves where validation occurs, including first observed exception and
its `raise ... from error` cause. A blank Host key fails provenance validation
only when a non-None value is supplied; missing remains a merger diagnostic.
No blanket exception conversion or zero/default substitution is permitted.
Do not infer stronger dtype checking from the merger than it actually performs.
Conflict/unknown handling of the public merger remains unchanged; the resolver
does not enumerate the entire port. No-placeholder early return intentionally
does not return literal arrays; downstream binder lowering owns those literals.

Phase 1 must map every row and listed subcase to exact test nodes or an explicit
reviewed unreachable disposition. Passing characterizations and expected
structural Red must be reported separately; import/setup failures are not
accepted product Red. Existing authoritative tests are reused read-only.

## Consumer and state inventory

Inventory is grounded in tracked source at the baseline, not historical Issue
rules. `rg` finds the only direct production call in
`evaluation/execution.py::_prepare_execution_context`, line 62. Execution
stores its result in `_resolved_host_arrays` and passes it to
`lower_finite_binder_operators`. `evaluation/operators.py` reads this store;
`evaluation/observation.py` resets it. Evaluator constructor owns `host_input`.
`host.py` wraps supplied inputs with MappingHostInputAdapter. Dynamic-lane
Host reads and selection binding are separate consumers and remain untouched.

`finite_binder.py` re-exports `_host_placeholder_keys` and
`merge_host_coefficient_arrays` from the 1,027-line finite_binder_legacy.py.
This extraction does not retire or split that implementation: it remains
active. Scientific validation stays in scientific_input.py (286 lines).
Local private hooks, public imports, wildcard exports and lazy imports must
be checked; static search cannot prove external/dynamic consumer completeness.
Resolved dependency graph/cycles remain unassessed until dedicated checks.

## H09 accepted bounded guard transition

The real shared guard `tests/liss_0583_guard_support.py` projects evaluator
and compatibility AST; 0584's readonly guard delegates to it. Tensor support
from 0585 reconstructs its old method before the inherited projections.
The Host method is currently part of the unaffected evaluator digest, so a
legitimate move would fail without a reviewed disposition.

After separate Phase 1 approval, add test-only Host projection support with
an immutable, hash-pinned original 42-line method from baseline evaluator
lines 421–462. It must reconstruct exactly that method at its original position,
permit only the exact new installer import/setup/mapping, and retain Tensor /
foreach protection. Only receiver spelling, location-relative imports and
non-executable docstring changes may differ in the moved algorithm; imports
must still resolve to the same modules. The successor is checked independently.
No generic `ignore_method` or permissive future extraction exemption.

Allowed test-only integration is limited to invoking this projection in the
existing shared helper, copying the new dependency in temporary guard roots,
and explicit shape construction/setup assertions in affected 0583/0585 tests
if needed. Existing assertions and mutation cases are not removed or softened.
Before accepting Red, invoke actual fixture construction and real guard checks
against distinct pre-Host and post-Host roots (body/setup/successor assertions),
including current Tensor and historical reconstructed shapes. Preserve all
missing/changed-successor negatives. Any extra integration beyond this bounded
setup must be presented for acceptance, not silently patched during Green.

Keep original 0583/0584 JSON and 0585 Tensor fixture hashes unchanged. Retain
byte protection for pipeline_legacy.py, baseline JSON/capture script, both
0583 source/behavior tests, binding.py and context.py. New Host fixture is
additional evidence, not replacement provenance. Neither ActiveRed exclusions
nor historical baselines may be refreshed to mask failures.

## Scope matrix and stop conditions

- Phase 0 now: dedicated Issue/spec/trace and WP navigation only.
- Phase 1 later: behavior/ownership/guard tests, immutable Host fixture,
  narrowly reviewed test-only projection/fixture integration; no runtime edit.
- Phase 2 later: new host_coefficients.py, evaluator body removal/private setup,
  compatibility import/installer only; reviewed tests unchanged.
- Phase 3 later: review within this boundary; no unrelated responsibility move.
- Read-only production: host_input_port.py, host.py, scientific_input.py,
  finite_binder facade/body, context.py, execution.py, operators.py, errors.py,
  Tensor/foreach successors, adapters and input-selection logic.

Stop if characterization exposes a defect, diagnostics/order need alteration,
port or DTO shape changes, new dependencies/state ownership or a changed
semantic authority is required. Such work needs a separate scope/spec or ADR.
This proposal applies existing decomposition and Host port decisions, so no
new ADR/technology is proposed. Rank 6 and Rust are excluded.

## Verification and quality disposition

Baseline before documentation edits: Python3.12.6 / pytest9.0.3 on local macOS,
clean a661fb17: selected 10 existing suites, 90 passed in 3.02s, exit0, no
failures/errors/skips/deselections. Exact command and suite list in trace.
This is scoped evidence, not root/spec/all-sanity verification or full Green.

Later declare focused, consumer and adjacent commands before implementation;
all blocking includes full root via active-Red lifecycle args, spec runner,
all applicable CI sanity steps, baseline comparison, import/cycle and syntax
audits and diff checks. Run every blocking suite again after the final commit
at the actual SHA, distinguishing local head and merge-result evidence.

Current physical sizes: evaluator1055, compatibility329, execution463,
finite_binder_legacy1027, scientific_input286. Host method42lines. Moving it
reduces evaluator-owned policy, not necessarily total source lines. Keep the
successor cohesive; count its real body and supporting modules, not facade only.
No numeric source_structure or enabled large_change settings exist; qualitative
rules and core-spec size guardrails apply. Normal review is same_context,
implementation host, empty model IDs; unknown consumer/cycle measures remain
gaps and never waive required verification or human acceptance.
