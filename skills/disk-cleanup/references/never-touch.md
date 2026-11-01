# Never-touch list (Bucket C)

If any of these turn up during a scan, don't offer them as deletion candidates — don't even
make the user say no. Just don't mention them as cleanup opportunities at all (noting their
existence is fine if relevant context, offering to delete them is not).

## Secrets and credentials
- `.env`, `.env.*`, or any dotenv-style file — these routinely hold real API keys and database
  credentials, including inside projects that otherwise look fully disposable (a project's
  `node_modules` is fair game; its `.env` sitting right next to it is not).
- `~/.ssh/*`, `~/.aws/*`, `~/.config/gcloud/*`, any `*.pem`, `*.key`, `id_rsa*`, or similar key
  material.
- `~/Library/Keychains/*`.
- Anything that looks like a credentials/secrets file by name, regardless of location.

## Source and user-authored content
- Tracked source files inside a git repository. Build artifacts and dependency trees *inside*
  a repo (`node_modules`, `build/`, `.next/`) are Bucket A; the actual source is not, ever.
- Anything in `~/Documents`, `~/Desktop`, `~/Pictures`, `~/Downloads` that isn't a verified,
  specific duplicate or a confirmed-already-applied installer. These directories routinely hold
  irreplaceable personal material (financial records, immigration/legal paperwork, one-of-a-
  kind downloads) — even a "stale, never opened, probably junk" heuristic isn't good enough
  justification on its own. This is Bucket B, reviewed item-by-item, not Bucket C exactly, but
  treat it with Bucket-C caution: never bulk-delete based on age or access-time heuristics
  alone (macOS's `kMDItemLastUsedDate` is often null/unreliable anyway, so don't trust it as a
  staleness signal).

## Data that doesn't regenerate
- Database data directories, Docker named volumes, or any VM/container persistent storage that
  the user hasn't explicitly said to wipe. Removing the image/container that *uses* this data
  (Bucket A) is different from removing the data itself (Bucket C) — know which one a command
  actually does before running it. `docker system prune --volumes` only removes *unused*
  volumes, which is a reasonable default, but confirm with `docker volume ls` rather than
  assuming.
- Photos library, Mail downloads/attachments store, Messages attachments — these back real
  user content even though they live under `~/Library`.

## System scope
- Nothing outside the user's home directory, and nothing requiring `sudo`, unless the user
  explicitly asks for that specific action and is told what it does first. This skill operates
  within the current user's own files.
- Local Time Machine snapshots (`tmutil listlocalsnapshots /`) — mention if present, but don't
  thin or delete them without the user asking; they're usually not the issue, and removing them
  has consequences for backup recovery.

## General principle
When in doubt about whether something is Bucket A, B, or C, treat it as Bucket B at worst and
Bucket C if there's any chance it holds unique data or secrets. The cost of asking one extra
question is near zero; the cost of deleting someone's immigration paperwork or leaking a
credential into a `rm -rf` is not.
