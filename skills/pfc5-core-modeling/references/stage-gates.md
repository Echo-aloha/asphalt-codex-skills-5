# PFC5 Core Stage Gates

| Gate | Pass condition |
| --- | --- |
| Version | PFC product, 5.0 family, dimension, units, axes and sign are explicit. |
| Determinism | Seed, domain, creation order and identifiers are recorded. |
| Objects | Particle/clump counts, size distribution and boundary IDs/groups are checked. |
| Contacts | Future defaults and existing contacts are handled separately. |
| Equilibrium | A declared force/unbalanced-force criterion passes. |
| Reset | Contact changes are followed by state audit, cycling and re-equilibration. |
| Measurement | Stress, strain, force, displacement and sampling definitions exist before load. |
| V&V | Seed, size, rate, timestep and boundary sensitivities are addressed. |
| Delivery | Sources, parameters, saves, raw exports and rerun instructions are complete. |

Recommended stages:

```text
00_parameters
10_boundaries
20_particles_or_clumps
30_prepare_and_compact
40_install_contacts
50_equilibrate
60_instrument
70_load
80_export_and_verify
```
