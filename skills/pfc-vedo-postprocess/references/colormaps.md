# Colormap Guidance

- Displacement, velocity, stress magnitude: `viridis` for robust quantitative figures; `jet` only for high-contrast qualitative inspection.
- Signed pressure/tension, dilation/contraction, residuals: `coolwarm` or `RdBu`, with a color range symmetric about zero.
- Material groups and crack types: `Set2` or explicit colors.
- Force chains: commonly red/orange for compression and blue for tension, but state the sign convention in the caption.
- Keep the same scalar range across panels and animation frames when comparing time steps.
