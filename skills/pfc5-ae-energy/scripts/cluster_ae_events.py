from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Cluster PFC5 AE hits by time and distance")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--time-window", type=float, required=True)
    parser.add_argument("--space-window", type=float, required=True)
    parser.add_argument("--dimension", type=int, choices=(2, 3), required=True)
    args = parser.parse_args()
    if args.time_window < 0 or args.space_window < 0:
        parser.error("windows must be non-negative")
    with args.input.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    hits = []
    for index, row in enumerate(rows):
        try:
            pos = [float(row["x"]), float(row["y"])] + ([float(row["z"])] if args.dimension == 3 else [])
            hits.append({"id": row.get("hit_id") or str(index + 1), "time": float(row["time"]), "pos": pos, "mode": row.get("mode", "")})
        except (KeyError, TypeError, ValueError) as exc:
            raise SystemExit(f"invalid hit row {index + 2}: {exc}") from exc
    hits.sort(key=lambda h: h["time"])
    parent = list(range(len(hits)))
    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    for i, hit in enumerate(hits):
        for j in range(i - 1, -1, -1):
            dt = hit["time"] - hits[j]["time"]
            if dt > args.time_window:
                break
            dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(hit["pos"], hits[j]["pos"])))
            if dist <= args.space_window:
                union(i, j)
    groups: dict[int, list[dict[str, object]]] = {}
    for i, hit in enumerate(hits):
        groups.setdefault(find(i), []).append(hit)
    fieldnames = ["event_id", "time_start", "time_end", "x", "y"] + (["z"] if args.dimension == 3 else []) + ["hit_count", "tension_hits", "shear_hits", "member_ids"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for event_id, members in enumerate(sorted(groups.values(), key=lambda g: min(h["time"] for h in g)), 1):
            row: dict[str, object] = {
                "event_id": event_id,
                "time_start": min(h["time"] for h in members),
                "time_end": max(h["time"] for h in members),
                "hit_count": len(members),
                "tension_hits": sum("tens" in str(h["mode"]).lower() for h in members),
                "shear_hits": sum("shear" in str(h["mode"]).lower() for h in members),
                "member_ids": ";".join(str(h["id"]) for h in members),
            }
            for axis, name in enumerate(("x", "y", "z")[: args.dimension]):
                row[name] = sum(h["pos"][axis] for h in members) / len(members)  # type: ignore[index]
            writer.writerow(row)
    print(json.dumps({"hits": len(hits), "events": len(groups), "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
