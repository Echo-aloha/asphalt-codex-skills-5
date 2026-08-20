from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter

matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans", "Liberation Sans"]
matplotlib.rcParams["svg.fonttype"] = "none"
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.rcParams["axes.unicode_minus"] = False

# Chinese-traditional sequential palette for porosity: low -> high.
ZHONGGUO = [
    "#003371",  # Gan qing / lowest porosity
    "#10557E",  # transition blue
    "#177CB0",  # Dian qing
    "#1685A9",  # Shi qing
    "#12A182",  # Lan lu
    "#41B349",  # Cong lu
    "#A3CF62",  # Liu lu
    "#F0C239",  # Xiang se
    "#FF8C31",  # Ju huang
    "#FF461F",  # Zhu sha / highest porosity
]
PORO_CMAP = LinearSegmentedColormap.from_list("zhongguo_seq", ZHONGGUO, N=256)

COL_SPINE = "#3A3A3A"
COL_GRID = "#E2E2E2"
COL_TEXT = "#1A1A1A"
COL_BG = "#FFFFFF"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Draw a smooth 3D porosity surface from plotdata_porosity.csv."
    )
    parser.add_argument(
        "case_dir",
        nargs="?",
        default=".",
        help="Case directory containing plotdata_porosity.csv (default: current directory).",
    )
    parser.add_argument(
        "--csv",
        default="plotdata_porosity.csv",
        help="CSV filename or path. Relative paths are resolved under case_dir.",
    )
    parser.add_argument(
        "--prefix",
        default="porosity_3d_surface_zhongguo",
        help="Output prefix. Relative paths are resolved under case_dir.",
    )
    parser.add_argument("--up", type=int, default=8, help="Bicubic upsampling factor.")
    parser.add_argument("--elev", type=float, default=22.0, help="3D view elevation.")
    parser.add_argument("--azim", type=float, default=-128.0, help="3D view azimuth.")
    parser.add_argument("--no-tiff", action="store_true", help="Skip TIFF export.")
    return parser.parse_args()


def resolve_paths(args: argparse.Namespace) -> tuple[Path, Path]:
    case_dir = Path(args.case_dir).resolve()
    csv = Path(args.csv)
    if not csv.is_absolute():
        csv = case_dir / csv
    prefix = Path(args.prefix)
    if not prefix.is_absolute():
        prefix = case_dir / prefix
    return csv, prefix


def draw(csv: Path, out_prefix: Path, up: int = 8, elev: float = 22.0, azim: float = -128.0, export_tiff: bool = True) -> None:
    df = pd.read_csv(csv)[["x", "y", "porosity"]].dropna().copy()
    df["x_mm"] = df["x"] * 1000.0
    df["y_mm"] = df["y"] * 1000.0

    xs = np.sort(df["x_mm"].unique())
    ys = np.sort(df["y_mm"].unique())
    grid = df.pivot(index="y_mm", columns="x_mm", values="porosity").reindex(index=ys, columns=xs)
    z0 = grid.to_numpy(dtype=float)

    zmin = float(np.nanmin(z0))
    zmax = float(np.nanmax(z0))
    norm = colors.Normalize(vmin=zmin, vmax=zmax)

    ny, nx = z0.shape
    zf = cv2.resize(z0, (nx * up, ny * up), interpolation=cv2.INTER_CUBIC)
    zf = np.clip(zf, zmin, zmax)
    xf = np.linspace(xs.min(), xs.max(), nx * up)
    yf = np.linspace(ys.min(), ys.max(), ny * up)
    xf_grid, yf_grid = np.meshgrid(xf, yf)

    fig = plt.figure(figsize=(10.6, 7.2), dpi=240)
    fig.patch.set_facecolor(COL_BG)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor(COL_BG)
    ax.computed_zorder = False

    surf = ax.plot_surface(
        xf_grid,
        yf_grid,
        zf,
        cmap=PORO_CMAP,
        norm=norm,
        rcount=200,
        ccount=200,
        linewidth=0,
        edgecolor="none",
        antialiased=True,
        shade=True,
        alpha=1.0,
        zorder=8,
    )

    ax.contourf(
        xf_grid,
        yf_grid,
        zf,
        zdir="z",
        offset=zmin,
        levels=24,
        cmap=PORO_CMAP,
        norm=norm,
        alpha=0.18,
    )

    ax.set_xlabel("X coordinate (mm)", labelpad=12, fontsize=12, color=COL_TEXT)
    ax.set_ylabel("Y coordinate (mm)", labelpad=12, fontsize=12, color=COL_TEXT)
    ax.set_zlabel("Porosity", labelpad=10, fontsize=12, color=COL_TEXT)

    pad = float(np.median(np.diff(xs))) if len(xs) > 1 else 1.0
    ax.set_xlim(xs.min() - pad, xs.max() + pad)
    ax.set_ylim(ys.min() - pad, ys.max() + pad)
    ax.set_zlim(zmin, zmax)
    ax.set_xticks([-15, -10, -5, 0, 5, 10, 15])
    ax.set_yticks([-15, -10, -5, 0, 5, 10, 15])
    ax.set_zticks(np.round(np.linspace(zmin, zmax, 6), 3))
    ax.view_init(elev=elev, azim=azim)
    ax.set_box_aspect((1.05, 1.05, 0.66))
    ax.tick_params(axis="both", which="major", labelsize=9.5, pad=2, colors=COL_TEXT, length=0)
    ax.zaxis.set_tick_params(labelsize=9.5, pad=3, colors=COL_TEXT, length=0)

    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis._axinfo["grid"]["color"] = COL_GRID
        axis._axinfo["grid"]["linewidth"] = 0.6
        axis._axinfo["axisline"]["color"] = COL_SPINE
        axis._axinfo["axisline"]["linewidth"] = 0.9
    for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        pane.set_facecolor((1, 1, 1, 1))
        pane.set_edgecolor("#ECECEC")

    mappable = plt.cm.ScalarMappable(norm=norm, cmap=PORO_CMAP)
    mappable.set_array([])
    cbar = fig.colorbar(mappable, ax=ax, fraction=0.040, pad=0.02, shrink=0.70, aspect=20, extend="neither")
    cbar.set_ticks(np.linspace(zmin, zmax, 6))
    cbar.ax.set_ylim(zmin, zmax)
    cbar.set_label("Porosity", fontsize=11, color=COL_TEXT, labelpad=8)
    cbar.ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.3f}"))
    cbar.ax.tick_params(labelsize=9, length=0, colors=COL_TEXT, pad=3)
    cbar.outline.set_linewidth(0.6)
    cbar.outline.set_edgecolor("#333333")

    fig.text(
        0.52,
        0.045,
        f"{csv.parent.name} final state - porosity interval [{zmin:.3f}, {zmax:.3f}]",
        ha="center",
        va="center",
        fontsize=9,
        color="#666666",
    )
    fig.subplots_adjust(left=0.0, right=0.92, bottom=0.07, top=0.99)

    exports = [("png", {"dpi": 300}), ("svg", {}), ("pdf", {})]
    if export_tiff:
        exports.append(("tiff", {"dpi": 600}))
    for ext, kwargs in exports:
        fig.savefig(f"{out_prefix}.{ext}", bbox_inches="tight", pad_inches=0.04, **kwargs)
    plt.close(fig)
    print(f"OK | points {len(df)} | interval [{zmin:.4f}, {zmax:.4f}] | prefix {out_prefix}")


def main() -> None:
    args = parse_args()
    csv, prefix = resolve_paths(args)
    draw(csv, prefix, up=args.up, elev=args.elev, azim=args.azim, export_tiff=not args.no_tiff)


if __name__ == "__main__":
    main()
