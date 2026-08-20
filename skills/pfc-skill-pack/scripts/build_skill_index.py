from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    for skill_dir in sorted(path for path in ROOT.parent.iterdir() if path.is_dir() and (path / "SKILL.md").exists()):
        print(skill_dir.name)


if __name__ == "__main__":
    main()
