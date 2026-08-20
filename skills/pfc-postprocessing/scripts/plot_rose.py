from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import ensure_dir, find_column, find_first_existing, make_argument_parser, read_csv_required, slugify


def main() -> None:
    parser = make_argument_parser("Plot a rose diagram from fracture or contact orientation data")
    parser.add_argument("--filename", default="", help="Optional explicit filename")
    parser.add_argument("--bins", type=int, default=18)
    args = parser.parse_args()

    output_dir = ensure_dir(args.output_dir)
    if args.filename:
        input_path = args.input_dir / args.filename
    else:
        input_path = find_first_existing(args.input_dir, ["plotdata_fracture_orientations.csv", "contact_orientations.csv"])
        if input_path is None:
            raise FileNotFoundError("Could not find plotdata_fracture_orientations.csv or contact_orientations.csv")

    df = read_csv_required(input_path, [])
    angle_col = find_column(df, ["angle_deg", "angle"])
    angles = pd.to_numeric(df[angle_col], errors="coerce").dropna().to_numpy(dtype=float)
    if angles.size == 0:
        raise ValueError(f"{input_path.name} contains no valid angles")
    angles = np.mod(angles, 180.0)

    bins = np.linspace(0.0, 180.0, args.bins + 1)
    counts, edges = np.histogram(angles, bins=bins)
    theta = np.deg2rad((edges[:-1] + edges[1:]) / 2.0)
    width = np.deg2rad(edges[1] - edges[0])

    fig = plt.figure(figsize=(5.2, 4.8))
    ax = fig.add_subplot(111, projection="polar")
    ax.bar(theta, counts, width=width, bottom=0.0, color="#4C78A8", alpha=0.85, edgecolor="white", linewidth=0.6)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_title(f"{args.case_name} rose diagram")
    fig.tight_layout()
    out = output_dir / f"{slugify(args.case_name)}_plot_rose_{args.stage}.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)
    print(out)


if __name__ == "__main__":
    main()
