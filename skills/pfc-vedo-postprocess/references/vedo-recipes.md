# vedo Recipes for PFC Post-processing

## Particles colored by displacement

```python
import numpy as np
from vedo import Spheres, Plotter

d = np.load('pfc_step000.npz', allow_pickle=False)
pos, rad, disp = d['pos'], d['rad'], d['disp']
if pos.shape[1] == 2:
    pos = np.c_[pos, np.zeros(len(pos))]
dmag = np.linalg.norm(disp, axis=1)
balls = Spheres(pos, r=rad, res=12)
balls.cmap('viridis', dmag, on='points').add_scalarbar('|disp| (m)')
plt = Plotter(axes=1, bg='white', title='PFC particles colored by displacement')
plt.show(balls, viewup='z')
plt.screenshot('balls_disp.png')
plt.close()
```

## Force chains

For per-contact variable width, bin forces by quantile and render each bin separately.

```python
import numpy as np
from vedo import Lines, Plotter

d = np.load('pfc_step000.npz', allow_pickle=False)
p1, p2, fn = d['c_p1'], d['c_p2'], d['c_fn']
fmag = np.abs(fn)
if len(fmag) == 0:
    raise SystemExit('No contacts in this snapshot')
q = np.quantile(fmag, [0, .5, .75, .9, 1])
actors = []
for i in range(len(q)-1):
    mask = (fmag >= q[i]) & (fmag <= q[i+1])
    if not mask.any():
        continue
    comp = fn[mask] >= 0  # adjust after verifying PFC/export sign convention
    pp1, pp2 = p1[ma
