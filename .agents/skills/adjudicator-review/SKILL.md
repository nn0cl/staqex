---
name: adjudicator-review
description: Ask the human Adjudicator for a typed approval. Use when requesting phase, architecture, technology-selection, scope, implementation, or bounded-batch approval, or when a decision gate requires a human stop.
---

# Adjudicator review

Canonical template: `docs/templates/adjudicator-review.md`. Fill that shape.

Name the approval type explicitly. Do not infer a later approval from an
earlier one. A proposed ADR is a design artifact, not implementation
approval. Scope approval does not authorize technology selection, ADR
acceptance, or implementation.

The packet must state approved scope, current phase, requested approval type,
implementation permission, and any post-review requirement.

This skill does not replace the standing Approval Model in the contract
files.
