from __future__ import annotations

from pathlib import Path
import argparse
import re

import pandas as pd

from _common import ensure_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert legacy ball export text into a public ball-field CSV")
    parser.add_argument("--input-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    output_dir = ensure_dir(args.output_dir)
    rows: list[dict[str, float | str]] = []
    with args.input_file.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            numbers = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", line)
            if len(numbers) < 4:
                continue
            x, y, radius, ball_id = map(float, numbers[:4])
            rows.append(
                {
                    "x": x,
                    "y": y,
                    "radius": radius,
                    "disp_x": 0.0,
                    "disp_y": 0.0,
                    "vel_x": 0.0,
                    "vel_y": 0.0,
                    "ball_id": int(ball_id),
                }
            )
    if not rows:
        raise ValueError("No parseable ball rows found in legacy export")
    out = output_dir / "plotdata_ball_fields.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(out)


if __name__ == "__main__":
    main()
