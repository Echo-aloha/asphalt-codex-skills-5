from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SOURCE_SUFFIXES = {".dat", ".p2dat", ".p3dat", ".fis", ".p2fis", ".p3fis"}
FORBIDDEN = {
    "newer contact-table prefix": re.compile(r"\bcontact\s+" + r"cmat\b", re.I),
    "newer FISH definition prefix": re.compile(r"\bfish\s+define\b", re.I),
    "newer model lifecycle prefix": re.compile(
        r"^\s*model\s+(?:new|save|restore|domain)\b", re.I
    ),
    "embedded object API": re.compile(r"\bimport\s+itasca\b", re.I),
}


def source_files(targets: list[Path]) -> list[Path]:
    found: list[Path] = []
    for target in targets:
        if target.is_file() and target.suffix.lower() in SOURCE_SUFFIXES:
            found.append(target)
        elif target.is_dir():
            found.extend(
                p for p in target.rglob("*") if p.is_file() and p.suffix.lower() in SOURCE_SUFFIXES
            )
    return sorted(set(found))


def audit(path: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    for line_no, line in enumerate(text.splitlines(), 1):
        code = line.split(";", 1)[0]
        for label, pattern in FORBIDDEN.items():
            if pattern.search(code):
                findings.append(
                    {"file": str(path), "line": line_no, "rule": label, "text": line.strip()}
                )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit PFC5 source files for known version contamination")
    parser.add_argument("targets", nargs="+", type=Path)
    parser.add_argument("--json", type=Path, help="optional JSON report path")
    args = parser.parse_args()

    files = source_files(args.targets)
    findings = [item for path in files for item in audit(path)]
    report = {
        "syntax_family": "pfc5",
        "static_only": True,
        "files_checked": len(files),
        "findings": findings,
        "ok": not findings,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.json:
        args.json.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
