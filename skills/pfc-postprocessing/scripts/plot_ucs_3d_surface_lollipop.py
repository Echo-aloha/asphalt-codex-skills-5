# FigMirror — UCS 3D overlay figure (grammar aligned to the reference figure)
# Styling follows the GitHub "nature-figure" skill (Yuan1z0825/nature-skills):
# sans-serif cascade, editable-text SVG as the primary export, restrained palette.
#
# Reference-figure grammar (paper-style 3D plots):
#   * Smooth interpolated SURFACE whose color maps the QUANTITY VALUE itself
#     (low -> dark blue, high -> yellow via 'cividis'), with a right-side colorbar.
#   * Discrete RED LOLLIPOPS for the comparison points: a vertical stick whose
#     SIGNED LENGTH encodes the error (positive -> up, negative -> down) and a
#     red ball at the stick tip, annotated with the error value. They are drawn
#     ON TOP of the surface (computed_zorder = False).
#
# Role mapping for THIS dataset:
#   * Experimental UCS is complete over the full (d, beta) grid -> SURFACE.
#   * Simulated UCS is only calibrated for some cases -> lollipop error sticks.
#
# No scipy required: smooth surface via matplotlib.tri cubic refinement.
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm, colors
from matplotlib.lines import Line2D
from matplotlib.tri import Triangulation, CubicTriInterpolator, UniformTriRefiner
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# -- nature-figure mandatory rcParams (editable SVG text, sans-serif cascade) --
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
matplotlib.rcParams['svg.fonttype'] = 'none'
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
matplotlib.rcParams['axes.unicode_minus'] = False

# ============================ DATA (replace with real data) ============================
# case, boundary distance d (mm), inclination beta (deg), experimental UCS, simulated UCS (None = not calibrated)
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
# ======================================================================================

# ---- style constants ----
COL_SPINE = '#222222'
COL_GRID  = '#dedede'
COL_TEXT  = '#202020'
COL_BALL  = '#e8413a'   # lollipop ball
COL_STEM  = '#c21f30'   # lollipop stick
VALUE_CMAP = 'cividis'  # simulated-mean surface colormap (cool, colorblind-safe; contrasts the red lollipops)

# Lollipop stick = SIGNED error.  err = simulated - experimental (model error):
#   positive (model over-predicts) -> stick points UP; negative -> DOWN.
ERR_AS_PERCENT = True          # True: err in %, False: err in MPa (true units)
STICK_MAX_FRAC = 0.16          # longest stick = this fraction of the z-axis span
# Set AMP_OVERRIDE to a number to force a fixed amplification (e.g. 1.0 = true scale).
AMP_OVERRIDE = None

# ---- unpack ----
exp = np.array([(d, b, e) for _, d, b, e, _ in DATA], dtype=float)
sim = np.array([(d, b, e, s) for _, d, b, e, s in DATA if s is not None], dtype=float)
x, y, z_exp = exp[:, 0], exp[:, 1], exp[:, 2]
xs, ys, e_exp, e_sim = sim[:, 0], sim[:, 1], sim[:, 2], sim[:, 3]

# signed error per calibrated point
if ERR_AS_PERCENT:
    err = (e_sim - e_exp) / e_exp * 100.0
    err_unit = '%'
else:
    err = (e_sim - e_exp)
    err_unit = ' MPa'

# ---- smooth surface from experimental data via cubic triangulation refinement ----
tri = Triangulation(x, y)
interp = CubicTriInterpolator(tri, z_exp, kind='geom')
tri_ref, z_ref = UniformTriRefiner(tri).refine_field(z_exp, triinterpolator=interp, subdiv=4)

z_floor = float(z_exp.min() * 0.94)
z_top   = float(z_exp.max() * 1.10)
z_span  = z_top - z_floor
val_norm = colors.Normalize(vmin=float(np.nanmin(z_ref)), vmax=float(np.nanmax(z_ref)))

# amplification so the LONGEST error stick is STICK_MAX_FRAC of the z span (visible)
max_abs = float(np.max(np.abs(err))) or 1.0
amp = AMP_OVERRIDE if AMP_OVERRIDE is not None else (STICK_MAX_FRAC * z_span) / max_abs

# lollipop geometry: stick base on the experimental surface, ball at base + signed error
base = e_exp                      # the experimental value sits ON the surface
tip  = base + err * amp           # ball height: + error up, - error down

fig = plt.figure(figsize=(10.2, 6.2), dpi=240)
fig.patch.set_facecolor('white')
ax = fig.add_subplot(111, projection='3d')
ax.computed_zorder = False        # respect manual zorder so the experimental lollipops always stay on top

# --- SURFACE: smooth experimental field colored by value ---
surf = ax.plot_trisurf(tri_ref, z_ref, cmap=VALUE_CMAP, norm=val_norm,
                       antialiased=True, alpha=0.9, linewidth=0.0, shade=False, zorder=1)
surf.set_edgecolor((0.35, 0.35, 0.35, 0.12))
surf.set_linewidth(0.1)

# --- RED LOLLIPOPS: vertical stick (length = signed error) + ball at tip, ON TOP ---
for xi, yi, zb, zt in zip(xs, ys, base, tip):
    ax.plot([xi, xi], [yi, yi], [zb, zt], color=COL_STEM,
            linewidth=1.8, alpha=0.95, solid_capstyle='round', zorder=10)
ax.scatter(xs, ys, tip, s=72, c=COL_BALL, edgecolor='#5a0d0d',
           linewidth=0.6, depthshade=False, zorder=20)
# small anchor dot where the stick meets the surface
ax.scatter(xs, ys, base, s=10, c=COL_STEM, depthshade=False, zorder=9)

for xi, yi, zt, ev in zip(xs, ys, tip, err):
    up = ev >= 0
    ax.text(xi, yi, zt + (0.02 if up else -0.02) * z_span,
            f'{ev:+.1f}{err_unit}', ha='center', va='bottom' if up else 'top',
            fontsize=7.0, color=COL_TEXT, zorder=30)

# --- axes ---
ax.set_xlabel('Boundary distance d (mm)', labelpad=8, fontsize=9.0, color=COL_TEXT)
ax.set_ylabel('Inclination beta (deg)', labelpad=9, fontsize=9.0, color=COL_TEXT)
ax.set_zlabel('UCS (MPa)', labelpad=7, fontsize=9.0, color=COL_TEXT)
ax.set_xlim(13.3, 20.7)
ax.set_ylim(-4, 94)
ax.set_zlim(z_floor, z_top)
ax.set_xticks([14, 16, 18, 20])
ax.set_yticks([0, 30, 45, 60, 90])
ax.set_zticks([0.05, 0.07, 0.09, 0.11, 0.13])
ax.view_init(elev=22, azim=-58)
ax.set_box_aspect((1.10, 1.45, 0.80))
ax.tick_params(axis='both', which='major', labelsize=7.6, pad=1.6, colors=COL_TEXT, length=0)
ax.zaxis.set_tick_params(labelsize=7.6, pad=2.0, colors=COL_TEXT, length=0)

for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
    axis._axinfo['grid']['color'] = COL_GRID
    axis._axinfo['grid']['linewidth'] = 0.55
    axis._axinfo['axisline']['color'] = COL_SPINE
    axis._axinfo['axisline']['linewidth'] = 0.8
ax.xaxis.pane.set_facecolor((0.965, 0.965, 0.965, 0.5))
ax.yaxis.pane.set_facecolor((0.965, 0.965, 0.965, 0.5))
ax.zaxis.pane.set_facecolor((0.985, 0.985, 0.985, 0.7))
for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
    pane.set_edgecolor('#eeeeee')

# --- colorbar = the value itself ---
cbar = fig.colorbar(surf, ax=ax, fraction=0.038, pad=0.04, shrink=0.74, aspect=18)
cbar.set_label('UCS (MPa)', fontsize=8.6, color=COL_TEXT, labelpad=6)
cbar.ax.tick_params(labelsize=7.2, length=0, colors=COL_TEXT, pad=2)
cbar.outline.set_linewidth(0.55)
cbar.outline.set_edgecolor('#333333')

# --- legend ---
try:
    base_cmap = matplotlib.colormaps[VALUE_CMAP]
except Exception:
    base_cmap = cm.get_cmap(VALUE_CMAP)
legend_handles = [
    Line2D([0], [0], color=base_cmap(0.7), lw=6.0, alpha=0.9, label='Experimental UCS (surface)'),
    Line2D([0], [0], marker='o', color=COL_STEM, markerfacecolor=COL_BALL,
           markeredgecolor='#5a0d0d', lw=1.8, markersize=7.0,
           label='Sim. error lollipop (↑ over / ↓ under)'),
]
leg = ax.legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(0.02, 0.98),
                frameon=True, fontsize=7.8, borderpad=0.4, handlelength=1.6, labelspacing=0.4)
leg.get_frame().set_facecolor((1, 1, 1, 0.8))
leg.get_frame().set_edgecolor('#d0d0d0')
leg.get_frame().set_linewidth(0.6)

fig.text(0.51, 0.03, f'Lollipop stick length = simulation error (sim − exp, {("%" if ERR_AS_PERCENT else "MPa")}), scaled for visibility; up = over-, down = under-prediction.',
         ha='center', va='center', fontsize=7.2, color='#555555')
fig.subplots_adjust(left=0.06, right=0.88, bottom=0.1, top=0.96)
fig.savefig('figure.svg', bbox_inches='tight', pad_inches=0.03)            # primary: editable text (nature-figure rule)
fig.savefig('figure.png', dpi=300, bbox_inches='tight', pad_inches=0.03)   # raster preview
fig.savefig('figure.pdf', bbox_inches='tight', pad_inches=0.03)
plt.close(fig)
print('OK: amp', round(amp, 1), '| err range', round(err.min(), 2), round(err.max(), 2), err_unit, '| sim points', len(sim))