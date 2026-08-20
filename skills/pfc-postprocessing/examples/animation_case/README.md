# Animation Case

This example demonstrates a version-independent final step after PFC 5.0 has
already exported PNG frames.

## What is inside

- `raw_frames/` with `jieguo_*.png`

## Teaching point

Animation is just ordered frame images plus one assembly step.

## Recommended commands

```bash
python <SKILLS_ROOT>/pfc-postprocessing/scripts/export_animation_frames.py ^
  --input-dir <SKILLS_ROOT>/pfc-postprocessing/examples/animation_case/raw_frames ^
  --output-dir <SKILLS_ROOT>/pfc-postprocessing/examples/demo_outputs/ordered_frames

python <SKILLS_ROOT>/pfc-postprocessing/scripts/export_animation.py ^
  --input-dir <SKILLS_ROOT>/pfc-postprocessing/examples/demo_outputs/ordered_frames ^
  --output-dir <SKILLS_ROOT>/pfc-postprocessing/examples/demo_outputs/animations ^
  --stem demo_animation
```
