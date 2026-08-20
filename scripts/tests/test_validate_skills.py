from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).parents[2]


def load_validator():
    path = ROOT / "scripts" / "validate_skills.py"
    spec = importlib.util.spec_from_file_location("validate_skills", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_generated_index_excludes_cache_files_and_counts_only_files(tmp_path):
    skill = tmp_path / "skills" / "sample-skill"
    scripts = skill / "scripts"
    cache = scripts / "__pycache__"
    cache.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: sample-skill\ndescription: Sample description for deterministic index testing.\n---\n",
        encoding="utf-8",
    )
    (scripts / "helper.py").write_text("pass\n", encoding="utf-8")
    (cache / "helper.cpython-314.pyc").write_bytes(b"generated")

    output = load_validator().generate_index(tmp_path / "skills")

    assert "| `sample-skill` | `sample-skill` | 2 | 0 | 1 |" in output


def test_skill_name_must_match_directory(tmp_path):
    skill = tmp_path / "wrong-directory"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: another-name\ndescription: A sufficiently detailed test description for validation.\n---\n"
        "# Test\n\nUse this skill. Required inputs. Workflow. Outputs. Local contents.\n",
        encoding="utf-8",
    )

    findings = load_validator().validate_skill(skill)

    assert any("must match directory" in finding.message for finding in findings)


def test_agent_short_description_is_bounded(tmp_path):
    skill = tmp_path / "sample"
    agent = skill / "agents"
    agent.mkdir(parents=True)
    (agent / "openai.yaml").write_text(
        'interface:\n  short_description: "' + ("x" * 65) + '"\n',
        encoding="utf-8",
    )

    findings = load_validator().validate_agent_metadata(skill)

    assert any("exceeds 64" in finding.message for finding in findings)


def test_unsafe_python_patterns_are_detected(tmp_path, monkeypatch):
    validator = load_validator()
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    script = tmp_path / "unsafe.py"
    script.write_text(
        "np.load(path, allow_pickle=True)\nsubprocess.run(cmd, shell=True)\n",
        encoding="utf-8",
    )

    findings = validator.validate_file(script)

    assert {finding.message for finding in findings} >= {
        "unsafe NumPy pickle loading",
        "shell=True command execution",
    }
