# Scripts

This directory is the executable core of the public `pfc-postprocessing` skill.

## Learning order

1. `run_demo.py`
2. `plot_curves.py`
3. `plot_fields.py`
4. `plot_rose.py`
5. `export_animation_frames.py`
6. `export_animation.py`
7. `plot_porosity_3d_surface_zhongguo.py`
8. `plot_nature_ball_displacement_vectors.py`
9. `plot_nature_ball_velocity_vectors.py`

After that, read the legacy text-conversion helpers:

- `convert_legacy_contact_export.py`
- `convert_legacy_ball_export.py`

## What each script does

- `run_demo.py` — runs the public examples end to end
- `plot_curves.py` — draws a global response curve from `stress_strain.csv`
- `plot_fields.py` — draws displacement, velocity, stress, and porosity field figures
- `plot_rose.py` — draws a rose diagram from fracture or contact orientation data
- `export_animation_frames.py` — normalizes frame order and filenames
- `export_animation.py` — assembles GIF and optional MP4 outputs
- `convert_legacy_contact_export.py` — converts old contact text exports into a public CSV
- `convert_legacy_ball_export.py` — converts old ball text exports into a public CSV
- `plot_porosity_3d_surface_zhongguo.py` — draws a smooth 3D porosity surface from `plotdata_porosity.csv` using a Chinese-traditional sequential palette

## Public contract

- All scripts use directory-based inputs.
- No script depends on the author's local absolute paths.
- Old `.exe` utilities are not required.
- Proprietary project/save files must be exported to CSV or PNG in the licensed PFC 5.0 environment first.
- Outputs should land in `figures/`, `animations/`, `tables/`, or the requested case/output directory.

## Porosity 3D Surface

Use this when a case has `plotdata_porosity.csv` with `x`, `y`, and `porosity` columns:

```bash
python <SKILLS_ROOT>/pfc-postprocessing/scripts/plot_porosity_3d_surface_zhongguo.py Intact
```

Default outputs are written beside the CSV:

- `porosity_3d_surface_zhongguo.png`
- `porosity_3d_surface_zhongguo.svg`
- `porosity_3d_surface_zhongguo.pdf`
- `porosity_3d_surface_zhongguo.tiff`

## Displacement Vector Figure

Use this when a case has:

- `plotdata_ball_displacement_arrows_stage_A.csv`
- `plotdata_ball_displacement_arrows_stage_B.csv`
- `plotdata_ball_displacement_arrows_stage_C.csv`
- `plotdata_ball_displacement_arrows_stage_D.csv`
- `plotdata_ball_displacement_arrows_stage_peak.csv`
- `plotdata_ball_displacement_arrows_stage_final.csv`

Run:

```bash
python <SKILLS_ROOT>/pfc-postprocessing/scripts/plot_nature_ball_displacement_vectors.py <case-dir> --thin 2
```

Outputs:

- `nature_ball_displacement_vectors.png`
- `nature_ball_displacement_vectors.svg`
- `nature_ball_displacement_vectors.pdf`
- `nature_ball_displacement_vectors.tiff`

## Velocity Vector Figure

Use this when a case has:

- `plotdata_ball_velocity_arrows_stage_A.csv`
- `plotdata_ball_velocity_arrows_stage_B.csv`
- `plotdata_ball_velocity_arrows_stage_C.csv`
- `plotdata_ball_velocity_arrows_stage_D.csv`
- `plotdata_ball_velocity_arrows_stage_peak.csv`
- `plotdata_ball_velocity_arrows_stage_final.csv`

Run:

```bash
python <SKILLS_ROOT>/pfc-postprocessing/scripts/plot_nature_ball_velocity_vectors.py <case-dir> --thin 2
```

Outputs:

- `nature_ball_velocity_vectors.png`
- `nature_ball_velocity_vectors.svg`
- `nature_ball_velocity_vectors.pdf`
- `nature_ball_velocity_vectors.tiff`
