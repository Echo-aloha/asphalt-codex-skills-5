from __future__ import annotations

from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from check_fistpkg import inspect  # noqa: E402


def make_minimal_tree(root: Path, compatibility: str = "5.0") -> None:
    (root / "ExampleProjects/fistSrc").mkdir(parents=True)
    for name in ("MatGen-Linear", "MatGen-ContactBonded", "MatGen-ParallelBonded",
                 "MatGen-FlatJointed", "MatGen-Hill"):
        (root / "ExampleProjects" / name).mkdir()
    (root / "fistPkg-README.txt").write_text("PFC 5.0 FISHTank", encoding="utf-8")
    (root / "fistPkg-publicMods.txt").write_text(
        f"26 | {compatibility} | 08/24/18\n", encoding="utf-8"
    )
    source = root / "ExampleProjects/fistSrc"
    (source / "fistPkg-version.txt").write_text(
        "This is PFC 5.0 FISHTank version 26.\n", encoding="utf-8"
    )
    for name in ("ft.fis", "ck.fis", "ct.fis", "dc.fis", "tt.fis"):
        (source / name).write_text(f"; {name}\n", encoding="utf-8")


def test_accepts_fistpkg26_layout(tmp_path: Path) -> None:
    make_minimal_tree(tmp_path)
    result = inspect(tmp_path)
    assert result["ok"] is True
    assert result["release"] == 26
    assert result["pfc_compatibility"] == "5.0"
    assert result["runtime_validated"] is False


def test_accepts_other_pfc5_subversion_marker(tmp_path: Path) -> None:
    make_minimal_tree(tmp_path, compatibility="5.01.7")
    result = inspect(tmp_path)
    assert result["ok"] is True
    assert result["pfc_compatibility"] == "5.0"


def test_rejects_non_pfc5_marker(tmp_path: Path) -> None:
    make_minimal_tree(tmp_path, compatibility="6.0")
    result = inspect(tmp_path)
    assert result["ok"] is False
    assert "PFC 5.0 compatibility marker was not found" in result["warnings"]


def test_reports_missing_source_file(tmp_path: Path) -> None:
    make_minimal_tree(tmp_path)
    (tmp_path / "ExampleProjects/fistSrc/dc.fis").unlink()
    result = inspect(tmp_path)
    assert result["ok"] is False
    assert "ExampleProjects/fistSrc/dc.fis" in result["missing"]
