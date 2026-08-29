# WP-0090: Documentation canonicalization and archive compression

| Field | Value |
|---|---|
| Status | **LISS-0473 and LISS-0474 classifier slices complete — current-main compaction batch not authorized** |
| Branch | `docs/wp-0090-reassessment` |
| Scope | Documentation inventory, versioned baseline, cross-artifact compression, canonical-page consolidation, and source-history routing |
| Implementation permission | Granted for documentation-only compaction by Adjudicator direction |
| Baseline tag | `docs/pre-canonicalization-2026-08-03` → `8663ba7` |
| Requested by | Adjudicator direction, 2026-08-03 |
| Follow-up Issue | [LISS-0473](../issues/LISS-0473-documentation-compression-classifier.md) |

[LISS-0473](../issues/LISS-0473-documentation-compression-classifier.md) and
[LISS-0474](../issues/LISS-0474-documentation-compression-maintenance.md) are
complete after their review packets. The remaining follow-up is a separately
authorized deletion/compaction batch; no deletion is authorized by this WP.

## Design Note

- **Target behavior:** Reduce the number of documents a developer must read to
  understand current decisions and open work, while preserving historical
  decisions, review evidence, and the pre-compression repository state.
- **Current inventory:** the baseline and current counts are generated in
  `documentation-compression-map.md`; the map is the authoritative inventory
  for this batch. The current-main refresh is recorded in
  `docs/collaboration/traces/2026-08-28-wp-0090-current-main-reassessment.md`.
- **Phase to execute:** documentation-only implementation and deterministic
  review. No language/runtime behavior or test behavior is in scope.
- **Context included:** `AGENTS.md`, `docs/architecture/agent-quickstart.md`,
  `docs/architecture/implementation-readiness.md`,
  `docs/architecture/README.md`, `docs/architecture/open-work-register.md`,
  `docs/collaboration/doc-audit-2026-07-23.md`,
  `docs/work-plans/WP-0077-docs-hygiene-0212-0216.md`, and the current file
  inventory.
- **Context omitted:** Source code, tests, examples, private data, provider
  credentials, and the full contents of historical Issues/ADRs/traces. They
  are not needed for the design intake.
- **VO/DTO candidates:** None. The proposed metadata is document front matter
  or a small index table, not runtime data.
- **Ports/adapters involved:** None.
- **Suggested task routing:** Deterministic inventory and link checks; strong
  reasoning review for canonical-document boundaries and archive policy.
- **Input/output/reasoning contract:** Inventory output must be reproducible
  from repository paths; every consolidation mapping must name its source
  files, destination canonical file, retained decision/open-work fields, and
  archive rationale. No unverified semantic rewrite is accepted.
- **Resolved direction:** historical Issue, Work Plan, and Trace files are
  deleted after their entries are recorded in the central compression map;
  unresolved Issues remain full; ADRs and normative specs remain full source
  records.

## Proposed document model

1. **Entry layer (small and current):** one developer-facing index that links
   to the current language specification, current architecture principles,
   current open-work register, current collaboration rules, and the archive
   policy. This is the only mandatory starting point.
2. **Canonical decision layer:** one current page per theme, containing only
   current rules, accepted decisions, compatibility constraints, and links to
   the ADRs that provide the immutable decision record. Candidate themes are
   language surface/semantics, runtime/backend boundaries, developer workflow,
   and documentation policy.
3. **Canonical open-work layer:** `open-work-register.md` remains the single
   current task/status register. Completed rows are compressed to a short
   outcome and historical reference instead of repeating implementation
   narratives.
4. **Evidence layer:** only evidence that is still needed to explain a live
   decision, an unresolved issue, a compatibility constraint, or a review
   boundary remains in the current tree. The source record is referenced by
   `source_tag`, `source_commit`, and `source_path`; it is not duplicated as a
   second narrative.
5. **Git history:** an original Issue, Work Plan, or Trace may be deleted when
   its useful content has been extracted and it has no independent current
   obligation. The compression index retains the immutable baseline tag, full
   source commit hash, original path, and canonical destination. `git show
   <tag>:<source_path>` recovers the original.

## Safety rules

- Create an annotated baseline tag before any bulk move or rewrite. The tag
  must point to the current pre-compression commit and be recorded in the
  work-plan and PR description.
- The baseline tag is the recovery mechanism; keeping every historical file in
  the current tree is not required. Deletion is allowed only after a mapping
  row records the full source commit hash and extraction destination.
- Never delete a source record that contains a still-live decision, an open
  obligation, a required acceptance boundary, a unique compliance/process rule,
  or evidence needed to interpret a current specification.
- A source record may be removed from the current tree when it is only a
  superseded narrative, duplicated status prose, completed execution detail,
  or a trace whose facts are already captured in the canonical decision/open-
  work record.
- Do not renumber ADRs, Issues, work plans, or trace identifiers.
- Do not silently rewrite accepted decisions. A consolidation may summarize a
  decision, but the original record and its status must remain linkable.
- Preserve inbound links where practical. When a source file is deleted, use a
  machine-checkable mapping table and update current references; redirect stubs
  are not created.
- Keep generated inventories and archive indexes deterministic and reviewable.

## Acceptance criteria for the implementation batch

- A version tag identifies the exact pre-compression repository state.
- A developer can reach all current normative documents from one entry page.
- Each consolidated theme has one named canonical page and an explicit source
  mapping.
- Open work is represented once in the canonical register; repeated status
  prose is removed from current entry documents.
- Every compressed ADR, Issue, Work Plan, and Trace has an extraction row with
  its original path, baseline tag, full source commit hash, and canonical
  destination.
- Historical records judged to have no remaining independent meaning are
  deleted after their index pointers are recorded; only explicitly safe
  records may be removed. Original contents remain recoverable through the tag
  and commit.
- Markdown links, repository documentation checks, and the existing spec
  verification suite pass.
- A before/after inventory records file counts and the number of canonical
  entry points.

## Ordered execution plan

### Phase A — Freeze and inventory

1. Commit this reviewed plan.
2. Create an annotated baseline tag, for example
   `docs/pre-canonicalization-2026-08-03`, on the exact pre-compression commit.
3. Generate a deterministic inventory of ADR, Issue, Work Plan, Trace, and
   current architecture/spec entry points with status and inbound-link counts.
4. Classify each document as `retain-canonical`, `extract-and-remove`,
   `retain-evidence`, or `unresolved-review`.

### Phase B — Canonical extraction

1. Create the developer entry page and documentation policy.
2. Consolidate current decisions by theme, preserving normative wording and
   explicit source references.
3. Consolidate open work into the canonical register; retain only the current
   status, next action, dependency, and source reference.
4. Create a compression map containing `source_path`, `source_commit`,
   `source_tag`, `destination`, `classification`, and `reason`.

### Phase C — Remove low-value duplication

1. Remove only documents classified `extract-and-remove`.
2. Update links from current documents to the central compression map. Do not
   create redirect stubs for deleted records.
3. Leave `unresolved-review` files untouched and list them for human review.

### Phase D — Deterministic review

1. Verify every compression-map source with `git cat-file` and recoverability
   checks against the baseline tag.
2. Run Markdown link checks, repository documentation checks, spec verification,
   and `git diff --check`.
3. Produce a before/after report, review the unresolved set, and stop for final
   Adjudicator review.

### Phase E — PR and merge

1. Open one documentation-only PR containing the plan, baseline tag reference,
   canonical documents, compression map, and before/after report.
2. Merge only after CI is green and the final review confirms that no current
   decision or open obligation was lost.
3. Verify the merged `main` page and the baseline recovery commands.

## Out of scope

- Changing Staqex language semantics, syntax, compiler behavior, or examples.
- Changing ADR decisions or issue status solely to make the index shorter.
- Deleting Git history, force-pushing, or rewriting published commit history.
- Choosing a documentation site generator, database, or external knowledge
  base.

## Current-main reassessment (2026-08-28)

The original implementation branch predates the current `main` and contains
unrelated compiler changes, so it is not a safe merge source. The current tree
already contains the entry page, decision register, documentation policy, and
compression map. A fresh inventory reports 1,022 `docs/` files, 983 Markdown
files, 37 ADRs, 239 Issues, 81 Work Plans, and 234 Traces.

The existing candidate classifier reports 138 historical candidates, but this
set includes current-generation completed Issues and Work Plans that remain
required acceptance or review evidence. No deletion batch is therefore
authorized by this reassessment. The classifier must be corrected and its
output separately reviewed before any further removal.

## Approval request

Architecture approval is requested for the four-layer model, the
`extract-and-remove` classification, the baseline-tag/commit recovery rule,
and the ordered execution plan. After approval, Phase A may create the tag and
inventory; Phase B–D may proceed only within the listed scope, with final
Adjudicator review required before Phase E merge.
