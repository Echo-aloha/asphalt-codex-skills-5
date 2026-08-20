from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


NEWER_MARKERS = [
    re.compile(r"\bfish\s+define\b", re.I),
    re.compile(r"\bfish\s+history\b", re.I),
    re.compile(r"^\s*model\s+history\b", re.I),
]


def audit(path: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    function_stack: list[tuple[str, int]] = []
    command_depth = 0
    for line_no, raw in enumerate(path.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1):
        code = raw.split(";", 1)[0].strip()
        if not code:
            continue
        for pattern in NEWER_MARKERS:
            if pattern.search(code):
                findings.append({"line": line_no, "rule": "newer-major FISH marker", "text": raw.strip()})
        match = re.match(r"def(?:ine)?\s+([A-Za-z_][A-Za-z0-9_]*)\b", code, re.I)
        if match:
            function_stack.append((match.group(1), line_no))
        elif re.fullmatch(r"end", code, re.I):
            if function_stack:
                function_stack.pop()
            else:
                findings.append({"line": line_no, "rule": "unmatched function end", "text": raw.strip()})
        if re.fullmatch(r"command", code, re.I):
            command_depth += 1
        elif re.fullmatch(r"endcommand", code, re.I):
            command_depth -= 1
            if command_depth < 0:
                findings.append({"line": line_no, "rule": "unmatched endcommand", "text": raw.strip()})
                command_depth = 0
    for name, line_no in function_stack:
        findings.append({"line": line_no, "rule": f"unclosed function {name}", "text": ""})
    if command_depth:
        findings.append({"line": 0, "rule": "unclosed command block", "text": ""})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit PFC5 FISH source structure")
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()
    report: dict[str, object] = {"syntax_family": "pfc5", "static_only": True, "files": {}}
    all_findings = 0
    for path in args.files:
        findings = audit(path)
        report["files"][str(path)] = findings  # type: ignore[index]
        all_findings += len(findings)
    report["ok"] = all_findings == 0
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if all_findings == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
