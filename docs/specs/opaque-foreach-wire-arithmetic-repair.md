# Opaque foreach Wire numeric-arithmetic repair

Current update2026-10-06: approved A=a14ab3af, B=14973d84, C=6517c208 committed;
C focused48/consumer74/root2419 (4 approved0583 exclusions)/spec161 and all10
local sanity checks pass. R01–R07 unchanged. Earlier pending/gap statements are
historical. Phase3 explicitly authorized2026-10-06; code review passed without
source/test changes. [Phase3 packet](../collaboration/reviews/2026-10-06-liss-0584-phase3-review.md)
separates fresh focused48/consumer74/spec161/sanity10 from prior909 root evidence.
Final verification / six-file record commit separately approved2026-10-06.
Actual final-SHA results live outside tree under `/private/tmp/liss0584-closeout-*`;
completion conditional on all checks passing, no future pass or delivery inferred.
Previous record-head evidence under `/private/tmp/liss0584-final-*` is historical.

Status: accepted — dedicated Issue/spec R01–R07 / Phase 0, 2026-10-05.
Owner: [LISS-0584](../issues/LISS-0584-opaque-foreach-wire-arithmetic-repair.md).
Repair Scope / Phase 0 design start and unchanged dedicated Issue/spec R01–R07
/ Phase 0 acceptance approved. Human `専用Issue/spec R01–R07 と Phase 0 acceptance`
on2026-10-05 accepts the uniquely preceding target. Human
`LISS-0584 Phase 1 Red（受入テスト作成・既存F05テスト引継ぎ）の実行承認`
then authorizes Feature Path Phase 1 test preparation/adoption only.
Human `LISS-0584 Phase 1 Red テストレビュー／acceptance` on2026-10-06
accepts the preceding test packet unchanged. Human
`LISS-0584 Phase 2 Green／implementation approval（実装承認）` separately
authorizes minimal implementation on2026-10-06. No Phase 3/technology selection
inferred; numeric requirements below remain unchanged.

## Design Note / [DESIGN CHECK]

- Target: restore rejection of numeric use of opaque foreach element handles.
- Path/phase: Architecture Path / Phase 0; next proposed Feature Path Phase 1.
- Authority: [Static Hilbert Kernel](staqex-static-hilbert-kernel.md),
  [LISS-0583 accepted F05](evaluator-static-foreach-elaboration.md).
- Inspected: TypeChecker foreach env, binary inference, dimension assignment,
  promotion/index handling, pipeline hard-code inventory, existing F05 and
  neighboring numeric/Hilbert/parametric regressions.
- Boundaries: TypeChecker owns static rejection; Ty remains existing frozen
  dataclass, no VO/DTO/port/adapter/provider or new state owner.
- Decisions: infer operands once in normal order, reject inferred Wire kind
  before numeric dispatch; do not reject by identifier spelling or Qubit payload.
- Ambiguities: wider Wire escaping through calls/returns, relational/logical
  operators and direct assignment policy are not resolved by this numeric repair.
- Included: local diagnostic/source probes and adjacent contracts. Omitted:
  Rust, whole-TypeChecker decomposition, backend changes, unrelated runtime
  snapshots, global consumer graph, external/private data.
- Routing: host, same_context review (weaker isolation), empty model IDs,
  no enabled large-change override; deterministic local tools verified in use.
- Evidence contract: source plus inferred kinds, complete diagnostic codes and
  compile status; no AI runtime output or new canonical semantic authority.
- Verification: R01–R07 clause-to-test mapping, both positive/negative forms,
  scoped results separately from all-blocking suites; no implementation now.

## Confirmed cause and scope (pre-repair baseline)

At unchanged `a287be51da358eed195f836afa21b07286128940`:

1. `_check_foreach_stmt` assigns `Ty("Wire", "Qubit", DIMLESS)` to element q.
2. `_infer_binop` infers lhs/rhs but has no Wire-kind rejection. Numeric paths
   fall through to State results. For `q + 1`: Wire/Qubit + State/Int yields
   State/Qubit, without a hard diagnostic.
3. `_check_assign` accepts matching dimensionless types; it does not recover
   the lost opacity. Broadening this shared assignment checker is not required
   by this repair and would affect unrelated supported assignments.
4. `index(q)` already emits hard `QPU_CLASSICAL_CONTROL_ERROR`; that code is
   already in pipeline HARD_CODES. Reuse it rather than adding another code.

Read-only in-process instrumentation confirms actual `.kind` values;
`Ty.__str__` displays Wire as State<Qubit>, so formatted type text alone is
not evidence of its kind. Both operand inference order and actual result kind
were inspected; no source monkeypatch/file edit persisted.

| Source body | Current compile result |
|---|---|
| `Int k = q + 1`, `Int k = 1 + q`, `Int k = q - 1` | accepted incorrectly |
| `Int k = q * 2`, `Float k = q / 2`, `Float k = q ^ 2` | accepted incorrectly |
| `Int alias = q; Int k = alias + 1` (separate source lines) | accepted incorrectly; alias retains Wire kind |
| `Int k = index(q)` | rejected with QPU_CLASSICAL_CONTROL_ERROR |
| `apply(H, q)`, `apply(X, q)` | accepted; must stay accepted |
| `Int k = 2 + 1` | accepted; must stay accepted |
| `State<Bool> k = q == q` | rejected by LINEAR_IMPLICIT_DISCARD, not a dedicated opacity check; outside this repair |

Wrongly accepted numeric cases carry only lane-soft / semantic finite-evidence
and approximation advisory diagnostics. Their presence is not numeric rejection.
No claim is made that comparisons, calls, aliases outside the tested binding
path or all possible Wire escape paths are now safe.

## Accepted requirements R01–R07

| ID | Contract / minimum Phase 1 evidence |
|---|---|
| R01 | Numeric binary `+`, `-`, `*`, `/`, `^` rejects when either inferred operand has kind Wire. Test each operator with Wire on left and on right; direct TypeChecker and valid public compile fixtures. |
| R02 | Rejection is based on inferred kind, not variable name, declared Int annotation or Qubit payload. Alias then arithmetic and nested arithmetic retain hard rejection; renamed foreach elements also reject. A normal numeric variable named q outside foreach remains valid. |
| R03 | Emit existing QPU_CLASSICAL_CONTROL_ERROR at the offending binary-expression source span, with an explicit opaque-element/numeric-use message. Public compile returns ok=False even with existing soft/advisory diagnostics. At least one such hard diagnostic is required, not an invented global diagnostic-count guarantee. |
| R04 | `apply(H, q)` / `apply(X, q)` compile and retain ordered QASM gates. Index rejection and foreach Measure/Snapshot diagnostics remain unchanged. Reuse existing authoritative F05 nodes without modifying them to pass. |
| R05 | No-Wire numeric arithmetic retains result kind/payload/dimension and diagnostic behavior: State numeric, classical coefficient/literal mixing, multiply/divide, power and unit/dimension behavior. Use existing dedicated suites and positive compile/type probes. No blanket rejection of Qubit State or all foreach body arithmetic. |
| R06 | Keep foreach environment isolation: aliases retain inferred Wire for detection, outer numeric names are restored after loop checking, nested-loop elements remain correctly scoped. This repair must not add shared state or change statement order/binding semantics. |
| R07 | Change only the numeric Wire validation responsibility, leaving runtime expansion, compatibility imports, baseline capture/manifests, plan eligibility and accepted source bodies unrelated to type inference unchanged. Existing consumer/adjacent tests and all blocking suites run before Green/Refactor completion under verification policy. |

EARS: When either operand of a numeric binary expression is an opaque foreach
Wire, compilation shall reject with a hard control diagnostic before that value
can be treated as a numeric State result. When neither operand is a Wire, this
repair shall preserve the existing numeric typing and diagnostics.

```gherkin
Scenario: Opaque element is not a number
  Given QubitRegister<3> reg = system()
  And ForEach q in reg contains Int k = q + 1
  When the source is compiled
  Then compilation fails with QPU_CLASSICAL_CONTROL_ERROR

Scenario: A legal gate operation is unaffected
  Given ForEach q in reg contains apply(H, q)
  When the source is compiled and projected to QASM
  Then compilation succeeds and all three ordered H operations remain
```

## Accepted change boundary / rejected alternative

Small inferred-kind guard after operands are inferred and before existing
numeric dispatch in `_infer_binop`, limited to the five named numeric operators.
Error recovery must not make an outer nested expression silently valid; exact
recovery Ty is an implementation choice to be checked by R02, not a new type
architecture. Avoid new walker or duplicated name-based checks in foreach.

Do not globally tighten `_check_assign`, redefine all Qubit arithmetic, treat
Wire as a number, copy validation into runtime/backend, change HARD_CODES,
change accepted F05, or introduce new typed-object architecture in this repair.
Relational/logical/other-call opacity enforcement and general type rendering
are expressly outside the approved numeric defect investigation; discoveries
remain open questions, not automatic new work or implicit compatibility promises.

The [Phase 1 review packet](../collaboration/reviews/2026-10-05-liss-0584-phase1-review.md)
names the prepared tests for each R01–R07 item and outstanding evidence limits.
The existing failing F05 case remains unexcluded; no lifecycle waiver is added.

## Verification / approval target

Fresh design baseline: existing F05 selector1failed; adjacent21passed and
numeric12passed. HEAD a287be51 + pre-existing dirty0583 tests/docs, unchanged
compiler; no errors/skips/exclusions. See
[trace](../collaboration/traces/2026-10-05-liss-0584-opaque-wire-arithmetic-repair.md)
for commands, environment, timestamps and durations. Root/spec/sanity not_run;
no Green or final-SHA verification claim.

Dedicated LISS-0584 Issue/spec R01–R07 and Phase 0 acceptance received unchanged.
Phase 1 Red test review/acceptance received2026-10-06.
Phase 2 implementation separately approved and minimal guard implemented.
[Current verification/handoff](../collaboration/reviews/2026-10-06-liss-0584-phase2-verification.md)
distinguishes focused Green from the unresolved all-blocking sanity gap.
Next decision: test-carrier/document dependency separation and commit permission;
Phase 3 and final verification remain distinct. No ADR/technology selection proposed.

## Historical Pre-Commit Adjudicator Review Target

- Artifact: Phase 2 verification/handoff under this accepted R01–R07 specification.
- Current phase: Feature Path / phase-2-green, all-blocking gap.
- Requested approval/type: dependency-separation/commit scope decision, not Phase 3.
- Approved scope: separate numeric Wire repair design and unchanged dedicated
  Issue/spec / Phase 0 acceptance and subsequent explicit Phase 1 execution,2026-10-05;
  unchanged Phase 1 test acceptance,2026-10-06.
- Implementation allowed: yes, minimal R01–R07 repair only, separately approved2026-10-06.
  Post-review required: yes. Batch ID: N/A.
- What changed: standalone acceptance/boundary tests and provenance fixture;
  existing F05 assertions and production source remain unchanged.
- Why: block invalid numeric compile acceptance without widening runtime split.
- Checklist: phase/scope, included/omitted context, proposed numeric-only boundary,
  diagnostic contract, branch/test dependency, verification limits and separate
  implementation gate are reviewable above.
- Decision: Phase 2 implementation approved; focused tests pass, but all-blocking
  gap prevents completion/Phase 3. No dependency/delivery waiver inferred.
