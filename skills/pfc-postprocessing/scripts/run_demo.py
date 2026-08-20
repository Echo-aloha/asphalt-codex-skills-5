from __future__ import annotations

import argparse
import csv
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
EXAMPLES = ROOT / "examples"
DEMO_OUT = EXAMPLES / "demo_outputs"
MINIMAL_FILES = {
    "stress_strain.csv": {"strain", "stress_mpa"},
    "plotdata_ball_fields.csv": {"x", "y", "disp_x", "disp_y", "vel_x", "vel_y", "radius"},
    "plotdata_stress.csv": {"x", "y", "stress_xx", "stress_yy", "stress_xy"},
    "plotdata_porosity.csv": {"x", "y", "porosity"},
    "plotdata_fracture_orientations.csv": {"angle_deg"},
}


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], check=True)


def validate_inputs() -> None:
    minimal = EXAMPLES / "minimal_case" / "data"
    for name, required in MINIMAL_FILES.items():
        path = minimal / name
        if not path.is_file():
            raise FileNotFoundError(f"missing demo input: {path}")
        with path.open("r", encoding="utf-8", newline="") as handle:
            fields = set(next(csv.reader(handle), []))
        missing = sorted(required - fields)
        if missing:
            raise ValueError(f"{name} missing columns: {', '.join(missing)}")
    if not (EXAMPLES / "plugin_migration_case" / "legacy_contact_export.txt").is_file():
        raise FileNotFoundError("missing legacy contact demo input")
    if not (EXAMPLES / "plugin_migration_case" / "legacy_ball_export.dat").is_file():
        raise FileNotFoundError("missing legacy ball demo input")
    if not list((EXAMPLES / "animation_case" / "raw_frames").glob("*.png")):
        raise FileNotFoundError("missing animation demo frames")


def require_runtime_dependencies() -> None:
    required = ["numpy", "pandas", "matplotlib", "scipy", "imageio", "PIL"]
    missing = [name for name in required if importlib.util.find_spec(name) is None]
    if missing:
        raise SystemExit(
            "Missing demo dependencies: "
            + ", ".join(missing)
            + ". Install the package requirements.txt in an isolated environment."
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run or validate the public post-processing demo")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="validate bundled inputs without plotting dependencies or output writes",
    )
    args = parser.parse_args()

    validate_inputs()
    if args.check_only:
        print("demo inputs: ok")
        return
    require_runtime_dependencies()

    if DEMO_OUT.exists():
        shutil.rmtree(DEMO_OUT)
    (DEMO_OUT / "figures").mkdir(parents=True, exist_ok=True)
    (DEMO_OUT / "animations").mkdir(parents=True, exist_ok=True)
    (DEMO_OUT / "tables").mkdir(parents=True, exist_ok=True)

    minimal = EXAMPLES / "minimal_case" / "data"
    plugin = EXAMPLES / "plugin_migration_case"
    anim = EXAMPLES / "animation_case" / "raw_frames"

    run(str(SCRIPTS / "plot_curves.py"), "--input-dir", str(minimal), "--output-dir", str(DEMO_OUT / "figures"), "--case-name", "minimal_case", "--stage", "demo")
    run(str(SCRIPTS / "plot_fields.py"), "--input-dir", str(minimal), "--output-dir", str(DEMO_OUT / "figures"), "--case-name", "minimal_case", "--stage", "demo")
    run(str(SCRIPTS / "plot_rose.py"), "--input-dir", str(minimal), "--output-dir", str(DEMO_OUT / "figures"), "--case-name", "minimal_case", "--stage", "demo")

    converted = DEMO_OUT / "converted_plugin"
    run(str(SCRIPTS / "convert_legacy_contact_export.py"), "--input-file", str(plugin / "legacy_contact_export.txt"), "--output-dir", str(converted))
    run(str(SCRIPTS / "plot_rose.py"), "--input-dir", str(converted), "--output-dir", str(DEMO_OUT / "figures"), "--case-name", "plugin_contact_case", "--stage", "demo")

    run(str(SCRIPTS / "convert_legacy_ball_export.py"), "--input-file", str(plugin / "legacy_ball_export.dat"), "--output-dir", str(converted))
    run(str(SCRIPTS / "plot_fields.py"), "--input-dir", str(converted), "--output-dir", str(DEMO_OUT / "figures"), "--case-name", "plugin_ball_case", "--stage", "demo")

    ordered = DEMO_OUT / "ordered_frames"
    run(str(SCRIPTS / "export_animation_frames.py"), "--input-dir", str(anim), "--output-dir", str(ordered), "--glob", "*.png")
    run(str(SCRIPTS / "export_animation.py"), "--input-dir", str(ordered), "--output-dir", str(DEMO_OUT / "animations"), "--stem", "demo_animation", "--fps", "4")
    print(DEMO_OUT)


if __name__ == "__main__":
    main()
