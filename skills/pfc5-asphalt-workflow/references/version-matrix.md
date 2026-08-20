# PFC 5.0 Version Boundary

## Supported route

| Route | Syntax authority | Status |
| --- | --- | --- |
| PFC2D/PFC3D 5.0 asphalt + optional fistPkg26 | licensed local PFC5 docs/runtime and legal fistPkg26 tree | supported |
| any other major-version target | that version's separate tooling | out of scope for this package |

## Purity rules

- Keep commands, FISH intrinsics, callbacks, histories, wall conventions, and `cmat` semantics in the PFC 5.0 family.
- Reject unsupported command families rather than translating them implicitly.
- Mark each executable asset as PFC2D or PFC3D 5.0.
- Treat a historical example as evidence only; run a minimal PFC5 runtime probe.
- Keep the original fistPkg project intact and put asphalt overrides in a private, traceable working copy.

## Required version record

```yaml
pfc:
  product: PFC3D
  version: "5.0"
  syntax_family: pfc5
fistpkg:
  release: 26
  compatibility_family: PFC 5.0
runtime_probe:
  passed: false
  evidence: null
```

A family marker does not replace execution in the user's licensed runtime.
