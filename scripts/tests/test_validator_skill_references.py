from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_validator():
    path = ROOT / "scripts" / "validate_skills.py"
    spec = importlib.util.spec_from_file_location("validate_skills_inline_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class InlineSkillReferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.temp = tempfile.TemporaryDirectory()
        self.skill = Path(self.temp.name) / "sample"
        self.skill.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_skill(self, body: str) -> None:
        (self.skill / "SKILL.md").write_text(
            "---\nname: sample\ndescription: A detailed sample skill for validator tests.\n---\n"
            + body,
            encoding="utf-8",
        )

    def test_rejects_unknown_inline_pfc_skill_reference(self) -> None:
        self.write_skill("Route this work to `pfc-standard-tests`.\n")

        findings = self.validator.validate_inline_skill_references(
            self.skill,
            {"pfc5-standard-tests"},
            set(),
        )

        self.assertEqual(len(findings), 1)
        self.assertIn("pfc-standard-tests", findings[0].message)

    def test_accepts_known_skill_and_explicit_allowlist(self) -> None:
        self.write_skill("Use `pfc5-standard-tests`; exchange type is `pfc-flac`.\n")

        findings = self.validator.validate_inline_skill_references(
            self.skill,
            {"pfc5-standard-tests"},
            {"pfc-flac"},
        )

        self.assertEqual(findings, [])

    def test_ignores_product_labels_and_non_inline_text(self) -> None:
        self.write_skill("PFC5 is supported; pfc-missing outside inline code is prose.\n")

        findings = self.validator.validate_inline_skill_references(
            self.skill,
            set(),
            set(),
        )

        self.assertEqual(findings, [])

    def test_rejects_broken_inline_local_path(self) -> None:
        self.write_skill("Read `references/missing.md`.\n")

        findings = self.validator.validate_inline_local_paths(
            self.skill,
            Path(self.temp.name),
        )

        self.assertEqual(len(findings), 1)
        self.assertIn("broken inline local path", findings[0].message)

    def test_accepts_existing_inline_local_path(self) -> None:
        references = self.skill / "references"
        references.mkdir()
        (references / "contract.md").write_text("# Contract\n", encoding="utf-8")
        self.write_skill("Read `references/contract.md`.\n")

        findings = self.validator.validate_inline_local_paths(
            self.skill,
            Path(self.temp.name),
        )

        self.assertEqual(findings, [])

    def test_rejects_path_that_escapes_portable_skills_directory(self) -> None:
        self.write_skill("Read `../../references/pfc5-skill-set.json`.\n")

        findings = self.validator.validate_inline_local_paths(
            self.skill,
            Path(self.temp.name),
        )

        self.assertEqual(len(findings), 1)
        self.assertIn("escapes the portable skills directory", findings[0].message)

    def test_rejects_undeclared_cross_skill_asset(self) -> None:
        skills = Path(self.temp.name) / "skills"
        source = skills / "source-skill"
        target = skills / "target-skill"
        (source / "references").mkdir(parents=True)
        (target / "references").mkdir(parents=True)
        (source / "SKILL.md").write_text(
            "---\nname: source-skill\ndescription: Source skill for dependency tests.\n---\n",
            encoding="utf-8",
        )
        (target / "SKILL.md").write_text(
            "---\nname: target-skill\ndescription: Target skill for dependency tests.\n---\n",
            encoding="utf-8",
        )
        (target / "references" / "ledger.json").write_text("{}\n", encoding="utf-8")
        (source / "references" / "contract.md").write_text(
            "Ledger: `../../target-skill/references/ledger.json`.\n",
            encoding="utf-8",
        )

        findings = self.validator.validate_cross_skill_dependency_references(
            source,
            skills,
        )

        self.assertEqual(len(findings), 1)
        self.assertIn("target-skill/references/ledger.json", findings[0].message)

    def test_accepts_declared_cross_skill_asset(self) -> None:
        skills = Path(self.temp.name) / "skills"
        source = skills / "source-skill"
        target = skills / "target-skill"
        (source / "references").mkdir(parents=True)
        (target / "references").mkdir(parents=True)
        (source / "SKILL.md").write_text(
            "---\nname: source-skill\ndescription: Source skill for dependency tests.\n---\n",
            encoding="utf-8",
        )
        (target / "SKILL.md").write_text(
            "---\nname: target-skill\ndescription: Target skill for dependency tests.\n---\n",
            encoding="utf-8",
        )
        (target / "references" / "ledger.json").write_text("{}\n", encoding="utf-8")
        (source / "references" / "contract.md").write_text(
            "Ledger: `../../target-skill/references/ledger.json`.\n",
            encoding="utf-8",
        )
        (source / "dependencies.json").write_text(
            json.dumps({
                "requires": [{
                    "skill": "target-skill",
                    "paths": ["references/ledger.json"],
                }]
            }),
            encoding="utf-8",
        )

        findings = self.validator.validate_cross_skill_dependency_references(
            source,
            skills,
        )

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
