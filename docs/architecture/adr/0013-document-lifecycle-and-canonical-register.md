# ADR 0013: Document Lifecycle and Canonical Register

## Status

Accepted

## Context

Long-running agent collaboration creates ADRs, Issues, Work Plans, Traces, and
review records faster than agents can reliably distinguish current guidance
from historical evidence. Template rules can also become mixed with a target
project's domain decisions. The result is specification drift and unnecessary
review context.

## Decision

Adopt four document layers: Entry, Canonical, Evidence, and Archive. Each topic
has one current Canonical document, and a target-owned Canonical Register maps
that document to its Entry and source evidence. Current and Historical status
must be explicit in the register. Agents read the Register and Current
Canonical documents before Evidence, and only read Archive material when
explicitly referenced.

Template-owned rules remain separate from target-owned specifications and
decisions. A consolidation ledger records source path, source commit, source
tag, canonical destination, classification, and reason so compression remains
recoverable through Git history.

AI work Traces are retained as evidence but are created or expanded only for a
new decision boundary, unresolved matter, approval, or unique verification
evidence. Completed work is summarized in a representative Trace or Review
Summary.

The template supplies a Canonical Register template, a Review Summary
template, and a deterministic checker. It does not impose retention periods,
automatic deletion, or a target-specific deprecated-term catalog.

The Register and Review Summary are derived navigation and review artifacts.
They do not become new agreement units and do not replace the existing accepted
specification, ADR, Issue, Work Plan, or Adjudicator approval boundaries.

## Consequences

Positive:

- Agents and reviewers have a short, explicit entry point for current state.
- Historical evidence remains recoverable without competing with current
  guidance.
- Template updates and target customizations have distinct ownership.
- Register consistency can be checked without AI judgment.

Negative:

- Adopting projects must maintain their target-owned Register.
- Consolidation still requires human judgment about evidence and history.
- The checker cannot infer domain-specific obsolete terms or decide whether a
  document is ready for archival.

## References

- `docs/collaboration/document-lifecycle.md`
- `docs/templates/canonical-document-register.md`
- `docs/templates/review-summary.md`
- `docs/collaboration/ai-work-trace-log.md`
