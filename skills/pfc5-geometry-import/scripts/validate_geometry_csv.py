from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate portable node/element geometry CSVs")
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--elements", type=Path)
    parser.add_argument("--dimension", type=int, choices=(2, 3), required=True)
    args = parser.parse_args()
    errors: list[str] = []
    node_rows = rows(args.nodes)
    required = {"id", "x", "y"} | ({"z"} if args.dimension == 3 else set())
    if not node_rows:
        errors.append("node file is empty")
    elif not required.issubset(node_rows[0]):
        errors.append(f"node columns missing: {sorted(required - set(node_rows[0]))}")
    ids: set[str] = set()
    coords: list[list[float]] = []
    for index, row in enumerate(node_rows, 2):
        node_id = row.get("id", "").strip()
        if not node_id or node_id in ids:
            errors.append(f"line {index}: blank or duplicate node id {node_id!r}")
        ids.add(node_id)
        try:
            coords.append([float(row["x"]), float(row["y"])] + ([float(row["z"])] if args.dimension == 3 else []))
        except (KeyError, TypeError, ValueError):
            errors.append(f"line {index}: invalid coordinates")
    element_count = 0
    if args.elements:
        element_rows = rows(args.elements)
        element_count = len(element_rows)
        for index, row in enumerate(element_rows, 2):
            refs = [value.strip() for key, value in row.items() if key.lower().startswith("n") and value and value.strip()]
            if len(set(refs)) < 2:
                errors.append(f"element line {index}: fewer than two distinct nodes")
            missing = [ref for ref in refs if ref not in ids]
            if missing:
                errors.append(f"element line {index}: missing nodes {missing}")
    extents = None
    if coords:
        extents = [[min(c[i] for c in coords), max(c[i] for c in coords)] for i in range(args.dimension)]
    report = {"ok": not errors, "nodes": len(node_rows), "elements": element_count, "extents": extents, "errors": errors}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
