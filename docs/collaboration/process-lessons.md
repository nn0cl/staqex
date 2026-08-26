# Process Lessons

This policy is the Canonical document for how review outcomes become reusable
guidance. It does not replace typed Adjudicator approval.

Live lessons live at:

```text
docs/collaboration/process-lessons-log.md
```

Create that file from `docs/templates/process-lesson.md` on the first lesson.
The live log is target-owned: copy and update scripts must not overwrite it.

## When to write

Write or update the log when:

- an agent review packet is produced;
- a completion process review (see `docs/collaboration/process-review.md`)
  finds a reusable pattern;
- the Adjudicator asks to capture a process lesson.

Do not write a lesson for a one-off typo or a purely mechanical Fast Path
edit with no process signal.

## Meta, not incidents

Record the class of event, not the play-by-play of a session.

Write:

- which operating-path, phase, or contract rule was weak or skipped;
- the failure or cost class (for example: phase skipped, placeholder treated
  as a fact, review used author reasoning as evidence);
- what later design or implementation must do differently.

Do not write:

- a narrative of who said what in a specific chat;
- file-by-file incident logs;
- private data, secrets, or adopter customer content.

One lesson should still make sense after the original issue is `done` and the
branch is deleted.

## Apply at the next design and implementation

At design intake, and again before Phase 1, 2, or process implementation:

1. Read `docs/collaboration/process-lessons-log.md` if it exists.
2. List lessons that apply to the current path, phase, or area.
3. State how each is honored (applied, already closed with evidence, or out
   of scope with reason).
4. Do not silently ignore an open lesson that matches the work.

Missing log means no recorded lessons yet, not permission to skip later
reviews.
