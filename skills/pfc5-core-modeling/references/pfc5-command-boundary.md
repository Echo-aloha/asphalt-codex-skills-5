# PFC5 Command Boundary

Use the licensed PFC 5.0 help and the target runtime as syntax authority. In the
table below, `<PFC5_HELP_ROOT>` means the directory containing `contents.html`;
the commercial help itself is not part of this package.

## Official-help anchors

| Concern | Page below `<PFC5_HELP_ROOT>` | Decision-changing semantics |
| --- | --- | --- |
| domain | `common/kernel/doc/manual/domain_manual/command_reference/cmd_domain/cmd_domain.html` | The domain is required before model components; changing extents may delete objects; `destroy`, `stop`, `reflect`, and `periodic` are materially different. |
| contact assignment | `docproject/source/manual/pfc_model_components/contacts/cmat_description.html` | Non-default CMAT slots are visited in order; the first matching range wins, otherwise the contact-type default is used. |
| future contacts | `common/contact/doc/contact_manual/contact_commands/cmd_cmat.default.html` | `cmat default` defines the default slot(s) used when contacts are created. |
| existing contacts | `common/contact/doc/contact_manual/contact_commands/cmd_cmat.apply.html` | `cmat apply` entirely reassigns each selected contact model and loses information stored in the previous model. Use `contact property`/`contact method` when only supported fields should change. |
| contact creation/spatial map | `common/kernel/doc/manual/command_processing/commands/cmd_clean.html` | `clean` creates/deletes contacts as needed, initializes piece properties, and updates spatial-search structures. After restore, run it before changing extent tolerances. |
| solve limits | `common/kernel/doc/manual/command_processing/commands/cmd_solve.html` | If several solve limits are supplied, cycling stops when any one is met. `time` is elapsed since that solve; `age` is total process age. |
| histories | `common/kernel/doc/manual/history_manual/history_commands/cmd_history.html` | History sampling interval and history declaration/output are separate controls. Keep stable unique IDs and an explicit time/age history. |
| global settings | `common/kernel/doc/manual/command_processing/commands/cmd_set.html` | Energy tracking is off by default; callback registration/removal and random/deterministic state are global model settings. |
| wall generation/motion | `pfcmodule/doc/manual/wall_manual/wall_commands/cmd_wall_generate.html` and `cmd_wall_attribute.html` | Wall facets must lie in the domain; velocity is translational, spin is angular velocity, and center of rotation must match the intended mechanism. |

## Maintained PFC5 family

- top-level lifecycle commands such as `new`, `domain`, `cycle`, `solve`, `save`,
  and `restore`;
- top-level `cmat default`, ordered `cmat add` slots, `cmat list`, and guarded
  `cmat apply`;
- canonical FISH `define ... end` (`def` may be accepted as an abbreviation by the
  command parser, but generated source should prefer the documented spelling);
- numbered histories such as `history id ... @symbol` used by the PFC5 examples;
- PFC5 wall/ball/clump commands and FISH intrinsics verified in the target product.

## Operational invariants

- Treat a multi-limit `solve` as OR logic. If both equilibrium and a cycle/time cap
  are required, inspect which limit actually ended the solve and reject a cap-ended
  state that missed the equilibrium criterion.
- Save and inventory contacts before `cmat apply`; the operation is not a property-only
  edit and does not preserve the old contact-model state.
- Turn on `set energy mechanical on` before the interval whose energies are needed;
  a later activation cannot reconstruct earlier work.
- Do not use the domain `destroy` condition around a specimen unless deletion is an
  explicit escape policy with object-count auditing.

The audit script detects several known newer-major markers. It is not a parser, and
absence of findings is not proof of runtime compatibility.
