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
0482 suite is **16 passed, 2 failed** because two reviewed assertions encode
the superseded fixed-value/synthetic-input behavior. Production was not
rolled back and those tests were not silently changed.

## Next safe action / approval gate

Review the legacy 0482 assertions and authorize their explicit disposition,
then run the full regression suite. Phase 3 review is required. Broader
aliases/composition/projection conformance remains unfinished; do not mark the
issue or WP done.
