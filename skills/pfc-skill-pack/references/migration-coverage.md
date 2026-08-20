# PFC5 Functional Migration Coverage

This record prevents useful capabilities from disappearing when an older, mixed-version
module is removed. Migration means rewriting the capability around a PFC5 contract; it
does not mean restoring the old command files.

## High-value capabilities

| Former capability | PFC5 owner | Retained result |
| --- | --- | --- |
| end-to-end workflow | `pfc5-asphalt-workflow`, `pfc5-core-modeling` | staged case contract, saves, audit and delivery gates |
| basic elements and contact lifecycle | `pfc5-core-modeling` | boundary/object sequence, present-versus-future contact assignment |
| FISH programming | `pfc5-fish` | `def`/`end`, histories, command blocks and callback activation probes |
| servo and modeling techniques | `pfc5-servo-calibration` | sign probe, bounded gain, target ledger and validation sequence |
| dual-target calibration | `pfc5-servo-calibration` | guarded two-by-two update with determinant and bounds checks |

## Conditional capabilities

| Former capability | PFC5 owner | Condition for use |
| --- | --- | --- |
| CAD and shape import | `pfc5-geometry-import` | convert to an explicit node/element CSV contract, then implement the final importer against the licensed runtime |
| dynamics and stress waves | `pfc5-dynamics-wave` | pass dimension, direction, wavelength/spacing and timestep checks |
| general mechanical tests | `pfc5-standard-tests` | declare geometry, sign convention, standard formula and raw channels |
| AE and energy analysis | `pfc5-ae-energy` | declare hit/event and energy conventions; do not infer them from plots |
| fluid and solver coupling | `pfc5-coupling` | validate both solvers independently and freeze the exchange contract |
| Python support | offline scripts in the eight migrated skills | use for generation, audit and post-processing only; embedded object APIs are outside this package |
| fast calibration | `pfc5-servo-calibration` | retain DOE/ledger/two-target mechanics; material formulas require independent provenance and unit checks |

## Deliberate exclusions

- command files from an unsupported major version;
- rock-only constitutive assumptions, crack laws and empirical coefficients that have
  no validated asphalt interpretation;
- commercial examples, binaries, manuals, projects or save states;
- unverified embedded Python object APIs;
- claims of runtime success based only on static checks.

Every row above has one current owner. If an owner is renamed or removed, update this
record, the root required-skill manifest and all dependency contracts in the same change.
