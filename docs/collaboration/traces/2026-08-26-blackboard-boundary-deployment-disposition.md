# PR #574 asset disposition: blackboard, boundary, and deployment reorganization

## Evidence

- Source branch: `codex/adr-quantum-mental-model`
- Source tip: `e87937ea3da73beb840652fb308b31072f3bd9c0`
- Base: `origin/main` at design intake
- PR: #574, currently open and conflicted; not merged
- Deterministic inventory: 6 commits, 318 changed files, 1,790 additions,
  13,559 deletions, and a dirty merge state against `main`.

## Disposition rule

The branch is an evidence source only. No commit is accepted as an authority
because it exists on the branch. Each asset must be mapped to the current
canonical Issue, Spec, WP, or ADR before migration.

| Asset group | Evidence | Disposition | Reason / next action |
|---|---|---|---|
| Scientific aliases and parser/runtime support | `scientific_vocabulary.py`, parser/evaluator changes, alias Red test | Selective port candidate | Re-check current parser/runtime authority and preserve source spelling; create a bounded Issue/Spec slice before code migration. |
| Quantum mental-model follow-up documents | ADR 0189 / WP-0092 / H1 follow-up material | Preserve selectively | Current accepted and shipped portions must be compared with `main`; retain only unresolved, still-authoritative design gaps. |
| Decision-theme canonicalization | DEC theme documents, register, compression map, historical ADR deletions | Do not re-merge wholesale | Current `main` already contains this design family; use duplicate evidence and current canonical documents. |
| Agent and collaboration instruction edits | `AGENTS.md`, `CLAUDE.md`, quickstarts, traces, reviews | Authority check required | Keep only changes that are current contract corrections; never reintroduce stale mirrored or historical text by conflict resolution. |
| Parser/evaluator conflict hunks | `compiler/staqex/parser.py`, `compiler/staqex/runtime/evaluator.py` | Stop for feature-level review | Conflicts touch existing behavior and cannot be resolved mechanically without semantic regression analysis. |
| H1 theory/basis/realize diagnostics | H1 docs, AST/diagnostic changes, tests | Compare against current shipped slices | Retain only missing acceptance evidence; do not duplicate already shipped LISS-0325/LISS-0326 behavior. |
| Broad historical ADR removals | `docs/architecture/adr/0001..0186` deletions | Reject as merge material | Historical canonicalization is already represented on current `main`; recovery remains through the documented baseline. |
| New H1 acceptance specification | `staqex-v1-quantum-mental-model-follow-up.md` | Preserve as design input | Extract a small source-preserving acceptance slice; no new keyword or implementation follows automatically. |
| Tests and CI edits | CI workflow and Red tests | Rebase-aware review | Re-run against current CI contract; preserve only tests that assert current accepted behavior and do not mask conflicts. |

## Required evidence before any migration

1. `git cherry` and path-level duplicate analysis against current `main`.
2. Current canonical Issue/Spec/WP/ADR mapping for every selected asset.
3. Negative evidence that legacy DTOs, caller-injected objects, soft
   diagnostics, or AST-pattern shortcuts cannot create executable meaning.
4. Projection evidence covering semantic payload and emitted instruction
   payload, not source node identity alone.
5. Independent read-only review of the disposition table.

## Current conclusion

PR #574 must not be merged or conflict-resolved as one batch. The appropriate
path is selective extraction into WP-0117 and subsequent bounded Issues.
