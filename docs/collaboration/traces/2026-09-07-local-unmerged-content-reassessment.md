# Local unmerged content reassessment — 2026-09-07

[DESIGN CHECK]
- Scope and expected behavior: Reassess the remaining local branches after
  the approved local integrations. Preserve useful requirements and source
  evidence while avoiding stale snapshots, competing canonical documents, and
  duplicate operating authorities.
- Specifications and files inspected: current `main`, branch tips, existing
  branch inventory/reassessment traces, current S02 specifications, the
  documentation canonicalization policy, the semantic meaning-preservation
  specifications, and the current evaluator/parser implementation.
- Applicable constraints: main's current specification and implementation are
  authoritative; historical status must not be revived; deleted historical
  records must not be restored; provider/QPU and operating-rule boundaries
  require their own acceptance decisions.
- Decisions: use current main directly when the capability is already present;
  selectively reimplement only when a current requirement identifies a gap;
  retain mixed or conflicting branches as references until a new scoped Issue,
  WP, and acceptance specification exists.
- Verification plan: compare branch-specific claims with current source and
  canonical documents; run `git diff --check` and Python compilation after
  repository changes.

## Integration result

The following approved local merges are now part of `main`:

| Series | Merge commit | Result |
|---|---|---|
| LISS-0476–0486 semantic consumers | `87cc1fea` | New bounded artifacts retained; later canonical runtime and conformance behavior from main preserved. |
| LISS-0088 planner | `6e702274` | Planner implementation and integrated test retained; deleted historical Issue not restored. |
| LISS-0089 optimization | `5e8a8740` | Optimization implementation and test retained; deleted historical Issue not restored. |
| LISS-0090 measurement planning | `5178aadc` | Measurement planning implementation and test retained; deleted historical Issue not restored. |
| State-transformer review lineage | `f598d616` | Existing current H1 versions won duplicate conflicts. |
| WP-0069 operations review | `75574a8f` | Current Issue statuses won; new ADR/Issue artifacts absent from main were added. |

## Remaining local branches

| Branch | Disposition | Analysis |
|---|---|---|
| `codex/drug-discovery-benchmark-design` | Reference | Its project-call parser fix is already in `compiler/staqex/parser.py`; its S02 surface is represented by the accepted ADR 0190, S02 specifications, WP-0093, and current tests. The branch also mixes unrelated showcase and fixture rewrites, so it is not a safe merge unit. |
| `codex/s02-ebola-benchmark-design` | Reference / superseded alternative | It proposes a geography-grounded Ebola S02 under a separate specification and WP-0093 name. The current canonical S02 is the indication-agnostic drug-discovery benchmark; direct merging would create competing S02 authorities. Reimplementation requires a new Issue/WP/spec and explicit scope. |
| `docs/decision-theme-canonicalization` | Superseded snapshot | Current main already contains the decision-theme surface and canonical decision register. Direct merge would reintroduce old ADR topology and deletions. |
| `docs/documentation-canonicalization` | Superseded snapshot | Current main already contains the documentation policy, compression map, and decision register. The branch is an older broad compaction snapshot. |
| `docs/documentation-canonicalization-clean` | Superseded alternative | It is a second historical cleanup snapshot with a different base; use the current canonicalization policy rather than merging its tree wholesale. |
| `feature/liss-0195-host-mc-finite-inject` | Mixed reference | The tip is labelled for Host-MC finite injection but its unique implementation is polynomial fusion plus mixed historical material. Host-MC and polynomial fusion have separate realization boundaries; no current gap justifies porting it. |
| `feature/wp-0063-poly2-fusion` | Already implemented / historical reference | Polynomial fusion behavior and tests are present in current main; the branch's historical ADR/WP files are represented by the compression map and current hardening Issue. |
| `process/meaning-preservation-operating-gate` | Duplicate operating authority | Current AGENTS/CLAUDE and semantic/QPU documents already carry the meaning-preservation and fail-closed rules. Directly merging this branch would create a competing instruction authority. |

## Reimplementation decision

No reimplementation is opened by this reassessment. The current main already
contains the actionable source changes identified in the remaining branches.
Any future revival must first split the requirement into a current Issue/WP,
record the blackboard-to-semantic and semantic-to-finite boundaries in a
specification, and obtain the applicable phase/architecture approval.

## Verification

- `git diff --check`: passed.
- Python `compileall` for `compiler/`: passed.
- The current worktree remains on `main` and clean after the merge commits.
