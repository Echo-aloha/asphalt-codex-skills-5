from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Guarded two-parameter/two-target local update")
    parser.add_argument("input", type=Path, help="JSON containing parameters, residual and jacobian")
    parser.add_argument("--det-min", type=float, default=1e-10)
    parser.add_argument("--cond-max", type=float, default=1e8)
    parser.add_argument("--step-scale", type=float, default=1.0)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    p = [float(x) for x in data["parameters"]]
    r = [float(x) for x in data["residual"]]
    j = [[float(x) for x in row] for row in data["jacobian"]]
    if len(p) != 2 or len(r) != 2 or len(j) != 2 or any(len(row) != 2 for row in j):
        parser.error("parameters, residual and jacobian must define a 2x2 problem")
    values = [*p, *r, *j[0], *j[1]]
    if not all(math.isfinite(value) for value in values):
        parser.error("parameters, residual and jacobian must be finite")
    if args.det_min <= 0 or args.cond_max <= 1 or not 0 < args.step_scale <= 1:
        parser.error("det-min must be positive, cond-max > 1 and step-scale in (0, 1]")
    det = j[0][0] * j[1][1] - j[0][1] * j[1][0]
    if abs(det) < args.det_min:
        raise SystemExit(f"local solve rejected: |det|={abs(det):.6g} < {args.det_min:.6g}")
    norm_j = max(abs(j[0][0]) + abs(j[0][1]), abs(j[1][0]) + abs(j[1][1]))
    norm_inv = max(
        (abs(j[1][1]) + abs(j[0][1])) / abs(det),
        (abs(j[1][0]) + abs(j[0][0])) / abs(det),
    )
    condition_inf = norm_j * norm_inv
    if condition_inf > args.cond_max:
        raise SystemExit(
            f"local solve rejected: condition_inf={condition_inf:.6g} > {args.cond_max:.6g}"
        )
    delta = [
        (-j[1][1] * r[0] + j[0][1] * r[1]) / det,
        (j[1][0] * r[0] - j[0][0] * r[1]) / det,
    ]
    proposed = [p[i] + args.step_scale * delta[i] for i in range(2)]
    bounds = data.get("bounds")
    if bounds:
        if (
            not isinstance(bounds, list)
            or len(bounds) != 2
            or any(not isinstance(item, list) or len(item) != 2 for item in bounds)
        ):
            parser.error("bounds must contain two [minimum, maximum] pairs")
        numeric_bounds = [[float(value) for value in item] for item in bounds]
        if any(not math.isfinite(value) for item in numeric_bounds for value in item):
            parser.error("bounds must be finite")
        if any(item[0] > item[1] for item in numeric_bounds):
            parser.error("each lower bound must not exceed its upper bound")
        proposed = [
            max(numeric_bounds[i][0], min(numeric_bounds[i][1], proposed[i]))
            for i in range(2)
        ]
    print(json.dumps({
        "determinant": det,
        "condition_inf": condition_inf,
        "delta": delta,
        "proposed_parameters": proposed,
        "requires_true_pfc5_confirmation": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
