#!/usr/bin/env python3
"""Read-only compatibility check for an external PFC 5.0 fistPkg tree."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REQUIRED_ROOT = ("fistPkg-README.txt", "fistPkg-publicMods.txt")
REQUIRED_FISH = ("ft.fis", "ck.fis", "ct.fis", "dc.fis", "tt.fis")
REQUIRED_PROJECTS = (
    "MatGen-Linear",
    "MatGen-ContactBonded",
    "MatGen-ParallelBonded",
    "MatGen-FlatJointed",
    "MatGen-Hill",
)


def inspect(root: Path) -> dict[str, object]:
    root = root.expanduser().resolve()
    source = root / "ExampleProjects" / "fistSrc"
    missing = [name for name in REQUIRED_ROOT if not (root / name).is_file()]
    missing += [
        f"ExampleProjects/fistSrc/{name}"
        for name in REQUIRED_FISH
        if not (source / name).is_file()
    ]
    missing += [
        f"ExampleProjects/{name}"
        for name in REQUIRED_PROJECTS
        if not (root / "ExampleProjects" / name).is_dir()
    ]

    release = None
    version_file = source / "fistPkg-version.txt"
    if version_file.is_file():
        version_text = version_file.read_text(encoding="utf-8-sig", errors="replace")
        match = re.search(
            r"(?:fistPkg\s*|FISHTank\s+version\s+)([0-9]+)",
            version_text,
            flags=re.IGNORECASE,
        )
        if match:
            release = int(match.group(1))
    else:
        missing.append("ExampleProjects/fistSrc/fistPkg-version.txt")

    compatibility = None
    mods = root / "fistPkg-publicMods.txt"
    if mods.is_file():
        text = mods.read_text(encoding="utf-8-sig", errors="replace")
        match = re.search(r"^\s*26\s*\|\s*(5(?:\.[0-9]+)+)\s*\|", text, flags=re.MULTILINE)
        if match:
            compatibility = "5.0"

    warnings: list[str] = []
    if release is None:
        warnings.append("fistPkg release marker was not found")
    elif release != 26:
        warnings.append(f"expected fistPkg26, found fistPkg{release}")
    if compatibility != "5.0":
        warnings.append("PFC 5.0 compatibility marker was not found")

    return {
        "root": str(root),
        "ok": not missing and not warnings,
        "release": release,
        "pfc_compatibility": compatibility,
        "source_dir": str(source),
        "missing": missing,
        "warnings": warnings,
        "runtime_validated": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="external fistPkg root directory")
    parser.add_argument("--json", action="store_true", help="emit JSON only")
    args = parser.parse_args()
    result = inspect(args.root)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"fistPkg root: {result['root']}")
        print(f"release: {result['release']}")
        print(f"PFC compatibility: {result['pfc_compatibility']}")
        print(f"layout check: {'PASS' if result['ok'] else 'FAIL'}")
        for item in result["missing"]:
            print(f"MISSING: {item}")
        for item in result["warnings"]:
            print(f"WARNING: {item}")
        print("runtime validation: NOT RUN")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
