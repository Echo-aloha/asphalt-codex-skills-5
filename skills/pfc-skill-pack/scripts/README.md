# Scripts

Scripts in this folder support package-level maintenance. They should stay small, deterministic, and independent of private local project layouts.

## Current Scripts

### `build_skill_index.py`

Lists sibling directories that contain `SKILL.md`. Use it to check which skills in a pack are valid entrypoints.

Run from the skill-pack root or repository root:

```bash
python scripts/build_skill_index.py
```

## Suggested Future Helpers

### `check_portability.py`

Purpose: scan a skill pack for machine-local references and non-portable path conventions.

Expected behavior:

- Search markdown, YAML, JSON, and script files.
- Report drive-letter paths, home-directory paths, private download-folder names, and project-only folder names.
- Allow an ignore list for intentionally documented examples.

### `check_skill_tree.py`

Purpose: validate the PFC5 asphalt parent/specialist relationships.

Expected behavior:

- Confirm `pfc5-asphalt-workflow` lists the retained specialist skills.
- Confirm dependency manifests resolve only to retained skills.
- Confirm every skill has a `SKILL.md` with required frontmatter.

### `check_assets.py`

Purpose: verify that bundled source assets follow the asset inventory policy.

Expected behavior:

- Flag generated plots, videos, save files, and private project metadata.
- Confirm large source bundles have a manifest.
- Report executable files so maintainers can decide whether to exclude or document them.

## Rules For New Scripts

- Use explicit CLI arguments.
- Do not assume a particular drive, user name, download folder, or project directory.
- Do not mutate files unless a `--write` flag is provided.
- Print clear next steps when checks fail.
- Keep helper scripts optional; skills should remain understandable from markdown and bundled templates.
