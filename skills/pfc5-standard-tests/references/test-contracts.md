# PFC5 Test Contracts

Before selecting a formula, record the source chain: aggregate characterization,
mixture preparation, specimen forming, density/void measurement, performance method and
acceptance context. For JTG 3410-2025, method IDs that look mechanically similar still
represent distinct geometries and metrics.

## Compression or direct tension

Required CSV columns: `strain,stress_mpa`. Optional:
`lateral_strain,load,displacement,time`.

State sign conversions before fitting. Fit stiffness only over a declared strain
interval and export the selected rows.

Do not collapse JTG 3410-2025 T 0713/T 0714 compression, T 0738 dynamic modulus,
T 0742 shear or T 0745 repeated compression into one generic “compression” result.
Store loading mode, confinement, waveform/rate, temperature, cycle definition and the
method-specific output separately.

## Diametral loading

Required: load history, head displacement, specimen diameter and thickness/2D
out-of-plane convention. Preserve raw peak load separately from any derived
stress or normative correction.

If the target is T 0716 splitting, freeze its conditioning, loading direction, specimen
dimensions and stress formula. A fistPkg diametral controller is a kinematic baseline,
not proof that the normative method has been reproduced.

## Creep-recovery

Required: `time,strain` plus load/stress stage labels. Record instantaneous,
delayed, residual and recovered strain with the actual hold/recovery durations.

All tests require equilibrium/inertia evidence and a load-relative time/cycle origin.
Raw histories, corrected histories and normative metrics must be separate outputs. Link
each correction or fitting window to a method/clause locator and preserve the unmodified
rows used by `extract_test_metrics.py`.

See
[`standards-method-map.md`](../../pfc5-asphalt-workflow/references/standards-method-map.md)
for the reviewed source roles and JTG 3410-2025 method families.
