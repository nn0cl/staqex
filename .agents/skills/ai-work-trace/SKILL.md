---
name: ai-work-trace
description: Create or update an AI work trace. Use when changing agent instructions, templates, ADRs, or collaboration rules; when a task is size M, L, or XL; on a second bug-fix attempt; when work spans phases or uses non-default routing; when pausing for another agent; or when the Adjudicator asks for an audit trail.
---

# AI work trace

Canonical policy: `docs/collaboration/ai-work-trace-log.md`. Template:
`docs/templates/ai-work-trace.md`. Follow those files.

Store one Markdown file per substantial task under
`docs/collaboration/traces/YYYY-MM-DD-short-task-name.md`.

A change to an agent operating contract file always needs a trace. The tiny
documentation-only exception does not apply to those files.

Do not put secrets or full private-data exports in a trace. Create a new
trace only for a new decision boundary, unresolved matter, distinct approval,
or unique verification evidence; otherwise update or link the representative
trace.
