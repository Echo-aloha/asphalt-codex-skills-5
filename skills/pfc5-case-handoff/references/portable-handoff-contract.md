# Portable PFC5 Case Handoff Contract

## 1. Evidence Layers

Keep these claims separate:

| Layer | Evidence | Does not prove |
| --- | --- | --- |
| integrity | digest match and complete file inventory | PFC compatibility or physical validity |
| static portability | relative dependencies, no private absolute path, PFC5 source audit | successful restore or solve |
| restore | target PFC5 opens the saved state and expected objects exist | equilibrium, calibration, or load readiness |
| audit runtime | a bounded probe reproduces declared invariants | later constitutive or test stages |
| production runtime | intended stage completes and acceptance gates pass | experimental validation unless compared with data |

## 2. State Classification

Classify saves and entrypoints by evidence, not by filename:

- `accepted`: all declared gates for that stage passed.
- `restart_only`: preserves useful geometry or objects but has an unpassed solve or
  acceptance gate; it may seed a guarded recovery branch.
- `diagnostic_only`: retained for inspection and provenance, never for a production
  comparison or downstream calibration.
- `failed`: known failed gate or corrupted/incomplete state.
- `obsolete`: superseded but retained for traceability.
- `unknown`: claim has not been independently checked.

An accepted specimen-generation save is not automatically load-ready. Record contact
model state, equilibration after contact replacement, instrumentation, and loading
authorization independently.

## 3. Restore-First Audit

For a migrated case, prefer the cheapest evidence-preserving sequence:

1. verify the supplied integrity manifest;
2. identify the installed PFC product and exact release;
3. scan executable sources and dependency paths;
4. restore a copy of the claimed last-good save;
5. compare object/boundary counts, extents, units, contact state, and saved gates;
6. run a bounded audit driver or minimal probe;
7. rebuild from zero only when restore evidence is absent, invalid, or insufficient for
   the requested claim.

Never overwrite the only accepted save during first-machine validation. New audit saves
and logs need distinct names until the handoff is accepted.

## 4. Recovery Without Gate Erosion

A stopped solve can still leave a useful `restart_only` geometry state. Recovery is
permitted only when the state has explicit object-conservation and geometry checks, the
failed criterion is named, and the recovery branch applies a documented numerical
change. Preserve the failed branch, re-run the final acceptance gates, and do not make
the target easier merely to obtain a green status.

Use stage-specific mechanics. Near-zero-force particle relaxation may need an overlap
or geometry criterion, while a gravity-supported or loaded stage needs equilibrium and
reaction evidence. A fixed cycle count is a budget, not an acceptance gate.

## 5. Path And Dependency Portability

- Record the runtime working directory for every entrypoint.
- Prefer relative `call` and `restore` targets within the private handoff root.
- Treat absolute paths as provenance records only; remove them from executable routes.
- Avoid save behavior whose destination depends on an installation directory or an
  ambiguous `localdir` interpretation.
- Keep external licensed dependencies unbundled. Record logical names, roles, expected
  layouts, legal source, and optional digests.
- Quarantine historical drivers that no longer represent the successful chain.

Run `scripts/audit_pfc5_handoff.py <private-root> --expected-major 5` after every path
rewrite. Add `--checksums <manifest.csv>` when a digest manifest exists. The auditor is
read-only and does not establish runtime success.

## 6. Geometry And Object Invariants

At each recoverable milestone, record the invariants relevant to that model:

- seed and object counts by type/group;
- no unintended domain escape or silent deletion;
- boundary count, IDs/groups, extents, and moving-wall positions;
- specimen dimensions and declared dimensional idealization;
- maximum overlap or other stage-appropriate geometry check;
- equilibrium/reaction criterion only where it has a meaningful force scale;
- contact model and current-versus-future assignment state;
- callback/history activation state across save/restore.

Spatial occupancy, local porosity, surface-gap, or boundary-corrected diagnostics may
support uniformity review. Keep their resolution, boundary treatment, and interpretation
explicit; they are not automatically physical air voids or a standard acceptance test.

## 7. Private/Public Split

The private handoff may contain project sources, inputs, logs, saves, project files, and
licensed dependency locators. A reusable public skill or release may contain only the
general contract, empty templates, synthetic tests, and privacy-safe tools. Do not use a
real project identifier, path, material, dimension, seed, parameter, hash, metric, source
excerpt, or save name as a packaged example.
