# PFC5 Coupling Contract

Minimal JSON:

```json
{
  "coupling_type": "seepage",
  "dimension": 3,
  "length_unit": "m",
  "time_unit": "s",
  "force_unit": "N",
  "exchange_interval_cycles": 100,
  "fluid": {"density": 1000.0, "viscosity": 0.001},
  "mesh": {"nodes": "mesh_nodes.csv", "elements": "mesh_elements.csv"},
  "runtime_validated": false
}
```

Allowed coupling types are `buoyancy`, `seepage`, `pore-pressure`, and
`pfc-flac`. For continuum handoff, add source/target field names, coordinate
transform, interpolation rule, sign convention and residual tolerance.

Mesh files remain project assets. Their licensing and provenance must be recorded.
