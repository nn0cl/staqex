# LISS-0453 Unmerged Branch Inventory and Initial Disposition

- Governing policy: ADR 0214 (accepted in PR #568)
- Inventory base: `main` at `75718b57`
- Scope: 27 local branches whose remote tracking refs are gone and whose tips
  are not ancestors of `main`; worktree-held branches are listed separately.
- Method: deterministic `git rev-list`, `git cherry`, `git merge-base`,
  `git merge-tree`, changed-file inspection, and current canonical-document
  comparison.
- Implementation permission: not granted
- Deletion permission: granted by the Adjudicator after PR #569 was merged;
  only branches explicitly classified below as `duplicate` are in scope.

## Disposition vocabulary

- `duplicate`: the capability or record is already represented by current
  `main`; no selective port is needed.
- `reference`: contains historical design or implementation reasoning that may
  inform a future current Issue/WP/Spec, but must not be merged directly.

## Initial disposition

| Branch | Tip | Cherry evidence | Disposition | Rationale |
|---|---:|---:|---|---|
| `codex/ascii-quantum-notation-design` | `7b90e103` | 2 unique | duplicate | ASCII source policy and tensor hardening are already shipped in current `main`; branch mixes old migration context. |
| `codex/completion-status-preflight` | `573f3907` | equivalent | duplicate | Commit is already represented in `main`. |
| `codex/drug-discovery-benchmark-design` | `b173c65f` | 2 unique, 1 equivalent | reference | Mixed parser/S02/showcase changes; current S02 numerical migration has a separate boundary and requires fresh design. |
| `codex/liss-0082-completion-sync` | `82347284` | equivalent | duplicate | Completion record is already represented in current canonical documents. |
| `codex/liss-0088-ci-status-fix` | `4dfecb32` | equivalent | duplicate | No distinct current design remains. |
| `codex/liss-0088-design` | `d0b72904` | 6 unique | reference | Historical Algorithm Planner design; current records are compressed and no direct merge authority remains. |
| `codex/liss-0089-design` | `414b198d` | 6 unique | reference | Historical exact-circuit optimization design; requires a new concrete requirement before reopening. |
| `codex/liss-0090-completion-audit` | `b743a323` | equivalent | duplicate | Audit wording is represented by current completion records. |
| `codex/liss-0090-completion-audit-final` | `461fe581` | equivalent | duplicate | Audit wording is represented by current completion records. |
| `codex/liss-0090-integrated-plan` | `98007b60` | 6 unique | reference | Historical measurement-grouping plan; no direct merge into the canonicalized current tree. |
| `codex/quantum-symbol-aliases` | `d7c0c8c8` | equivalent | duplicate | Current source policy and symbol decisions already supersede this branch. |
| `codex/s0-showcase-cleanup` | `15db23c2` | equivalent | duplicate | S0 canonical showcase state is already in `main`. |
| `codex/s02-ebola-benchmark-design` | `eec60b6a` | 1 unique | reference | Scientific benchmark design may inform a future S02 Issue, but numerical migration and solver work remain separately gated. |
| `codex/state-transformer-language-review` | `da32c5a6` | 2 unique, 1 equivalent | reference | H1 boundary reasoning is useful historical context; current semantic consumer work is authoritative. |
| `codex/wp0092-doc-closeout` | `0d6de1d4` | equivalent | duplicate | Observation-type implementation is already represented in `main`. |
| `codex/wp0092-observation-red` | `531fa102` | equivalent | duplicate | Observation rejection contract is already represented in `main`. |
| `codex/wp0092-observation-types` | `abaa7cb6` | equivalent | duplicate | Observation type contract is already represented in `main`. |
| `codex/wp0094-completion-packet` | `060d7edc` | equivalent | duplicate | ASCII tensor completion record is already represented in `main`. |
| `codex/wp0094-tensor-hardening` | `8174f162` | 6 unique | duplicate | Tensor hardening shipped in PR #339; this branch is an obsolete pre-merge history. |
| `docs/decision-theme-canonicalization` | `5642a69b` | 4 unique | reference | Historical canonicalization work; current ADR 0188/theme pages are authoritative. |
| `docs/documentation-canonicalization` | `54060a38` | 6 unique, 1 equivalent | reference | Broad historical compaction branch; direct merge would reintroduce stale tree topology. |
| `docs/documentation-canonicalization-clean` | `3a26d7ea` | 4 unique | reference | Alternate historical cleanup snapshot; use current canonicalization policy instead. |
| `docs/documentation-canonicalization-delete` | `0bccf76c` | equivalent | duplicate | Historical deletion record is already represented by current compression-map policy. |
| `docs/trace-topic-consolidation` | `42e76708` | equivalent | duplicate | Trace consolidation is already represented in current documentation. |
| `docs/wp-0069-operations-review-intake` | `e1fc0740` | 6 unique | reference | Historical operations intake; settled records and current operating contract supersede direct merge. |
| `feature/wp-0063-poly2-fusion` | `ac1fce26` | 2 unique | reference | Potential operator-fusion reasoning, but no current ship ADR or demonstrated requirement authorizes revival. |
| `fix/wp-0069-operations-review` | `41363663` | 7 unique | reference | Broad historical bug/operations bundle; current fixes and records must be revalidated individually. |

## Worktree-held branches

These are not unmerged candidates: their tips are already merged into `main`,
but their worktrees remain active and require separate cleanup:

- `codex/liss-0082-completion-audit` → `/private/tmp/qpex-liss-0082-slice-e`
- `feature/liss-0082-slice-d-red-codex` → `/private/tmp/qpex-liss-0082-slice-d`

## Next disposition gate

The inventory contains 15 `duplicate` branches (the original count of 13
omitted `docs/documentation-canonicalization-delete` and
`docs/trace-topic-consolidation`). After PR #569 was reviewed and merged, the
Adjudicator approved deletion of those 15 local branches, provided no worktree
depends on them. The 12 `reference` branches remain until the Adjudicator
confirms whether each historical design has a current requirement; any reuse
must create or update a current Issue/WP/Spec and, where required, ADR before
implementation. No branch is a merge candidate from this inventory alone.

## Correction record

- 2026-08-25: corrected the duplicate count from 13 to 15 and recorded the
  two omitted duplicate rows already present in the table.
- 2026-08-25: recorded explicit deletion approval after PR #569 merge.
