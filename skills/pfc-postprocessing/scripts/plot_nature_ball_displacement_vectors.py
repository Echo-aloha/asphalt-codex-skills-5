from pathlib import Path
import argparse
import string
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "font.size": 7,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "legend.frameon": False,
})

STAGES = ["A", "B", "C", "D", "peak", "final"]
STAGE_TITLES = {
    "A": "Stage A",
    "B": "Stage B",
    "C": "Stage C",
    "D": "Stage D",
    "peak": "Peak",
    "final": "Post-peak",
}


def load_stage(case: Path, stage: str) -> pd.DataFrame:
    csv_path = case / f"plotdata_ball_displacement_arrows_stage_{stage}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)
    df = pd.read_csv(csv_path)
    # Convert model metres to millimetres for paper-style axes and colorbar.
    for col in ["x", "y", "disp_x", "disp_y", "disp_mag", "radius"]:
        df[col + "_mm"] = df[col].astype(float) * 1000.0
    return df


def save_pub(fig: plt.Figure, out_prefix: Path, dpi: int = 600):
    fig.savefig(out_prefix.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(out_prefix.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(out_prefix.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(out_prefix.with_suffix(".tiff"), dpi=dpi, bbox_inches="tight")


def make_figure(case: Path, stages=STAGES, thin: int = 1):
    data = {s: load_stage(case, s) for s in stages}
    global_vmax = max(float(df["disp_mag_mm"].max()) for df in data.values())
    norm = Normalize(vmin=0.0, vmax=global_vmax)
    cmap = mpl.colormaps["viridis"]

    # Nature full-width page: ~183 mm wide.
    fig, axes = plt.subplots(2, 3, figsize=(7.2, 4.65), constrained_layout=False)
    axes = axes.ravel()
    fig.subplots_adjust(left=0.075, right=0.895, bottom=0.105, top=0.865, wspace=0.28, hspace=0.34)
    fig.suptitle(f"{case.name} 2D - Ball displacement vector field", y=0.965, fontsize=12, fontweight="bold")

    # Common specimen extents from all stages.
    all_x = np.concatenate([df["x_mm"].to_numpy(float) for df in data.values()])
    all_y = np.concatenate([df["y_mm"].to_numpy(float) for df in data.values()])
    xmin, xmax = float(np.nanmin(all_x)), float(np.nanmax(all_x))
    ymin, ymax = float(np.nanmin(all_y)), float(np.nanmax(all_y))
    pad = 2.0

    # Arrow scale: largest vector about 7% of specimen width. Matplotlib quiver scale uses data units.
    specimen_span = max(xmax - xmin, ymax - ymin)
    target_len = specimen_span * 0.070
    quiver_scale = global_vmax / target_len if target_len > 0 else 1.0

    for i, stage in enumerate(stages):
        ax = axes[i]
        df = data[stage]
        if thin > 1:
            df = df.iloc[::thin, :].copy()
        x = df["x_mm"].to_numpy(float)
        y = df["y_mm"].to_numpy(float)
        u = df["disp_x_mm"].to_numpy(float)
        v = df["disp_y_mm"].to_numpy(float)
        mag = df["disp_mag_mm"].to_numpy(float)

        ax.quiver(
            x, y, u, v, mag,
            cmap=cmap, norm=norm,
            angles="xy", scale_units="xy", scale=quiver_scale,
            width=0.0035, headwidth=3.8, headlength=4.6, headaxislength=4.0,
            pivot="mid", minlength=0.0,
        )
        ax.set_title(STAGE_TITLES[stage], fontsize=9, pad=5)
        ax.text(-0.17, 1.08, string.ascii_lowercase[i], transform=ax.transAxes,
                fontsize=10.5, fontweight="bold", va="bottom", ha="left")
        ax.set_xlim(xmin - pad, xmax + pad)
        ax.set_ylim(ymin - pad, ymax + pad)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xticks([-20, -10, 0, 10, 20])
        ax.set_yticks([-20, -10, 0, 10, 20])
        ax.set_xlabel("x (mm)", fontsize=8)
        ax.set_ylabel("y (mm)", fontsize=8)
        ax.tick_params(labelsize=7)
        # Very light grid helps compare positions without looking like PFC UI.
        ax.grid(True, color="#E6E6E6", linewidth=0.45, zorder=0)

        # A small reference arrow in panel f for physical scale, outside dense data region.
        if stage == "final":
            ref = 5.0  # mm displacement
            ax.quiver(xmin - 0.5, ymin - 0.5, ref, 0, ref,
                      cmap=cmap, norm=norm, angles="xy", scale_units="xy", scale=quiver_scale,
                      width=0.0042, headwidth=4.0, headlength=5.0, pivot="tail")
            ax.text(xmin - 0.5, ymin - 2.6, "5 mm", fontsize=6.5, ha="left", va="top")

    cax = fig.add_axes([0.915, 0.18, 0.018, 0.60])
    sm = ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cb = fig.colorbar(sm, cax=cax, extend="max")
    cb.set_label("Displacement magnitude (mm)", fontsize=8)
    cb.ax.tick_params(labelsize=7, width=0.7, length=2.5)
    ticks = np.linspace(0, global_vmax, 6)
    cb.set_ticks(ticks)
    cb.ax.set_yticklabels([f"{t:.1f}" for t in ticks])

    # Add concise source-data note inside figure margin, not as a distracting panel.
    fig.text(0.075, 0.025, f"Arrows: ball displacement vectors; shared colour scale, max = {global_vmax:.2f} mm.",
             fontsize=6.5, color="#444444")
    return fig


def main():
    ap = argparse.ArgumentParser(description="Nature-style multi-panel ball displacement vector figure.")
    ap.add_argument("case", nargs="?", default="Intact")
    ap.add_argument("--thin", type=int, default=1, help="Plot every nth ball arrow; default 1 uses all balls.")
    args = ap.parse_args()
    case = Path(args.case)
    fig = make_figure(case, thin=max(1, args.thin))
    out = case / "nature_ball_displacement_vectors"
    save_pub(fig, out)
    plt.close(fig)
    print(f"saved {out.name} (.png/.svg/.pdf/.tiff)")


if __name__ == "__main__":
    main()
