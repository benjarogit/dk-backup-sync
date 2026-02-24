#!/usr/bin/env bash
# Erstellt changelog.txt aus Git-Commits seit letztem Tag.
# Usage: ./changelog_entry.sh 1.0.22
# Repo: https://github.com/benjarogit/dk-backup-sync
set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"
VERSION="${1:-}"
if [ -z "$VERSION" ]; then
  echo "Usage: ./changelog_entry.sh <version>"
  echo "Example: ./changelog_entry.sh 1.0.22"
  exit 1
fi
VERSION="${VERSION#v}"

# Letzten Tag finden (Commits seit diesem Tag)
PREV_TAG=""
for t in $(git tag -l 'v*' | sort -V); do
  [ "$t" = "v$VERSION" ] && continue
  case "$(printf '%s\n%s\n' "v$VERSION" "$t" | sort -V | head -1)" in
    "v$VERSION") break ;;
    *) PREV_TAG="$t" ;;
  esac
done

DATE=$(date +%Y-%m-%d)
COMMITS=""
if [ -n "$PREV_TAG" ]; then
  COMMITS_RAW=$(git log "$PREV_TAG"..HEAD --pretty=format:"- %s" 2>/dev/null || true)
  if [ -n "$COMMITS_RAW" ]; then
    COMMITS=$(echo "$COMMITS_RAW" | while read -r line; do
      if [[ "$line" =~ ^-\ Release\ [0-9]+\.[0-9]+\.[0-9]+ ]]; then continue; fi
      if [[ "$line" =~ ^-\ Update\ repo\ output ]]; then
        echo "- Plugin- und Repo-Build aktualisiert."
        continue
      fi
      echo "$line"
    done | sort -u)
  fi
fi
if [ -z "$(echo "$COMMITS" | tr -d '\n' | tr -d ' ')" ]; then
  COMMITS="- Plugin- und Repo-Updates seit ${PREV_TAG:-letztem Release}."
fi

# Neuer Block (neueste Version oben)
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT
cat > "$TMP" << BLOCK
Version $VERSION – $DATE

$COMMITS

BLOCK

# changelog.txt: Neuer Block oben einfügen
CHANGELOG_TXT="changelog.txt"
if [ -f "$CHANGELOG_TXT" ]; then
  EXISTING=$(cat "$CHANGELOG_TXT")
  { cat "$TMP"; echo ""; printf '%s' "$EXISTING"; } > "$CHANGELOG_TXT"
else
  cat "$TMP" > "$CHANGELOG_TXT"
fi

echo "changelog.txt: Eintrag für $VERSION ergänzt (aus Git-Commits seit ${PREV_TAG:-Anfang})."
