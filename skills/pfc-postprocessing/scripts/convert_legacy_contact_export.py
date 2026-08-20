from __future__ import annotations

from pathlib import Path
import argparse
import math
import re

import pandas as pd

from _common import ensure_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert legacy PFC5 contact export text into a public orientation CSV")
    parser.add_argument("--input-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    output_dir = ensure_dir(args.output_dir)
    rows: list[dict[str, float | str]] = []
    with args.input_file.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            numbers = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", line)
            if len(numbers) < 8:
                continue
            _, x, y, normal_x, normal_y, shear_x, shear_y, normal_force = map(float, numbers[:8])
            angle_deg = math.degrees(math.atan2(normal_y, normal_x))
            rows.append(
                {
                    "x": x,
                    "y": y,
                    "angle_deg": angle_deg,
                    "magnitude": abs(normal_force),
                    "type": "contact_normal",
                    "shear_x": shear_x,
                    "shear_y": shear_y,
                }
            )
    if not rows:
        raise ValueError("No parseable contact rows found in legacy export")
    out = output_dir / "contact_orientations.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(out)


if __name__ == "__main__":
    main()
