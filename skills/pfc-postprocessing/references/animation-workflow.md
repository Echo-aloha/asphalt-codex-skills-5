# Animation Workflow

This route starts from image frames already exported by PFC 5.0 or another renderer.

1. Keep the original frame directory read-only.
2. Run `export_animation_frames.py` to sort numeric filenames and copy them to `frame_0001.png`, `frame_0002.png`, and so on.
3. Inspect `frames_manifest.csv` for source-to-frame mapping.
4. Run `export_animation.py` with the declared FPS.
5. Confirm frame count, duration, resolution, fixed camera, and fixed scalar range.

No PFC project/save parser is bundled. If only proprietary save/project files exist, export frames or CSVs from the licensed PFC 5.0 environment first.
