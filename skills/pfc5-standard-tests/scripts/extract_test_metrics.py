from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def numeric_rows(path: Path, x_col: str, y_col: str) -> list[tuple[float, float, dict[str, str]]]:
    out = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            try:
                out.append((float(row[x_col]), float(row[y_col]), row))
            except (KeyError, TypeError, ValueError):
                continue
    return out


def slope(points: list[tuple[float, float]]) -> float | None:
    if len(points) < 2:
        return None
    mx = sum(x for x, _ in points) / len(points)
    my = sum(y for _, y in points) / len(points)
    den = sum((x - mx) ** 2 for x, _ in points)
    return None if den == 0 else sum((x - mx) * (y - my) for x, y in points) / den


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract PFC5 calibration-test metrics from CSV")
    parser.add_argument("csv", type=Path)
    parser.add_argument("--x-col", default="strain")
    parser.add_argument("--y-col", default="stress_mpa")
    parser.add_argument("--x-sign", type=float, choices=(-1.0, 1.0), default=1.0)
    parser.add_argument("--y-sign", type=float, choices=(-1.0, 1.0), default=1.0)
    parser.add_argument("--fit-min", type=float)
    parser.add_argument("--fit-max", type=float)
    parser.add_argument("--diameter", type=float)
    parser.add_argument("--thickness", type=float)
    parser.add_argument("--load-col")
    args = parser.parse_args()
    raw = numeric_rows(args.csv, args.x_col, args.y_col)
    if not raw:
        parser.error("no numeric x/y rows")
    points = [(args.x_sign * x, args.y_sign * y) for x, y, _ in raw]
    peak_index = max(range(len(points)), key=lambda i: points[i][1])
    peak_x, peak_y = points[peak_index]
    if args.fit_min is None or args.fit_max is None:
        lo, hi = sorted((0.2 * peak_x, 0.5 * peak_x))
    else:
        lo, hi = sorted((args.fit_min, args.fit_max))
    fit = [(x, y) for x, y in points if lo <= x <= hi]
    result: dict[str, object] = {
        "rows": len(points),
        "peak_x": peak_x,
        "peak_y": peak_y,
        "final_x": points[-1][0],
        "final_y": points[-1][1],
        "fit_interval": [lo, hi],
        "linear_slope": slope(fit),
    }
    if args.load_col:
        try:
            peak_load = max(float(row[args.load_col]) for _, _, row in raw)
        except (KeyError, TypeError, ValueError):
            parser.error("load column is missing or non-numeric")
        result["peak_load"] = peak_load
        if args.diameter and args.thickness:
            result["diametral_strength"] = 2.0 * peak_load / (math.pi * args.diameter * args.thickness)
            result["diametral_strength_units_follow_inputs"] = True
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
