#!/bin/sh

set -eu

repo_root=$(git rev-parse --show-toplevel)
default_branch="${DEFAULT_BRANCH:-main}"
remote_name="${REMOTE_NAME:-origin}"
push_remote="${PUSH_REMOTE:-0}"
current_branch=$(git rev-parse --abbrev-ref HEAD)

if [ "$current_branch" = "HEAD" ]; then
  echo "error: curator finalize requires a named branch, not detached HEAD" >&2
  exit 1
fi

curator_branch="${CURATOR_BRANCH:-$current_branch}"
current_worktree=$(pwd -P)
curator_worktree="${CURATOR_WORKTREE:-$current_worktree}"

if [ "$curator_branch" = "$default_branch" ]; then
  echo "error: curator finalize must run from a non-$default_branch branch" >&2
  exit 1
fi

find_branch_worktree() {
  git -C "$repo_root" worktree list --porcelain | awk -v target="refs/heads/$1" '
    $1 == "worktree" { wt = $2 }
    $1 == "branch" && $2 == target { print wt; exit }
  '
}

main_worktree=$(find_branch_worktree "$default_branch")
if [ -z "$main_worktree" ]; then
  echo "error: could not find worktree for branch $default_branch" >&2
  exit 1
fi

if [ -z "${CURATOR_WORKTREE:-}" ]; then
  detected_worktree=$(find_branch_worktree "$curator_branch")
  if [ -n "$detected_worktree" ]; then
    curator_worktree="$detected_worktree"
  fi
fi

ensure_clean() {
  worktree_path="$1"
  if [ ! -d "$worktree_path" ]; then
    echo "error: worktree does not exist: $worktree_path" >&2
    exit 1
  fi

  status_output=$(git -C "$worktree_path" status --porcelain)
  if [ -n "$status_output" ]; then
    echo "error: worktree is not clean: $worktree_path" >&2
    echo "$status_output" >&2
    exit 1
  fi
}

ensure_clean "$curator_worktree"
ensure_clean "$main_worktree"

echo "Running eval on curator branch worktree: $curator_worktree"
make -C "$curator_worktree" eval

echo "Switching main worktree to $default_branch: $main_worktree"
git -C "$main_worktree" switch "$default_branch"

echo "Fast-forward merging $curator_branch into $default_branch"
git -C "$main_worktree" merge --ff-only "$curator_branch"

echo "Running eval on $default_branch after merge"
make -C "$main_worktree" eval

if [ "$push_remote" = "1" ]; then
  echo "Pushing $default_branch to $remote_name"
  git -C "$main_worktree" push "$remote_name" "$default_branch"
fi

if [ "$curator_worktree" != "$main_worktree" ] && [ -d "$curator_worktree" ]; then
  echo "Removing merged curator worktree: $curator_worktree"
  cd /tmp
  git -C "$repo_root" worktree remove --force "$curator_worktree"
fi

if git -C "$repo_root" show-ref --verify --quiet "refs/heads/$curator_branch"; then
  echo "Deleting merged curator branch: $curator_branch"
  git -C "$repo_root" branch -D "$curator_branch"
fi

echo "Curator finalize completed for branch $curator_branch"
