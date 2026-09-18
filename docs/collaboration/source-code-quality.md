# Source Code Quality for AI-TDD Collaboration

Generated code must be easy for a human Adjudicator to review.

This is a collaboration rule, not an application-internal design decision.

## Primary Goal

Minimize human cognitive load while preserving AT-TDD discipline.

The code should make it obvious:

- what behavior is being implemented.
- where business decisions live.
- which dependencies are external.
- which test caused the code to exist.
- what can be safely changed later.

## Readability Rules

Prefer:

- direct, descriptive names.
- small modules with one responsibility.
- small functions with one reason to change.
- explicit data flow.
- explicit error boundaries.
- tests organized around Given, When, and Then.

Avoid:

- clever compression.
- broad utility modules.
- mixed abstraction levels in one function.
- large files that require scanning unrelated behavior.
- speculative generic abstractions.
- comments that explain confusing code instead of simplifying the code.

## Splitting Rules

Split code when it reduces the reader's working memory.

Good reasons to split:

- separating domain, application, adapter, and delivery concerns.
- extracting a named value object or policy already required by tests.
- isolating provider-specific mapping from core behavior.
- making a test scenario readable without unrelated setup.

Poor reasons to split:

- creating layers that do not own a decision.
- adding an abstraction for a future provider not in scope.
- hiding a simple expression behind a vague helper.

## Review Checklist

Structure budgets live in target-owned `[source_structure]` in runtime-routing
TOML. The form suggests 300 source/implementation lines and 500 changed lines.
Missing settings retain qualitative rules. Exceedance prompts responsibility
splitting, a rationale for retaining the structure, an owner/deadline follow-up,
or explicit human exception; it is not an automatic ban. Follow-up planning
cannot waive failing blocking verification.

Measure implementation bodies including private, legacy and helper files,
not only public facades. `python3 scripts/review-change.py --base BASE` reports
both base/head physical lines, changed files/lines and Python syntax counts/
imports. Unsupported language counts, semantic responsibilities, dynamic
dependencies and resolved cycles remain explicit review gaps. Document any
generated/vendor exclusions. Use project dependency tools for resolved graphs.

For splits also follow `docs/collaboration/verification-policy.md` to preserve
actual consumers, private imports and behavioral boundaries.

Before asking for review, the agent should check:

- Can the reviewer understand the changed behavior in a few minutes?
- Does each changed file have a clear responsibility?
- Does each function have one main reason to change?
- Are framework, provider, and persistence details outside core code?
- Are names based on domain or capability rather than implementation trivia?
- Are tests small enough that failures point to one behavior?
- Did Phase 2 stay minimal without becoming dense or clever?
- Does each change map directly to an acceptance clause, without special-case
  behavior added only to satisfy a test?
- Are assertion/fixture/exclusion changes visible and approved, rather than
  weakening tests, hiding errors or moving failures into another Issue?
- Were serialization, diagnostics, ordering and indirect consumers assessed?

## Refactor Guidance

Phase 3 should improve readability when:

- Phase 2 code passed tests but is hard to scan.
- duplicate setup obscures the behavior under test.
- names are too technical for the domain concept.
- adapter mapping details distract from use-case behavior.

Do not refactor just to apply a pattern. Refactor to reduce review cost,
clarify ownership, or remove meaningful duplication.
