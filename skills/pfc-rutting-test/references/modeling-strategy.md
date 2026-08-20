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
        assign verified PFC5 angular velocity with consistent sign
    record command, reaction, error, position, rut reference and count
```

Do not prescribe contact reaction by writing an output force intrinsic. A position- or
velocity-controlled actuator with measured reaction is the normal DEM control pattern.

## Load-equivalence audit

For a physical pressure `p` and declared reference area `A_ref`, an equivalent target
force may be `F_target = p A_ref`. Record:

- how `A_ref` is defined;
- whether it is fixed or measured;
- difference between reference area and actual discrete contact footprint;
- reaction error during acceleration, reversal and steady travel;
- sensitivity to wheel/facet resolution.

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

## Runtime gates

- empty-motion probe passes;
- contact/load-servo probe passes;
- short strip pilot reaction error is within tolerance;
- no wall penetration/particle escape/callback duplication;
- timestep and facet-resolution sensitivity are acceptable;
- restart reproduces the history without callback multiplication.
