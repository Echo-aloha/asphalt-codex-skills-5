# Third-party, provenance, and trademark notice

## Upstream PFC Codex Skills project

Portions of this repository are derived from, retain, or adapt material from:

- project: `jiangnan030-del/pfc-codex-skills`;
- source: <https://github.com/jiangnan030-del/pfc-codex-skills>;
- audited upstream baseline: commit
  `743a1119be791eee52b69d8e292167e02d6a29df` (2026-08-09);
- license for the retained material: MIT;
- upstream copyright: Copyright (c) 2026 PFC Codex Skills contributors.

Retained or adapted material includes repository governance patterns, validation
logic, post-processing scripts, visualization assets, example inputs, and selected
skill documentation. This repository substantially modifies that material for a
PFC2D/PFC3D 5.0-only asphalt-mixture scope, including version-purity enforcement,
asphalt specimen workflows, Burger contact calibration, Marshall and rutting tests,
fistPkg external boundaries, standards provenance, and PFC5 runtime probes.

The upstream `skills/dual-target-calibration/` child directory is separately licensed
under AGPL-3.0-or-later. It is not vendored as a directory, file set, or declared
dependency in this repository, and the upstream root MIT license does not relicense
that child directory. Future contributions must not copy or adapt material from that
child directory without preserving its AGPL license, notices, modification records,
and corresponding-source obligations.

The affected self-contained Skill directories carry their own `LICENSE` and
`NOTICE.md` so that the upstream MIT notice remains present when a Skill is copied
without the repository root.

## Commercial and standards boundaries

It does not distribute PFC, fistPkg/FISHTank, commercial manuals, standards text,
DLL/EXE files, PFC projects, or save states. Users must obtain those materials from
their lawful sources and comply with their licenses.

PFC, Itasca, FISHTank, fistPkg, and related names may be trademarks or product names
of their respective owners. Their use here is descriptive and does not imply
affiliation, sponsorship, certification, or endorsement by Itasca Consulting Group,
Inc. Standard designations are used only to identify user-supplied procedures; the
standards themselves are not included.

## Python dependencies

The optional Python packages listed in the requirements files remain under their own
licenses. Review those licenses before redistribution in a bundled environment.
