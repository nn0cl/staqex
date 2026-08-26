# PR #574 asset disposition: blackboard, boundary, and deployment reorganization

## Evidence

- Source branch: `codex/adr-quantum-mental-model`
- Source tip: `e87937ea3da73beb840652fb308b31072f3bd9c0`
- Base: `origin/main` at design intake
- PR: #574, currently open and conflicted; not merged
- Exact path manifest: `2026-08-26-pr-574-path-disposition-manifest.md`
- Deterministic inventory: 6 commits, 318 changed files, 1,790 additions,
  13,559 deletions, and a dirty merge state against `main`.
- Merge-base: `9ca049f6d27af871a8ce02e0ba8df87c61efca8c`
- `git cherry origin/main e87937ea`: four `+` commits and one `-` commit;
  the `-` commit is the scientific-alias patch equivalent already present on
  `main`.

### Source commit inventory

| SHA | Subject | `git cherry` | Representative changed paths | Canonical owner / classification | Disposition |
|---|---|---:|---|---|---|
| `42e76708` | consolidate trace records by topic | `+` | `docs/architecture/adr/0187*`, `docs/architecture/trace-topic-register.md`, collaboration traces | WP-0090 / documentation canonicalization; distinct documentation proposal | compare to current canonical traces; selective extraction only |
| `1c713ebc` | introduce decision theme reading surface | `+` | `docs/architecture/decision-themes/dec-0001..0007`, decision registers | ADR 0188 / WP-0091; overlaps canonicalization already on main | do not re-merge; retain current main authority |
| `3f71458d` | canonicalize decision themes and archive settled ADRs | `+` | `AGENTS.md`, `CLAUDE.md`, `docs/architecture/adr/0001..0186`, decision-theme docs | ADR 0188 / WP-0091; overlaps canonicalization already on main | do not re-merge; recover history from documented baseline |
| `227b65a5` | sync decision canonicalization with main | `+` | merge synchronization; no first-parent path delta | WP-0091 synchronization evidence | historical evidence only; no cherry-pick |
| `5642a69b` | validate decision theme surface | `+` | `.github/workflows/ci.yml` | current CI contract; validation proposal | compare with current CI; no blind migration |
| `e87937ea` | add compact scientific symbol aliases | `-` | `compiler/staqex/{parser.py,runtime/evaluator.py,scientific_vocabulary.py}`, alias test, ADR 0189/WP-0092 docs | ADR 0189 / WP-0092; patch-equivalent to `f21be487` on current main | already canonical; do not port again |

The table is a disposition inventory, not an approval to merge any listed
commit.

## Disposition rule

The branch is an evidence source only. No commit is accepted as an authority
because it exists on the branch. Each asset must be mapped to the current
canonical Issue, Spec, WP, or ADR before migration.

| Asset group | Evidence | Disposition | Reason / next action |
|---|---|---|---|
| Scientific aliases and parser/runtime support | `scientific_vocabulary.py`, parser/evaluator changes, alias Red test; `git cherry` marks `e87937ea` as `-`; current `main` contains equivalent `f21be487` | Main-equivalent / already canonical | Do not port again. Split any residual alias differences from the equivalent patch and map only residual work to the existing scientific-lexicon authority. |
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
   The current baseline is `origin/main=c179a2c7`, merge-base `9ca049f6`,
   with source commits `42e76708`, `1c713ebc`, `3f71458d`, `227b65a5`,
   `5642a69`, and `e87937ea` recorded in the commit inventory below.
2. Exact path-level selected/rejected manifest:
   `2026-08-26-pr-574-path-disposition-manifest.md`; current canonical
   Issue/Spec/WP/ADR mapping for every selected asset.
3. Negative evidence that legacy DTOs, caller-injected objects, soft
   diagnostics, or AST-pattern shortcuts cannot create executable meaning.
4. Projection evidence covering semantic payload and emitted instruction
   payload, not source node identity alone.
5. Independent read-only review of the disposition table.

## Current conclusion

PR #574 must not be merged or conflict-resolved as one batch. The appropriate
path is selective extraction into WP-0117 and subsequent bounded Issues.

## Independent review iteration 2

The fresh read-only reviewer returned **NOT READY** with no P0 and seven P1
findings. All seven are accepted as design-preserving corrections under the
existing ADR/Spec boundaries:

1. Scientific Semantic IR is the canonical source-derived authority; Physics
   IR, Quantum Semantic IR, and QASM/QPU IR are projections.
2. H1 maps to the existing H1-01–H1-06 specifications and canonical dispatch;
   it does not create a second acceptance authority.
3. The scientific-alias asset is main-equivalent, not a new selective port.
4. The six source commits, SHA set, merge-base, cherry result, and path-level
   classification must be reproducible.
5. Exact/symbolic inspection is distinct from finite `Realize` and cannot
   perform hidden finiteization.
6. Executable projection fingerprints must cover instruction payload,
   provenance boundary, symmetric comparison, and terminal `Measure`.
7. Deployment is deferred for H1; any future delivery port must define
   identity, failure, retry/rollback, partial-delivery, and no-mutation rules.

The corrections are recorded in WP-0117 and the boundary matrix. No finding
authorizes Phase 1, implementation, provider selection, or deployment work.
