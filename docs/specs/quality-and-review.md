# Quality and review acceptance specification

Status: execution scope accepted by the Adjudicator on 2026-09-17 with
“この計画で修正を着手する。開始して”. Implements the integrated review F01–F17.
This is template maintenance evidence, not an adopter domain specification.

## Distribution and validation

- Given a proposed update branch already exists, when update is invoked,
  then it fails before changing target files or its selected branch.
- Given an existing adoption marker, when copy is repeated, then its original
  marker is retained even when existing files are skipped or force is used.
- Given uncommitted distributed source content (including untracked files),
  when copy/update runs, then it refuses before target mutation; unrelated
  excluded history does not affect the distributed snapshot.
- Given project text containing dollar signs, at signs, quotes, slashes or
  backslashes, when copy substitutes it, then the literal text is preserved.
- Given a model identifier containing a backslash, when configuration is
  written and parsed, then the identifier is unchanged.
- Given an expired active batch on its execution branch, when validated,
  then execution is rejected; historical completed records remain readable.
- Given an out-of-scope committed change on a batch branch, when validated,
  then it fails even if its record says post_reviewed.
- Given a Current register entry with placeholder source evidence, when
  checked, then it fails; unfilled template rows remain valid forms.
- Given a selected PR base, when GitHub delivery is requested, then that base
  is passed explicitly to the CLI. Given numbered document collisions, then
  auto-merge is never requested and delivery stops for local resolution.

## Verification and consumer compatibility

Given a phase is being completed, when evidence is reported, then focused,
adjacent/import and all-blocking results are distinct and carry the tested
SHA, environment, commands, counts (or unknown), exclusions and failure IDs.
Only successful completion of every declared blocking suite establishes full
Green. Expected Red, excluded, unrun, environment-blocked and collection
errors are not successes. Baseline comparison records new/resolved failures
and unassessed suites separately from root-cause counts.

Given module splitting, when reviewed, then static consumer inventory includes
private names and dynamic-loading limitations, and consumer import smoke,
adjacent regression and final all-blocking runs are supplied. Spec/behavior/
assertion/exclusion changes must be visible to the reviewer.

## Structure and routing

Given no live settings or a disabled large-change section, when review is
routed, then the existing review isolation/model is retained.
Given enabled large-change settings, when any measured condition strictly
exceeds its threshold, or the configured cross-module trigger applies, then
the override isolation/model is selected for an already-required review.
Defaults offered by the form: 300 implementation lines, 500 added+deleted
lines, 5 files, cross-module trigger enabled, separate_context override.
Values exactly at thresholds do not trigger. Both base and head file lengths
are considered; renames count as delete/add for conservative measurement.
Deleted files still contribute. Binary/undecodable content, missing module
classification, dirty worktrees or unavailable measurements are unknown,
never a small-change verdict; enabled review escalates to ask when unknown
and no known condition already triggers the stronger route.

Given invalid settings, when parsed, then a nonzero error is returned. No
provider is invoked. Review budget exhaustion or unavailable isolation must
not silently downgrade review. Optional token budget is a host instruction,
not a claim that this tool measures or enforces model usage.

Given configured structure budgets, when changed source is reported, then
private/legacy implementations are included and threshold exceedances require
split, rationale, follow-up owner/deadline, or human exception. Counts/imports
are mechanical where supported; responsibilities and dynamic edges remain
review judgments. Unknown metrics are explicitly unknown.

Given adopter-specific layout/test commands/settings, when later sync occurs,
then they remain in target-owned conventions/settings. Shared architecture
documents contain generic rules, not fields adopters must overwrite.
