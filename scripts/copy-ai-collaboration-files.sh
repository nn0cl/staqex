#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/copy-ai-collaboration-files.sh --target PATH [options]

Copies the AI-human collaboration template files into another repository.
Existing files are skipped by default so an existing project's architecture and
specifications are not overwritten.

Options:
  --target PATH          Target repository directory. Required.
  --project-name TEXT    Replace generic project-name placeholders.
  --domain-summary TEXT  Replace generic one-line domain summary placeholders.
  --stack TEXT           Replace generic stack placeholders.
  --force                Overwrite existing files that are part of this template.
  --dry-run              Print planned actions without copying.
  -h, --help             Show this help.
USAGE
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

target=""
project_name=""
domain_summary=""
stack=""
force=false
dry_run=false

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      target="${2:-}"
      shift 2
      ;;
    --project-name)
      project_name="${2:-}"
      shift 2
      ;;
    --domain-summary)
      domain_summary="${2:-}"
      shift 2
      ;;
    --stack)
      stack="${2:-}"
      shift 2
      ;;
    --force)
      force=true
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

# shellcheck source=lib/collaboration-template-paths.sh
source "$script_dir/lib/collaboration-template-paths.sh"
paths=("${collaboration_template_paths[@]}")

copied_files=()

copy_path() {
  local rel="$1"
  local src="$repo_root/$rel"
  local dest="$target/$rel"

  if [ ! -e "$src" ]; then
    echo "Missing template path: $rel" >&2
    exit 1
  fi

  if [ -d "$src" ]; then
    echo "merge $rel"
    if [ "$dry_run" = true ]; then
      return
    fi

    mkdir -p "$dest"
    while IFS= read -r src_file; do
      local subpath="${src_file#$src/}"
      local rel_file="$rel/$subpath"
      local dest_file="$dest/$subpath"
      if is_collaboration_template_excluded "$rel_file"; then
        echo "skip template-history $rel_file"
        continue
      fi
      if [ -e "$dest_file" ] && [ "$force" != true ]; then
        echo "skip existing $rel_file"
        continue
      fi
      mkdir -p "$(dirname "$dest_file")"
      cp "$src_file" "$dest_file"
      copied_files+=("${dest_file#$target/}")
    done < <(find "$src" -type f)
  else
    if [ -e "$dest" ] && [ "$force" != true ]; then
      echo "skip existing $rel"
      return
    fi

    echo "copy $rel"
    if [ "$dry_run" = true ]; then
      return
    fi

    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    copied_files+=("$rel")
  fi
}

escape_perl_replacement() {
  printf '%s' "$1" | sed 's/[\/&]/\\&/g'
}

write_project_conventions() {
  local form="$repo_root/docs/templates/project-conventions.md"
  local dest="$target/docs/collaboration/project-conventions.md"

  if [ ! -f "$form" ]; then
    echo "Missing template: docs/templates/project-conventions.md" >&2
    exit 1
  fi

  if [ -e "$dest" ]; then
    echo "skip existing docs/collaboration/project-conventions.md"
    return
  fi

  echo "create docs/collaboration/project-conventions.md"
  if [ "$dry_run" = true ]; then
    return
  fi

  mkdir -p "$(dirname "$dest")"
  cp "$form" "$dest"

  if [ -n "$project_name" ]; then
    perl -0pi -e "s/<PROJECT_NAME>/$(escape_perl_replacement "$project_name")/g" "$dest"
  fi
  if [ -n "$domain_summary" ]; then
    perl -0pi -e "s/<one-line domain summary>/$(escape_perl_replacement "$domain_summary")/g" "$dest"
  fi
  if [ -n "$stack" ]; then
    perl -0pi -e "s/<FILL IN: e\\.g\\. backend language, frontend framework, package manager>/$(escape_perl_replacement "$stack")/g" "$dest"
  fi
}

write_version_marker() {
  [ "$dry_run" = true ] && return

  local source_ref
  source_ref="$(git -C "$repo_root" rev-parse HEAD 2>/dev/null || echo "unknown")"
  local source_origin
  source_origin="$(git -C "$repo_root" remote get-url origin 2>/dev/null || echo "$repo_root")"

  cat > "$target/.collaboration-template-version" <<MARKER
# Records which commit of the AI-human collaboration template this project
# last synced against. Read by scripts/update-ai-collaboration-files.sh.
# Do not edit by hand except to correct the source.
source: $source_origin
ref: $source_ref
MARKER
}

for rel in "${paths[@]}"; do
  copy_path "$rel"
done

write_project_conventions
write_version_marker

cat <<SUMMARY

Done.
Target: $target
Existing files were $([ "$force" = true ] && echo "overwritten when matched" || echo "left unchanged")
Recorded sync point in .collaboration-template-version for future updates.

Next:
  Fill docs/collaboration/project-conventions.md (copy may have filled name/stack).
  scripts/configure-ai-collaboration.sh --target "$target"
  cd "$target"
  scripts/init-llm-context.sh .

Later, to pull in template updates:
  scripts/update-ai-collaboration-files.sh --target "$target"
SUMMARY
