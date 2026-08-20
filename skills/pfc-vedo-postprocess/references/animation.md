# Time-series Animation Recipe

Key rules:
1. Sort snapshots numerically.
2. Compute global `vmin/vmax` before the frame loop.
3. Fix the camera and use `resetcam=False` after the first frame.
4. Use `offscreen=True` for batch rendering.

```python
import glob, re
import numpy as np
from vedo import Spheres, Plotter, Video

def natural_key(path):
    return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', path)]

files = sorted(glob.glob('pfc_step*.npz'), key=natural_key)
vmax = max(np.linalg.norm(np.load(f, allow_pickle=False)['disp'], axis=1).max() for f in files)
camera = {'pos': (0.3, -0.3, 0.3), 'focal_point': (0, 0, 0), 'viewup': (0, 0, 1)}
plt = Plotter(axes=1, bg='white', offscreen=True, size=(2400, 1800))
vid = Video('pfc_loading.mp4', fps=20, backend='ffmpeg')
for f in files:
    d = np.load(f, allow_pickle=False)
    pos, rad, disp = d['pos'], d['rad'], d['disp']
    dmag = np.linalg.norm(disp, axis=1)
    balls = Spheres(pos, r=rad, res=10)
    balls.cmap('viridis', dmag, on='points', vmin=0, vmax=vmax)
    plt.clear()
    plt.show(balls, viewup='z', resetcam=False, camera=camera)
    vid.add_frame()
vid.close()
plt.close()
```
