# LISS-0432: retire `feasible(...)`; Host-bound `Bool[N]…` arrays; classical array visibility

## Metadata

- Local issue ID: LISS-0432
- Status: complete
- Type: Feature Path (`compiler/staqex/parser.py`, `typecheck.py`,
  `finite_binder.py`, `scientific_input.py`, `pipeline.py`,
  `runtime/evaluator.py`; `examples/showcase/S02_drug_discovery/**`)
- Priority: P1
- Planning size: L — the batch record's own estimate ("retire feasible(...)
  and _bind_feasible_predicate, migrate Host binding to plain
  host()-bound arrays") undersized the real surface: `Bool[N]…` Host
  arrays and classical-body array visibility did not exist yet at all
  (see Findings)
- Owner / agent: Claude Code
- Parent: WP-0099 (batch `s02-step2-literal-transcription`), ADR 0207
- Branch: `batch/s02-step2-literal-transcription` (batch-level)
- GitHub Issue / PR: (opened at batch completion)

## Intent

ADR 0207 Decision 10 (Accepted): "`feasible(...)` is retired outright...
Host data moves to the plain `host(...)`-bound-array pattern step 3 already
uses." $C\in\{0,1\}^{n\times n}$ and $D\in\mathbb{R}^{n\times n}$ become
literal Host-bound arrays `F` itself indexes (`C[i][j]`, `D[i][j]`),
replacing the closed-vocabulary `feasible(exactly_selected=…,
pairwise_compatible=…, diversity_at_least=…)` kwargs entirely.

## Scope

1. Retire `feasible(...)`'s runtime dispatch (`evaluator.py`'s `project`
   handler `Call`-target branch) and `_bind_feasible_predicate` outright —
   no replacement special-case; an unrecognized `feasible(...)` call now
   fails with the same generic error any other undefined-function
   reference would (`KernelError: call cannot be classical value in
   Phase 2.2 value context` at runtime; the construct itself still
   compiles, since `feasible` was never a reserved keyword, only an
   evaluator-special-cased identifier).
2. Retire ADR 0192's `Projector<Selection>` closed-vocabulary machinery in
   `pipeline.py` outright, together with it: `_append_selection_projector_
   region`, `_collect_feasible_predicates`, `_S02_KNOWN_CONSTRAINT_
   PREDICATES`, its caller wiring, and the `S02_UNKNOWN_CONSTRAINT_
   PREDICATE`/`S02_DUPLICATE_CONSTRAINT_PREDICATE` hard diagnostics. This
   also retires the traversal gap LISS-0431 found and deliberately
   deferred here (the mechanism itself is gone, not patched).
   `ProjectorRegion`'s IR *type* is left in `quantum_semantic_ir.py` --
   deliberately not deleted, since it is generic semantic-IR vocabulary
   ("an explicit projector applied, without terminal sampling") with no
   ADR-0192-specific typing, and a future producer could reuse it; only
   its one, retired producer is removed.
3. Retire `host_input_binding.py` (`validate_matrix_binding`) outright —
   ADR 0194's own shape/dtype/symmetry validation module, whose only
   caller was `_bind_feasible_predicate`. The generalized `CoefficientTensor`
   path (below) is its replacement.
4. Generalize the ADR 0119 Host coefficient-tensor path from Float-only to
   Float/Bool dtype (`Bool[N]…` arrays), so `Bool[8][8] C =
   host("pairwise_compatible")` works end to end: parser (`Bool[N]…` type
   syntax), typecheck (`_check_bool_array_bind`), `_host_placeholder_keys`
   (dtype-carrying), `CoefficientTensor`/`_normalize_bool_tensor_values`
   (Bool leaves preserved as `bool`, not coerced to `float`).
5. Make Host-bound `Float[N]…`/`Bool[N]…` arrays visible from *classical*
   Sigma/ForAll/Min/Set-comprehension bodies (`_eval_op_expr_classical`'s
   `OpVar` case), not only from `Operator = Sigma(...) {...}` bodies — the
   confirmed design's `C[i][j]`/`D[i][j]` inside `ForAll`/`Min` conditions
   need this.
6. Rewrite `main_selection.sqx` step 2 to the confirmed literal form (the
   full equation from ADR 0207/WP-0099), since `feasible(...)`'s only
   remaining caller in the whole corpus was this file — retiring
   `feasible(...)` without updating it would leave the corpus non-
   compiling until LISS-0433 (S11), breaking this Issue's own full-
   regression exit criterion. LISS-0433 (S11) still owns the *dedicated*
   distributional-equivalence verification against the pre-rewrite
   baseline; this Issue's own rewrite is the mechanical prerequisite for
   that, verified here only to the extent needed to keep the suite green.
7. Rename the Host input key `diversity_at_least` → `diversity` (the old
   name conflated the matrix with `feasible`'s own threshold kwarg name;
   the threshold is now the separate literal `Float theta = 0.3`) across
   `run_selection.py`, `benchmark_report.py`, and their tests.

## Real findings during Green

1. **The batch record's own "no new Host contract" claim (ADR 0207) was
   not fully accurate for `Bool[N]…`.** Direct testing found FOUR
   independent gaps, not one: (a) `_type_ref()`'s `Float[N]…` dims grammar
   was hardcoded to `name == "Float"` — `Bool[2][2]` didn't even parse
   (silently misparsed, swallowed by the same implicit-final-expression
   backtracking recovery LISS-0423 found); (b) typecheck had no
   `Bool[N]…` array-bind path at all; (c) `_host_placeholder_keys` only
   recognized `Float`; (d) `CoefficientTensor`'s own `_normalize_tensor_
   values` explicitly *rejected* `bool` leaves (`isinstance(values, bool)
   or not isinstance(values, Real)` → error) and coerced everything else
   to `float` — a Bool-dtype Host tensor was structurally impossible, not
   just unwired. Generalized all four narrowly (Bool alongside Float, not
   a new grammar) rather than inventing new machinery.
2. **A second, independent, load-bearing gap: `C[i][j]`/`D[i][j]` used
   inside `ForAll`/`Min`/Set-comprehension conditions had no visibility
   into Host-bound arrays at all.** `_eval_op_expr_classical`'s `OpVar`
   case only checked `assign` (the local binder scope) and `self.scalars`
   — `Float[N]…`/`Bool[N]…` arrays were, by design, consumed *only*
   inside an `Operator = Sigma(...) {...}` body via
   `_operator_array_context()` (confirmed by reading the main statement
   loop's own comment: "compile-time coefficient data consumed only via
   the Operator sum-binder lowering above... they have no live
   Joint/scalar role"). The confirmed design's `ForAll`/`Min` conditions
   are *classical*, not Operator-typed, so they never went through that
   path. Fixed by adding the same `_operator_array_context()` fallback to
   `_eval_op_expr_classical`'s `OpVar` case.
3. **A real, significant performance defect, found only by actually
   profiling the rewritten `main_selection.sqx` end to end (not
   discoverable from the smaller n=3 tests S1-S9 used): the confirmed
   design's own `psi_0`/`psi_sel` two-name split (mirroring the
   blackboard's own $\lvert\psi_0\rangle$/$\lvert\psi_{sel}\rangle$
   notation) left `psi_0` lingering in every surviving World's `assign`
   dict after `project`, since `project`'s `bind_pushforward` adds
   `psi_sel` without removing `psi_0`.** The OLD program never hit this,
   because it *rebound the same name* (`State psi_sel = ...; State
   psi_sel = project psi_sel onto feasible(...)`), which structurally
   erases the pre-projection value. `_hamiltonian_evolve_tuple_
   coordinate`'s own World-grouping (`key = ... if k != src`) groups
   Worlds by every *other* assign key -- with `psi_0` lingering as an
   extra per-World-distinct key, all 25 of the fixture's surviving Worlds
   (confirmed `|F|=25` at $n=8$) fell into 25 separate groups instead of
   1, forcing 25 independent `expm_ih_apply` Suzuki-Trotter exponentials
   instead of one batched exponential. Confirmed directly by profiling
   (`cProfile`): 54+ seconds and 695,552 `_apply_term_add` calls before
   the fix, vs the git-HEAD (pre-rewrite) baseline's 1.9 seconds and
   28,160 calls for the identical physics. Root-caused, not worked
   around: added an explicit `trace_out(psi_0)` statement to
   `main_selection.sqx` right after `psi_0`'s only two reads are both
   complete (ADR 0173's own "no leftovers to trace out" principle,
   already referenced by this file's existing final comment) — this drops
   the stray key, restoring the 1-group/1-`expm_ih_apply` batching. Total
   `main_selection.sqx` runtime: 54s+ → ~5.6s. Verified numerically
   identical either way (marginal size and total probability unchanged
   with/without the `trace_out`), confirming this is a pure performance
   fix, not a behavior change. Also added a small, safe, correctness-
   neutral memoization (`self._compiled_operator_cache`) in
   `_project_onto_operator`, since `self.operators[name]` never rebinds
   mid-run: avoids literally recompiling the identical $P_F$ matrix twice
   per equation (once for the projection, once inside `/ ||...||`) —
   confirmed harmless by re-running the full end-to-end numeric check
   after adding it (unchanged result, `~5.6s` measured with the cache
   already applied). This remaining ~5.6s (dense $2^n\times 2^n$ matrix
   construction in `hamiltonian.py`'s `kron`/`embed_pauli` for the
   Pauli-Z-decomposed $P_F$, once) is an accepted, disclosed cost of the
   literal design at $n=8$, not further optimized here (out of scope; a
   future sparse-construction Issue if it becomes a real blocker) --
   per this project's standing "never shrink scope for perf" precedent.
4. **`selection pattern` at seed 0 came out byte-identical to the
   pre-rewrite baseline** (`(0, 1, 1, 1, 1, 1, 0, 0)`, `marginal size:
   256`, matching the previously captured `status: succeeded` / `Vacuum:
   False` run) once the `trace_out` fix was in place — encouraging
   evidence for LISS-0433's own dedicated verification, though that
   Issue still owns the systematic check (this was one seed, checked
   incidentally while diagnosing the performance defect above, not a
   substitute for LISS-0433's planned comparison).

## Design verification performed

1. Direct compile/typecheck/runtime tests for `Bool[N]…` host-bound array
   declarations (parse, shape validation, dtype preservation as `bool`
   not coerced to `float`).
2. Direct runtime test: `C[i][j]`/`D[i][j]` resolved correctly inside
   `ForAll`/`Min`/Set-comprehension conditions at $n=3$ (a synthetic
   fixture, not the real S02 one) before touching `main_selection.sqx`.
3. `main_selection.sqx` recompiled clean (only the pre-existing soft
   `QSEM_*` diagnostics, unchanged from before this Issue) and executed
   end to end via `host/run_selection.py`, producing a well-formed,
   feasible, non-Vacuum selection pattern.
4. Performance regression found, root-caused, and fixed as described
   above — confirmed numerically neutral (identical marginal distribution
   with/without the fix) via direct before/after comparison, not assumed.
5. Full regression sweep, spec verification, and full `.sqx` corpus
   `staqex check` — see the batch record's own `progress_notes["LISS-
   0432"]` entry for the exact counts (written after this doc, matching
   the established per-Issue pattern).

## Exit criteria

- [x] `feasible(...)` and its ADR 0192/0194 supporting machinery
  (`_bind_feasible_predicate`, `_append_selection_projector_region`,
  `_collect_feasible_predicates`, `host_input_binding.py`) retired
  outright, per ADR 0207 Decision 10.
- [x] `Bool[N]…` Host-bound coefficient arrays work end to end (parser,
  typecheck, Host-binding, dtype-preserving).
- [x] Host-bound `Float[N]…`/`Bool[N]…` arrays visible from classical
  Sigma/ForAll/Min/Set-comprehension bodies, not only Operator bodies.
- [x] `main_selection.sqx` step 2 rewritten to the confirmed literal
  form; corpus compiles and runs clean.
- [x] The real performance defect found while verifying the rewrite
  (25x evolve slowdown from a lingering un-traced-out `psi_0`) root-
  caused and fixed, not worked around or silently left in place.
- [x] Full regression sweep passes; spec verification 100.00%; full
  `.sqx` corpus `staqex check` clean (counts recorded in the batch
  record's progress note).
