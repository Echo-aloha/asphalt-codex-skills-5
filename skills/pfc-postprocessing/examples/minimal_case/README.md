# Minimal Case

This is the first example a new user should touch.

## Goal

Teach the full post-processing idea without requiring PFC itself.

## What is inside

- `stress_strain.csv`
- `plotdata_ball_fields.csv`
- `plotdata_stress.csv`
- `plotdata_porosity.csv`
- `plotdata_fracture_orientations.csv`
- `rutting_history.csv`
- `rutting_shear_profile.csv`

## What you can learn here

- how one curve file becomes one response figure
- how scattered field data becomes contour-like maps
- how angle lists become rose diagrams
- how solver/equivalent time, vector reactions, face asymmetry and a signed shear-depth
  profile remain auditable in one rutting evidence figure
- how data contracts make the workflow portable

## Recommended commands

```bash
python <SKILLS_ROOT>/pfc-postprocessing/scripts/run_demo.py
```

Or run each script separately against this folder.
