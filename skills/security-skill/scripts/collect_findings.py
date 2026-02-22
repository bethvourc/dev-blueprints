#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize security scan artifacts into findings.")
    parser.add_argument("--scan-dir", required=True, help="Directory produced by run_scan.sh")
    parser.add_argument("--output-json", required=True, help="Output JSON path")
    parser.add_argument("--output-markdown", required=True, help="Output markdown path")
    parser.add_argument("--template", required=False, help="Optional markdown template path")
    return parser.parse_args()


def load_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return [dict(row) for row in reader]


def parse_match_line(line: str) -> tuple[str, int, str] | None:
    match = re.match(r"^(.*?):([0-9]+):(.*)$", line)
    if not match:
        return None
    file_path, line_no, content = match.groups()
    return file_path.strip(), int(line_no), content.strip()


def extract_json_blob(text: str) -> Any:
    text = text.strip()
    if not text:
        return None

    if text[0] in "[{":
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    for index, char in enumerate(text):
        if char not in "[{":
            continue
        candidate = text[index:]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    return None


def normalize_severity(value: str | None, default: str = "MEDIUM") -> str:
    if not value:
        return default
    v = value.strip().upper()
    if v not in SEVERITY_ORDER:
        return default
    return v


def finding_key(finding: dict[str, Any]) -> tuple[str, str, int, str]:
    return (
        finding["title"],
        finding["location"]["file"],
        finding["location"]["line"],
        finding["category"],
    )


def collect_pattern_findings(scan_dir: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    pattern_defs = load_tsv(scan_dir / "meta" / "patterns.tsv")
    secret_defs = load_tsv(scan_dir / "meta" / "secret_patterns.tsv")

    for definition in pattern_defs + secret_defs:
        pattern_id = definition.get("id", "").strip()
        if not pattern_id:
            continue

        prefix = "secret_" if definition in secret_defs else "pattern_"
        raw_file = scan_dir / "raw" / f"{prefix}{pattern_id}.txt"
        if not raw_file.exists():
            continue

        for raw_line in raw_file.read_text(encoding="utf-8", errors="replace").splitlines():
            parsed = parse_match_line(raw_line)
            if not parsed:
                continue

            file_path, line_no, snippet = parsed
            findings.append(
                {
                    "category": definition.get("category", "Uncategorized"),
                    "severity": normalize_severity(definition.get("severity"), default="MEDIUM"),
                    "confidence": "Potential",
                    "title": definition.get("title", f"Pattern match: {pattern_id}"),
                    "location": {"file": file_path, "line": line_no},
                    "attack_path": "Pattern-based signal detected; validate attacker-controlled input reachability.",
                    "why_it_matters": "Potential security weakness that may be exploitable depending on surrounding controls.",
                    "evidence": snippet[:500],
                    "tool": "pattern-scan",
                }
            )

    return findings


def collect_npm_findings(scan_dir: Path, filename: str, manager: str) -> list[dict[str, Any]]:
    path = scan_dir / "raw" / filename
    if not path.exists():
        return []

    payload = extract_json_blob(path.read_text(encoding="utf-8", errors="replace"))
    if not isinstance(payload, dict):
        return []

    vulnerabilities = payload.get("vulnerabilities")
    if not isinstance(vulnerabilities, dict):
        return []

    findings: list[dict[str, Any]] = []

    for package_name, details in vulnerabilities.items():
        if not isinstance(details, dict):
            continue

        severity = normalize_severity(str(details.get("severity", "MEDIUM")), default="MEDIUM")

        via = details.get("via")
        advisory_refs: list[str] = []
        if isinstance(via, list):
            for item in via:
                if isinstance(item, dict):
                    ref = item.get("source") or item.get("url") or item.get("name")
                    if ref:
                        advisory_refs.append(str(ref))
                elif isinstance(item, str):
                    advisory_refs.append(item)

        findings.append(
            {
                "category": "Dependency & Supply Chain",
                "severity": severity,
                "confidence": "Confirmed",
                "title": f"Vulnerable dependency detected: {package_name}",
                "location": {"file": f"{manager} dependency graph", "line": 1},
                "attack_path": "Dependency resolution includes a package version with known advisories.",
                "why_it_matters": "Known vulnerable third-party code may expose exploitable behavior.",
                "evidence": ", ".join(advisory_refs[:5]) if advisory_refs else "Advisory details present in audit output.",
                "tool": f"{manager}-audit",
            }
        )

    return findings


def collect_pip_findings(scan_dir: Path) -> list[dict[str, Any]]:
    path = scan_dir / "raw" / "deps_pip_audit.log"
    if not path.exists():
        return []

    payload = extract_json_blob(path.read_text(encoding="utf-8", errors="replace"))
    if not isinstance(payload, list):
        return []

    findings: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue

        pkg = item.get("name")
        vuln_id = item.get("id")
        if not pkg:
            continue

        evidence = f"id={vuln_id}" if vuln_id else "pip-audit reported a vulnerability for this dependency"
        findings.append(
            {
                "category": "Dependency & Supply Chain",
                "severity": "MEDIUM",
                "confidence": "Probable",
                "title": f"Potential vulnerable Python dependency: {pkg}",
                "location": {"file": "requirements/lock context", "line": 1},
                "attack_path": "Dependency audit reported a package with known advisories.",
                "why_it_matters": "Outdated or vulnerable dependencies can introduce exploitable paths.",
                "evidence": evidence,
                "tool": "pip-audit",
            }
        )

    return findings


def collect_cargo_findings(scan_dir: Path) -> list[dict[str, Any]]:
    path = scan_dir / "raw" / "deps_cargo_audit.log"
    if not path.exists():
        return []

    payload = extract_json_blob(path.read_text(encoding="utf-8", errors="replace"))
    if not isinstance(payload, dict):
        return []

    vulnerabilities = payload.get("vulnerabilities", {}).get("list", [])
    if not isinstance(vulnerabilities, list):
        return []

    findings: list[dict[str, Any]] = []
    for item in vulnerabilities:
        if not isinstance(item, dict):
            continue

        advisory = item.get("advisory", {})
        package = item.get("package", {})
        pkg_name = package.get("name")
        advisory_id = advisory.get("id")

        if not pkg_name:
            continue

        findings.append(
            {
                "category": "Dependency & Supply Chain",
                "severity": "MEDIUM",
                "confidence": "Probable",
                "title": f"Potential vulnerable Rust dependency: {pkg_name}",
                "location": {"file": "Cargo.lock/Cargo.toml context", "line": 1},
                "attack_path": "Dependency audit reported a package with known advisories.",
                "why_it_matters": "Known vulnerabilities in dependencies can propagate to runtime behavior.",
                "evidence": f"advisory={advisory_id}" if advisory_id else "cargo audit reported a vulnerability",
                "tool": "cargo-audit",
            }
        )

    return findings


def dedupe_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, int, str]] = set()
    unique: list[dict[str, Any]] = []

    for finding in findings:
        key = finding_key(finding)
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)

    return unique


def sort_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        findings,
        key=lambda item: (
            SEVERITY_ORDER.get(item["severity"], 99),
            item["location"]["file"],
            item["location"]["line"],
            item["title"],
        ),
    )


def render_findings_markdown(findings: list[dict[str, Any]]) -> str:
    if not findings:
        return "No findings were generated by automated checks. Manual validation is still required."

    blocks: list[str] = []
    for finding in findings:
        location = f"{finding['location']['file']}:{finding['location']['line']}"
        block = "\n".join(
            [
                f"### [{finding['severity']}] {finding['title']}",
                f"- **Category**: {finding['category']}",
                f"- **Confidence**: {finding['confidence']}",
                f"- **Location**: `{location}`",
                f"- **Attack Path**: {finding['attack_path']}",
                f"- **Why It Matters**: {finding['why_it_matters']}",
                "- **Evidence**:",
                "  ```code",
                f"  {finding['evidence']}",
                "  ```",
                "- **Quick Fix**:",
                "  ```code",
                "  [Implement targeted remediation after confirming exploitability in context.]",
                "  ```",
                "- **Durable Fix**: Add layered controls, tests, and policy checks for this vulnerability class.",
                "- **Validation**: Add tests and manual checks demonstrating exploit path is blocked.",
            ]
        )
        blocks.append(block)

    return "\n\n---\n\n".join(blocks)


def highest_risk(findings: list[dict[str, Any]]) -> str:
    if not findings:
        return "LOW"
    return min(findings, key=lambda item: SEVERITY_ORDER.get(item["severity"], 99))["severity"]


def build_summary(findings: list[dict[str, Any]]) -> dict[str, Any]:
    severity_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()

    for finding in findings:
        severity_counts[finding["severity"]] += 1
        confidence_counts[finding["confidence"]] += 1

    return {
        "total": len(findings),
        "by_severity": dict(sorted(severity_counts.items(), key=lambda kv: SEVERITY_ORDER.get(kv[0], 99))),
        "by_confidence": dict(confidence_counts),
    }


def default_template() -> str:
    return """# Security Audit Report

**Project**: {{PROJECT}}
**Date**: {{DATE}}
**Scope**: {{SCOPE}}
**Assumptions**: {{ASSUMPTIONS}}
**Overall Risk**: {{OVERALL_RISK}}

## Executive Summary
{{EXEC_SUMMARY}}

## Threat Surface Snapshot
{{THREAT_SURFACE}}

## Findings
{{FINDINGS}}

## Prioritized Remediation Plan
{{REMEDIATION_PLAN}}

## Security Tooling Recommendations
{{TOOLING_RECOMMENDATIONS}}
"""


def render_report(template_text: str, findings: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    by_severity = summary.get("by_severity", {})
    severity_text = ", ".join(f"{k}: {v}" for k, v in by_severity.items()) or "No findings"
    confidence_text = ", ".join(
        f"{k}: {v}" for k, v in summary.get("by_confidence", {}).items()
    ) or "No findings"

    replacements = {
        "{{PROJECT}}": "[set project name]",
        "{{DATE}}": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"),
        "{{SCOPE}}": "[set scope scanned]",
        "{{ASSUMPTIONS}}": "[set deployment/trust assumptions]",
        "{{OVERALL_RISK}}": highest_risk(findings),
        "{{EXEC_SUMMARY}}": (
            f"Automated scan generated {summary['total']} candidate findings. "
            f"Severity distribution: {severity_text}. Confidence distribution: {confidence_text}. "
            "Manually validate all Potential/Probable items before remediation prioritization."
        ),
        "{{THREAT_SURFACE}}": "- Internet-facing entry points: [fill]\n- Auth boundaries: [fill]\n- Sensitive data paths: [fill]",
        "{{FINDINGS}}": render_findings_markdown(findings),
        "{{REMEDIATION_PLAN}}": "1. Immediate (0-48h): [fill]\n2. Sprint (1-2 weeks): [fill]\n3. Backlog hardening: [fill]",
        "{{TOOLING_RECOMMENDATIONS}}": "- Add CI SAST/dependency/secrets gates and enforce fail-on-high for confirmed issues.",
    }

    rendered = template_text
    for key, value in replacements.items():
        rendered = rendered.replace(key, value)
    return rendered


def main() -> int:
    args = parse_args()
    scan_dir = Path(args.scan_dir).resolve()

    findings: list[dict[str, Any]] = []
    findings.extend(collect_pattern_findings(scan_dir))
    findings.extend(collect_npm_findings(scan_dir, "deps_npm_audit.log", "npm"))
    findings.extend(collect_npm_findings(scan_dir, "deps_pnpm_audit.log", "pnpm"))
    findings.extend(collect_pip_findings(scan_dir))
    findings.extend(collect_cargo_findings(scan_dir))

    findings = dedupe_findings(findings)
    findings = sort_findings(findings)
    summary = build_summary(findings)

    payload = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "scan_dir": str(scan_dir),
        "summary": summary,
        "findings": findings,
    }

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    template_text = default_template()
    if args.template:
        template_path = Path(args.template)
        if template_path.exists():
            template_text = template_path.read_text(encoding="utf-8")

    report = render_report(template_text, findings, summary)

    output_markdown = Path(args.output_markdown)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.write_text(report + "\n", encoding="utf-8")

    print(f"[collect_findings] wrote {output_json}")
    print(f"[collect_findings] wrote {output_markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
