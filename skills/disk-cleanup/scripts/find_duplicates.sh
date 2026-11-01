#!/bin/bash
# Efficient duplicate-file finder for the disk-cleanup skill.
#
# Never hashes an entire tree: groups files by exact size first (cheap), then only runs
# md5 on files that already share a size with at least one other file. This is the approach
# that worked after a naive full-tree hash caused an OOM kill in an earlier cleanup session.
#
# Usage: find_duplicates.sh <directory> [min_size]
#   <directory>  Required. Always pass a specific, narrow directory (e.g. ~/Downloads).
#                Never pass "/" or an unqualified "$HOME" -- scope it.
#   [min_size]   Optional, default 10M. Passed straight to `find -size +SIZE`, e.g. 50M, 1G.
set -uo pipefail

dir="${1:?Usage: find_duplicates.sh <directory> [min_size]}"
minsize="${2:-10M}"

if [ ! -d "$dir" ]; then
  echo "Not a directory: $dir" >&2
  exit 1
fi

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

find "$dir" -xdev -type f -size +"$minsize" ! -path '*/.git/*' 2>/dev/null | while IFS= read -r f; do
  sz=$(stat -f%z "$f" 2>/dev/null) || continue
  printf '%s\t%s\n' "$sz" "$f"
done > "$tmp/sizes.tsv"

if [ ! -s "$tmp/sizes.tsv" ]; then
  echo "No files above $minsize found under $dir"
  exit 0
fi

# Sizes that occur more than once -- only these are worth hashing.
cut -f1 "$tmp/sizes.tsv" | sort -n | uniq -d > "$tmp/dupe_sizes.txt"

if [ ! -s "$tmp/dupe_sizes.txt" ]; then
  echo "No same-size candidates above $minsize in $dir -- nothing to hash, no duplicates by this method."
  exit 0
fi

: > "$tmp/hashes.tsv"
while IFS= read -r sz; do
  awk -F'\t' -v s="$sz" '$1==s {print $2}' "$tmp/sizes.tsv" > "$tmp/candidates.txt"
  while IFS= read -r f; do
    h=$(md5 -q "$f" 2>/dev/null) || continue
    printf '%s\t%s\n' "$h" "$f"
  done < "$tmp/candidates.txt" >> "$tmp/hashes.tsv"
done < "$tmp/dupe_sizes.txt"

echo "Duplicate groups (same content, confirmed by hash) under $dir, min size $minsize:"
sort "$tmp/hashes.tsv" | awk -F'\t' '
{
  if ($1 == prev_hash) {
    if (!printed) { print "---"; print prev_line; printed = 1 }
    print $0
  } else {
    printed = 0
  }
  prev_hash = $1; prev_line = $0
}
END { if (!printed && NR == 0) print "(no duplicates found)" }
'
