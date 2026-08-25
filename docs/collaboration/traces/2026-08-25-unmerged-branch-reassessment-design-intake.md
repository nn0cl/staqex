# Unmerged Branch Reassessment Design Intake

- Current phase: Architecture Path / design intake
- User scope approval: proceed with policy design and branch reassessment plan
- Implementation permission: not granted
- Deletion permission: not granted by this design intake

## [DESIGN CHECK]

- Scope and expected behavior: establish a physicist-first, evidence-backed
  lifecycle for unmerged branch assets before selective reuse or deletion.
- Specifications and files inspected: `AGENTS.md`,
  `docs/architecture/agent-quickstart.md`,
  `docs/collaboration/ai-human-scheme.md`,
  `docs/architecture/ai-request-routing.md`,
  `docs/collaboration/model-tool-capability-matrix.md`,
  `docs/collaboration/independent-review-perspectives.md`,
  `docs/architecture/open-work-register.md`, and current branch inventory.
- Component boundaries, ports/adapters, and VO/DTO candidates when applicable:
  not applicable; this is a process and design-asset boundary.
- Applicable constraints: blackboard spelling is primary; ideal meaning and
  finite/QPU realization remain separate; no phase skipping; no implementation
  without reviewed acceptance specification; no direct revival of settled rows.
- Decisions, assumptions, and unresolved ambiguities: ADR 0214 is proposed;
  Architecture approval is unresolved. A useful branch may require a new
  Issue/WP/Spec/ADR rather than a merge.
- Included and omitted AI context: included current operating rules, canonical
  register, review lenses, and deterministic branch metadata; omitted private
  data, secrets, provider logs, and unrelated source trees.
- Task routing (model/assistant/tool): strong reasoning for architecture
  policy; deterministic Git inspection for inventory and duplicate/conflict
  evidence.
- Input/output evidence contract when AI output is involved: output must cite
  branch name, source commit, current authority, disposition, and deterministic
  verification; no hidden reasoning is recorded.
- Independent review lenses selected and why: contract completeness,
  architecture/boundary integrity, source-to-domain fidelity, realization and
  fail-closed behavior, migration/regression safety, phase/approval discipline,
  evidence hygiene, and canonical authority.
- Verification plan: validate the new documents, run the branch inventory,
  conduct independent review, obtain Architecture approval, then process
  redesign candidates one at a time.

## Initial observation

The remaining unmerged branches are stale relative to current `main`; several
contain equivalent commits, while others are historical design candidates.
None is authorized for direct merge by this intake.

## Next gate

Fresh independent review of this design packet, followed by typed Architecture
approval or correction. Do not delete the remaining unmerged branches until
their disposition has been recorded under the accepted policy.
