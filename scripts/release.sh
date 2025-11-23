#!/usr/bin/env bash
# POSIX shell release helper script
# Usage: ./scripts/release.sh v0.1.1 "Release v0.1.1" --push --gh

TAG="$1"
MSG="${2:-Release $TAG}"
shift 2 || true
PUSH=false
GH=false
ALLOW_DIRTY=false

for arg in "$@"; do
  case "$arg" in
    --push) PUSH=true ;;
    --gh) GH=true ;;
    --allow-dirty) ALLOW_DIRTY=true ;;
  esac
done

command -v git >/dev/null 2>&1 || { echo "git is required" >&2; exit 1; }

if [ -z "$TAG" ]; then
  echo "Usage: $0 <tag> [message] [--push] [--gh] [--allow-dirty]" >&2
  exit 1
fi

if [ "$ALLOW_DIRTY" = false ]; then
  if [ -n "$(git status --porcelain)" ]; then
    echo "Working tree is dirty. Commit or stash changes, or pass --allow-dirty." >&2
    git status --porcelain
    exit 2
  fi
fi

echo "Creating annotated tag $TAG"
if ! git tag -a "$TAG" -m "$MSG"; then
  echo "Failed to create tag" >&2
  exit 3
fi

if [ "$PUSH" = true ]; then
  echo "Pushing tag $TAG to origin"
  if ! git push origin "$TAG"; then
    echo "Failed to push tag" >&2
    exit 4
  fi
fi

if [ "$GH" = true ]; then
  if ! command -v gh >/dev/null 2>&1; then
    echo "gh CLI not found; skipping GitHub release creation" >&2
  else
    if [ -f RELEASE_NOTES.md ]; then
      gh release create "$TAG" --title "$TAG" --notes-file RELEASE_NOTES.md || { echo "gh release failed" >&2; exit 5; }
    else
      gh release create "$TAG" --title "$TAG" || { echo "gh release failed" >&2; exit 5; }
    fi
  fi
fi

echo "Done."
