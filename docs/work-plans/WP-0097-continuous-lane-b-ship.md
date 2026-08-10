# WP-0097: Continuous Lane B ship (`Continuous<T>` type, weight/mask, finiteize overload)

| Field | Value |
|---|---|
| Status | **complete** (2026-08-10) — LISS-0399/0400/0401 all Green/Refactor complete; full regression 1440 passed; awaiting post-review |
| Purpose | Implement the Lane B ship shape [ADR 0204](../architecture/adr/0204-continuous-lane-b-type-world.md) (Accepted 2026-08-10) authorized: `Continuous<T>` type + hard gates, `ContinuousFieldPort`, `weight`/`mask` ops, `finiteize` Continuous-argument overload |
| Parent program | Reopened backlog — "Continuous PDF / Monte Carlo" (`CLAUDE.md` Current Open Topics); Adjudicator selected this item first (2026-08-10), "上から" ordering for the remaining reopened-backlog items |
| Prior wave | ADR 0126 (design boundary) → ADR 0162 (Host/Bridge-first) → ADR 0185 / LISS-0313 (Lane A `finiteize`, shipped) → Lane B expressiveness scenarios (LISS-0315–0319, frozen baseline) → ADR 0204 (this ADR, ship shape, Accepted) |
| Review input | ADR 0204's own Consequences section ("likely a multi-Issue batch... a Feature Plan investigation... would do that separately") |
| Branch (docs intake) | `docs/wp-continuous-lane-b-batch-investigation` |
| Execution branch (when approved) | `batch/wp-0097-continuous-lane-b-ship` (or per-Issue feature branches, per Adjudicator preference at approval time) |
| Batch record | [execution-batch-wp-0097.json](../collaboration/reviews/execution-batch-wp-0097.json) — **`status: approved_for_execution`** |
| Batch proposal | [2026-08-10-wp-0097-batch-proposal.md](../collaboration/reviews/2026-08-10-wp-0097-batch-proposal.md) |

## One-line goal

> Ship exactly the ADR 0204 MVP surface — `Continuous<T>` + hard gates,
> `field_from_host`, `weight`/`mask`, and a `finiteize` overload — so
> `CH-field-compose` can move off its frozen **weak** score, without
> touching `CH-field-fork`, `CH-field-theory`, the S01 spine, or any
> unrelated reopened-backlog item.

## Product rules (binding)

| Rule | Meaning |
|---|---|
| Type gate | `Continuous` never reaches `measure`/`evolve`/Joint/QPU — compiler-enforced, not just documented |
| Single consumption | A `Continuous` root is consumed by `finiteize` at most once in this batch (`CH-field-fork` out) |
| No spine rewrite | `main_disaster_response.sqx` and every other shipped example stay untouched |
| No new numerics | `weight`/`mask`/`finiteize`-backend reuse already-shipped Host bucketing (ADR 0163); no new math is invented |
| Honesty | Lane A `finiteize(lo,hi,n,samples[,seed])` stays valid and unchanged; this batch is additive only |

## Issue rows

| Order | ID | Title | Path | Depends | Status |
|---|---|---|---|---|---|
| 1 | [LISS-0399](../issues/LISS-0399-continuous-type-hard-gates.md) | `Continuous<T>` type + `ContinuousFieldPort` + hard gates | Feature | ADR 0204 | **complete** |
| 2 | [LISS-0400](../issues/LISS-0400-continuous-weight-mask-ops.md) | `weight` / `mask` continuous ops | Feature | LISS-0399 | **complete** |
| 3 | [LISS-0401](../issues/LISS-0401-finiteize-continuous-overload.md) | `finiteize` Continuous-argument overload | Feature | LISS-0399, LISS-0400 | **complete** |

## Execution order and rationale

```text
LISS-0399 (type + port + hard gates + LINEAR introduce/discard)
        │
        ▼
LISS-0400 (weight / mask — needs a Continuous value to operate on)
        │
        ▼
LISS-0401 (finiteize overload — needs a composed chain to finiteize;
           closes the LINEAR consumption story LISS-0399 opened)
```

Strictly sequential — no parallel-eligible pair in this batch. Each Issue's
own tests need the previous Issue's shipped surface to exist (LISS-0400
cannot construct a `Continuous` value without LISS-0399's
`field_from_host`; LISS-0401 cannot meaningfully finiteize a multi-step
chain without LISS-0400's ops, and closes the discard-diagnostic story
LISS-0399 opened one-sided).

## Granularity rationale

| Split | Why |
|---|---|
| Type + port + gates together (0399) | Cannot test hard gates or LINEAR tracking without *some* producing operation; the smallest such producer (`field_from_host`) is trivial bookkeeping, so bundling avoids an untestable intermediate Issue |
| `weight`/`mask` together, not split (0400) | Two symmetric, near-identical Kernel-side bookkeeping ops (opaque handle composition + provenance); splitting would force two review cycles over near-duplicate code, same precedent as this session's LISS-0394/0395 DRY extractions |
| `finiteize` overload last, separate (0401) | Distinct component boundary (extends an already-shipped, already-tested Lane A surface) and closes a LINEAR story spanning two prior Issues — large enough and different enough in risk profile to warrant its own reviewable unit |
| Not one single Issue | Crosses TypeChecker, hir.py, a new port, evaluator Call dispatch, and an existing-surface extension — four distinct component boundaries; matches this session's established precedent of small, tightly-scoped Issues over one large one |

**Out of this WP:** `CH-field-fork` (dual finiteize), `CH-field-theory`
(Theory vocabulary unification), any S01 showcase `.sqx` wiring, live QPU
work, Joint rational mode, trait specialization, CUDA workers — all
separate reopened-backlog rows or explicitly deferred by ADR 0204 itself.

## Out of scope (program-wide)

- Any change to the S01 spine or other shipped examples.
- `CH-field-fork` / `CH-field-theory` (explicitly parked by the
  expressiveness scenarios doc and by ADR 0204 Decision 5/Non-goals).
- Live QPU, CUDA, Joint rational mode, trait specialization — unrelated
  reopened-backlog items.
- Cloud/HPC Monte Carlo SDK selection (ADR 0162 Non-goals, still standing).

## Verification (program, after approved Issues land)

```bash
python3 -m pytest -q
# Lane A regression guard specifically:
python3 -m pytest -q -k "finiteize or 0313"
```

**Expressiveness check (manual / review, after LISS-0401 Green):**

- [x] `CH-field-compose` (Lane B expressiveness scenarios doc §2A) can now
  be written in real Staqex source close to the Ideal form (§2A.6) — the
  shipped grammar is positional
  (`finiteize(continuous, lo, hi, n_bins[, seed])`), not the Ideal's
  named-argument sketch; the field/weight/mask chain itself matches §2A.6
  closely (`field_from_host`/`weight`/`mask` names and arities match the
  Ideal chalk exactly).
- [ ] Seat scoring in
  `docs/specs/staqex-v1-continuous-lane-b-expressiveness-scenarios.md` is
  updated in a follow-up docs-only Issue (not part of this batch) —
  intentionally not done here, per this WP's own scope boundary.

## Approval model

| Step | Approval |
|---|---|
| ADR 0204 | Architecture approval — **granted** 2026-08-10 |
| This WP + Issue files | Investigation approval — **granted** 2026-08-10 |
| Batch execution of LISS-0399–0401 | Batch approval — **granted** 2026-08-10; [execution-batch-wp-0097.json](../collaboration/reviews/execution-batch-wp-0097.json) `approved_for_execution` |
| Per-Issue Feature Red/Green | Covered by batch approval once granted; otherwise per-Issue Plan/Completion approval |

Historical note: the planning PR alone did not authorize implementation;
implementation began only after both Investigation approval and Batch
approval were granted and the JSON record was promoted to
`approved_for_execution` with a real `approval_commit`/`expires_at`.

## Success definition

WP closes when LISS-0399–0401 are all **complete** (or explicitly
**deferred** by Adjudicator), full regression passes, and Lane A
`finiteize` remains byte-for-byte unaffected for its existing grammar.
