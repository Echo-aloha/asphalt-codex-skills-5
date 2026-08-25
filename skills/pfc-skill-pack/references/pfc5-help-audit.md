# PFC5 Official-Help Audit

This package was audited against an installed PFC 5.0 HTML help tree. The help is a
commercial external dependency and is not redistributed. Resolve
`<PFC5_HELP_ROOT>` to the directory that contains `contents.html`; never commit the
private absolute path.

## Source identity

- Product family: PFC2D/PFC3D 5.0.
- Audited HTML pages carry Itasca copyright and a 2016 update marker.
- Runtime evidence remains separate: the maintained probes were manually recorded on
  PFC3D build 5.00.25, as documented in `docs/pfc5-runtime-verification.md`.
- The HTML help can contain local inconsistencies. When an index page, model page,
  official verification data file, and runtime disagree, record all four and prefer a
  minimal target-build probe over silent normalization.

## Corrected package assumptions

| Area | Official-help result | Package consequence |
| --- | --- | --- |
| CMAT | Ordered non-default slots are tested first; first range match wins; the type default is fallback. `cmat apply` entirely replaces selected contact models and loses old model state. | Contact-pair rules now require deliberate slot order and transactional apply/audit. |
| solve | Multiple limits stop on the first limit met. `time` is solve-relative; `age` is process-total. | Equilibrium and safety caps are checked separately and the terminating limit is recorded. |
| clean | Builds/updates contacts, piece properties, and spatial search; it is required after restore before extent-tolerance edits. | `clean` is no longer described as a cosmetic overlap-removal step. |
| particle generation | `distribute` permits significant overlap and its target porosity ignores overlap; ball distribute also ignores pre-existing balls for that invocation. `generate` rejects overlap but may stop at the tries limit. | Initial generation target and achieved post-compaction voids are kept separate; actual counts/overlaps are audited. |
| clump volume | Template/create commands require declared or calculated inertial properties; overlapping pebbles are not a valid volume sum. | Mass-volume closure uses clump volume, not the sum of pebble sphere volumes. |
| Burger | `bur_mode=0` allows tensile normal force and `bur_mode=1` does not; contacts are inactive for positive gap. The model has no inheritance, methods, or energy partitions. | The package distinguishes transient tensile force from separated-gap damageable cohesion and no longer assumes Burger energy output. |
| FISH callbacks | `whilestepping` auto-registers at `-1.0`; explicit duplicate registrations cause duplicate calls; one remove clears one instance. | Callback ledgers/counters replace unconditional re-registration after restore. |
| wall mechanics | Contact reaction is a global-coordinate sum. Translation, spin, center of rotation, and conveyor velocity have distinct meanings. | Marshall keeps two signed head reactions; rutting distinguishes translation, rolling, and conveyor surrogates. |
| energy | Mechanical energy tracking is off by default, and not every contact model provides partitions. | Energy tracking is enabled before the measured interval and missing partitions stay explicit. |
| geometry import | Native geometry import supports Itasca geometry, partial DXF, and STL. `wall import nothrow` may ignore offending facets. | A successful import is followed by topology/closure/contact checks; `nothrow` is diagnostic only. |

## Primary page map

All paths are below `<PFC5_HELP_ROOT>`:

- `docproject/source/manual/pfc_model_components/contacts/cmat_description.html`
- `common/contact/doc/contact_manual/contact_commands/cmd_cmat.default.html`
- `common/contact/doc/contact_manual/contact_commands/cmd_cmat.add.html`
- `common/contact/doc/contact_manual/contact_commands/cmd_cmat.apply.html`
- `common/kernel/doc/manual/command_processing/commands/cmd_clean.html`
- `common/kernel/doc/manual/command_processing/commands/cmd_solve.html`
- `common/kernel/doc/manual/command_processing/commands/cmd_set.html`
- `common/kernel/doc/manual/domain_manual/command_reference/cmd_domain/cmd_domain.html`
- `pfcmodule/doc/manual/ball_manual/ball_commands/cmd_ball.distribute.html`
- `pfcmodule/doc/manual/ball_manual/ball_commands/cmd_ball.generate.html`
- `pfcmodule/doc/manual/clump_manual/clump_commands/cmd_clump_template.html`
- `pfcmodule/doc/manual/clump_manual/clump_commands/cmd_clump_distribute.html`
- `pfcmodule/doc/manual/clump_manual/clump_commands/cmd_clump_generate.html`
- `common/contactmodel/burger/doc/manual/cmburger.html`
- `docproject/source/manual/examples/verification/burger_contact_model/stress_relaxation/cmburger_stressrelaxation_datafiles.html`
- `docproject/source/manual/scripting/fish_scripting/fish_fishcallback.html`
- `docproject/source/manual/examples/tutorials/callbacks/callbacks_datafiles.html`
- `pfcmodule/doc/manual/wall_manual/wall_fish/wall_intrinsics/fish_wall.force.contact.html`
- `pfcmodule/doc/manual/wall_manual/wall_commands/cmd_wall_attribute.html`
- `common/module/doc/manual/geom_manual/geom_commands/cmd_geometry.import.html`
- `pfcmodule/doc/manual/wall_manual/wall_commands/cmd_wall_import.html`

This map is an audit locator, not a copied manual. Recheck the pages and rerun the
minimal probes whenever the target PFC5 build or any maintained `.p2dat`/`.p3dat`
asset changes.
