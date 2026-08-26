#!/usr/bin/env bash
# Create or refresh docs/collaboration/runtime-routing.toml for an adopting
# repository. Does not call an LLM, store secrets, or invoke a subagent.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/configure-ai-collaboration.sh --target PATH [options]

Writes target-owned docs/collaboration/runtime-routing.toml from
docs/templates/runtime-routing.toml. Records how agent-to-agent review and
implementation should be isolated and which optional host-displayed model
identifiers to use. The human Adjudicator remains the approval authority.

Options:
  --target PATH                      Target repository. Required.
  --review-isolation MODE            same_context, separate_context, or ask.
  --review-model TEXT                Optional host-displayed model identifier.
  --implementation-isolation MODE    host, separate_context, or ask.
  --implementation-model TEXT        Optional host-displayed model identifier.
  --force                            Replace an existing live file.
  --dry-run                          Print planned actions without writing.
  --non-interactive                  Never prompt; use flags or defaults.
  -h, --help                         Show this help.

Defaults without a TTY, or with --non-interactive and omitted flags:
  review isolation           same_context
  implementation isolation   host
  model identifiers          empty (capability-class routing)

Examples:
  scripts/configure-ai-collaboration.sh --target /path/to/repo
  scripts/configure-ai-collaboration.sh --target /path/to/repo --non-interactive
  scripts/configure-ai-collaboration.sh --target /path/to/repo \
    --review-isolation separate_context \
    --implementation-isolation host \
    --force
USAGE
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
template_repo="$(cd "$script_dir/.." && pwd)"

target=""
review_isolation=""
review_model=""
review_model_set=false
implementation_isolation=""
implementation_model=""
implementation_model_set=false
force=false
dry_run=false
non_interactive=false

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      target="${2:-}"
      shift 2
      ;;
    --review-isolation)
      review_isolation="${2:-}"
      shift 2
      ;;
    --review-model)
      review_model="${2:-}"
      review_model_set=true
      shift 2
      ;;
    --implementation-isolation)
      implementation_isolation="${2:-}"
      shift 2
      ;;
    --implementation-model)
      implementation_model="${2:-}"
      implementation_model_set=true
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
    --non-interactive)
      non_interactive=true
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

validate_review_isolation() {
  case "$1" in
    same_context|separate_context|ask) return 0 ;;
    *) echo "--review-isolation must be same_context, separate_context, or ask: $1" >&2; return 1 ;;
  esac
}

validate_implementation_isolation() {
  case "$1" in
    host|separate_context|ask) return 0 ;;
    *) echo "--implementation-isolation must be host, separate_context, or ask: $1" >&2; return 1 ;;
  esac
}

validate_model_text() {
  local value="$1" label="$2"
  if printf '%s' "$value" | grep -q '[[:cntrl:]]'; then
    echo "$label must not contain control characters." >&2
    return 1
  fi
  if printf '%s' "$value" | grep -q '"'; then
    echo "$label must not contain double quotes." >&2
    return 1
  fi
}

toml_escape() {
  printf '%s' "$1" | sed 's/\\/\\\\/g'
}

find_form() {
  local candidate
  for candidate in \
    "$target/docs/templates/runtime-routing.toml" \
    "$template_repo/docs/templates/runtime-routing.toml"
  do
    if [ -f "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

select_review_isolation() {
  if [ -n "$review_isolation" ]; then
    validate_review_isolation "$review_isolation"
    return
  fi
  if is_interactive_setup; then
    echo "Review isolation for agent-to-agent review" >&2
    echo "(does not replace the human Adjudicator):" >&2
    echo "  1) same_context     - review in this session using the same-context template" >&2
    echo "  2) separate_context - host launches a subagent in a clean context" >&2
    echo "  3) ask              - ask the Adjudicator each time" >&2
    case "$(prompt_choice 'Choice [1]: ' '1')" in
      1|same_context|"") review_isolation="same_context" ;;
      2|separate_context) review_isolation="separate_context" ;;
      3|ask) review_isolation="ask" ;;
      *) echo "Invalid review isolation choice." >&2; exit 2 ;;
    esac
  else
    review_isolation="same_context"
  fi
  validate_review_isolation "$review_isolation"
}

select_review_model() {
  if [ "$review_model_set" = true ]; then
    return
  fi
  if is_interactive_setup; then
    review_model="$(prompt_choice 'Review model identifier as displayed by the host (empty = capability class only): ' '')"
  else
    review_model=""
  fi
}

select_implementation_isolation() {
  if [ -n "$implementation_isolation" ]; then
    validate_implementation_isolation "$implementation_isolation"
    return
  fi
  if is_interactive_setup; then
    echo "Implementation isolation:" >&2
    echo "  1) host             - current agent implements" >&2
    echo "  2) separate_context - host launches an implementer subagent" >&2
    echo "  3) ask              - ask the Adjudicator each time" >&2
    case "$(prompt_choice 'Choice [1]: ' '1')" in
      1|host|"") implementation_isolation="host" ;;
      2|separate_context) implementation_isolation="separate_context" ;;
      3|ask) implementation_isolation="ask" ;;
      *) echo "Invalid implementation isolation choice." >&2; exit 2 ;;
    esac
  else
    implementation_isolation="host"
  fi
  validate_implementation_isolation "$implementation_isolation"
}

select_implementation_model() {
  if [ "$implementation_model_set" = true ]; then
    return
  fi
  if is_interactive_setup; then
    implementation_model="$(prompt_choice 'Implementation model identifier as displayed by the host (empty = capability class only): ' '')"
  else
    implementation_model=""
  fi
}

form="$(find_form || true)"
if [ -z "$form" ]; then
  echo "Missing template: docs/templates/runtime-routing.toml" >&2
  echo "Copy the collaboration template into the target first." >&2
  exit 1
fi

dest_dir="$target/docs/collaboration"
dest="$dest_dir/runtime-routing.toml"

if [ ! -d "$dest_dir" ]; then
  echo "Missing directory: docs/collaboration (is the template installed?)" >&2
  exit 1
fi

select_review_isolation
select_review_model
select_implementation_isolation
select_implementation_model

validate_model_text "$review_model" "--review-model"
validate_model_text "$implementation_model" "--implementation-model"

echo "Form:     $form"
echo "Target:   $dest"
echo "Review:   isolation=$review_isolation model=${review_model:-"(capability class)"}"
echo "Implement: isolation=$implementation_isolation model=${implementation_model:-"(capability class)"}"

if [ -f "$dest" ] && [ "$force" != true ]; then
  echo "Already exists: $dest" >&2
  echo "Re-run with --force to replace, or edit the file in place." >&2
  exit 1
fi

if [ "$dry_run" = true ]; then
  echo "Dry run: no file written."
  exit 0
fi

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

review_iso="$review_isolation"
review_mod="$(toml_escape "$review_model")"
impl_iso="$implementation_isolation"
impl_mod="$(toml_escape "$implementation_model")"

awk -v review_iso="$review_iso" -v review_mod="$review_mod" \
    -v impl_iso="$impl_iso" -v impl_mod="$impl_mod" '
  BEGIN { section = "" }
  /^\[review\]/ { section = "review"; print; next }
  /^\[implementation\]/ { section = "implementation"; print; next }
  /^\[/ { section = ""; print; next }
  section == "review" && $0 ~ /^isolation[[:space:]]*=/ {
    print "isolation = \"" review_iso "\""
    next
  }
  section == "review" && $0 ~ /^model[[:space:]]*=/ {
    print "model = \"" review_mod "\""
    next
  }
  section == "implementation" && $0 ~ /^isolation[[:space:]]*=/ {
    print "isolation = \"" impl_iso "\""
    next
  }
  section == "implementation" && $0 ~ /^model[[:space:]]*=/ {
    print "model = \"" impl_mod "\""
    next
  }
  { print }
' "$form" >"$tmp"

mv "$tmp" "$dest"
trap - EXIT

cat <<EOF

Created $dest

Agents will:
  - apply [review] isolation when an agent review packet is already required
  - apply [implementation] isolation for implementation work
  - treat empty model fields as capability-class routing
  - not treat this file as Adjudicator approval

This file is target-owned. Template sync will not overwrite it.

See docs/collaboration/runtime-routing.md
EOF
