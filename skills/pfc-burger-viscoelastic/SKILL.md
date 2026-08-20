---
name: pfc-burger-viscoelastic
description: Select, probe, calibrate, and audit the Burger viscoelastic contact model for PFC 5.0 asphalt-mixture cases, including Maxwell-Kelvin parameter roles, units, temperature/rate dependence, PFC5 cmat assignment, timestep checks, creep/recovery validation, and PFC5-only syntax boundary checks.
---

# PFC Burger Viscoelastic Contact Model

Use this skill for the viscoelastic contact-law stage of
`pfc5-asphalt-workflow`. Burger may represent homogenized asphalt mastic behavior at
selected contacts, but it does not by itself create an explicit binder phase or guarantee
mixture-scale behavior.

## When to use

- assign or audit Burger contacts in a PFC5 asphalt specimen;
- interpret Maxwell and Kelvin spring/dashpot roles;
- fit temperature- and rate-dependent mixture/mastic response;
- build a two-contact or small-RVE verification probe;
- review a Burger command block for non-PFC5 contamination.

Do not use this skill to invent production constants from a generic table.

## Required inputs

- PFC2D or PFC3D 5.0 and the unit system;
- object/contact pairs that Burger is intended to represent;
- all Burger properties with units, or raw calibration curves with units;
- test temperature, loading rate/frequency and conditioning history;
- specimen/contact geometry and resolution used during inverse fitting;
- target creep/recovery, dynamic modulus/phase or other macro curves;
- material level and test provenance: binder, mastic or mixture; for JTG 3410-2025
  inputs, record the exact DSR/BBR/MSCR/LAS or mixture-performance method rather than
  writing only “rheology data”;
- contact replacement policy for existing versus future contacts;
- timestep/damping/stop criteria and acceptance tolerances.

## Constitutive interpretation

Burger combines a Maxwell branch (spring plus dashpot in series) and a Kelvin branch
(spring plus dashpot in parallel). Normal and shear directions have separate parameters.
Stiffness-like terms control instantaneous/delayed compliance; dashpot terms control time
scale and permanent or delayed deformation. Friction and interface choices remain
separate physical assumptions.

Property names and dimensions are syntax-family-specific. Read
`references/burger-theory.md` for theory and `references/pfc-command.md` for
version-labelled syntax notes.

## Workflow

1. Freeze units, temperature, rate/frequency, geometry and contact-pair meaning.
2. Verify the PFC5.0 Burger property names with a minimal runtime probe.
3. Run a minimal PFC5 two-body contact probe: contact creation, load/hold/unload,
   recovery, save/restore and property listing.
4. Install the model using PFC5 `cmat` semantics, distinguishing future defaults from
   current-contact changes.
5. Re-equilibrate the specimen and preserve a pre-load save.
6. Classify every curve as binder, mastic or mixture before fitting. JTG T 0627/T 0628,
   T 0647 and T 0648 binder data are priors or trend constraints, not direct mastic-contact
   targets. Only a declared test on the same mastic may target a mastic RVE; contact
   constants still require inverse fitting through the fixed PFC discretization.
7. Validate creep and recovery at the calibration condition, then confirm at another
   duration/rate/temperature or independent specimen.
8. Check timestep sensitivity and rerun the target Marshall/rutting pilot.

## Working rules

- PFC5 is the only supported target in this package. Unsupported-major-version
  command blocks are rejected, not retained as migration references.
- Do not use numerical “60 °C reference values” as production defaults; their units,
  geometry scaling and provenance are not established for the user's case.
- Never reuse one parameter set at another temperature without an explicit,
  experimentally supported shift/fitting method.
- Do not mix binder-level JTG 3410-2025 outputs with mixture-level T 0738/T 0745/T 0719
  curves as if they had the same geometry or stress measure. Record the scale transition
  and validate it through the RVE/specimen.
- Do not label a binder DSR/BBR curve as mastic evidence merely because the Burger
  contact represents homogenized mastic. If no same-material mastic test exists, record
  the mastic calibration layer as assumption-bound and test its sensitivity.
- Do not delete/recreate all contacts merely as a generic recipe. Choose and verify a
  version-correct current/future contact transition that preserves the intended state.
- Treat a linear fallback as a diagnostic branch, never as evidence that Burger is
  calibrated.
- Mark commands `runtime_verified` only after a PFC5.0 runtime accepts them and
  the probe response passes.

## Output contract

- PFC2D/PFC3D 5.0, units, temperature/rate and contact-pair meaning;
- exact version-labelled assignment command and current/future contact policy;
- parameter table with units, bounds, provenance and fitted values;
- two-body/RVE probe histories and timestep sensitivity;
- calibration/confirmation curves and error metrics;
- pre/post contact-installation save map;
- unresolved runtime or identifiability risks.

## Local contents

- `references/burger-theory.md` — Maxwell-Kelvin mechanics.
- `references/pfc-command.md` — version-labelled command notes and legacy examples.
- `references/calibration.md` — guarded macro-response fitting route.
- `../pfc5-asphalt-workflow/references/standards-method-map.md` — reviewed test-method roles and scale boundaries.
- `scripts/burger_contact_probe.p3dat` — executable PFC3D 5.0 two-ball relaxation probe; parameters are not calibrated material values.
- `agents/openai.yaml` — Agent metadata.
- `dependencies.json` — package-level link to the standards method map.
