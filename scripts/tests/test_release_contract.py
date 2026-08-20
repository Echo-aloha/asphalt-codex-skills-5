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
    spec = importlib.util.spec_from_file_location("validate_release_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ReleaseContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "sample-plugin"
        (self.root / ".codex-plugin").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_manifest(self, name: str = "sample-plugin") -> None:
        payload = {
            "name": name,
            "version": "0.1.0-preview.1",
            "description": "Test plugin",
            "author": {"name": "Test contributors"},
            "skills": "./skills/",
            "interface": {
                "displayName": "Sample",
                "shortDescription": "Sample plugin",
                "longDescription": "A sample plugin used by release tests.",
                "developerName": "Test contributors",
                "category": "Productivity",
                "capabilities": ["Testing"],
                "defaultPrompt": ["Test this plugin."],
            },
        }
        (self.root / ".codex-plugin" / "plugin.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )

    def test_valid_preview_manifest(self) -> None:
        self.write_manifest()
        self.assertEqual(self.validator.validate_plugin_manifest(self.root), [])

    def test_rejects_mismatched_plugin_name(self) -> None:
        self.write_manifest("wrong-name")
        findings = self.validator.validate_plugin_manifest(self.root)
        self.assertTrue(any("root directory" in item.message for item in findings))

    def test_release_requirements_include_optional_backends(self) -> None:
        (self.root / "requirements.txt").write_text(
            "numpy\npandas\nmatplotlib\nscipy\nimageio\npillow\n", encoding="utf-8"
        )
        (self.root / "requirements-visualization.txt").write_text(
            "-r requirements.txt\nimageio-ffmpeg\nopencv-python-headless\nvedo\n", encoding="utf-8"
        )
        (self.root / "requirements-dev.txt").write_text(
            "-r requirements.txt\npytest\n", encoding="utf-8"
        )
        self.assertEqual(self.validator.validate_requirement_contract(self.root), [])

    def test_missing_optional_backend_is_an_error(self) -> None:
        (self.root / "requirements.txt").write_text(
            "numpy\npandas\nmatplotlib\nscipy\nimageio\npillow\n", encoding="utf-8"
        )
        (self.root / "requirements-visualization.txt").write_text(
            "-r requirements.txt\nimageio-ffmpeg\nvedo\n", encoding="utf-8"
        )
        (self.root / "requirements-dev.txt").write_text(
            "-r requirements.txt\npytest\n", encoding="utf-8"
        )
        findings = self.validator.validate_requirement_contract(self.root)
        self.assertTrue(any("opencv-python-headless" in item.message for item in findings))


if __name__ == "__main__":
    unittest.main(verbosity=2)
