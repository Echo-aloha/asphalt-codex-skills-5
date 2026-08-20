# fistPkg26 external dependency contract

## Provenance

The inspected package identifies itself as PFC 5.0 FISHTank `fistPkg26`, dated
2018-08-24. This skill treats the dependency at the PFC 5.0 family level and does not
require a particular PFC5.0 subversion. Its public README places source under
`ExampleProjects/fistSrc`.

This skill package does not grant redistribution rights for those files. Keep the
licensed package external and record its checksum/location only in the user's private
case manifest.

## Expected layout

```text
<FISTPKG_ROOT>/
├── fistPkg-README.txt
├── fistPkg-publicMods.txt
├── Documentation/
└── ExampleProjects/
    ├── fistSrc/
    │   ├── fistPkg-version.txt
    │   ├── ft.fis
    │   ├── ck.fis
    │   ├── ct.fis
    │   ├── dc.fis
    │   └── tt.fis
    ├── MatGen-Linear/
    ├── MatGen-ContactBonded/
    ├── MatGen-ParallelBonded/
    ├── MatGen-FlatJointed/
    └── MatGen-Hill/
```

Hill additionally uses `hl.p3fis`, `udm_hl.p3fis` and a platform-specific DLL. It is
not required for the normal PFC5 asphalt route.

## Integration procedure

1. Run the bundled checker against `<FISTPKG_ROOT>`.
2. Copy only the needed `fistSrc` and one selected `MatGen-X` project into a private
   case work directory, following the fistPkg README.
3. Preserve upstream files; implement asphalt parameters and overrides in separately
   named files when the PFC5 project loader permits it.
4. Record source release, PFC2D/PFC3D 5.0 product, copied files and any changed functions.
5. Run the original baseline project before applying asphalt changes.
6. Run a small adapted pilot before the production specimen/test.

## dc.fis adapter boundary

The inspected `dc.fis`:

- calls `_dcMakeWalls` from `dcSetupPhase`;
- expects walls with IDs 1 and 2 to become `dcWp0` and `dcWp1`;
- measures and drives the second coordinate as the axial direction;
- calls `ft_SmoothGrainWallInterface`, initializes callbacks and uses a post-peak stop
  rule.

Replacing `_dcMakeWalls` is therefore the minimum geometry hook, not proof that a
Marshall adaptation is complete. Audit pointer IDs, head placement/rotation, contact
behavior, smoothing, sign, force/displacement calculation, stop rule and flow
post-processing.

## Checker semantics

`check_fistpkg.py` is read-only. Exit code 0 means the expected text/source layout,
release marker and PFC 5.0 family marker were found. It does not:

- validate the PFC license;
- install the Hill DLL;
- execute FISH;
- prove that a modified case is mechanically valid.
