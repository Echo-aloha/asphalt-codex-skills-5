#!/usr/bin/env python3
"""Check that recorded PFC5 runtime evidence matches the current probe sources."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = SKILL_DIR / "references" / "runtime-verification-manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_manifest() -> dict[str, object]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    checked: list[str] = []
    assets = manifest.get("assets")
    if not isinstance(assets, list) or not assets:
        errors.append("assets must be a non-empty array")
        assets = []

    package_root = PACKAGE_ROOT.resolve()
    for index, entry in enumerate(assets):
        if not isinstance(entry, dict):
            errors.append(f"assets[{index}] must be an object")
            continue
        relative = entry.get("path")
        expected = entry.get("sha256")
        if not isinstance(relative, str) or not isinstance(expected, str):
            errors.append(f"assets[{index}] must contain string path and sha256 fields")
            continue
        candidate = (PACKAGE_ROOT / relative).resolve()
        if candidate != package_root and package_root not in candidate.parents:
            errors.append(f"unsafe asset path: {relative}")
            continue
        if not candidate.is_file():
            errors.append(f"missing asset: {relative}")
            continue
        actual = sha256(candidate)
        if actual != expected:
            errors.append(f"hash mismatch: {relative}; expected {expected}, got {actual}")
        checked.append(relative)

    return {
        "ok": not errors,
        "manifest": str(MANIFEST_PATH.relative_to(PACKAGE_ROOT)).replace("\\", "/"),
        "checked": checked,
        "errors": errors,
        "evidence_quality": manifest.get("evidence_quality"),
    }


def main() -> int:
    result = check_manifest()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
