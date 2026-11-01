#!/bin/bash
# One-shot, read-only disk diagnostic for the disk-cleanup skill.
# Safe to run anytime with no approval needed — makes no changes.
#
# Note: the free-space/swap/snapshot/Docker sections intentionally read real system state and
# are NOT affected by overriding $HOME (df, diskutil, sysctl, tmutil, and `docker system df` are
# machine-wide, not per-user-directory). Only the directory-size sections below are scoped to
# $HOME. That's correct for real use; if you're ever testing this script against a fake/sandboxed
# home directory, expect those specific sections to still reflect the real machine.
set -uo pipefail

echo "=== Free space ==="
df -h /System/Volumes/Data 2>/dev/null || df -h /
diskutil info / 2>/dev/null | grep -E "Container (Total|Free) Space"

echo
echo "=== Swap ==="
sysctl vm.swapusage 2>/dev/null

echo
echo "=== Local Time Machine snapshots ==="
tmutil listlocalsnapshots / 2>/dev/null || echo "(none, or tmutil unavailable)"

echo
echo "=== Home directory top-level sizes ==="
( cd "$HOME" 2>/dev/null && for d in */; do du -sh "$d" 2>/dev/null; done | sort -rh | head -20 )

echo
echo "=== Known cache / build-tool locations ==="
paths=(
  "$HOME/Library/Caches"
  "$HOME/Library/Developer/Xcode/DerivedData"
  "$HOME/Library/Developer/CoreSimulator/Devices"
  "$HOME/Library/Android/sdk"
  "$HOME/.android/avd"
  "$HOME/.gradle/caches"
  "$HOME/.cache/uv"
  "$HOME/.cache/pip"
  "$HOME/.cache/yarn"
  "$HOME/.npm"
  "$HOME/.pnpm-store"
  "$HOME/Library/Containers/com.docker.docker"
)
for p in "${paths[@]}"; do
  [ -e "$p" ] && du -sh "$p" 2>/dev/null
done

echo
echo "=== node_modules under ~/projects (top 15 by size) ==="
if [ -d "$HOME/projects" ]; then
  find "$HOME/projects" -xdev -maxdepth 6 -type d -name node_modules 2>/dev/null \
    | grep -v '/node_modules/.*/node_modules$' \
    | while IFS= read -r d; do du -sh "$d" 2>/dev/null; done \
    | sort -rh | head -15
else
  echo "(no ~/projects directory)"
fi

echo
echo "=== Docker (if installed and running) ==="
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  docker system df
  echo "--- Real on-disk size of Docker's VM disk (du, not ls -- that file is sparse) ---"
  find "$HOME/Library/Containers/com.docker.docker/Data" \( -iname "Docker.raw" -o -iname "*.qcow2" \) 2>/dev/null \
    | while IFS= read -r f; do du -h "$f"; done
  true
else
  echo "(docker not installed or not running)"
fi
exit 0
