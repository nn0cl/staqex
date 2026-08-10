# WP-0097 bounded-batch proposal (draft)

| Field | Value |
|---|---|
| Date | 2026-08-10 |
| Work plan | [WP-0097](../../work-plans/WP-0097-continuous-lane-b-ship.md) |
| Batch record | [execution-batch-wp-0097.json](execution-batch-wp-0097.json) |
| Status | **draft** — awaiting Adjudicator batch approval |
| Requested approval | bounded-batch |
| Implementation allowed by this doc alone | no |

```markdown
[DESIGN CHECK]
- Scope: file a bounded batch for the Continuous Lane B ship Issues
  LISS-0399–0401 under ADR 0204 (Accepted); document order, paths,
  invalidators, and approval recipe.
- Not in scope: Red/Green source edits; S01 spine/example wiring;
  CH-field-fork / CH-field-theory; any other reopened-backlog item.
- Inputs: ADR 0204 (2026-08-10, Accepted); Lane B expressiveness scenarios
  doc frozen baseline (LISS-0319); Host-proven weight/mask semantics
  (LISS-0317, field_compose_inject.py).
- Verification: JSON schema_version 1 fields; links resolve; status remains
  draft until Adjudicator promotes.
```

## 1. Why a batch

ADR 0204's own Consequences section names this as "likely a multi-Issue
batch, not one Issue" and explicitly defers sizing/ordering to a separate
Feature Plan investigation. Three Issues, strictly sequential, each
depending on the previous one's shipped surface — a single bounded batch
keeps the dependency chain and path/phase gates explicit without implying
scope beyond the ADR 0204 MVP.

## 2. Issue set and order

| Order | ID | Role |
|---|---|---|
| 1 | LISS-0399 | `Continuous<T>` type + `ContinuousFieldPort` + hard gates + LINEAR introduce/discard |
| 2 | LISS-0400 | `weight` / `mask` continuous ops |
| 3 | LISS-0401 | `finiteize` Continuous-argument overload; closes the LINEAR consumption story |

No parallel-eligible pair — see WP-0097's execution-order rationale for why
each Issue genuinely needs the previous one's surface to test against.

## 3. Path boundary (summary)

**In:** `compiler/staqex/typecheck.py`, `compiler/staqex/hir.py`,
`compiler/staqex/runtime/evaluator.py`, a new
`compiler/staqex/continuous_field.py` port + fake adapter, WP-0097 /
LISS-0399–0401 docs, the Lane B expressiveness scenarios spec, ADR
0204, open-work register, related tests.

**Out:** `examples/showcase/S01_quantum_disaster_response/**` (spine/example
wiring is a separate, later Issue), `compiler/staqex/host_monte_carlo.py`
(reused unchanged — editing its existing bucketing behavior invalidates
this batch), `CH-field-fork`/`CH-field-theory` scope, live QPU, Joint
rational mode, trait specialization, CUDA.

If any Issue discovers a genuine need to touch `host_monte_carlo.py`'s
existing bucketing behavior, or to solve `CH-field-fork` along the way:
**stop**; do not expand this batch silently.

## 4. Approval recipe (Adjudicator)

1. Review WP-0097 + Issues (LISS-0399–0401) + this proposal + JSON draft.
2. Optionally amend `issue_ids`, `allowed_paths`, or drop an Issue from the
   batch (none are parallel-eligible, so dropping the last Issue is the
   only partial-approval shape that preserves a coherent dependency chain).
3. On execution branch tip, set in `execution-batch-wp-0097.json`:
   - `status`: `approved_for_execution`
   - `approved_by`, `approved_at`, `expires_at` (~14d)
   - `approval_commit`: that commit SHA
   - `approved_scope`: copy or edit `proposed_scope`
4. Agents may then run Issues in `issue_order` within path/phase gates.
5. After batch complete: `post_reviewed_*` + merge discipline per branch
   policy.

**Partial approval:** Adjudicator may approve only `{LISS-0399}` or
`{LISS-0399, LISS-0400}` by editing `issue_ids` before status promotion —
the dependency chain means a prefix, not an arbitrary subset.

## 5. Success / post-review checklist

- [ ] LISS-0399: `Continuous<T>` recognized; port + fake adapter ship;
  `CONTINUOUS_ESCAPE_ERROR` fires on measure/evolve/Joint/QPU use;
  unconsumed root produces `LINEAR_IMPLICIT_DISCARD`
- [ ] LISS-0400: `weight`/`mask` compose new handles; ordinary linear move
  semantics on inputs
- [ ] LISS-0401: Lane A `finiteize` grammar unchanged; new overload accepts
  `Continuous`; consumption closes LISS-0399's discard story; single-use
  limitation (no `CH-field-fork`) holds
- [ ] Full regression passes, including unchanged LISS-0313 Lane A tests
- [ ] No `examples/showcase/S01_quantum_disaster_response/**` edits unless
  batch amended
- [ ] No `compiler/staqex/host_monte_carlo.py` behavior change

## 6. Explicit non-authorization

This proposal and the JSON `status: draft` **do not** grant:

- Phase 1/2/3 on any Issue
- S01 showcase / example wiring for `CH-field-compose`
- Resolution of `CH-field-fork` or `CH-field-theory`
- Any other reopened-backlog item (trait specialization, Joint rational
  mode, CUDA)
- Mutation on `main`

## 7. Agent payload (after approval only)

```text
Execute approved batch execution-batch-wp-0097.json only if status is
approved_for_execution and approval_commit matches current batch branch
base. Follow issue_order (0399 -> 0400 -> 0401); stay in allowed_paths;
stop on invalidating_triggers. Start LISS-0399; do not touch
examples/showcase/S01_quantum_disaster_response/** or
compiler/staqex/host_monte_carlo.py's existing behavior. Report
Red/Green/Refactor per Issue; keep Lane A finiteize's existing grammar
byte-for-byte unaffected.
```
