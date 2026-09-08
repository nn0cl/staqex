# ADR 0217: Scientific Workflow metadata, domain extensions, and projections

## Status

**Proposed overall — 0217-A Architecture approved, 2026-09-08.**
User-authorized scope is design correction across scientific domains only.
0217-B/C remain Proposed. No technology selection, Phase 1, implementation,
SDK, credentials, or real submission is authorized.
Sol independently inspected the separate Sora draft before correcting it. A
fresh independent read-only contract review of the corrected proposal completed
with `approve` and no P0/P1/P2 findings; this does not grant Architecture,
Phase, or Implementation approval.

## Context

The accepted Scientific Semantic IR authority (ADR 0211) and finite boundary
(ADRs 0210/0212) already protect source meaning. Existing scientific input and
Workflow specifications cover bounded scalar/Host iteration slices. They do
not establish a common observational graph, continuous-field workflow, or
real-assay S02. The former synthetic S02 was moved to Basic by LISS-0513.
Making those bounded slices the full scientific model would discard units,
space/time, uncertainty, provenance, and model validation.

## Proposed decision

1. Adopt the responsibilities in the [complete design](../scientific-workflow-complete-design.md).
   External Adapter -> Canonical Scientific Metadata Graph -> Domain Extension
   -> validated binding + source -> Scientific Semantic IR -> projections.
2. Metadata Graph is authoritative for versioned descriptions and evidence;
   source-derived Semantic IR alone owns executable expression meaning.
   Graph/DTO injection is never an alternate execution authority.
3. Preserve entity/relation, observation, sample, event, time/space, uncertainty,
   evidence/provenance, dataset/model/objective/constraint/plan/result meanings
   through typed contracts. Keep domain profiles extensible beyond S01/S02.
4. Extend source-visible Realize contracts, through separately accepted method
   profiles, to explicit numerical solver/discretization policies. No new
   syntax or solver method is approved by this ADR alone.
5. Keep classical data and workflow orchestration outside quantum Kernel.
   Require binding and decode evidence even when a legacy host array is used.
   All supported quantum values preserve State and existing measurement rules.
6. Separate Job completion, scientific verification, Plan acceptance, and human
   authorization; bind approval to immutable snapshots and plan revisions.
7. Keep CPU/classical, simulator, QASM, and QPU lanes observable. Unsupported
   projection rejects atomically; explicit fallback is a new classified Job.
8. Connect chemistry, sensor/geographic, astronomy, and numerical ecosystems
   through ports and adapters. No datastore, ontology engine, provider SDK,
   or numerical library is selected here.

## Alternatives considered

- Copy external standards into language syntax: creates a second semantics and
  couples the Kernel to evolving formats. Rejected in this proposal.
- Generic Float arrays plus opaque host callbacks: cannot establish scientific
  identity, missingness, or replay. Retain only as transport inside typed bindings.
- Make Metadata Graph executable IR: conflicts with ADR 0211. Rejected.
- Put classical curation/optimization in quantum Kernel: violates phase and
  state boundaries. Rejected.
- Limit the design to selection and disaster graphs: cannot represent PDE,
  fields, samples, spectral data, or tensor/frame meaning. Rejected.

## Compatibility and consequences

Existing accepted specifications and ADRs are unchanged until this proposal is
accepted. This ADR supplements their domain coverage; it does not reopen
completed WPs or silently change `when`/`mix`, static/dynamic measurement,
Realize overflow evidence, or source spelling. Observational Graph records
are not the deferred public quantum Observation algebra of WP-0092.

Costs include profile governance, explicit conversion evidence, replay storage,
unit/frame checking, and per-method verification. Benefits are one inspectable
scientific chain and separate testing of semantic support and target capability.

## Acceptance and review gates

[Acceptance proposal](../../specs/staqex-scientific-workflow-acceptance.md) and
[WP-0131](../../work-plans/WP-0131-scientific-workflow-program.md) define bounded
work. Independent review must test the metadata/IR distinction, source reachability,
loss detection, explicit finiteization, safety approval expiry, and leakage.
Self-review is not independent acceptance. Architecture approval does not grant
Phase 1 or implementation permission. Technology choices require separate records.

## Separately reviewable architecture decisions

| Decision key | Scope | Status |
|---|---|---|
| 0217-A | Metadata identity/trust/roles and its non-executable relationship to Semantic IR; adapter mapping responsibility, no technology choice (decision 1–3 and 8, metadata portion only) | **Accepted — Architecture approval 2026-09-08** |
| 0217-B | Rich binding, continuous numerical profiles, and quantum transformation contracts (decision 4–5) | Proposed |
| 0217-C | Deadline/replan/approval/fallback lifecycle (decision 6–7) | Proposed |

The next minimum target is **M0 acceptance** for WP-0132/LISS-0515. 0217-B/C
and the ADR as a whole remain Proposed. This partial approval names its key and
retained exclusions in this table; every later WP must name the relevant
accepted key(s).

## Architecture approval record

- Adjudicator decision: `ADR 0217-A Architecture承認` (2026-09-08).
- Accepted boundary: Metadata identity/trust/roles, adapter mapping
  responsibility, and the non-executable relationship to Scientific Semantic IR.
- Retained exclusions: 0217-B/C, technology selection, Phase 1, implementation,
  provider/SDK, credentials, and live submission.
