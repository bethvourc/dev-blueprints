---
name: disk-cleanup
description: Check free disk space on this Mac, find what is safe to delete versus what needs a human decision, and clean it up with explicit per-category approval before anything is deleted. Covers app/browser caches, package-manager caches (npm/pnpm/yarn/pip/uv/gradle/cocoapods), node_modules and other build artifacts, Xcode DerivedData and simulators, Docker, Android SDK/emulator images, and duplicate files. Use when the user asks to free up disk space, check how much storage is left, clean up their Mac, find duplicate or stale files, or mentions running low on disk space / storage.
---

# Mac Disk Cleanup

## Mission

Find out how much disk space is free, figure out what is actually consuming it, and reclaim
space from things that are safe to delete — without ever deleting something the user didn't
explicitly approve, and without burning time or memory on inefficient scans.

This skill exists because a past cleanup session got several things wrong before getting them
right: it hashed entire directory trees instead of only same-size candidates (got OOM-killed),
it reported a sparse VM disk file's logical size as if it were real disk usage (overstated a
"60 GB problem" that was really ~6 GB), and `docker system prune -a` quietly deleted stopped
containers the user hadn't been told would be removed. Every rule below exists to not repeat
one of those mistakes. Read them once; they're short.

## The non-negotiable rule

**Never delete anything without the user explicitly approving that specific category or item
first.** Read-only investigation (df, du, find, docker system df, etc.) needs no permission —
run as much of it as needed. The moment an action would remove, overwrite, or truncate a file,
stop and get a yes first. Default to proposing in categories (with sizes) in one batched
question so the user can approve several safe categories at once instead of being asked five
separate times.

Exception to even asking: nothing. Not "it's just a cache," not "this is obviously junk." Say
what you found and why it looks safe, then wait for a yes. The one thing that's fine to do
unprompted is read-only measurement.

## Step 0 — Orient (read-only, no approval needed)

Run `scripts/disk_summary.sh`. It gathers in one pass what used to take six separate commands:
free space (both `df -h /System/Volumes/Data` and `diskutil info /`, which report in different
units — GiB vs decimal GB — mention this if the two numbers look inconsistent to the user),
swap usage, local Time Machine snapshots, the biggest top-level folders in `$HOME`, known
cache/build-tool directories, `node_modules` folders under `~/projects` (or wherever the user's
projects live), and Docker's real disk usage if Docker is installed.

If the user wants a quick check only, stop after this step and just report free space plus the
single biggest few consumers — don't go into full categorization or propose deletions unless
they ask to go further. Otherwise continue to Step 1.

## Step 1 — Report free space in plain terms

Give the user a one-line plain-language number ("you have X GB free out of Y GB"), not just
raw command output. If this isn't the first check in a session and the number has moved,
say so and say whether that's explained (active builds, Docker images, caches regenerating —
all normal) or not (worth digging into before assuming anything).

## Step 2 — Find and categorize cleanup candidates

Everything found falls into exactly one of three buckets. Get this categorization right before
proposing anything — it's the difference between a safe cleanup and a bad afternoon.

### Bucket A — Safe / regenerable
Caches and build artifacts that some tool will transparently recreate. See
`references/safe-targets.md` for the checklist of known locations and exactly how each one
regenerates. These are still subject to the non-negotiable rule — "safe" means safe to approve
in bulk via one batched question, not safe to delete without asking.

### Bucket B — Needs human review
Things a script cannot judge on its own: files in Downloads/Documents/Desktop, installers that
might or might not already be applied, large files that haven't been opened recently, candidate
duplicate files, nested/duplicate project checkouts, VM or emulator disk images that are large
because of real use rather than bloat. Never bulk-propose these the way Bucket A is proposed —
surface specifics (filename, size, why it looks like a candidate) and let the user decide
item-by-item or in a tightly-scoped group they define: verify the claim, then ask.

### Bucket C — Never touch
See `references/never-touch.md`. If something in this bucket turns up during a scan (e.g. you
notice a `.env` file sitting next to a project's `node_modules`), don't offer it as a deletion
candidate at all — don't even make the user say no to it.

## Step 3 — Propose and get approval

For Bucket A, batch related categories into a single multi-select question so the user can
approve several at once. State the size of each category and, for anything with a non-obvious
consequence (Docker prune removing stopped containers, deleting a simulator device, clearing a
tool's entire cache vs. just its contents), say what actually happens in one sentence before
they choose.

For Bucket B, propose individually or in a small explicit group, never as a blanket "delete all
of Downloads older than N days" — that pattern has a high chance of catching something that
matters (tax documents, immigration paperwork, a one-of-a-kind download) and the cost of being
wrong is much higher than the disk space saved.

## Step 4 — Execute only what was approved

Before running any delete:
- Resolve to an absolute path and confirm the path exists and is non-empty before building an
  `rm` command around it — a failed `cd` or an unset variable turning into an empty string has
  historically been the way "rm -rf" scripts delete the wrong thing. Quote every path.
- Prefer deleting the *contents* of a cache directory (`find … -mindepth 1 -maxdepth 1 … | xargs rm -rf`)
  over the directory itself when a running app expects that directory to still exist.
- For Docker, default to the tiered options in `references/safe-targets.md` (`docker image prune
  -f` for dangling layers, `docker container prune -f` for stopped containers shown by name)
  rather than reaching for `docker system prune -a --volumes` as the first move. The full sweep
  removes *all* unused images, not just dangling ones, and *all* stopped containers — it's a
  separate, higher-risk action that needs `docker system df -v` shown to the user first, not a
  default. This isn't theoretical: an earlier run of the full sweep removed three stopped
  containers the user still wanted, because the scope wasn't spelled out before running it.
  Whichever option is used, check `docker volume ls` before and after so you can tell the user
  whether named data volumes survived — they usually do, since volumes are separate from the
  images/containers that reference them, but verify rather than assume.
- macOS will sometimes refuse to delete a handful of Apple-owned cache subfolders with
  "Operation not permitted." That's expected and harmless — they're protected and tiny; don't
  try to force past it (no sudo, no chflags), just note it was skipped.
- For any file suspected of being a VM/container disk image (`.raw`, `.qcow2`, `.vdi`, `.vmdk`,
  sparse bundles) or anything else that might be sparse, always size it with `du -h`, never
  `ls -lh`. `ls -lh` reports the logical/apparent size, which for a sparse file can claim tens
  of GB more than what's actually allocated on disk. Getting this backwards is exactly what
  turned a real ~6 GB Docker issue into a reported "60 GB problem" before — verify with `du`
  before making any size claim about such a file, and before and after any action meant to
  shrink one.
- If deleting an installer/dmg/pkg on the premise that "the app is already installed," actually
  check (`ls /Applications`, or equivalent) rather than assuming — don't skip this just because
  it feels obvious.

## Step 5 — Verify and report

Re-check free space the same way as Step 0 and give a before/after number. Report, per approved
category, roughly how much was reclaimed. If the total doesn't match expectations (e.g. nothing
moved, or it moved far more than the sum of what was deleted), say so plainly rather than
rounding it off to a tidy story.

The most common real cause of "I deleted things but free space didn't move" is a local Time
Machine snapshot holding onto the deleted file's blocks — APFS can keep a deleted file's data
alive as long as a snapshot still references it, and Finder/`df` count that space as available
even though the kernel hasn't actually released it yet. Check `tmutil listlocalsnapshots /`; if
snapshots are present, `tmutil thinlocalsnapshots / <bytes-to-reclaim>` asks macOS to reclaim
space from them, and free space may take a few minutes to rise afterward even after that. Swap
usage and purgeable space in general can also make the numbers wobble by a few GB. Treat
anything else (e.g. "Spotlight is reindexing") as an unverified guess, not an explanation —
don't present it as settled unless you've actually confirmed it.

End with a short list of what's still open: Bucket B items the user hasn't decided on yet, and
anything flagged but deferred. Don't let these silently disappear between runs — carry them
into the next cleanup pass if the user brings it up again.

## Efficiency rules (apply throughout, not just in the bundled scripts)

- **Scope every scan.** Never run `find` or `du` against `/` or an unbounded tree. Pass a
  specific starting directory, and use `-xdev` so a scan of the data volume doesn't wander into
  other mounted volumes. A previous unscoped background scan got killed by macOS for using too
  much memory — that's the failure mode this avoids.
- **Filter before hashing.** When hunting for duplicate files, never hash an entire directory
  tree. Group candidate files by exact size first (a cheap `stat`), and only run `md5`/`shasum`
  on files that already share a size with at least one other file. `scripts/find_duplicates.sh`
  does this and should be used instead of writing this logic fresh each time.
- **Batch read-only checks.** When several independent measurements are needed (free space,
  swap, a handful of directory sizes), combine them into one shell invocation rather than one
  round-trip per command.
- **Don't re-measure what's already known.** If a directory's size was already checked this
  session and nothing has been deleted from it since, don't `du` it again.

## Reference files

- `references/safe-targets.md` — the checklist of common cache/build-tool locations on a dev
  Mac, what each one is, and the exact command that regenerates it. Read this when populating
  Bucket A.
- `references/never-touch.md` — the exclusion list and the reasoning behind each entry. Read
  this before proposing any deletion, not just when something looks borderline.
- `scripts/disk_summary.sh` — run first, every time. One-shot read-only diagnostic (macOS-specific).
- `scripts/find_duplicates.sh <directory> [min_size]` — efficient duplicate finder, scoped to
  one directory you pass explicitly (never pass `/` or `$HOME` as the scope without narrowing
  further — point it at `~/Downloads` or similar). Defaults to a 10M size floor.

## Platform note

This skill's bundled scripts are macOS-specific (`diskutil`, `tmutil`, BSD `stat -f`, `du -h`
conventions). The categorization framework (the three buckets, the non-negotiable approval
rule, the efficiency rules) applies on any OS; porting the scripts to Linux would mean swapping
`diskutil`/`tmutil` for `df`/`lsblk`-based checks and `stat -f%z` for `stat -c%s`.
