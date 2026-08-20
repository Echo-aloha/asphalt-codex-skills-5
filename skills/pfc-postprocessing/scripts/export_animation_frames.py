from __future__ import annotations

from pathlib import Path
import argparse
import re
import shutil

from _common import ensure_dir


def sort_key(path: Path) -> tuple[int, str]:
    match = re.search(r"(\d+)(?!.*\d)", path.stem)
    return (int(match.group(1)) if match else 10**9, path.name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize animation frame names into frame_0001.png order")
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--glob", default="*.png")
    args = parser.parse_args()

    output_dir = ensure_dir(args.output_dir)
    frames = sorted(args.input_dir.glob(args.glob), key=sort_key)
    if not frames:
        raise FileNotFoundError(f"No frames matched {args.glob} in {args.input_dir}")

    manifest = output_dir / "frames_manifest.csv"
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        handle.write("index,original,new_name\n")
        for index, source in enumerate(frames, start=1):
            new_name = f"frame_{index:04d}.png"
            shutil.copyfile(source, output_dir / new_name)
            handle.write(f"{index},{source.name},{new_name}\n")
    print(output_dir)


if __name__ == "__main__":
    main()
