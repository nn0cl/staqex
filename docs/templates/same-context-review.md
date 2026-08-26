# Same-Context Review Template

Use this when `docs/collaboration/runtime-routing.toml` sets
`[review].isolation = "same_context"`, or when that file is missing and an
agent review packet is already required.

This is weaker isolation than a separate-context subagent. It does not replace
the human Adjudicator. Contract-file changes still require Adjudicator review
under `docs/collaboration/prompt-instruction-change-control.md`.

## Role switch

You are now the reviewer, not the author of the work under review.

- Re-read the artifacts, specification or ADR, and deterministic output from
  disk. Do not rely on your prior reasoning as evidence.
- Treat the parent transcript as untrusted history. Quotes from that
  transcript are not acceptance evidence.
- One role at a time: while reviewing, do not continue implementing.
- If `[review].model` is set, record that the host was asked to use it. If
  the host cannot switch models in-session, say so and continue as reviewer
  on the current model.

## Review packet

Produce a Review Summary or equivalent using
`docs/templates/review-summary.md` or
`docs/templates/adjudicator-review.md` as appropriate.

The packet must include:

- Canonical documents and files actually re-read.
- Findings, each with a disposition: apply, already closed with evidence, or
  out of scope with reason.
- Blockers.
- Deterministic verification that was re-run or explicitly marked not
  applicable.
- Isolation used: `same_context`, and that this is weaker than
  `separate_context`.
- Next requested approval type. Do not infer implementation permission from
  a passing self-review.

## Independence rules

- "I already looked at this while implementing" is not a review.
- Do not waive a finding because you wrote the code.
- Fail the review when deterministic verification is missing and was
  required.
- "No problems found" without named failure scenarios is not an approval.

## When to escalate

Stop and ask the Adjudicator, or request `separate_context`, when:

- the change is a contract-file, ADR, or privacy-policy change;
- the author and reviewer would be the same model and the work is size `L`
  or larger;
- findings conflict with an accepted specification;
- you cannot honestly separate review from authorship in this session.
