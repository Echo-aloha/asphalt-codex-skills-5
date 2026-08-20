---
name: pfc-rutting-test
description: Design, implement, and audit PFC3D 5.0 asphalt wheel-tracking/rutting simulations using RVE-to-strip-to-full-size scaling, PFC5-compatible wall motion and reaction-force control, Burger-calibrated contacts, rut-depth histories, edition-specific dynamic-stability calculations, and explicit equivalent-load validation.
---

# PFC5 Wheel-Tracking and Rutting Test

Use this skill after specimen generation and Burger calibration. Prefer PFC3D because
wheel width, lateral confinement, contact patch and rut geometry are intrinsically
three-dimensional.

## When to use

- plan a wheel-tracking/rutting model in PFC 5.0;
- choose a moving, rolling-faceted or fixed equivalent cyclic load;
- servo a wall/head to a target reaction rather than assign a read-only contact force;
- extract rut-depth histories and an edition-specific dynamic-stability metric;
- scale an RVE to a strip/pilot and then a full-size slab.

Do not use this skill for Marshall or for specimen generation.

## Required inputs

- exact PFC3D 5.0 build, units and runtime budget;
- governing standard edition, method ID, clauses and machine/specimen coefficients;
- slab, mold, wheel and travel geometry;
- conditioning/test temperature;
- wheel motion definition and whether “count” means one-way pass or complete cycle;
- prescribed pressure/load and the physical/equivalent contact-area definition;
- load-control implementation and tolerance;
- load-ready specimen plus calibrated contact parameters;
- rut-depth measurement region/reference and stop condition;
- laboratory rut curve/dynamic-stability targets.

The current reviewed route is JTG 3410-2025 T 0719-2025, effective 2025-10-01.
JTG E20-2011 T0719 is a legacy route and must not supply current default dimensions,
time windows or coefficients.

## Modeling hierarchy

1. **RVE/material check** — calibrate creep/recovery and timestep sensitivity.
2. **Strip/pilot model** — verify boundaries, contact patch, load servo, wheel motion,
   rut measurement and computational cost.
3. **Full-size model** — use only after the first two gates pass.

The exact dimensions and test values come from the selected standard edition or
laboratory protocol, not from a remembered default.

## Loading routes

| Route | Meaning | Acceptance gate |
| --- | --- | --- |
| moving faceted wheel/head | translation over slab | reaction and footprint match target throughout travel |
| rolling faceted wheel | translation plus angular velocity | kinematic sign, slip and facet-resolution sensitivity |
| fixed equivalent cyclic patch | accelerated surrogate | correlation to moving-wheel pilot; never label as normative motion |

In PFC5, contact force is normally an observed reaction. Apply load by a verified servo
or velocity/position control and demonstrate that the reaction meets the target.
Pressure-to-force conversion requires a declared reference area; the evolving DEM
contact area is not automatically that area.

## Workflow

1. Freeze standard edition, physical parameters and numerical equivalents separately.
2. Restore the load-ready specimen, audit boundaries/contact groups and equilibrate.
3. Build and motion-test the wheel/head with no specimen.
4. Run a small contact/load-servo probe; quantify reaction error and oscillation.
5. Run the strip pilot for a short declared number of cycles/passes.
6. Record wheel position, commanded motion, reaction, reference surface, rut depth,
   the seven fixed-position measurements or an approved equivalent, timestep,
   equilibrium/inertia indicators, one-way pass count and round-trip count.
7. Confirm no wall penetration, particle escape, axis/sign error or callback duplication.
8. Run the production duration with restart saves.
9. Compute the standard metric only from the selected edition's formula, intervals and
   coefficients; otherwise report the raw rut history with the metric pending.
10. Compare against laboratory curves and run seed/resolution/rate/load-route
    sensitivity.

## Working rules

- Keep PFC5 command/FISH syntax version-pure.
- Do not set `wall.force` as if it were a prescribed actuator without proof from the
  exact PFC5 API; use a verified motion/servo controller.
- Do not assume a rectangular patch, accelerated cycle or fixed load is equivalent to a
  moving rubber wheel. Calibrate and label the surrogate.
- For T 0719-2025, compute DS from the current method's pass-count interval and width
  coefficient. Do not use the legacy `45 min/60 min` shorthand or an unverified extra
  correction coefficient.
- Preserve RVE, strip, pre-load, pilot and production milestone saves.
- Full-size output without pilot load-control evidence is not validated.

## Output contract

- PFC build/units and standard edition/method/clause;
- physical versus DEM-equivalent parameter table;
- specimen/wheel/boundary/contact assignment;
- actuator/servo pseudocode or PFC5-verified code plus reaction-error history;
- rut-depth measurement definition and raw time/pass/cycle history;
- edition-correct metric calculation with units/coefficients, or pending status;
- RVE/strip/full-size stage evidence and sensitivity results;
- laboratory comparison and `runtime_validated` status.

## Local contents

- `references/overview.md` — current T 0719-2025 measurement, count and PFC3D mapping.
- `references/jtg-t0719.md` — current-version gate, user-input template and symbolic metric; no standard data tables.
- `references/modeling-strategy.md` — PFC5-safe hierarchy and controller pseudocode.
- `../pfc5-asphalt-workflow/references/standards-policy.md` — standards policy.
- `scripts/rutting_contact_pilot.p3dat` — executable curved-wheel PFC3D 5.0 contact/translation pilot; not a normative wheel-tracking model.
- `dependencies.json` — package-level sibling-skill assets required for the complete workflow.
- `agents/openai.yaml` — Agent metadata.
