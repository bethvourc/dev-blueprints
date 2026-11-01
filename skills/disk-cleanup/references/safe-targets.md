# Safe / regenerable cleanup targets (Bucket A)

Everything here regenerates automatically or via a one-line command, so it's a reasonable
default list to propose for bulk approval. "Safe to propose in bulk" still means propose —
see the non-negotiable rule in SKILL.md. Sizes vary a lot machine to machine; always measure
rather than assume.

| Location | What it is | Regenerates via | Notes |
|---|---|---|---|
| `~/Library/Caches/*` | Per-app caches | Automatically, next time the app runs | Delete contents, not the `Caches` dir itself. A few Apple-owned subfolders will refuse deletion with "Operation not permitted" — expected, skip them, don't force. Regenerates fast if apps are actively running (seeing it back at several GB within a day of emptying it is normal, not a leak). |
| `~/Library/Caches/<Browser>` (Chrome/Firefox/Arc/etc.) | Browser cache | Automatically | Often one of the largest single contributors; safe. |
| `node_modules` anywhere under a project | JS/TS dependency tree | `npm install` / `pnpm install` / `yarn` | Confirm the project still has its lockfile and isn't mid-edit before deleting; this is about the dependency tree, never the project source. |
| `~/.pnpm-store` | pnpm's global content-addressable store | `pnpm store prune` (prunes unreferenced packages) or re-fetched automatically on next install | Prefer `pnpm store prune` over deleting the directory outright. |
| `~/.npm` (npm cache) | npm's cache | Automatically / `npm cache clean --force` | |
| `~/.cache/yarn` | Yarn cache | Automatically | |
| `~/.cache/uv` | uv's Python package cache | `uv cache clean`, or automatically on next install | Prefer the `uv` command if the CLI is present — it's accurate about what it removes; fall back to `rm -rf` only if `uv` isn't installed. |
| `~/.cache/pip` | pip's wheel/package cache | Automatically | |
| `~/Library/Caches/CocoaPods` | CocoaPods cache | `pod cache clean --all`, or automatically | |
| `~/.gradle/caches` | Gradle build cache (Android/Flutter/JVM) | Automatically, next build | Can be large (double digits of GB) after active Android/Flutter work; normal churn, not a leak. |
| `~/Library/Developer/Xcode/DerivedData/*` | Xcode build cache | Automatically, next build in Xcode | Safe to delete contents entirely; Xcode rebuilds from scratch next time, which costs build time but not data. |
| `~/Library/Developer/CoreSimulator/Devices` (unavailable only) | iOS/watchOS/tvOS simulator devices | `xcrun simctl delete unavailable` | Only removes devices tied to a runtime that's no longer installed — it's a safe no-op if nothing qualifies. Do **not** delete devices that still show as available just because they're large; a simulator with real app data installed belongs in Bucket B if the user wants it gone. |
| Docker: dangling (untagged) images and unused build cache | `docker image prune -f` | Re-pulled/rebuilt on demand | **Default to this, not `system prune -a`.** Only removes image layers nothing references — doesn't touch containers, named images, or volumes. This is the actual Bucket-A-safe Docker action. |
| Docker: stopped containers | `docker container prune -f` | Recreated via `docker compose up` / `docker run` | Still show the user which containers (name + how long stopped) before running — a container being "stopped" doesn't mean it's unwanted; it previously removed containers the user still needed, see the caveat below. |
| Project `build/`, `dist/`, `.next/`, `target/`, `out/` directories | Build output | Next build command | Only inside directories that are clearly build output (check for a sibling `src/` or a build config referencing the dir), never a directory that might itself be hand-maintained output. |
| `~/Library/Application Support/<App>/CachedExtensionVSIXs/.trash` or similar app-level trash folders | An app's own internal trash | N/A — it's already been "deleted" by the app | Safe to empty; the app already considers this gone. |

## Moderate-risk, still often safe, but size-worth-double-checking

| Location | What it is | Why it's not a blind default |
|---|---|---|
| Android SDK packages (`~/Library/Android/sdk/{platforms,system-images,build-tools}/...`) | Installed SDK components, tracked by `sdkmanager` via a `package.xml` per component | Prefer `sdkmanager --uninstall "<package>"` (list candidates with `sdkmanager --list_installed`) over `rm -rf` on the folder directly. `sdkmanager` tracks what's installed per-package; manually deleting a folder just makes it vanish from `sdkmanager --list` without necessarily confusing anything *else*, but there's no guarantee across SDK versions, so prefer the command when the CLI is available. Never hand-delete `cmdline-tools` or `tools` — that can break `sdkmanager` itself. |
| `~/.android/avd/*.avd` / `*.qcow2` (emulator disk images) | A specific emulator device's own disk state | Not an SDK package (no `package.xml`), so manual deletion is mechanically fine — but it holds that emulator's installed-app state. Propose with size shown; let the user decide whether they still use that specific device. |
| Docker: full sweep — `docker system prune -a --volumes` | Removes **all** unused images (not just dangling ones) and **all stopped containers**, plus prunes unused volumes | This is not the Bucket A default — it's a separate, higher-risk action. Before proposing it, run `docker system df -v` and show the user exactly which stopped containers and tagged images would go, and confirm with `docker volume ls` which named volumes exist. A past run of this removed three stopped containers (postgres/redis/mailpit) the user still wanted, without that being called out beforehand — their named volumes survived (so the data was fine), but the containers themselves had to be recreated. Only reach for the full sweep when the tiered options above aren't enough and the user has seen the specifics. |
| `~/Library/Containers/com.docker.docker` as a whole | Docker Desktop's entire data dir | Don't delete this wholesale — go through the tiered Docker options above instead, or this becomes a Bucket C "would destroy data" situation. |

## A sizing gotcha that applies to several of the above

VM/container/emulator disk image files (Docker's `Docker.raw`, Android's `*.qcow2`, any `.vdi`/
`.vmdk`/sparse bundle) are usually sparse files. `ls -lh` reports their logical/maximum size,
which can overstate real disk usage by tens of GB. Always confirm with `du -h` before reporting
a size or deciding whether cleanup is even worth proposing for one of these.
