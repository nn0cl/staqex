# WP-0118: Implementation-readiness backlog

## Status

**approved planning baseline — phase-0-design**

Approval: user approved all Work Plans on 2026-08-27. This is planning/scope
approval only; it does not authorize Phase 1 Red, implementation, provider
installation, or real-QPU submission.

## [DESIGN CHECK]

- **Scope and expected behavior:** Convert the current open-work register into
  an ordered, implementation-ready backlog for the blackboard, semantic
  boundary, and deployment concerns. Each executable slice must have an
  accepted specification, a named owner boundary, explicit exclusions, and a
  typed Phase 1 approval before tests or production changes begin.
- **Specifications and files inspected:** `AGENTS.md`,
  `docs/architecture/agent-quickstart.md`,
  `docs/architecture/implementation-readiness.md`,
  `docs/architecture/open-work-register.md`, ADRs 0210–0213,
  `docs/specs/staqex-scientific-semantic-consumer-migration.md`,
  `docs/specs/staqex-s02-numerical-migration.md`, WP-0105–WP-0117,
  `docs/collaboration/project-conventions.md`, and the local issue-planning
  and branch-discipline rules.
- **Component boundaries, ports/adapters, and VO/DTO candidates:**
  Scientific Semantic IR remains the source-derived semantic authority.
  Physics IR, QASM, QPU IR, simulator, Host Job/JobResult, and deployment are
  projections or delivery boundaries. `RealizePlan`, `CapabilityProfile`,
  `ExecutionArtifact`, `JobRequest`, and `JobResult` remain design candidates;
  this plan does not authorize new types. Provider-neutral QPU ports remain the
  only external execution boundary.
- **Applicable constraints:** preserve blackboard meaning, terminal
  `measure`, explicit finite `Realize`, provenance, exact/symbolic versus
  finite separation, and fail-closed no-artifact rejection. No provider SDK,
  credentials, network, deployment technology, Rust migration, solver, or
  live QPU submission is included.
- **Decisions, assumptions, and unresolved ambiguities:** existing accepted
  ADRs are authoritative; this plan introduces no new language semantics or
  technology choice. The S02 status in the register must be synchronized with
  WP-0106 before selecting its next implementation slice. WP-0117 remains a
  design/review work item until its final review is recorded.
- **Included and omitted AI context:** included canonical ADRs, specs, WPs,
  register, conventions, and deterministic Git status. Omitted historical
  branches, provider credentials, private data, and unrelated completed
  feature ledgers.
- **Task routing:** architecture and contract decisions stay with the host
  agent and Adjudicator; inventory, link, diff, and test commands are
  deterministic. Review routing follows `runtime-routing.toml` (`same_context`);
  no model is selected here.
- **Input/output evidence contract:** inputs are named repository artifacts and
  command output. Outputs are local Issues/WPs, acceptance tables, dependency
  edges, and phase gates. No AI-generated prose becomes normative without an
  accepted Spec or ADR.
- **Verification plan:** `git diff --check`, local-link/reference checks,
  register/WP/Issue status consistency, specification verification, targeted
  Phase 1 Red suites, then full regression in CI. No implementation or test
  execution is part of this planning change.

## Goal

Make the next implementation choices explicit without treating a completed
bounded slice as permission to widen scope. The backlog is ordered by safety:
canonical authority first, numerical/example migration second, additional
meaning families third, and deployment/provider work last.

## Ordered backlog

| Order | Work item | Canonical record | Current gate | Unblocks |
|---:|---|---|---|---|
| 0 | Reconcile planning ledger and close stale status claims | WP-0118; `open-work-register.md`; WP-0106; WP-0117 | Design-only documentation; no code | Reliable next-slice selection |
| 1 | Scientific Semantic IR consumer continuation | LISS-0445 / WP-0108; parked LISS-0446 | New design review and Phase 1 approval for public QASM facades, old AST helpers, and remaining `symbolic_ir` consumers | Safe fallback retirement |
| 2 | Blackboard/semantic/deployment boundary review | LISS-0453 / WP-0116; WP-0117 | Complete final review and record dispositions; no implementation implied | H1/provider-neutral delivery design |
| 3 | S02 numerical and corpus migration follow-up | LISS-0443 / WP-0106; LISS-0452 / WP-0115 | Verify completion status and define any new bounded slice; separate Phase 1 approval | Reproducible numerical evidence |
| 4 | Meaning-preservation families | LISS-0450 / WP-0113 | New spec/ADR or explicit bounded extension for product/tensor, continuous/open-system, or measurement meaning | Broader semantic projections |
| 5 | Deployment contract | project convention says H1 deployment deferred | Provider-neutral delivery-port contract and ADR required before implementation | Host/deployment implementation |
| 6 | Explicitly deferred language/runtime enhancements | Existing register rows | Individual spec and approval only; do not batch | Future versions, not current release |

## Child execution packets

### Packet A — canonical consumer continuation

1. Update the LISS-0445 inventory with the exact remaining consumers and
   dispositions; do not reopen its completed binder slice.
2. For each public QASM facade or legacy path, write one EARS/Gherkin
   acceptance scenario covering canonical source identity, provenance, and
   no-fallback/no-artifact behavior.
3. Request review of Phase 1 scope. Phase 1 adds Red tests only.
4. Select one consumer slice for Phase 2; stop if it changes ADR-0211,
   `Realize`, `State<T>`, or terminal `measure` semantics.
5. Retire a legacy path only after replacement and rollback evidence exist.

### Packet B — boundary/deployment review

1. Finish WP-0117/WP-0116 disposition and reconcile candidate vocabulary with
   accepted specs; proposals such as `theory`, `model`, `experiment`, and
   `quantize` are not syntax decisions.
2. Keep deployment outside the Kernel. If a delivery contract is needed,
   define a provider-neutral port, request/response DTOs, failure semantics,
   credentials boundary, and artifact provenance in a new ADR.
3. Do not select AWS, a cloud deployment target, persistence, or a network
   topology in this packet.

### Packet C — S02 evidence

1. Synchronize the register with WP-0106's recorded completion evidence.
2. If a new numerical slice is still required, freeze source, seed, baseline,
   numeric identity, tolerances, and rejection behavior in a new acceptance
   spec before Phase 1.
3. Keep numerical migration separate from provider/live-QPU work.

### Packet D — meaning families

Treat product/tensor, continuous/open-system, and measurement as separate
contracts. For each family define source meaning, Scientific Semantic IR
representation, finite realization policy, QPU capability rejection, and
observable provenance. Do not generalize the Coin/Mix contract by analogy.

## Dependency and approval gates

```text
ledger reconciliation
        |
        +--> consumer continuation ----> one bounded Phase 1 Red slice
        |
        +--> boundary/deployment review -> provider-neutral ADR (if needed)
        |
        +--> S02 status/acceptance ------> separate numerical Phase 1 Red
        |
        `--> meaning-family contract ---> family-specific Spec/ADR
```

- Scope approval covers investigation and documentation only.
- Architecture approval is required for a new boundary, ADR, or deployment
  contract.
- Phase 1 approval authorizes failing tests only.
- Phase 2 implementation approval is separate and limited to reviewed Red
  tests.
- CI must be green before merge; a GitHub Actions startup failure is an
  infrastructure follow-up, not evidence of feature correctness.

## Definition of ready for implementation

An item may leave this backlog only when its local Issue and Work Plan name:

- an accepted Spec or ADR and exact Given/When/Then or EARS scenarios;
- included files and explicit exclusions;
- owning boundary, ports, adapters, and DTO/VO decisions;
- dependency edges and a dedicated feature-unit branch;
- Phase 1 test locations and deterministic verification;
- rollback/no-artifact behavior for unsupported meaning;
- typed Adjudicator approval for the next phase.

## Stop conditions

Stop for Adjudicator/ADR decision if the work changes source meaning, adds
syntax, selects a provider or deployment technology, introduces persistence,
changes the Scientific Semantic IR authority, or requires implicit
finiteization.

## Next safe action

The planning baseline and Packet 0 reconciliation are approved and recorded.
LISS-0456 and LISS-0457 are complete for their bounded slices. The next safe
action is the separately tracked human-operated WP-0126 pilot evidence step; no Phase 1 tests,
provider installation, or production implementation should start from this
document alone.

## Real-QPU roadmap extension

The end-to-end path from the current Kernel to a human-authorized real-QPU
run is decomposed in [WP-0119](WP-0119-real-qpu-readiness-roadmap.md). That
roadmap is subordinate to this planning baseline and does not reopen completed
semantic, realization, QASM, Host-port, or provider-adapter slices.
