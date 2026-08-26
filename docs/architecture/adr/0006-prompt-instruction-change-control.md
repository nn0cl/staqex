# ADR 0006: Prompt and Instruction Change Control

## Status

Accepted

## Context

`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`,
`.grok/rules/*.md`, and `.cursor/rules/*.mdc` are near-duplicate operating
contracts for different AI coding tools, together with
`docs/at-tdd/process.md`, `docs/collaboration/*.md`, and
`docs/templates/*.md`. Agent behavior depends directly on these files.
(Codex reads `AGENTS.md` directly and does not need its own contract file.)

As of 2026, several of these tools also read `AGENTS.md` (and in Grok
Build's case, `CLAUDE.md` too) natively, independent of their own dedicated
rule surface: Cursor documents `AGENTS.md` as a "simple alternative to
`.cursor/rules`", and current Grok Build documentation states it reads
`AGENTS.md` at three levels (`~/.grok/AGENTS.md`, `<repo-root>/AGENTS.md`,
`<cwd>/AGENTS.md`) plus `CLAUDE.md` "for compatibility" (verified via live
web search, 2026-07-14; see the accompanying trace).

LISS-0006 and LISS-0010 originally resolved this with one blanket rule: full
mirror across all five files, no thin pointers, so every tool gets the same
explicit, strongly-bound entry point. LISS-0015 (2026-07-16) revisited that
blanket rule on Adjudicator instruction, on the grounds that "we decided this
once before" is not itself evidence, and found the picture differs per
vendor:

- **GitHub Copilot** now reads `AGENTS.md` natively (coding agent since
  2025-08-28, code review GA since 2026-06-18), but GitHub's own
  documentation states this reading is "read-and-apply, not strict
  enforcement" and does not guarantee adherence as literal as Claude Code
  following `CLAUDE.md`. This is the same category of evidence that
  originally justified Grok's dedicated file (generic context loading proving
  insufficient in practice) applied to a different vendor.
- **Claude Code** supports `@path/to/file` imports that expand inline into
  context at session launch — a guaranteed content-inlining mechanism, not a
  hope-based pointer — and Anthropic's own documentation explicitly
  recommends `@AGENTS.md` specifically to avoid duplicating instructions
  between `AGENTS.md` and `CLAUDE.md`. This is a materially different
  mechanism from a plain-text cross-reference, and removes the original
  "thin pointers aren't reliable" objection for this one vendor pair.
- **Cursor** — shared contract via native `AGENTS.md`, not `@` inside `.mdc`.

  Evidence (primary sources, fetched 2026-07-16):

  1. Rules types list `AGENTS.md` separately from Project Rules
     (`.cursor/rules`): [Rules | Cursor Docs](https://cursor.com/docs/rules.md)
     ("Cursor supports four types of rules: … Project Rules … AGENTS.md").
  2. Help: "Create an `AGENTS.md` file in your project root. …
     Cursor picks it up automatically."
     ([Help: Rules](https://cursor.com/help/customization/rules.md)).
  3. Nested `AGENTS.md` is "automatically applied when working with files in
     that directory" ([Rules § AGENTS.md](https://cursor.com/docs/rules.md)).
  4. FAQ: `@filename` in a rule includes that file in rule context
     ([Rules FAQ](https://cursor.com/docs/rules.md)) — valid, but for root
     `AGENTS.md` it duplicates (1)–(2) rather than substituting for them.
  5. Live Cursor session 2026-07-16 (this repo, branch
     `process/agent-rule-file-parity`): agent context received root
     `AGENTS.md` as its own always-applied workspace rule *and* the three
     `alwaysApply` `.mdc` files; `@AGENTS.md` prose inside `.mdc` bodies was
     not expanded inline. Shared Expected Workflow / dependency-rule content
     was present via the `AGENTS.md` injection. Trace:
     `docs/collaboration/traces/2026-07-16-cursor-mdc-drop-agents-ref.md`.

  Conclusion: omitting shared sections from `.mdc` (and omitting `@AGENTS.md`
  there) does not drop them from Cursor Agent context while root `AGENTS.md`
  auto-apply remains in force. Keep `.mdc` for Cursor-only complements.
- **Grok**'s `.grok/rules/` stronger-binding finding (LISS-0006's live `grok
  inspect` test, 2026-07-08) was not re-examined this round.

Decision, per vendor (Adjudicator-confirmed 2026-07-16; Cursor policy refined
and **Adjudicator-approved** same day after live verification + cited grounds):

- `CLAUDE.md` now imports `AGENTS.md` (`@AGENTS.md`) instead of duplicating
  its body, keeping only genuinely Claude Code-specific sections.
  **Superseded 2026-07-25:** `CLAUDE.md` is a full effective-content mirror
  and does not import `@AGENTS.md`. See the 2026-07-25 revisit below.
- `.cursor/rules/*.mdc` keeps only Cursor-complementary content (phase gate
  detail, anti-hallucination, Decision Gates, handoff/completion). Shared
  sections formerly duplicated from `AGENTS.md` are omitted — not
  `@`-referenced — because Cursor already auto-applies root `AGENTS.md`
  (evidence items 1–5 above).
- `.github/copilot-instructions.md` and `.grok/rules/*.md` keep the full
  mirror. For Copilot, the Adjudicator weighed GitHub's documented weaker-adherence
  risk against the duplication cost and chose to keep the stronger, dedicated
  binding. For Grok, the original empirical grounding was not revisited.

These files can drift from each other silently: one file can gain a required
read step that the others do not, and none of them require the
operating-contract files themselves to be reviewed with the same rigor as
application code. The AI Work Trace Log already asks for a trace when
contract files change, but that alone does not name the exact file set,
require Adjudicator review specifically, or get enforced by CI.

This gap is tracked in `docs/collaboration/process-gap-register.md`.

### 2026-07-25 revisit: Claude Code's `@AGENTS.md` import (LISS-0018)

The Claude Code branch of the decision above (2026-07-16) reasoned that
`@path` imports are "a guaranteed content-inlining mechanism, not a
hope-based pointer," and that this "removes the... objection" that justified
Copilot's full mirror. Another adopter (qpex, LISS-0018) reported a concrete
incident that contradicts the practical conclusion, even though it does not
contradict the technical premise:

- The `@AGENTS.md` import worked exactly as documented — the day's current
  `AGENTS.md` content, including same-day additions, was verifiably present
  in a live session's context.
- In that same session, Claude Code still (A) repeatedly omitted the
  mandatory `[DESIGN CHECK]` scaffold for Feature/Architecture Path requests
  across multiple turns, and (B) on one occasion began Phase 2 Green
  implementation without stopping at an unchecked Adjudicator Decision Point
  left open in the active local issue.

Anthropic's own current documentation (fetched 2026-07-25) both supports and
complicates the fix this finding motivates:

- Supports treating imported content as no more binding than any other
  CLAUDE.md prose: "Claude treats them \[CLAUDE.md / auto memory] as context,
  not enforced configuration." ([*How Claude remembers your
  project*](https://code.claude.com/docs/en/memory))
- Complicates the specific "import vs. literal text" causal story: "Splitting
  into imports helps organization but doesn't reduce context, since imported
  files load at launch." ([*How Claude remembers your
  project*](https://code.claude.com/docs/en/memory)) Anthropic does not state
  that `@import` and literal duplication load identically — only that
  imported content still enters the context window at launch, so it is not
  exempt from the documented adherence drivers: total line count ("target
  under 200 lines... longer files consume more context and reduce
  adherence"), instruction specificity, and absence of cross-file conflicts.
  Converting `CLAUDE.md` to a full mirror is therefore not confirmed to fix
  the root cause; it may help only if the rewrite is also more concise and
  specific than what it replaced.
- Also from the same memory page: "To block an action regardless of what
  Claude decides, use a **PreToolUse hook** instead" — a stronger,
  deterministic alternative for exactly this failure class that this
  revision does **not** adopt yet. The separate *Automate actions with hooks*
  page confirms the mechanism: "`PreToolUse` hooks fire before any
  permission-mode check, in every permission mode, including `dontAsk`...
  blocks the tool even in `bypassPermissions` mode."
  ([hooks-guide](https://code.claude.com/docs/en/hooks-guide)) A hook could
  plausibly gate failure mode B, but requires reshaping local-issue
  "Adjudicator Decision Points" into a machine-checkable format first; not
  built in LISS-0018. Failure mode A is not naturally hook-gatable by the
  same mechanism.

Decision: given the uncertainty above, and on Adjudicator instruction not to
block this fix on resolving the causal mechanism, `CLAUDE.md` moves to a full
mirror as a precautionary measure consistent with how Copilot's weaker,
documented "read-and-apply, not strict enforcement" risk was already handled
— treating Claude Code's observed gap the same way pending further evidence,
rather than waiting for a confirmed mechanism. Whether to pursue
`PreToolUse`-hook enforcement, and whether recurrence should prompt
reconsidering Claude Code's status among this template's supported agents,
are both left open in LISS-0018 and not decided here.

## Decision

Adopt `docs/collaboration/prompt-instruction-change-control.md` as the
canonical definition of the agent operating contract file set.

- Name the exact files and glob patterns that count as the agent operating
  contract.
- Require Adjudicator review, a stated reason, and a cross-file consistency
  check whenever a contract file changes.
- Require an AI work trace under `docs/collaboration/traces/` for every
  contract change, including small wording changes.
- Enforce the trace requirement in CI: a pull request that changes a
  contract file must also add a trace file.
- Per LISS-0015 (Cursor) and LISS-0018 (Claude Code, 2026-07-25): the
  consistency check means the five files resolve to equivalent effective
  content, not that they are literal duplicates. `CLAUDE.md`,
  `copilot-instructions.md`, and `.grok/rules/*.md` are each independently
  phrased, full-coverage mirrors of `AGENTS.md`'s effective content for their
  own tool (not literal, byte-identical text of `AGENTS.md` or of each
  other — compare their differing headings, e.g. `CLAUDE.md` keeps a
  dedicated "Approval Model" section that `copilot-instructions.md` folds
  into "Mandatory Design Check" instead); `.cursor/rules/*.mdc` plus
  Cursor's native root `AGENTS.md` loading together supply the shared
  contract for Cursor.

## Consequences

Positive:

- Contract drift between `AGENTS.md`, `CLAUDE.md`,
  `.github/copilot-instructions.md`, `.grok/rules/*.md`, and
  `.cursor/rules/*.mdc` becomes visible in review instead of silently
  changing agent behavior.
- Every contract change has a recorded reason and expected behavior change.
- CI gives an automated signal instead of relying only on Adjudicator memory.
- Cursor `.mdc` files no longer carry redundant `@AGENTS.md` references or
  full shared-section mirrors; shared content rides on native `AGENTS.md`
  auto-apply.
- `CLAUDE.md` as a full mirror removes the open question of whether an
  imported instruction binds Claude Code's behavior as strongly as text
  physically present in the file it treats as its own contract (LISS-0018).

Negative:

- Adds a mandatory trace step even for small wording changes to contract
  files.
- Requires keeping the file list in
  `docs/collaboration/prompt-instruction-change-control.md` up to date as new
  contract-like files are introduced.
- The consistency check can no longer be a simple text diff for Cursor
  (`.mdc` + native `AGENTS.md`); a reviewer must confirm the effective union
  still matches `AGENTS.md`, which is a judgment call rather than a byte
  comparison.
- `CLAUDE.md` is now a full hand-maintained duplicate again: a future change
  to `AGENTS.md` needs a matching manual edit in `CLAUDE.md`, the same
  maintenance cost already accepted for Copilot and Grok.
- The causal mechanism behind the qpex incident that motivated this reversal
  is not confirmed (see LISS-0018 Adjudicator Decision Points); if line count
  and specificity are the real adherence drivers, as Anthropic's own
  documentation suggests, this change may not address the root cause by
  itself.
- If Cursor ever stopped auto-applying root `AGENTS.md`, shared rules would
  disappear from Cursor sessions unless `.mdc` or another binding were
  restored — watch product docs when upgrading Cursor.

## Enforcement

Code review should reject:

- agent operating contract changes without a stated reason or Adjudicator review.
- agent operating contract changes without an accompanying trace under
  `docs/collaboration/traces/`.
- agent operating contract changes that leave `AGENTS.md`, `CLAUDE.md`,
  `.github/copilot-instructions.md`, `.grok/rules/*.md`, and
  `.cursor/rules/*.mdc` inconsistent with each other in effective content
  (full-coverage effective-content mirror, independently phrased per tool,
  for `CLAUDE.md`, `copilot-instructions.md`, and `.grok/rules/*.md`;
  effective union of `.cursor/rules/*.mdc` plus native root `AGENTS.md` for
  Cursor).

CI should reject:

- a pull request that changes a file listed in
  `docs/collaboration/prompt-instruction-change-control.md` without adding a
  trace file under `docs/collaboration/traces/`.
