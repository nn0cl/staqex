# Validate only distributed source paths; never stamp a dirty tree as HEAD.
# Requires collaboration-template-paths.sh to have been sourced first.
require_clean_template_source() {
  local root="$1" rel
  git -C "$root" rev-parse --verify HEAD >/dev/null || return 1
  while IFS= read -r -d '' rel; do
    if ! is_collaboration_template_excluded "$rel"; then
      echo "Uncommitted distributed source: $rel. Commit it before distribution." >&2
      return 1
    fi
  done < <(
    git -C "$root" diff --name-only -z HEAD -- "${collaboration_template_paths[@]}"
    git -C "$root" ls-files --others -z -- "${collaboration_template_paths[@]}"
  )
}
