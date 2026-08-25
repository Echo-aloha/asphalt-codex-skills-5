# AE And Energy Contract

Hit CSV required columns:

`time,x,y,mode`; add `z` for 3D. Preserve a unique `hit_id` when available.

The bundled tool builds a hit graph: two hits receive an edge only when both
conditions pass, and one event is one connected component:

- maximum time separation;
- maximum Euclidean spatial separation.

This is single-link clustering. A chain can therefore join two endpoint hits that do
not directly satisfy the windows. Report the windows and review large chain-merged
events; choose a stricter project-specific linkage when that behavior is unsuitable.

Export event start/end time, centroid, hit count, tension/shear counts and member
IDs or a traceable membership file.

For stress in MPa and dimensionless strain:

- trapezoidal `integral(stress d strain)` has units MJ/m3;
- recoverable elastic approximation is `stress^2/(2E)` when E is in MPa;
- dissipated approximation is input minus elastic.

Negative dissipated values are diagnostics of sign, modulus, unloading or model
assumptions; do not silently clamp them.

Native PFC5 energy and this macro integral are separate ledgers. Native mechanical
energy tracking must be enabled before the interval of interest and only model-supported
partitions may be reported. In particular, PFC5 Burger exposes no energy partition;
do not label `input - elastic` as Burger dashpot energy.
