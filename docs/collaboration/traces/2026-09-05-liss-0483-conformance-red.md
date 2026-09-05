# LISS-0483 bounded Red trace and handoff

## Request and planning

- Date: 2026-09-05. User: continue the proposed Phase 1 test-only slice.
- Feature Path; size M; planning record: this trace and LISS-0483 evidence matrix.
- Scope: four observed lexicon/observation discrepancies, six test cases.
- Authority: quantum mental-model follow-up specification, detailed 0480–0483 design.
- Dependencies: 0480–0482 shipped; their bounded tests miss these defects.
- No implementation, grammar, provider, or technology approval inferred.

## Context and routing

- Included: target spec sections, lexicon/mapping modules, SemanticNode fields,
  existing 0482 tests, readiness/testing/workflow policies and process lessons.
- Omitted: AWS, credentials, Rust, unrelated backlog and broad historical ADRs.
- Host implementation; review isolation same_context; no separate reviewer claimed.
- Lessons applied: preserve authority and observable metadata; synchronize status;
  no consumer completion claim without unsupported-family coverage. No new IDs.
- No new DTOs, dependencies, ports or architecture decisions.

## Attempt 1

- Environment: local Codex, Python repository virtual environment.
- Model/reasoning identifiers and actual token usage: unavailable; not estimated.
- Branch: `codex/liss-0483-conformance-red`, from clean main.
- Branch creation required sandbox escalation; succeeded without changing main.
- System Python lacked pytest; existing `.venv/bin/python` used without installation.
- New suite: **5 failed, 1 passed**, failures match the five expected assertions.
- Existing 0480, 0481, 0482 suites: **18 passed**.
- Full suite not run: this intentionally Red slice does not claim regression Green.
- Commands: `.venv/bin/python -m pytest tests/test_liss_0483_observation_lexicon_conformance_red.py -q`;
  same invocation listing the existing three issue suites.
- Production and previously reviewed test files unchanged.

## Evidence and limitations

Fixtures generate semantic IR; they also produce the two explicitly asserted
finite-evidence/approximation diagnostics. No runtime or hardware success is
claimed. Exactness `unresolved` and dimensions `unknown` must remain visible,
not become the constant `preserved`. Existing 0482 assertions conflict with
that requirement. No old tests were silently revised.

## Changed files

- `tests/test_liss_0483_observation_lexicon_conformance_red.py`
- `docs/issues/LISS-0483-observation-lexicon-conformance.md`
- `docs/work-plans/WP-0092-quantum-mental-model-follow-up.md`
- This trace.

## Green continuation

On continuation, the bounded production correction was implemented:
comments are excluded from lexicon scanning, commutator display retains its
operands, observation comments do not alter lane handling, and mapping copies
canonical IR exactness/dimensions. The new suite is **6 passed**. The legacy
0482 suite is now **18 passed** after its two assertions were explicitly
updated to compare canonical IR values and describe unsupported synthetic
input accurately. Production was not rolled back. The combined 0480–0483
suites now pass **24 tests**. A full `pytest tests -q` run reached 43% before
the tool's 30-second execution window ended; no failure was reported, but
completion was not established.

## Next safe action / approval gate

Review the explicit 0482 assertion update and complete the full regression
suite. Broader
aliases/composition/projection conformance remains unfinished; do not mark the
issue or WP done.

## Merge preparation review

User authorized commit, push and merge. Isolation: same_context (weaker than
separate_context). Re-read production diff, tests, spec detailed 0480–0483
design and CI configuration. The named comment/operand/value regressions pass
24 related tests. No new execution authority or provider side effect appears
in the change. Unknown semantic values remain observable.

Findings/disposition: status drift in Issue/WP corrected; fixed-value legacy
assertions explicitly updated. Remaining raw-source regex limitations (only
the first simple-identifier commutator, no string-aware parsing) remain open
for broader conformance; this merge must not claim complete alias handling.
CI ignores `_red.py` suites, so the related 24-test local run is separate
required evidence. Full local run completed: **1913 passed in 309.87s** using
`.venv/bin/python -m pytest tests -q`. The prior 30-second window was a tool
yield, not a test timeout. Merge requires passing remote
checks. No Issue/WP completion is claimed by this review.

## Source-evidence follow-up / handoff

- Prior delivery: PR #577 merged as `da011801`; remote CI passed all three jobs.
- User requested continuation. Current branch: `codex/liss-0483-source-evidence`.
- Scope/phase: size M, conformance inventory and Phase 1 source-evidence Red.
- Planning: `docs/testing/liss-0483-conformance-matrix.md` names proofs,
  limitations and the next correction. Source spec remains authoritative.
- Included: 0481 API, 0480–0483 tests, 0320/0376/0448/0431 tests,
  S02 controlled classification, tomography capability, accepted ADR 0191.
- Lessons applied: unsupported boundaries require negative cases; observable
  records need real source evidence; Issue/WP status updated together.
- Findings: synthetic fragments produce noncanonical source IDs; real project
  source is absent from the inventory. Projection rejection test catches its
  own AssertionError; alias shadowing fixture never shadows anything.
- Verification: 43 selected existing tests plus 3 S02 tests pass; new
  `test_liss_0483_observation_source_evidence_red.py` has 5 expected failures.
  No full rerun required for this intentionally Red, test-only increment.
- Source compilation can retain finite-lowering diagnostics; the tests assert
  compile.ok and canonical nodes where appropriate, not finite execution.
- Changed: new matrix and Red test; Issue, WP and this trace synchronized.
- Production and old tests unchanged. No commit/push performed in this follow-up.
- Routing: host, same_context; no independent review claimed. Usage unavailable.
- Next: review five Red cases and authorize Green plus explicit disposition of
  four 0481 synthetic-success cases. Then remove fabricated metadata and map
  source-owned projection. Broader matrix gaps remain separate follow-ups.
