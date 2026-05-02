#!/usr/bin/env python3
"""Validate that a context handoff report is ready for another agent."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_HEADINGS = [
    "# Context Handoff Report",
    "## Next-Agent Start Prompt",
    "## Current User Goal",
    "## Session Summary",
    "## Repository State",
    "## Files Changed",
    "## Files Changed Details",
    "## Files Affected But Not Necessarily Changed",
    "## Work Completed",
    "## Reasoning Behind Key Changes",
    "## Remaining Implementation",
    "## Verification Performed",
    "## Known Risks And Constraints",
    "## Resume Checklist",
]

PLACEHOLDER_PATTERNS = [
    r"\bFill in\b",
    r"\[date/time\]",
    r"\[absolute path\]",
    r"\[branch\]",
    r"\[commit\]",
    r"\[Latest user request",
    r"\[What happened",
    r"\[path\]",
    r"\[status\]",
    r"\[reason\]",
    r"\[concrete implementation",
    r"\[constraints",
    r"\[tests/checks",
    r"\[Design or implementation",
    r"\[Exact next step",
    r"\[Likely files",
    r"\[Blockers",
    r"\[command\]",
    r"\[passed/failed/skipped\]",
    r"\[Risks",
    r"\bTODO\b",
]


def section_body(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    body_start = start + len(heading)
    level = len(heading) - len(heading.lstrip("#"))
    for match in re.finditer(r"\n(#{1,6}) ", text[body_start:]):
        if len(match.group(1)) <= level:
            return text[body_start : body_start + match.start()].strip()
    return text[body_start:].strip()


def validate(text: str) -> list[str]:
    errors: list[str] = []

    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"Missing required heading: {heading}")

    for pattern in PLACEHOLDER_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            errors.append(f"Unresolved placeholder found: {match.group(0)!r}")

    for heading in REQUIRED_HEADINGS[1:]:
        body = section_body(text, heading)
        if not body:
            errors.append(f"Required section is empty: {heading}")

    if "## Files Changed" in text and "| Path | Status | Reason / handoff notes |" in text:
        changed_body = section_body(text, "## Files Changed")
        if "(none detected)" not in changed_body and "Fill in" in changed_body:
            errors.append("Files Changed table still contains placeholder reasoning.")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a context handoff report.")
    parser.add_argument("report", help="Path to report.md.")
    args = parser.parse_args()

    report_path = Path(args.report).resolve()
    if not report_path.exists():
        print(f"FAIL: report does not exist: {report_path}")
        return 1

    text = report_path.read_text(encoding="utf-8")
    errors = validate(text)
    if errors:
        print(f"FAIL: {report_path} is not ready for handoff.")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PASS: {report_path} is ready for handoff.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
