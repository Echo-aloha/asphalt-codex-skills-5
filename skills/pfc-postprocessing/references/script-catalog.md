# PFC Postprocessing Script Catalog

This file is generated from the bundled Python scripts and is the first reference to read after `SKILL.md` when choosing a plotting route.

Hard rule: do not invent a plot from the prose description alone. Read the selected script before adapting or running it.

Scripts that call `_common.make_argument_parser(...)` also share these required/common arguments even if they are not repeated below:

- `--input-dir`: required directory containing input files.
- `--output-dir`: required directory to write outputs.
- `--case-name`: display name for titles; default `case`.
- `--stage`: stage label for output naming; default `final`.

## `convert_legacy_ball_export.py`

Convert legacy ball export text into a public ball-field CSV

Arguments:

- `--input-file`; required
- `--output-dir`; required

## `convert_legacy_contact_export.py`

Convert legacy PFC5 contact export text into a public orientation CSV

Arguments:

- `--input-file`; required
- `--output-dir`; required

## `export_animation.py`

Create GIF and optional MP4 from ordered PNG frames

Arguments:

- `--input-dir`; required
- `--output-dir`; required
- `--stem`; default `animation`
- `--fps`; default `4`
- `--write-mp4`

## `export_animation_frames.py`

Normalize animation frame names into frame_0001.png order

Arguments:

- `--input-dir`; required
- `--output-dir`; required
- `--glob`; default `*.png`

## `plot_curves.py`

Plot a public stress-strain figure from stress_strain.csv

Arguments:

- `--filename`; default `stress_strain.csv`

## `plot_fields.py`

Plot public field figures from standard CSV exports

Arguments:

- No command-line arguments detected; inspect the script before use.

## `plot_nature_ball_displacement_vectors.py`

Nature-style multi-panel ball displacement vector figure.

Arguments:

- `case`; default `Intact`
- `--thin`; default `1`. Plot every nth ball arrow; default 1 uses all balls.

## `plot_nature_ball_velocity_vectors.py`

Nature-style multi-panel ball velocity vector figure.

Arguments:

- `case`; default `Intact`
- `--thin`; default `1`. Plot every nth ball arrow; default 1 uses all balls.

## `plot_porosity_3d_surface_zhongguo.py`

Draw a smooth 3D porosity surface from plotdata_porosity.csv.

Arguments:

- `case_dir`; default `.`. Case directory containing plotdata_porosity.csv (default: current directory).
- `--csv`; default `plotdata_porosity.csv`. CSV filename or path. Relative paths are resolved under case_dir.
- `--prefix`; default `porosity_3d_surface_zhongguo`. Output prefix. Relative paths are resolved under case_dir.
- `--up`; default `8`. Bicubic upsampling factor.
- `--elev`; default `22.0`. 3D view elevation.
- `--azim`. 3D view azimuth.
- `--no-tiff`. Skip TIFF export.

## `plot_rutting_evidence.py`

Plot auditable rutting, vector-reaction, asymmetry and shear-depth evidence.

Arguments:

- `--history`; default `rutting_history.csv`
- `--shear-profile`; default `rutting_shear_profile.csv`; optional file
- `--check-only`; validate contracts without plotting dependencies or output writes

The script preserves signed vertical/horizontal reactions, checks monotonic solver/
equivalent time and pass counters, and writes a summary table. It does not compute a
normative dynamic-stability value.

## `plot_rose.py`

Plot a rose diagram from fracture or contact orientation data

Arguments:

- `--filename`. Optional explicit filename
- `--bins`; default `18`

## `plot_ucs_3d_surface_lollipop.py`

No argparse description found.

Arguments:

- No command-line arguments detected; inspect the script before use.

## `run_demo.py`

No argparse description found.

Arguments:

- No command-line arguments detected; inspect the script before use.
