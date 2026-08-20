from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[3]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_minimal_pfc5_assets_are_complete_and_version_pure():
    assets = {
        "skills/pfc-asphalt-mixture/scripts/minimal_specimen_smoke.p3dat": [
            "wall generate box", "ball distribute", "save 'minimal_specimen_smoke'"
        ],
        "skills/pfc-burger-viscoelastic/scripts/burger_contact_probe.p3dat": [
            "model burger", "bur_knk", "comp.x", "save 'burger_contact_probe'"
        ],
        "skills/pfc-marshall-test/scripts/marshall_head_contact_pilot.p3dat": [
            "cylinder", "wall.force.contact", "head_closure", "save 'marshall_head_contact_pilot'"
        ],
        "skills/pfc-rutting-test/scripts/rutting_contact_pilot.p3dat": [
            "cylinder", "wheel_vertical_force", "wheel_travel", "save 'rutting_contact_pilot'"
        ],
    }
    for relative, markers in assets.items():
        text = read(relative)
        assert all(marker in text for marker in markers), relative
        assert "contact cmat" not in text.lower(), relative


def test_contact_switch_policy_is_transactional():
    overview = read("skills/pfc-asphalt-mixture/references/overview.md")
    assert "不得作为" in overview
    assert "未来新接触设置" in overview
    assert "重新平衡" in overview
    assert "contact delete` +" not in overview


def test_standard_references_do_not_bundle_numeric_tables():
    gradation = read("skills/pfc-asphalt-mixture/references/gradation.md")
    rutting = read("skills/pfc-rutting-test/references/jtg-t0719.md")
    assert "sieve_mm,passing_percent" in gradation
    assert "AC-13 通过率" not in gradation
    assert "0.7 ±" not in rutting
    assert "300 × 300 × 50" not in rutting
    assert "2025 年第 27 号公告" in rutting


def test_runtime_manifest_matches_current_probe_sources():
    checker = ROOT / "skills/pfc5-asphalt-workflow/scripts/check_runtime_manifest.py"
    completed = subprocess.run(
        [sys.executable, str(checker)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert completed.returncode == 0, result
    assert result["ok"] is True
    assert len(result["checked"]) == 4
