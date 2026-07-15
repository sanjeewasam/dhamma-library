#!/usr/bin/env bash
#
# sync-tipitaka.sh — pull the Buddha Jayanti Tripiṭaka text from tipitaka.lk
# into ./static/text/ and rebuild manifest.json.
#
# The upstream text is CC BY-ND 4.0: we copy it verbatim and NEVER edit it.
# If you spot an error, report it to path.nirvana@gmail.com — do not fix it
# here; re-run this script after they publish the correction.
#
# Usage:   bash sync-tipitaka.sh
# Works in Linux, macOS, WSL, and Git-Bash on Windows. Needs: git, python3.
# Safe to re-run; incremental after the first pull.

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPSTREAM="https://github.com/pathnirvana/tipitaka.lk.git"
CACHE="$HERE/.cache/tipitaka.lk"          # git-ignore this
SUBPATH="public/static/text"
DEST="$HERE/static/text"

command -v git     >/dev/null || { echo "git not found"; exit 1; }
command -v python3 >/dev/null || { echo "python3 not found"; exit 1; }

mkdir -p "$HERE/.cache" "$DEST"

if [ ! -d "$CACHE/.git" ]; then
  echo "→ First run: cloning upstream (sparse, no blobs)…"
  git clone --filter=blob:none --sparse "$UPSTREAM" "$CACHE"
  git -C "$CACHE" sparse-checkout set "$SUBPATH" "public/static/data"
else
  echo "→ Fetching upstream updates…"
  git -C "$CACHE" fetch --filter=blob:none origin
  git -C "$CACHE" sparse-checkout set "$SUBPATH" "public/static/data"
  git -C "$CACHE" reset --hard "origin/$(git -C "$CACHE" rev-parse --abbrev-ref HEAD)"
fi

[ -d "$CACHE/$SUBPATH" ] || { echo "Upstream text not materialised. Delete .cache and re-run."; exit 1; }

echo "→ Copying *.json into $DEST (mirroring upstream)…"
rm -f "$DEST"/*.json
cp "$CACHE/$SUBPATH"/*.json "$DEST"/
COUNT=$(ls -1 "$DEST"/*.json | wc -l | tr -d ' ')
echo "  $COUNT text files synced."

echo "→ Building navigation index (books.json)…"
python3 "$HERE/build-manifest.py" --root "$HERE" --tree "$CACHE/public/static/data/tree.json"

echo "✓ Done. Review, then: git add tripitaka && git commit -m 'Sync T