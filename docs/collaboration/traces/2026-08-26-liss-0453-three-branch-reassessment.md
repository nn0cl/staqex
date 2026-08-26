# LISS-0453 Three Remaining Branches: Design Reassessment

[DESIGN CHECK]
- Scope and expected behavior: Reassess the three local branches that were
  outside the original 27-branch inventory. Classify each as a duplicate
  historical record, reusable reference, or unresolved design input. Do not
  merge branch content, implement code, or delete branches in this phase.
- Specifications and files inspected: ADR-0214; LISS-0453/WP-0116 inventory;
  `docs/architecture/open-work-register.md`; ADR-0189, ADR-0212, ADR-0213;
  current `AGENTS.md` and `CLAUDE.md`; the branch tips and deterministic
  `git cherry`/file comparisons listed below.
- Component boundaries, ports/adapters, and VO/DTO candidates when applicable:
  Not applicable to this documentation-only inventory. The reassessment
  preserves the Kernel/QPU boundary and does not propose a new port or
  implementation boundary.
- Applicable constraints: physicist mental model and blackboard spelling are
  primary; ideal meaning is distinct from finite realization; historical
  branches are not direct merge candidates; implementation requires a current
  Issue/WP/Spec/ADR and typed phase approval.
- Decisions, assumptions, and unresolved ambiguities: a capability already
  represented by the current canonical documents is a `duplicate` even when
  the historical branch has non-equivalent commit IDs. Mixed-scope code is a
  `reference` until its contents are split and re-authorized under current
  Issues. Deletion remains a separate explicit operation.
- Included and omitted AI context: included only branch tips, changed-file
  inventories, current canonical documents, and accepted policy records;
  omitted unrelated historical branch bodies and hidden model reasoning.
- Task routing (model/assistant/tool): deterministic Git inspection plus
  primary-agent design analysis; no external model or provider is used.
- Input/output evidence contract when AI output is involved: no AI-generated
  factual output is used as authority; every classification is tied to a
  branch tip and current repository path.
- Independent review lenses selected and why: contract and acceptance
  completeness (1), architecture and boundary integrity (2), source-to-domain
  fidelity (3), realization/fail-closed behavior (6), migration/regression
  safety (7), phase/approval discipline (8), evidence/context hygiene (9),
  canonical authority and implementation reality (10). These lenses cover
  both the blackboard/finite-realization rule and safe branch disposition.
- Verification plan: `git diff --check`; verify the current branch is not
  `main`; retain all branch tips until this design record is reviewed; any
  later deletion must name the exact branches and be separately approved.

## Deterministic inventory

Base: `main` at `c781b6ae`.

| Branch | Tip | Evidence | Disposition | Reason |
|---|---|---|---|---|
| `codex/adr-quantum-mental-model` | `e87937ea` | `git cherry main` shows four historical canonicalization/mental-model commits and one equivalent alias commit; current main contains ADR-0189, WP-0092/spec follow-up, and the alias regression test. | `duplicate` | The branch is a pre-canonicalization history. Its current capability is represented by authoritative main documents and tests. No source-to-physics or finite-realization behavior should be ported directly. |
| `feature/liss-0195-host-mc-finite-inject` | `835eef59` | Tip is labelled as LISS-0195 but its final commits implement WP-0063 polynomial operator fusion; it also carries host-Monte-Carlo and SI-residual material. `git diff` against `feature/wp-0063-poly2-fusion` shows mixed additional scope. | `reference` | This is a mixed historical bundle, not a coherent LISS-0195 unit. Poly2 fusion and host-MC finite injection have separate physics/realization boundaries and require current acceptance specifications before any selective port. |
| `process/meaning-preservation-operating-gate` | `995d3bb1` | Adds an older operating-contract gate and review trace. Current main already carries the physicist-first, ideal-vs-finite, provenance, fail-closed, and approval rules through AGENTS/CLAUDE plus ADR-0212/0213 and the LISS-0449–0452 records. | `duplicate` | The policy intent is already canonicalized in current operations and architecture records. Directly merging the historical contract would create competing instruction authorities. |

## Disposition boundary

- `duplicate` does not mean the historical branch was useless; it means its
  intended authority is already represented by current main. No selective port
  is justified from these two branches based on this inventory alone.
- `reference` is retained. If WP-0063 or LISS-0195 work is reopened, create or
  update a current Issue/WP/Spec and preserve the blackboard equation, ideal
  meaning, explicit finite realization, and QPU rejection boundary separately.
- No implementation approval, phase approval, technology approval, or branch
  deletion approval is granted by this record.

## Next gate

Review this classification. After explicit approval, the two `duplicate`
branches may be deleted if no worktree depends on them. The mixed
`feature/liss-0195-host-mc-finite-inject` branch remains until a current
requirement authorizes a split design or confirms retirement.
