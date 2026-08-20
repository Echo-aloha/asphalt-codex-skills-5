from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute macro energy density from PFC5 stress-strain CSV")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--modulus-mpa", type=float, required=True)
    parser.add_argument("--strain-sign", type=float, choices=(-1.0, 1.0), default=1.0)
    parser.add_argument("--stress-sign", type=float, choices=(-1.0, 1.0), default=1.0)
    args = parser.parse_args()
    if args.modulus_mpa <= 0:
        parser.error("modulus must be positive")
    data = []
    with args.input.open("r", encoding="utf-8-sig", newline="") as handle:
        for index, row in enumerate(csv.DictReader(handle), 2):
            try:
                data.append((args.strain_sign * float(row["strain"]), args.stress_sign * float(row["stress_mpa"])))
            except (KeyError, TypeError, ValueError):
                raise SystemExit(f"invalid stress-strain row {index}")
    if len(data) < 2:
        parser.error("at least two numeric rows are required")
    output_rows = []
    input_energy = 0.0
    negative = 0
    for i, (strain, stress) in enumerate(data):
        if i:
            prev_strain, prev_stress = data[i - 1]
            input_energy += 0.5 * (stress + prev_stress) * (strain - prev_strain)
        elastic = stress * stress / (2.0 * args.modulus_mpa)
        dissipated = input_energy - elastic
        negative += dissipated < -1e-12
        output_rows.append({"strain": strain, "stress_mpa": stress, "input_mj_m3": input_energy, "elastic_mj_m3": elastic, "dissipated_mj_m3": dissipated})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)
    print(json.dumps({"rows": len(data), "final_input_mj_m3": input_energy, "negative_dissipated_points": negative, "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
