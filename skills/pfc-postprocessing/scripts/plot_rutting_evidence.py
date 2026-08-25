from __future__ import annotations

import numpy as np
import pandas as pd

from _common import ensure_dir, make_argument_parser, read_csv_required, slugify


HISTORY_COLUMNS = [
    "solver_time_s",
    "equivalent_physical_time_s",
    "time_scale_lambda",
    "solver_cycle",
    "one_way_pass",
    "round_trip",
    "commanded_vertical_n",
    "vertical_reaction_n",
    "commanded_horizontal_n",
    "horizontal_reaction_n",
    "rut_depth_mm",
    "forward_face_deformation_mm",
    "reverse_face_deformation_mm",
    "lateral_heave_mm",
    "surrogate_route",
]


def numeric_frame(df: pd.DataFrame, columns: list[str], source: str) -> pd.DataFrame:
    result = df.copy()
    for column in columns:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    if result[columns].isna().any().any():
        bad = result.index[result[columns].isna().any(axis=1)].tolist()
        raise ValueError(f"{source} has non-numeric or missing values in rows: {bad}")
    return result


def require_monotonic(df: pd.DataFrame, column: str) -> None:
    values = df[column].to_numpy(dtype=float)
    if np.any(np.diff(values) < 0):
        raise ValueError(f"rutting_history.csv column {column} must be nondecreasing")


def main() -> None:
    parser = make_argument_parser(
        "Plot auditable rutting, vector-reaction, asymmetry and shear-depth evidence"
    )
    parser.add_argument("--history", default="rutting_history.csv")
    parser.add_argument("--shear-profile", default="rutting_shear_profile.csv")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="validate the rutting CSV contracts without plotting dependencies or writes",
    )
    args = parser.parse_args()

    history_path = args.input_dir / args.history
    history = read_csv_required(history_path, HISTORY_COLUMNS)
    numeric_columns = [name for name in HISTORY_COLUMNS if name != "surrogate_route"]
    history = numeric_frame(history, numeric_columns, history_path.name)
    if history.empty:
        raise ValueError("rutting_history.csv has no data rows")
    for column in ["solver_time_s", "equivalent_physical_time_s", "solver_cycle", "one_way_pass", "round_trip"]:
        require_monotonic(history, column)
    if (history["time_scale_lambda"] <= 0).any():
        raise ValueError("time_scale_lambda must be positive")
    if (history["surrogate_route"].astype(str).str.strip() == "").any():
        raise ValueError("surrogate_route must be non-empty")

    time = history["equivalent_physical_time_s"]
    vertical_error = history["vertical_reaction_n"] - history["commanded_vertical_n"]
    horizontal_error = history["horizontal_reaction_n"] - history["commanded_horizontal_n"]
    asymmetry = history["forward_face_deformation_mm"] - history["reverse_face_deformation_mm"]

    shear_path = args.input_dir / args.shear_profile
    shear = None
    if shear_path.exists():
        shear = read_csv_required(
            shear_path,
            [
                "sample_id",
                "depth_mid_mm",
                "shear_component",
                "shear_stress_mpa",
                "measure_radius_mm",
                "weighting_rule",
            ],
        )
        shear = numeric_frame(
            shear,
            ["depth_mid_mm", "shear_stress_mpa", "measure_radius_mm"],
            shear_path.name,
        )
        if shear.empty:
            raise ValueError("rutting_shear_profile.csv has no data rows")
        if (shear["measure_radius_mm"] <= 0).any():
            raise ValueError("measure_radius_mm must be positive")

    if args.check_only:
        print("rutting evidence inputs: ok")
        return

    import matplotlib.pyplot as plt

    output_dir = ensure_dir(args.output_dir)
    tables_dir = ensure_dir(output_dir.parent / "tables")

    fig, axes = plt.subplots(2, 2, figsize=(10.0, 7.2))
    axes[0, 0].plot(time, history["rut_depth_mm"], label="Rut depth", linewidth=2.0)
    axes[0, 0].plot(time, history["lateral_heave_mm"], label="Lateral heave", linewidth=1.5)
    axes[0, 0].set_ylabel("Deformation (mm)")
    axes[0, 0].legend()

    axes[0, 1].plot(time, history["commanded_vertical_n"], "--", label="Vertical command")
    axes[0, 1].plot(time, history["vertical_reaction_n"], label="Vertical reaction")
    axes[0, 1].plot(time, history["commanded_horizontal_n"], "--", label="Horizontal command")
    axes[0, 1].plot(time, history["horizontal_reaction_n"], label="Horizontal reaction")
    axes[0, 1].set_ylabel("Signed load/reaction (N)")
    axes[0, 1].legend(fontsize=8)

    axes[1, 0].plot(time, vertical_error, label="Vertical error")
    axes[1, 0].plot(time, horizontal_error, label="Horizontal error")
    axes[1, 0].axhline(0.0, color="black", linewidth=0.8)
    axes[1, 0].set_ylabel("Reaction error (N)")
    axes[1, 0].legend()

    if shear is not None:
        for sample_id, group in shear.groupby("sample_id", sort=False):
            group = group.sort_values("depth_mid_mm")
            component = ",".join(sorted(set(group["shear_component"].astype(str))))
            axes[1, 1].plot(
                group["shear_stress_mpa"],
                group["depth_mid_mm"],
                marker="o",
                label=f"{sample_id} ({component})",
            )
        axes[1, 1].invert_yaxis()
        axes[1, 1].set_xlabel("Signed shear stress (MPa)")
        axes[1, 1].set_ylabel("Depth (mm)")
        axes[1, 1].legend(fontsize=8)
    else:
        axes[1, 1].plot(time, asymmetry, label="Forward - reverse face")
        axes[1, 1].axhline(0.0, color="black", linewidth=0.8)
        axes[1, 1].set_ylabel("Deformation asymmetry (mm)")
        axes[1, 1].legend()

    for axis in axes.flat:
        axis.grid(alpha=0.25)
    for axis in axes[0, :]:
        axis.set_xlabel("Equivalent physical time (s)")
    axes[1, 0].set_xlabel("Equivalent physical time (s)")
    if shear is None:
        axes[1, 1].set_xlabel("Equivalent physical time (s)")
    fig.suptitle(f"{args.case_name} rutting evidence")
    fig.tight_layout()

    stem = output_dir / f"{slugify(args.case_name)}_rutting_evidence_{args.stage}"
    fig.savefig(stem.with_suffix(".png"), dpi=220)
    fig.savefig(stem.with_suffix(".svg"))
    plt.close(fig)

    summary = [
        {"metric": "final_rut_depth_mm", "value": float(history["rut_depth_mm"].iloc[-1])},
        {"metric": "max_rut_depth_mm", "value": float(history["rut_depth_mm"].max())},
        {"metric": "max_lateral_heave_mm", "value": float(history["lateral_heave_mm"].max())},
        {"metric": "final_face_asymmetry_mm", "value": float(asymmetry.iloc[-1])},
        {"metric": "vertical_reaction_rmse_n", "value": float(np.sqrt(np.mean(vertical_error**2)))},
        {"metric": "horizontal_reaction_rmse_n", "value": float(np.sqrt(np.mean(horizontal_error**2)))},
        {"metric": "time_scale_lambda_min", "value": float(history["time_scale_lambda"].min())},
        {"metric": "time_scale_lambda_max", "value": float(history["time_scale_lambda"].max())},
    ]
    pd.DataFrame(summary).to_csv(
        tables_dir / f"rutting_evidence_summary_{args.stage}.csv", index=False
    )
    print(stem.with_suffix(".png"))


if __name__ == "__main__":
    main()
