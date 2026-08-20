from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from _common import ensure_dir, make_argument_parser, read_csv_required, slugify


def main() -> None:
    parser = make_argument_parser("Plot a public stress-strain figure from stress_strain.csv")
    parser.add_argument("--filename", default="stress_strain.csv")
    args = parser.parse_args()

    output_dir = ensure_dir(args.output_dir)
    tables_dir = ensure_dir(output_dir.parent / "tables")
    csv_path = args.input_dir / args.filename
    df = read_csv_required(csv_path, ["strain", "stress_mpa"]).copy()
    df["strain"] = pd.to_numeric(df["strain"], errors="coerce")
    df["stress_mpa"] = pd.to_numeric(df["stress_mpa"], errors="coerce")
    df = df.dropna(subset=["strain", "stress_mpa"]).reset_index(drop=True)
    if df.empty:
        raise ValueError(f"{csv_path.name} has no numeric strain/stress rows")

    peak_idx = int(df["stress_mpa"].idxmax())
    peak_row = df.loc[peak_idx]

    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    ax.plot(df["strain"], df["stress_mpa"], color="#1f77b4", linewidth=2.0)
    ax.scatter([peak_row["strain"]], [peak_row["stress_mpa"]], color="crimson", zorder=5, label="Peak")
    ax.annotate(
        f"Peak = {peak_row['stress_mpa']:.2f} MPa",
        (peak_row["strain"], peak_row["stress_mpa"]),
        xytext=(8, 8),
        textcoords="offset points",
        fontsize=9,
    )
    ax.set_title(f"{args.case_name} stress-strain")
    ax.set_xlabel("Axial strain")
    ax.set_ylabel("Stress (MPa)")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()

    stem = output_dir / f"{slugify(args.case_name)}_plot_curve_{args.stage}"
    fig.savefig(stem.with_suffix(".png"), dpi=220)
    fig.savefig(stem.with_suffix(".svg"))
    plt.close(fig)

    summary = [
        {"metric": "peak_stress_mpa", "value": float(peak_row["stress_mpa"])},
        {"metric": "peak_strain", "value": float(peak_row["strain"])},
        {"metric": "final_stress_mpa", "value": float(df["stress_mpa"].iloc[-1])},
        {"metric": "final_strain", "value": float(df["strain"].iloc[-1])},
    ]
    pd.DataFrame(summary).to_csv(tables_dir / f"curve_summary_{args.stage}.csv", index=False)
    print(stem.with_suffix(".png"))


if __name__ == "__main__":
    main()
