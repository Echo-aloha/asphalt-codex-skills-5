from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "skills"


class StandardsContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def ledger(self) -> dict:
        return json.loads(
            self.read(
                "skills/pfc5-asphalt-workflow/references/standards-source-ledger.json"
            )
        )

    def source(self, designation: str) -> dict:
        matches = [
            item for item in self.ledger()["sources"]
            if item["designation"] == designation
        ]
        self.assertEqual(len(matches), 1, designation)
        return matches[0]

    def method(self, designation: str, method_id: str) -> dict:
        source = self.source(designation)
        matches = [
            item for item in source["methods"]
            if item["method_id"] == method_id
        ]
        self.assertEqual(len(matches), 1, method_id)
        return matches[0]

    def test_reviewed_standard_roles_are_present(self) -> None:
        method_map = self.read(
            "skills/pfc5-asphalt-workflow/references/standards-method-map.md"
        )
        for designation in (
            "JTG 3410-2025",
            "JTG 3432-2024",
            "JTG 3450-2019",
            "JTG 5110-2023",
            "JTG 5142-2019",
            "JTG 5210-2018",
            "JTG D30-2015",
            "JTG D50-2017",
            "JTG F40-2004",
            "JTG F80/1-2017",
            "JTG/T 3610-2019",
        ):
            self.assertIn(designation, method_map)
        self.assertNotIn("E" + chr(58) + "\\Codex", method_map)
        self.assertNotIn("C" + chr(58) + "\\Users", method_map)

    def test_source_ledger_covers_reviewed_standards(self) -> None:
        ledger = self.ledger()
        self.assertFalse(ledger["standards_text_bundled"])
        self.assertTrue(
            ledger["review_policy"]["human_confirmation_required_for_normative_use"]
        )
        expected = {
            "JTG 3410-2025", "JTG 3432-2024", "JTG 3450-2019",
            "JTG 5110-2023", "JTG 5142-2019", "JTG 5210-2018",
            "JTG D30-2015", "JTG D50-2017", "JTG F40-2004",
            "JTG F80/1-2017", "JTG/T 3610-2019",
        }
        sources = ledger["sources"]
        self.assertEqual({item["designation"] for item in sources}, expected)
        self.assertEqual(len(sources), len(expected))
        for source in sources:
            self.assertRegex(source["sha256"], r"^[0-9A-F]{64}$")
            self.assertGreater(source["bytes"], 0)
            self.assertTrue(source["source_id"])
            self.assertTrue(source["review_scope"])
            self.assertIsInstance(source["methods"], list)

    def test_current_marshall_contract_is_source_bound(self) -> None:
        contract = self.read(
            "skills/pfc-marshall-test/references/jtg-3410-2025-t0709.md"
        )
        source = self.source("JTG 3410-2025")
        method = self.method("JTG 3410-2025", "T 0709-2025")
        self.assertEqual(method["printed_pages_reviewed"], list(range(372, 378)))
        self.assertTrue(method["claims"]["origin_correction_required"])
        self.assertTrue(method["claims"]["unclear_peak_branch_required"])
        self.assertIn(source["source_id"], contract)
        self.assertIn(source["sha256"], contract)
        self.assertIn(method["method_id"], contract)

    def test_current_rutting_contract_rejects_legacy_shortcuts(self) -> None:
        overview = self.read("skills/pfc-rutting-test/references/overview.md")
        contract = self.read("skills/pfc-rutting-test/references/jtg-t0719.md")
        source = self.source("JTG 3410-2025")
        method = self.method("JTG 3410-2025", "T 0719-2025")
        claims = method["claims"]
        self.assertEqual(claims["normal_t1_passes"], 1890)
        self.assertEqual(claims["normal_t2_passes"], 2520)
        self.assertEqual(claims["interval_passes"], 630)
        self.assertEqual(claims["fixed_measurement_positions"], 7)
        self.assertIn(source["source_id"], contract)
        self.assertIn(source["sha256"], contract)
        self.assertNotIn("630/(d60-d45)", overview)
        self.assertNotIn("45 min/60 min", contract)

    def test_specimen_inputs_are_method_chained_not_hardcoded(self) -> None:
        skill = self.read("skills/pfc-asphalt-mixture/SKILL.md")
        intake = self.read(
            "skills/pfc5-asphalt-workflow/templates/pfc5-asphalt-intake.yaml"
        )
        self.assertNotIn("300×300×50", skill)
        self.assertNotIn("JTG E20 T0709", skill)
        chain_text = intake.split("  method_chain:\n", 1)[1].split("\nspecimen:\n", 1)[0]
        blocks = re.split(r"(?=    - role: )", chain_text)
        blocks = [block for block in blocks if block.startswith("    - role: ")]
        required_roles = {
            "aggregate_characterization", "sampling", "preparation", "forming",
            "bulk_density", "maximum_relative_density", "performance",
            "field_validation", "acceptance_context",
        }
        required_keys = {
            "designation", "method_id", "clause_or_printed_page", "source_id",
            "source_sha256", "reviewer", "reviewed_on", "values_used",
            "model_mapping",
        }
        parsed_roles = set()
        for block in blocks:
            lines = block.splitlines()
            parsed_roles.add(lines[0].split(":", 1)[1].strip())
            keys = {
                line.strip().split(":", 1)[0]
                for line in lines[1:]
                if ":" in line
            }
            self.assertTrue(required_keys <= keys, lines[0])
        self.assertEqual(parsed_roles, required_roles)
        standard_header = intake.split("  method_chain:\n", 1)[0]
        self.assertNotIn("  edition:", standard_header)
        self.assertNotIn("  source_id:", standard_header)

    def test_burger_material_levels_are_not_collapsed(self) -> None:
        calibration = self.read(
            "skills/pfc-burger-viscoelastic/references/calibration.md"
        )
        ledger = self.source("JTG 3410-2025")
        material_levels = {
            item["method_id"]: item["material_level"]
            for item in ledger["methods"]
        }
        self.assertEqual(material_levels["T 0627-2011"], "asphalt binder")
        self.assertEqual(material_levels["T 0628-2011"], "asphalt binder")
        self.assertIn("Step B1 结合料先验", calibration)
        self.assertIn("Step B2 砂浆尺度标定", calibration)
        self.assertNotIn("Step B  砂浆黏弹参数：DSR", calibration)

    def test_governance_manifest_path_is_portable(self) -> None:
        skill_dir = SKILLS / "pfc-skill-pack"
        skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        portable = skill_dir / "references" / "pfc5-skill-set.json"
        repository = ROOT / "references" / "pfc5-skill-set.json"
        self.assertIn("`references/pfc5-skill-set.json`", skill)
        self.assertNotIn("`../../references/pfc5-skill-set.json`", skill)
        self.assertEqual(
            json.loads(portable.read_text(encoding="utf-8")),
            json.loads(repository.read_text(encoding="utf-8")),
        )

    def test_cross_skill_method_map_dependencies_are_declared(self) -> None:
        for slug in (
            "pfc-asphalt-mixture",
            "pfc-burger-viscoelastic",
            "pfc5-standard-tests",
            "pfc-marshall-test",
            "pfc-rutting-test",
        ):
            data = json.loads((SKILLS / slug / "dependencies.json").read_text(encoding="utf-8"))
            workflow = [item for item in data["requires"] if item["skill"] == "pfc5-asphalt-workflow"]
            self.assertEqual(len(workflow), 1, slug)
            self.assertIn("references/standards-method-map.md", workflow[0]["paths"])
            if slug in {
                "pfc-burger-viscoelastic",
                "pfc-marshall-test",
                "pfc-rutting-test",
            }:
                self.assertIn(
                    "references/standards-source-ledger.json",
                    workflow[0]["paths"],
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
