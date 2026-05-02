#!/usr/bin/env python3
"""Create a context handoff report draft from local repository state."""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
from pathlib import Path


def run(command: list[str], cwd: Path) -> tuple[int, str, str]:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.returncode, completed.stdout.rstrip("\n"), completed.stderr.rstrip("\n")


def git_value(args: list[str], cwd: Path, default: str = "unavailable") -> str:
    code, stdout, _stderr = run(["git", *args], cwd)
    if code != 0 or not stdout:
        return default
    return stdout


def git_root(start: Path) -> Path | None:
    code, stdout, _stderr = run(["git", "rev-parse", "--show-toplevel"], start)
    if code != 0 or not stdout:
        return None
    return Path(stdout.strip()).resolve()


def git_output(args: list[str], cwd: Path) -> str:
    code, stdout, stderr = run(["git", *args], cwd)
    if code != 0:
        return f"[command failed: git {' '.join(args)}]\n{stderr or stdout}".strip()
    return stdout or "(none)"


def parse_status(short_status: str, output_path: Path, root: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    output_rel = None
    try:
        output_rel = output_path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        output_rel = None

    for raw_line in short_status.splitlines():
        if not raw_line.strip():
            continue
        code = raw_line[:2]
        path = raw_line[3:] if len(raw_line) > 3 else raw_line.strip()
        if output_rel and path == output_rel:
            continue
        rows.append((code, path))
    return rows


def status_description(code: str) -> str:
    labels = {
        "M": "modified",
        "A": "added",
        "D": "deleted",
        "R": "renamed",
        "C": "copied",
        "U": "unmerged",
        "?": "untracked",
        "!": "ignored",
        " ": "clean",
    }
    if code == "??":
        return "untracked"
    if len(code) < 2:
        return labels.get(code, code)

    index = labels.get(code[0], code[0])
    worktree = labels.get(code[1], code[1])
    if code[0] == " ":
        return f"worktree {worktree}"
    if code[1] == " ":
        return f"staged {index}"
    return f"staged {index}; worktree {worktree}"


def make_table(rows: list[tuple[str, str]]) -> str:
    if not rows:
        return "| Path | Status | Reason / handoff notes |\n| --- | --- | --- |\n| (none detected) | clean | No changed files detected by git status. |"

    lines = [
        "| Path | Status | Reason / handoff notes |",
        "| --- | --- | --- |",
    ]
    for code, path in rows:
        lines.append(f"| `{path}` | {status_description(code)} (`{code}`) | Fill in why this file matters and what changed. |")
    return "\n".join(lines)


def make_file_sections(rows: list[tuple[str, str]]) -> str:
    if not rows:
        return "No changed files were detected. If files were inspected or affected without changes, list them in the affected-files section."

    sections: list[str] = []
    for code, path in rows:
        sections.append(
            "\n".join(
                [
                    f"### `{path}`",
                    f"- **Status**: {status_description(code)} (`{code}`)",
                    "- **Reason behind change**: Fill in the user requirement, bug, design choice, or dependency that caused this change.",
                    "- **What changed**: Fill in the concrete edits, important functions/classes/config, and behavior change.",
                    "- **What the next agent should know**: Fill in constraints, edge cases, coupling, and follow-up hazards.",
                    "- **Verification touching this file**: Fill in tests, commands, manual checks, or gaps.",
                ]
            )
        )
    return "\n\n".join(sections)


def code_block(value: str) -> str:
    normalized = value.rstrip("\n")
    return f"```text\n{normalized if normalized.strip() else '(none)'}\n```"


def build_report(project_root: Path, output_path: Path, current_goal: str, notes: list[str]) -> str:
    root = git_root(project_root)
    is_git = root is not None
    root = root or project_root.resolve()

    now = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    branch = git_value(["branch", "--show-current"], root) if is_git else "not a git worktree"
    head = git_value(["rev-parse", "--short", "HEAD"], root) if is_git else "not a git worktree"
    status = git_output(["status", "--short"], root) if is_git else "(git unavailable)"
    rows = parse_status(status if is_git else "", output_path, root)

    note_block = "\n".join(f"- {note}" for note in notes) if notes else "- Fill in any session notes that are not obvious from the diff."

    return "\n".join(
        [
            "# Context Handoff Report",
            "",
            f"**Generated**: {now}",
            f"**Project root**: `{root}`",
            f"**Git branch**: `{branch}`",
            f"**HEAD**: `{head}`",
            "",
            "> This report is a handoff artifact. It is complete only after the active agent fills the narrative sections from conversation context, file review, and verification results.",
            "",
            "## Next-Agent Start Prompt",
            "",
            "Read this `report.md` first, then inspect the current git status and diffs before editing. Continue from the Remaining Implementation section, preserve unrelated user changes, and update this report if the handoff assumptions are stale.",
            "",
            "## Current User Goal",
            "",
            current_goal or "Fill in the latest user request and the practical outcome they wanted.",
            "",
            "## Session Summary",
            "",
            "- Fill in the high-level story of what happened in this session.",
            "- Include major decisions, pivots, constraints, and any user preferences that shaped the work.",
            "- Note whether the work is complete, partially complete, blocked, or only planned.",
            "",
            "## Important Session Notes",
            "",
            note_block,
            "",
            "## Repository State",
            "",
            "### Git Status",
            "",
            code_block(status),
            "",
            "### Unstaged Diff Stat",
            "",
            code_block(git_output(["diff", "--stat"], root) if is_git else "(git unavailable)"),
            "",
            "### Staged Diff Stat",
            "",
            code_block(git_output(["diff", "--cached", "--stat"], root) if is_git else "(git unavailable)"),
            "",
            "### Changed File Names",
            "",
            code_block(git_output(["diff", "--name-status"], root) if is_git else "(git unavailable)"),
            "",
            "### Staged File Names",
            "",
            code_block(git_output(["diff", "--cached", "--name-status"], root) if is_git else "(git unavailable)"),
            "",
            "## Files Changed",
            "",
            make_table(rows),
            "",
            "## Files Changed Details",
            "",
            make_file_sections(rows),
            "",
            "## Files Affected But Not Necessarily Changed",
            "",
            "| Path / area | Why it matters | What the next agent should inspect |",
            "| --- | --- | --- |",
            "| Fill in inspected files, contracts, APIs, tests, configs, docs, generated artifacts, or external systems. | Fill in impact. | Fill in next inspection step. |",
            "",
            "## Work Completed",
            "",
            "- Fill in completed implementation steps with file references.",
            "",
            "## Reasoning Behind Key Changes",
            "",
            "- Fill in the rationale for each important design or implementation choice.",
            "- Include rejected approaches only when they would prevent the next agent from repeating a mistake.",
            "",
            "## Remaining Implementation",
            "",
            "- Fill in exact next steps in execution order.",
            "- Include likely files to edit next.",
            "- Include blockers, decisions needed from the user, and known incomplete areas.",
            "",
            "## Verification Performed",
            "",
            "| Command / check | Result | Notes |",
            "| --- | --- | --- |",
            "| Fill in command or manual check. | passed / failed / skipped | Include output summary and follow-up. |",
            "",
            "## Known Risks And Constraints",
            "",
            "- Fill in risks, fragile assumptions, unrelated dirty files, environment constraints, skipped checks, and safety notes.",
            "",
            "## Resume Checklist",
            "",
            "- [ ] Read this report fully.",
            "- [ ] Run `git status --short` and compare it with the Repository State section.",
            "- [ ] Inspect diffs for every changed file before editing.",
            "- [ ] Continue from Remaining Implementation.",
            "- [ ] Run or update Verification Performed before final response.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a report.md context handoff draft.")
    parser.add_argument("--project-root", default=".", help="Project root or any path inside the target git worktree.")
    parser.add_argument("--output", default="report.md", help="Output markdown path. Relative paths resolve from the project root.")
    parser.add_argument("--current-goal", default="", help="Optional latest user goal to prefill in the report.")
    parser.add_argument("--note", action="append", default=[], help="Optional session note. Can be repeated.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    detected_root = git_root(project_root) or project_root
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = detected_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = build_report(detected_root, output_path, args.current_goal.strip(), args.note)
    output_path.write_text(report, encoding="utf-8")
    print(f"Wrote {output_path}")
    print("Review and complete all narrative sections before handing off.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
