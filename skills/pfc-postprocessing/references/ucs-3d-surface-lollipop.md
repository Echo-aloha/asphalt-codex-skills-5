# 3D UCS Figure-30 Reproduction Profile

This file is an opt-in reproduction profile for one named figure grammar. Apply it only
when the user requests this style. For general scientific visualization, choose marks,
interpolation, colours and exports from the actual data topology and publication target;
in particular, do not infer a complete continuous field from sparse data without a stated
and checked interpolation assumption.

## Role
You are a scientific visualization engineer. Use **Python + matplotlib** to generate a Nature-style 3D paper figure in the style of "numerical simulation continuous surface + discrete error lollipops". The runtime has no network and no scipy; the script must run out of the box.

## Reproduction-Profile Grammar
1. **Continuous field = smooth surface**: plot the more complete quantity as a smooth surface. Surface color maps the physical quantity value itself, with a right-side colorbar labelled with quantity and unit.
2. **No scipy smoothing**: use `matplotlib.tri.Triangulation` + `CubicTriInterpolator(kind='geom')` + `UniformTriRefiner().refine_field(..., subdiv=4)`. Do not import scipy.
3. **Discrete comparison points = error lollipops**: for each point with both experiment and simulation, plot a vertical stick plus red ball:
   - stick base is anchored on the surface value at `(x, y)`;
   - signed stick length is the error `err = sim - exp`, switchable between percent and original unit;
   - positive error points upward, negative error points downward, red ball sits at the tip;
   - if true errors are too small to see, scale so the longest stick is a fixed fraction of z-span, e.g. `STICK_MAX_FRAC = 0.16`;
   - expose `AMP_OVERRIDE`, where `1.0` forces true scale;
   - annotate the red ball using `ax.text` with signed error value.

## 3D Layering And Color
- Discrete marks must stay on top: set `ax.computed_zorder = False`; surface uses low `zorder=1`; sticks/balls/labels use high `zorder=10/20/30`; scatter uses `depthshade=False`.
- Surface and points use separate color semantics: surface uses a cool, perceptually uniform, colorblind-friendly colormap (`cividis` or `viridis`); lollipops are saturated red.

## Nature-Style Rules
- At the file top, set:

```python
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
matplotlib.rcParams['svg.fonttype'] = 'none'
```

- Primary export is editable-text SVG: `fig.savefig('figure.svg', bbox_inches='tight')`; also save PNG at 300 dpi and PDF; finish with `plt.close(fig)`.
- Use restrained colors; ranges should fit data rather than start from zero unnecessarily; green/red only for signed increase/decrease semantics.
- Recommended 3D view: `view_init(elev≈22, azim≈-58)` and `set_box_aspect(...)`; use light grey grid, near-black axis lines, light grey translucent panes.
- Legend has two entries: surface + error lollipop, with `↑ over / ↓ under`; bottom footnote states what stick length means and whether it is amplified.

## Project Data Convention
- X = Boundary distance `d` (mm)
- Y = Inclination `beta` (deg)
- Z = UCS (MPa)
- Data shape: `(case, d, beta, experimental_UCS, simulated_UCS or None)`.
- Experimental values are complete and form the surface.
- Simulated values currently exist only for `beta = 0` and `30`, so only those points get lollipops.
- Constants near the top: `ERR_AS_PERCENT`, `STICK_MAX_FRAC`, `AMP_OVERRIDE`.

## Current Data

```python
DATA = [
    ('b0_d14', 14, 0, 0.052791977, 0.052344800),
    ('b0_d16', 16, 0, 0.060522994, 0.061024900),
    ('b0_d18', 18, 0, 0.068452709, 0.068337400),
    ('b0_d20', 20, 0, 0.064874379, 0.064597400),
    ('b30_d14', 14, 30, 0.054484809, 0.054673200),
    ('b30_d16', 16, 30, 0.072220118, 0.072083100),
    ('b30_d18', 18, 30, 0.082434282, 0.083159400),
    ('b30_d20', 20, 30, 0.060515185, 0.060862600),
    ('b45_d14', 14, 45, 0.074732084, None),
    ('b45_d16', 16, 45, 0.090480575, None),
    ('b45_d18', 18, 45, 0.105330729, None),
    ('b45_d20', 20, 45, 0.072571372, None),
    ('b60_d14', 14, 60, 0.077387114, None),
    ('b60_d16', 16, 60, 0.098195785, None),
    ('b60_d18', 18, 60, 0.105362855, None),
    ('b60_d20', 20, 60, 0.086516257, None),
    ('b90_d14', 14, 90, 0.104148883, None),
    ('b90_d16', 16, 90, 0.113152106, None),
    ('b90_d18', 18, 90, 0.132837980, None),
    ('b90_d20', 20, 90, 0.114018954, None),
]
```

## Code Quality
- Single file with built-in example data, `matplotlib.use('Agg')`, and immediate SVG/PNG/PDF output.
- Clear blocks: data -> error calculation -> surface interpolation -> lollipop sticks/balls/labels -> axes/colorbar/legend -> export.
- Add concise Chinese comments at key places.
- Print self-check info after running: amplification factor, error range, and number of comparison points.
