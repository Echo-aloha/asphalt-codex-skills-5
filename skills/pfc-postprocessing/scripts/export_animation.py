from __future__ import annotations

from pathlib import Path
import argparse

import imageio.v2 as imageio
from PIL import Image

from _common import ensure_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Create GIF and optional MP4 from ordered PNG frames")
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--stem", default="animation")
    parser.add_argument("--fps", type=int, default=4)
    parser.add_argument("--write-mp4", action="store_true")
    args = parser.parse_args()

    output_dir = ensure_dir(args.output_dir)
    frames = sorted(args.input_dir.glob("frame_*.png"))
    if not frames:
        raise FileNotFoundError(f"No ordered frames found in {args.input_dir}")

    images = [Image.open(frame).convert("RGBA") for frame in frames]
    gif_path = output_dir / f"{args.stem}.gif"
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=int(1000 / max(args.fps, 1)),
        loop=0,
        disposal=2,
    )

    if args.write_mp4:
        mp4_path = output_dir / f"{args.stem}.mp4"
        with imageio.get_writer(mp4_path, fps=args.fps) as writer:
            for frame in frames:
                writer.append_data(imageio.imread(frame))
        print(mp4_path)
    print(gif_path)


if __name__ == "__main__":
    main()
