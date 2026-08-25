# PFC5 wheel-tracking modeling strategy

## Three gates

| Gate | Model | Purpose |
| --- | --- | --- |
| RVE | material-scale cell | Burger/contact calibration and timestep sensitivity |
| strip pilot | shortened/narrowed slab | controller, footprint, boundaries and cost |
| full size | selected standard geometry | final prediction after pilot acceptance |

Dimensions and run durations are case inputs. A convenient strip/RVE is a numerical
design, not a standard specimen.

## Controller pseudocode

Use pseudocode until the exact PFC5 wall/FISH intrinsics have been verified:

```text
initialize:
    locate wheel/head wall pointer
    set target reaction force and tolerance
    set maximum vertical correction velocity
    register exactly one callback

each callback:
    read current wheel position and grain-contact reaction
    compute horizontal position/velocity from the declared motion law
    error = target_reaction - measured_reaction
    compute bounded vertical velocity from error and controller gain
    assign verified PFC5 translational velocity
    if rolling route:
        set the wheel-axis center of rotation
        assign verified PFC5 angular velocity with consistent sign
        verify contact-point kinematics against |v| = |omega| R
    record command, reaction, error, position, rut reference and count
```

Do not prescribe contact reaction by writing an output force intrinsic. A position- or
velocity-controlled actuator with measured reaction is the normal DEM control pattern.

PFC5 wall semantics used by this controller:

- `wall.force.contact(w)` is the global-coordinate sum of all contact forces acting on
  the wall and is an observation, not the actuator command;
- `wall.vel`/wall `velocity` is translation, whereas `wall.spin`/wall `spin` is angular
  velocity in radians per second;
- the wall center of rotation defaults to the origin and translates with the wall when
  translational velocity is supplied. An offset wheel must therefore set and verify its
  axis center before applying spin;
- wall/facet `conveyor` is a fictitious velocity used in contact relative velocity
  without moving the facets, and the PFC5 help forbids a nonzero conveyor velocity
  while vertex velocities are active. Treat it as a separate fixed-geometry surrogate,
  not as proof of a geometrically rolling wheel.

For an intersection head, extend the callback conceptually to two axes. Keep separate
bounded gains and velocity limits, record both command/reaction errors, and verify the
signs first with positive and negative horizontal probes. A target ratio
`F_horizontal/F_vertical` is an external load demand; it is not permission to overwrite
the material or wheel contact-friction coefficient.

## Load-equivalence audit

For a physical pressure `p` and declared reference area `A_ref`, an equivalent target
force may be `F_target = p A_ref`. Record:

- how `A_ref` is defined;
- whether it is fixed or measured;
- difference between reference area and actual discrete contact footprint;
- reaction error during acceleration, reversal and steady travel;
- sensitivity to wheel/facet resolution.

## Physical-to-surrogate ledger

Every fixed patch, equivalent static load or accelerated-time route needs one row per
transformation:

| Stage | Required record |
| --- | --- |
| physical load | waveform, frequency/speed, path, dwell/rest, contact geometry and vector load |
| DEM actuator | moving/rolling/fixed route, reference area, command law and reaction tolerances |
| time mapping | `t -> t'`, `lambda`, changed constitutive parameters and derivation |
| preserved quantities | for example target reaction, declared impulse or selected linear-Burger creep terms |
| discarded quantities | moving footprint, unload/recovery, inertia, frictional path, damage or rearrangement as applicable |
| validation | unaccelerated/moving pilot cases, metrics, tolerance, result and evidence file |

For the linear Burger transform `t'=t/lambda` with fixed stiffness, candidate dashpots
are `c_m'=c_m/lambda` and `c_k'=c_k/lambda`. This is accepted only after a direct
`lambda=1` comparison. It does not prove moving-wheel or cyclic equivalence.

## Count and time

Store time, one-way passes, full cycles and solver cycles in separate columns. Do not
derive laboratory minutes from solver cycles unless a verified physical-time mapping
exists.

## Rut-depth measurement

Define a pre-load reference surface and a wheel-track measurement band. Report at least:

- deepest vertical displacement;
- robust band statistic (for example a documented percentile/median);
- lateral heave where relevant;
- wheel position at sampling;
- whether detached/ejected particles are included.

Use the exact selected-standard intervals and coefficients for dynamic stability. If the
standard text is unavailable, retain raw histories and leave the normative calculation
pending.

## Intersection diagnostics

Run a vertical-only baseline before coupled cases. For each positive/negative horizontal
case, retain:

- vertical and horizontal command/reaction/error histories;
- forward- and reverse-face vertical deformation plus lateral heave;
- phase-labelled aggregate/mastic displacement vectors;
- slip/contact-state/energy histories where available; PFC5 Burger has no own energy
  partition, so record that gap and do not synthesize a Burger dissipation history;
- shear-stress depth profiles with tensor component, axes, sign, measure radius,
  volume-weighting/overlap and sample time;
- free versus confined boundary and at least two thickness/resolution cases when making
  a depth-of-influence claim.

The reaction ratio, deformation asymmetry and shear-depth profile must be calculated
from raw signed data. Plotting absolute values is a separate disclosed transformation.

## Runtime gates

- empty-motion probe passes;
- contact/load-servo probe passes;
- short strip pilot reaction error is within tolerance;
- no wall penetration/particle escape/callback duplication;
- timestep and facet-resolution sensitivity are acceptable;
- restart reproduces the history without callback multiplication.
- positive and negative horizontal probes reproduce the intended vector-reaction signs;
- accelerated and unaccelerated pilots meet declared curve/state/energy tolerances;
- free/confined boundary sensitivity is reported for intersection interpretation;
- measure-region component and weighting definitions reconstruct the exported profile.
