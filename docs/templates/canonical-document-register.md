# Canonical Document Register

This is a target-owned navigation document, not an approval or implementation
authorization artifact. Copy it to
`docs/collaboration/canonical-document-register.md` and replace the examples.
Keep one row per topic and one Canonical path per topic.

| canonical_key | layer | status | entry_path | canonical_path | source_paths | owner |
| --- | --- | --- | --- | --- | --- | --- |
| `<topic-key>` | Entry | Current | `docs/<entry>.md` | `docs/<canonical>.md` | `docs/<source>.md` | `<team>` |

## Consolidation Ledger

Record every move or compression that must be recoverable from Git history.

| source_path | source_commit | source_tag | canonical_destination | classification | reason |
| --- | --- | --- | --- | --- | --- |
| `<old-path>` | `<commit>` | `<tag-or-empty>` | `<canonical-path>` | `<archive-or-compressed>` | `<reason>` |

## Rules

- `canonical_key` must be unique.
- `status` is `Current` or `Historical`.
- `layer` is `Entry`, `Canonical`, `Evidence`, or `Archive`.
- Current rows must point to a current Entry or Canonical document and at
  least one source path.
- This register does not replace an accepted specification, ADR, Issue, Work
  Plan, or Adjudicator approval. It only points to those agreement artifacts.
- Do not use this register for target secrets or private exports.
