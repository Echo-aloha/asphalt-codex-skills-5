from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import griddata

from _common import ensure_dir, find_column, find_first_existing, make_argument_parser, read_csv_required, slugify


def vector_magnitude(df: pd.DataFrame, x_name: str, y_name: str) -> np.ndarray:
    return np.sqrt(pd.to_numeric(df[x_name], errors="coerce") ** 2 + pd.to_numeric(df[y_name], errors="coerce") ** 2)


def field_figure(x, y, values, *, title: str, color_label: str, output_path, cmap: str = "viridis") -> None:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    values = np.asarray(values, dtype=float)
    valid = np.isfinite(x) & np.isfinite(y) & np.isfinite(values)
    x, y, values = x[valid], y[valid], values[valid]
    if x.size < 4:
        raise ValueError(f"Not enough valid points to plot {title}")

    xi = np.linspace(x.min(), x.max(), 160)
    yi = np.linspace(y.min(), y.max(), 160)
    Xi, Yi = np.meshgrid(xi, yi)
    Zi = griddata((x, y), values, (Xi, Yi), method="linear")

    fig, ax = plt.subplots(figsize=(5.2, 4.4))
    contour = ax.contourf(Xi, Yi, Zi, levels=18, cmap=cmap)
    ax.scatter(x, y, s=5, c="k", alpha=0.12)
    cbar = plt.colorbar(contour, ax=ax)
    cbar.set_label(color_label)
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def main() -> None:
    parser = make_argument_parser("Plot public field figures from standard CSV exports")
    args = parser.parse_args()
    output_dir = ensure_dir(args.output_dir)
    prefix = slugify(args.case_name)

    ball_path = find_first_existing(args.input_dir, ["plotdata_ball_fields_peak.csv", "plotdata_ball_fields.csv"])
    stress_path = find_first_existing(args.input_dir, ["plotdata_stress_peak.csv", "plotdata_stress.csv"])
    porosity_path = find_first_existing(args.input_dir, ["plotdata_porosity_peak.csv", "plotdata_porosity.csv"])

    if ball_path is not None:
        ball_df = read_csv_required(ball_path, ["x", "y", "disp_x", "disp_y", "vel_x", "vel_y", "radius"])
        disp_mag = vector_magnitude(ball_df, "disp_x", "disp_y")
        vel_mag = vector_magnitude(ball_df, "vel_x", "vel_y")
        field_figure(ball_df["x"], ball_df["y"], disp_mag, title=f"{args.case_name} displacement magnitude", color_label="disp", output_path=output_dir / f"{prefix}_plot_displacement_{args.stage}.png")
        field_figure(ball_df["x"], ball_df["y"], vel_mag, title=f"{args.case_name} velocity magnitude", color_label="vel", output_path=output_dir / f"{prefix}_plot_velocity_{args.stage}.png")

    if stress_path is not None:
        stress_df = read_csv_required(stress_path, ["x", "y"])
        sxx = find_column(stress_df, ["stress_xx", "sxx"])
        syy = find_column(stress_df, ["stress_yy", "syy"])
        sxy = find_column(stress_df, ["stress_xy", "sxy"])
        vm = np.sqrt(pd.to_numeric(stress_df[sxx], errors="coerce") ** 2 + pd.to_numeric(stress_df[syy], errors="coerce") ** 2 - pd.to_numeric(stress_df[sxx], errors="coerce") * pd.to_numeric(stress_df[syy], errors="coerce") + 3.0 * pd.to_numeric(stress_df[sxy], errors="coerce") ** 2)
        field_figure(stress_df["x"], stress_df["y"], vm, title=f"{args.case_name} von Mises-like stress", color_label="stress", output_path=output_dir / f"{prefix}_plot_stress_{args.stage}.png", cmap="RdBu_r")

    if porosity_path is not None:
        por_df = read_csv_required(porosity_path, ["x", "y", "porosity"])
        field_figure(por_df["x"], por_df["y"], por_df["porosity"], title=f"{args.case_name} porosity", color_label="porosity", output_path=output_dir / f"{prefix}_plot_porosity_{args.stage}.png", cmap="YlOrBr")

    print(output_dir)


if __name__ == "__main__":
    main()
