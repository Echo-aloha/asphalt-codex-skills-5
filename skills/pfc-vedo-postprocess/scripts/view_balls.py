import argparse
import numpy as np
from vedo import Spheres, Plotter


def xyz(a):
    a = np.asarray(a, dtype=float)
    return np.c_[a, np.zeros(len(a))] if a.ndim == 2 and a.shape[1] == 2 else a


def main():
    ap = argparse.ArgumentParser(description="Render PFC particles colored by displacement magnitude.")
    ap.add_argument("snapshot")
    ap.add_argument("--out", default="balls_disp.png")
    ap.add_argument("--sample", type=int, default=1)
    ap.add_argument("--res", type=int, default=12)
    args = ap.parse_args()

    if args.sample < 1:
        ap.error("--sample must be at least 1")
    if args.res < 3:
        ap.error("--res must be at least 3")

    with np.load(args.snapshot, allow_pickle=False) as d:
        if "pos" not in d.files:
            raise ValueError("snapshot must contain a numeric 'pos' array")
        raw_pos = np.asarray(d["pos"])
        raw_rad = np.asarray(d["rad"]) if "rad" in d.files else np.ones(len(raw_pos))
        raw_disp = np.asarray(d["disp"]) if "disp" in d.files else np.zeros_like(raw_pos)

    sl = slice(None, None, max(args.sample, 1))
    pos = xyz(raw_pos)[sl]
    rad = np.asarray(raw_rad, dtype=float)[sl]
    disp = xyz(raw_disp)[sl]
    if pos.ndim != 2 or pos.shape[1] != 3:
        raise ValueError("'pos' must have shape (n, 2) or (n, 3)")
    if len(rad) != len(pos) or len(disp) != len(pos):
        raise ValueError("'rad' and 'disp' must match the number of positions")
    dmag = np.linalg.norm(disp, axis=1)

    balls = Spheres(pos, r=rad, res=args.res)
    balls.cmap("viridis", dmag, on="points").add_scalarbar("|disp| (m)")
    plt = Plotter(axes=1, bg="white", title="PFC particles colored by displacement")
    plt.show(balls, viewup="z")
    plt.screenshot(args.out)
    plt.close()


if __name__ == "__main__":
    main()
