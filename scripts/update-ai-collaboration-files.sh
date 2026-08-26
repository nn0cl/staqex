#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/update-ai-collaboration-files.sh --target PATH [options]

Pulls later AI-human collaboration template updates into a repository that
already adopted the template (via copy-ai-collaboration-files.sh).

Template process and context files are template-authoritative: if the
target's copy differs from the template's current copy, the template's
version wins. Project facts and extra rules live in the target-owned
docs/collaboration/project-conventions.md, which this script never
overwrites. Before the first overwrite of customized AGENTS.md / CLAUDE.md
after this policy, move those facts into project-conventions.md (see
docs/templates/contract-file-sync-prompt.md).

A file the target deleted since the last sync, where the template changed it
again afterward, is not silently resolved either way: with an interactive
terminal, the script asks whether to restore it (default: restore); without
one (or with --non-interactive), it restores by default. The final report
lists the actual outcome for every affected file. Files listed in the
target's .collaboration-template-ignore are never touched, regardless of
tier.

This script never commits to the target's trunk branch. It creates a
dedicated branch, commits the result there, and (when possible) opens a pull
request, per docs/collaboration/branch-commit-pr-discipline.md.

The delivery route can be selected interactively or explicitly. GitHub mode
pushes the branch and opens a pull request; --merge-pr additionally requests
GitHub auto-merge after required checks pass. Local mode creates and commits a
local branch without pushing it. The base branch can be selected with
--base-branch. The provider-neutral --subagent option records whether a
subagent handoff is requested; this script does not choose or invoke an LLM
provider. Day-to-day review and implementation routing lives in the
target-owned docs/collaboration/runtime-routing.toml created by
scripts/configure-ai-collaboration.sh; this sync never overwrites that file.

Options:
  --target PATH        Target repository directory. Required.
  --source PATH         Local checkout of the template repository to pull
                        updates from. Defaults to this script's own repo.
  --branch-prefix TEXT  Branch name prefix. Default: process/update-collab-template
  --delivery MODE       github or local. If omitted in a TTY, ask; otherwise
                        default to local. Legacy --no-pr selects local.
  --base-branch BRANCH  Branch to branch from. If omitted in a TTY, ask from
                        local branches; otherwise use the current branch.
  --merge-pr            In github mode, request auto-merge after CI passes.
                        Never merges without this explicit option.
  --subagent MODE       ask, yes, or no. In a TTY, ask is interactive;
                        otherwise ask defaults to no.
  --no-pr               Legacy alias for --delivery local.
  --non-interactive     Never prompt for locally-deleted-but-upstream-changed
                        files; always take the default (restore).
  --dry-run             Report planned actions without changing anything.
  -h, --help            Show this help.
USAGE
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

target=""
source_repo="$repo_root"
branch_prefix="process/update-collab-template"
no_pr=false
delivery_mode=""
base_branch=""
merge_pr=false
subagent_mode="ask"
dry_run=false
non_interactive=false

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      target="${2:-}"
      shift 2
      ;;
    --source)
      source_repo="${2:-}"
      shift 2
      ;;
    --branch-prefix)
      branch_prefix="${2:-}"
      shift 2
      ;;
    --no-pr)
      no_pr=true
      delivery_mode="local"
      shift
      ;;
    --delivery)
      delivery_mode="${2:-}"
      shift 2
      ;;
    --base-branch)
      base_branch="${2:-}"
      shift 2
      ;;
    --merge-pr)
      merge_pr=true
      if [ -z "$delivery_mode" ]; then
        delivery_mode="github"
      fi
      shift
      ;;
    --subagent)
      subagent_mode="${2:-}"
      shift 2
      ;;
    --non-interactive)
      non_interactive=true
      shift
      ;;
    --dry-run)
      dry_run=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$delivery_mode" in
  ""|github|local) ;;
  *) echo "--delivery must be github or local: $delivery_mode" >&2; exit 2 ;;
esac

case "$subagent_mode" in
  ask|yes|no) ;;
  *) echo "--subagent must be ask, yes, or no: $subagent_mode" >&2; exit 2 ;;
esac

if [ "$no_pr" = true ] && [ "$delivery_mode" = "github" ]; then
  echo "--no-pr conflicts with --delivery github." >&2
  exit 2
fi

if [ "$merge_pr" = true ] && [ "$delivery_mode" = "local" ]; then
  echo "--merge-pr requires --delivery github." >&2
  exit 2
fi

if [ -z "$target" ]; then
  echo "--target is required." >&2
  usage >&2
  exit 2
fi

if [ ! -d "$target" ]; then
  echo "Target directory does not exist: $target" >&2
  exit 1
fi

target="$(cd "$target" && pwd)"
source_repo="$(cd "$source_repo" && pwd)"

if ! git -C "$target" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Target is not a git repository: $target" >&2
  exit 1
fi

if ! git -C "$source_repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Source is not a git repository: $source_repo" >&2
  exit 1
fi

if [ "$dry_run" != true ] && [ -n "$(git -C "$target" status --porcelain)" ]; then
  echo "Target has uncommitted changes; commit, stash, or clean before syncing." >&2
  exit 1
fi

is_interactive_setup() {
  [ "$non_interactive" != true ] && [ -t 0 ] && [ -t 1 ]
}

prompt_choice() {
  local prompt="$1" default_value="$2" answer=""
  if ! is_interactive_setup; then
    printf '%s\n' "$default_value"
    return
  fi
  read -r -p "$prompt" answer || true
  printf '%s\n' "${answer:-$default_value}"
}

select_delivery_mode() {
  if [ -n "$delivery_mode" ]; then
    return
  fi
  if is_interactive_setup; then
    echo "Select delivery route:" >&2
    echo "  1) github - push, create PR, and optionally auto-merge" >&2
    echo "  2) local  - create a local branch for review; do not push" >&2
    case "$(prompt_choice 'Choice [2]: ' '2')" in
      1|github) delivery_mode="github" ;;
      2|local|"") delivery_mode="local" ;;
      *) echo "Invalid delivery choice." >&2; exit 2 ;;
    esac
  else
    delivery_mode="local"
  fi
}

select_subagent_mode() {
  if [ "$subagent_mode" != ask ]; then
    return
  fi
  if is_interactive_setup; then
    echo "Create a provider-neutral subagent handoff request?" >&2
    echo "  1) yes - record a subagent request in the output and PR body" >&2
    echo "  2) no  - continue with one agent" >&2
    case "$(prompt_choice 'Choice [2]: ' '2')" in
      1|yes) subagent_mode="yes" ;;
      2|no|"") subagent_mode="no" ;;
      *) echo "Invalid subagent choice." >&2; exit 2 ;;
    esac
  else
    subagent_mode="no"
  fi
}

select_base_branch() {
  local current_branch branch_choice branches index
  current_branch="$(git -C "$target" branch --show-current)"
  if [ -n "$base_branch" ]; then
    git -C "$target" show-ref --verify --quiet "refs/heads/$base_branch" || {
      echo "Base branch does not exist locally: $base_branch" >&2
      exit 1
    }
  elif is_interactive_setup; then
    branches=()
    while IFS= read -r branch; do
      branches+=("$branch")
    done < <(git -C "$target" for-each-ref --format='%(refname:short)' refs/heads/)
    echo "Select the local base branch (current: $current_branch):" >&2
    for index in "${!branches[@]}"; do
      echo "  $((index + 1))) ${branches[$index]}" >&2
    done
    branch_choice="$(prompt_choice "Choice [$(( ${#branches[@]} ))]: " "$(( ${#branches[@]} ))")"
    if [[ "$branch_choice" =~ ^[0-9]+$ ]] && [ "$branch_choice" -ge 1 ] && [ "$branch_choice" -le "${#branches[@]}" ]; then
      base_branch="${branches[$((branch_choice - 1))]}"
    else
      echo "Invalid base branch choice." >&2
      exit 2
    fi
  else
    base_branch="$current_branch"
  fi

  if [ "$dry_run" != true ] && [ "$current_branch" != "$base_branch" ]; then
    git -C "$target" switch "$base_branch"
  fi
}

marker="$target/.collaboration-template-version"
if [ ! -f "$marker" ]; then
  echo "Missing $marker." >&2
  echo "Run scripts/copy-ai-collaboration-files.sh once to adopt the template before updating." >&2
  exit 1
fi

old_ref="$(sed -n 's/^ref:[[:space:]]*//p' "$marker" | head -n1)"
if [ -z "$old_ref" ]; then
  echo "Could not read 'ref:' from $marker." >&2
  exit 1
fi

if ! git -C "$source_repo" cat-file -e "${old_ref}^{commit}" 2>/dev/null; then
  echo "Recorded ref $old_ref is not reachable in $source_repo." >&2
  echo "Fetch full history in the source checkout and retry." >&2
  exit 1
fi

new_ref="$(git -C "$source_repo" rev-parse HEAD)"

if [ "$old_ref" = "$new_ref" ]; then
  echo "Target is already synced to $new_ref. Nothing to do."
  exit 0
fi

select_delivery_mode
select_subagent_mode
select_base_branch

if [ "$delivery_mode" = "local" ]; then
  no_pr=true
elif [ "$merge_pr" = true ] && [ "$delivery_mode" != "github" ]; then
  echo "--merge-pr requires github delivery." >&2
  exit 2
fi

ignore_file="$target/.collaboration-template-ignore"
ignore_patterns=()
if [ -f "$ignore_file" ]; then
  while IFS= read -r line; do
    line="${line%%#*}"
    line="$(echo "$line" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')"
    [ -z "$line" ] && continue
    ignore_patterns+=("$line")
  done < "$ignore_file"
fi

is_ignored() {
  local rel="$1"
  local pattern
  for pattern in "${ignore_patterns[@]+"${ignore_patterns[@]}"}"; do
    # shellcheck disable=SC2254
    case "$rel" in
      $pattern) return 0 ;;
    esac
  done
  return 1
}

# shellcheck source=lib/collaboration-template-paths.sh
source "$script_dir/lib/collaboration-template-paths.sh"

added=()
updated=()
overwritten=()

restored=()
kept_deleted=()
collisions=()
ignored=()
unchanged_count=0

# Whether stdin/stdout are both a real terminal, i.e. an operator is present
# to answer the restore-or-keep-deleted prompt interactively.
is_interactive_tty() {
  [ "$non_interactive" != true ] && [ -t 0 ] && [ -t 1 ]
}

# Asks whether to restore a target-deleted, template-since-changed file.
# Defaults to "restore" on empty input, non-interactive mode, or no TTY, per
# the 2026-07-16 restore default.
ask_restore_or_keep_deleted() {
  local rel="$1"
  if is_interactive_tty; then
    local answer=""
    echo "Before deciding: check whether '$rel' was renamed rather than deleted" >&2
    echo "(e.g. to the target's own sequential ADR/local-issue number) elsewhere" >&2
    echo "in the repository." >&2
    read -r -p "Target deleted '$rel' but the template changed it since the last sync. Restore it? [Y/n] " answer || true
    case "$answer" in
      [nN]*) return 1 ;;
      *) return 0 ;;
    esac
  fi
  return 0
}

# Classifies a relative path as a numbered ADR or local-issue file. On match,
# sets numbered_class_dir/_num/_kind and returns 0; otherwise returns 1.
# Two different files "at the same number" (e.g. an unrelated project ADR
# 0007 and this template's own ADR 0007) diff as unrelated adds under plain
# path comparison, so this class needs its own collision check.
classify_numbered_file() {
  local rel="$1"
  numbered_class_dir=""
  numbered_class_num=""
  numbered_class_kind=""
  case "$rel" in
    docs/architecture/adr/[0-9][0-9][0-9][0-9]-*.md)
      numbered_class_dir="docs/architecture/adr"
      numbered_class_num="$(basename "$rel" | cut -c1-4)"
      numbered_class_kind="adr"
      return 0
      ;;
    docs/issues/LISS-[0-9][0-9][0-9][0-9]-*.md)
      numbered_class_dir="docs/issues"
      numbered_class_num="$(basename "$rel" | sed -n 's/^LISS-\([0-9][0-9][0-9][0-9]\)-.*/\1/p')"
      numbered_class_kind="liss"
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

# Prints the basename of an existing target file with the same number but a
# different slug, if any, and returns 0. Returns 1 if none is found.
find_number_collision() {
  local dir="$1" num="$2" kind="$3" own_basename="$4"
  local f bn
  [ -d "$target/$dir" ] || return 1
  for f in "$target/$dir"/*; do
    [ -f "$f" ] || continue
    bn="$(basename "$f")"
    [ "$bn" = "$own_basename" ] && continue
    case "$kind" in
      adr)
        case "$bn" in
          "$num"-*.md) echo "$bn"; return 0 ;;
        esac
        ;;
      liss)
        case "$bn" in
          LISS-"$num"-*.md) echo "$bn"; return 0 ;;
        esac
        ;;
    esac
  done
  return 1
}

# Prints the lowest unused number (zero-padded to 4 digits) in the target's
# own sequence for the given numbered-file class.
next_free_number() {
  local dir="$1" kind="$2"
  local max=0 f bn n
  if [ -d "$target/$dir" ]; then
    for f in "$target/$dir"/*; do
      [ -f "$f" ] || continue
      bn="$(basename "$f")"
      case "$kind" in
        adr) n="$(echo "$bn" | sed -n 's/^\([0-9][0-9][0-9][0-9]\)-.*/\1/p')" ;;
        liss) n="$(echo "$bn" | sed -n 's/^LISS-\([0-9][0-9][0-9][0-9]\)-.*/\1/p')" ;;
      esac
      [ -z "$n" ] && continue
      n=$((10#$n))
      [ "$n" -gt "$max" ] && max=$n
    done
  fi
  printf '%04d' $((max + 1))
}

list_files() {
  local base="$1"
  local rel="$2"
  local full="$base/$rel"
  [ -e "$full" ] || return 0
  if [ -d "$full" ]; then
    while IFS= read -r file_rel; do
      if is_collaboration_template_excluded "$file_rel"; then
        continue
      fi
      echo "$file_rel"
    done < <(cd "$base" && find "$rel" -type f)
  else
    if ! is_collaboration_template_excluded "$rel"; then
      echo "$rel"
    fi
  fi
}

process_file() {
  local rel="$1"

  if is_ignored "$rel"; then
    ignored+=("$rel")
    return
  fi

  local theirs_file="$source_repo/$rel"
  local ours_file="$target/$rel"
  local base_content=""
  local base_missing=false

  if ! base_content="$(git -C "$source_repo" show "$old_ref:$rel" 2>/dev/null)"; then
    base_missing=true
  fi

  if [ ! -e "$theirs_file" ]; then
    return
  fi

  if [ ! -e "$ours_file" ]; then
    if [ "$base_missing" = true ]; then
      added+=("$rel")
      if classify_numbered_file "$rel"; then
        local own_bn collision_bn
        own_bn="$(basename "$rel")"
        if collision_bn="$(find_number_collision "$numbered_class_dir" "$numbered_class_num" "$numbered_class_kind" "$own_bn")"; then
          local suggestion
          suggestion="$(next_free_number "$numbered_class_dir" "$numbered_class_kind")"
          collisions+=("$rel collides with existing $numbered_class_dir/$collision_bn (same number, different document) -- renumber one of them; next free number in target's sequence: $suggestion")
        fi
      fi
      if [ "$dry_run" != true ]; then
        mkdir -p "$(dirname "$ours_file")"
        cp "$theirs_file" "$ours_file"
      fi
    else
      if [ "$base_content" = "$(cat "$theirs_file")" ]; then
        : # target deleted it on purpose, upstream never changed it since: respect deletion.
      else
        if ask_restore_or_keep_deleted "$rel"; then
          restored+=("$rel")
          if [ "$dry_run" != true ]; then
            mkdir -p "$(dirname "$ours_file")"
            cp "$theirs_file" "$ours_file"
          fi
        else
          kept_deleted+=("$rel")
        fi
      fi
    fi
    return
  fi

  local ours_content theirs_content
  ours_content="$(cat "$ours_file")"
  theirs_content="$(cat "$theirs_file")"

  if [ "$base_missing" = false ] && [ "$ours_content" = "$base_content" ] && [ "$theirs_content" = "$base_content" ]; then
    unchanged_count=$((unchanged_count + 1))
    return
  fi

  if [ "$ours_content" = "$theirs_content" ]; then
    unchanged_count=$((unchanged_count + 1))
    return
  fi

  if [ "$base_missing" = false ] && [ "$ours_content" = "$base_content" ]; then
    # Target had not diverged from the template: a plain copy is safe
    # regardless of tier, since there is no adopter customization to lose.
    updated+=("$rel")
    if [ "$dry_run" != true ]; then
      cp "$theirs_file" "$ours_file"
    fi
    return
  fi

  if [ "$base_missing" = false ] && [ "$theirs_content" = "$base_content" ]; then
    unchanged_count=$((unchanged_count + 1))
    return
  fi

  # Both sides changed since the marker commit.
  # Template is fully authoritative for shipped files. Project facts belong
  # in docs/collaboration/project-conventions.md, which is excluded.
  overwritten+=("$rel")
  if [ "$dry_run" != true ]; then
    mkdir -p "$(dirname "$ours_file")"
    cp "$theirs_file" "$ours_file"
  fi
}

for rel in "${collaboration_template_paths[@]}"; do
  while IFS= read -r file_rel; do
    [ -z "$file_rel" ] && continue
    process_file "$file_rel"
  done < <(list_files "$source_repo" "$rel")
done

print_list() {
  local title="$1"
  shift
  [ "$#" -eq 0 ] && return
  echo "$title"
  local item
  for item in "$@"; do
    echo "  - $item"
  done
}

echo "Source: $source_repo ($old_ref -> $new_ref)"
echo "Target: $target"
echo "Delivery: $delivery_mode (base branch: $base_branch)"
echo "Subagent handoff: $subagent_mode"
if [ "$subagent_mode" = "yes" ]; then
  echo "Subagent request: prepare a provider-neutral handoff for branch review;"
  echo "  the host agent must choose and launch any actual subagent separately."
fi
echo
print_list "Added (new upstream files):" "${added[@]+"${added[@]}"}"
print_list "Updated (target had not diverged from the template):" "${updated[@]+"${updated[@]}"}"
print_list "Overwritten (template is authoritative -- target had diverged):" "${overwritten[@]+"${overwritten[@]}"}"
print_list "Restored (was deleted locally; template changed it since last sync):" "${restored[@]+"${restored[@]}"}"
print_list "Kept deleted (operator decision):" "${kept_deleted[@]+"${kept_deleted[@]}"}"
print_list "NUMBER COLLISIONS (manual renumbering required):" "${collisions[@]+"${collisions[@]}"}"
print_list "Ignored (per .collaboration-template-ignore):" "${ignored[@]+"${ignored[@]}"}"
echo "Unchanged: $unchanged_count file(s)"

total_changes=$(( ${#added[@]} + ${#updated[@]} + ${#overwritten[@]} + ${#restored[@]} ))

if [ "$dry_run" = true ]; then
  echo
  echo "Dry run: no branch, commit, or PR created."
  exit 0
fi

if [ "$total_changes" -eq 0 ]; then
  echo
  echo "No file changes to apply; only advancing the sync marker."
fi

branch_name="${branch_prefix}-$(date +%Y%m%d)-${new_ref:0:8}"
if git -C "$target" show-ref --verify --quiet "refs/heads/$branch_name"; then
  echo "Branch $branch_name already exists in target; delete it or rerun with a different --branch-prefix." >&2
  exit 1
fi

git -C "$target" switch -c "$branch_name"

source_origin="$(git -C "$source_repo" remote get-url origin 2>/dev/null || echo "$source_repo")"
cat > "$marker" <<MARKER
# Records which commit of the AI-human collaboration template this project
# last synced against. Read by scripts/update-ai-collaboration-files.sh.
# Do not edit by hand except to correct the source.
source: $source_origin
ref: $new_ref
MARKER

git -C "$target" add -A
git -C "$target" commit -m "chore: sync collaboration template to ${new_ref:0:8}

Added: ${#added[@]}, updated: ${#updated[@]}, overwritten: ${#overwritten[@]}, restored: ${#restored[@]}, kept deleted: ${#kept_deleted[@]}, number collisions: ${#collisions[@]}.
See PR description or this commit's file list for details." >/dev/null

echo
echo "Committed sync on branch $branch_name."

if [ "${#collisions[@]}" -gt 0 ]; then
  echo "Manual resolution needed before merging (see NUMBER COLLISIONS above)."
fi

if [ "$no_pr" = true ]; then
  echo "Local review mode: branch $branch_name was committed locally and not pushed."
  echo "Review it against base branch $base_branch, then choose the branch for the next local action."
  exit 0
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found. Push and open a PR manually:"
  echo "  git -C \"$target\" push -u origin $branch_name"
  exit 0
fi

if ! git -C "$target" remote get-url origin >/dev/null 2>&1; then
  echo "Target has no 'origin' remote. Push and open a PR manually once one is configured."
  exit 0
fi

git -C "$target" push -u origin "$branch_name"

pr_body="$(cat <<BODY
Sync from collaboration template ${old_ref:0:8} -> ${new_ref:0:8}.

- Delivery route: github PR
- Base branch: $base_branch
- Subagent handoff requested: $subagent_mode
- Added: ${#added[@]}
- Updated (target had not diverged): ${#updated[@]}
- Overwritten (template authoritative): ${#overwritten[@]}
- Restored (was deleted locally, template changed since): ${#restored[@]}
- Kept deleted (operator decision): ${#kept_deleted[@]}
- Number collisions needing manual renumbering: ${#collisions[@]}
- Ignored: ${#ignored[@]}

Project facts belong in docs/collaboration/project-conventions.md (never
overwritten). Move any remaining facts out of AGENTS.md / CLAUDE.md before
merging this overwrite.

This branch follows docs/collaboration/branch-commit-pr-discipline.md: it
must pass CI before merge and should not be merged with unresolved NUMBER
COLLISIONS items.
BODY
)"

pr_url="$(cd "$target" && gh pr create --title "chore: sync collaboration template to ${new_ref:0:8}" --body "$pr_body")"
echo "Created pull request: $pr_url"

if [ "$merge_pr" = true ]; then
  echo "Requesting GitHub auto-merge after required checks pass..."
  (cd "$target" && gh pr merge "$pr_url" --auto --squash --delete-branch)
fi
