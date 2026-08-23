from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run_script(relative: str, *args: object, expected: int = 0) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, str(ROOT / relative), *(str(arg) for arg in args)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != expected:
        raise AssertionError(
            f"{relative} returned {result.returncode}, expected {expected}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result, json.loads(result.stdout)


class MigratedToolTests(unittest.TestCase):
    def test_private_case_handoff_auditor(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            case_dir = root / "case"
            common_dir = root / "common"
            case_dir.mkdir()
            common_dir.mkdir()
            helper = common_dir / "helper.p3fis"
            helper.write_text("def helper\n  value = 1\nend\n", encoding="utf-8")
            state = case_dir / "accepted.p3sav"
            state.write_bytes(b"synthetic-save-placeholder")
            driver = case_dir / "main.p3dat"
            driver.write_text(
                "call '../common/helper.p3fis'\nrestore 'accepted.p3sav'\n",
                encoding="utf-8",
            )
            manifest = root / "checksums.csv"
            rows = []
            for path in (helper, state, driver):
                rows.append(
                    (
                        path.relative_to(root).as_posix(),
                        hashlib.sha256(path.read_bytes()).hexdigest(),
                    )
                )
            with manifest.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(("relative_path", "sha256"))
                writer.writerows(rows)

            _, report = run_script(
                "skills/pfc5-case-handoff/scripts/audit_pfc5_handoff.py",
                root,
                "--expected-major",
                5,
                "--checksums",
                manifest,
            )
            self.assertTrue(report["ok"])
            self.assertEqual(report["references_checked"], 2)
            self.assertEqual(report["checksum_rows"], 3)
            self.assertFalse(report["runtime_validated"])

            driver.write_text(
                "call 'missing.p3fis'\nsave '" + "C:" + "/private/output' localdir\nPFC 7\n",
                encoding="utf-8",
            )
            _, rejected = run_script(
                "skills/pfc5-case-handoff/scripts/audit_pfc5_handoff.py",
                root,
                "--redact-paths",
                expected=1,
            )
            self.assertFalse(rejected["ok"])
            codes = {item["code"] for item in rejected["findings"]}
            self.assertIn("missing_dependency", codes)
            self.assertIn("private_absolute_path", codes)
            self.assertIn("unsupported_major_marker", codes)

    def test_core_and_fish_auditors(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            valid = base / "valid.fis"
            valid.write_text("def monitor\n  value = 1\nend\nhistory id 1 @monitor\n", encoding="utf-8")
            _, core = run_script("skills/pfc5-core-modeling/scripts/audit_pfc5_case.py", valid)
            _, fish = run_script("skills/pfc5-fish/scripts/audit_pfc5_fish.py", valid)
            self.assertTrue(core["ok"])
            self.assertTrue(fish["ok"])

            invalid = base / "invalid.fis"
            invalid.write_text("fish define wrong\nend\n", encoding="utf-8")
            _, core_bad = run_script(
                "skills/pfc5-core-modeling/scripts/audit_pfc5_case.py", invalid, expected=1
            )
            _, fish_bad = run_script(
                "skills/pfc5-fish/scripts/audit_pfc5_fish.py", invalid, expected=1
            )
            self.assertFalse(core_bad["ok"])
            self.assertFalse(fish_bad["ok"])

            unclosed = base / "unclosed.fis"
            unclosed.write_text("define controller\n  value = 1\n", encoding="utf-8")
            _, unclosed_report = run_script(
                "skills/pfc5-fish/scripts/audit_pfc5_fish.py", unclosed, expected=1
            )
            self.assertFalse(unclosed_report["ok"])

    def test_servo_and_dual_target(self) -> None:
        _, servo = run_script(
            "skills/pfc5-servo-calibration/scripts/servo_gain.py",
            "--target", 10, "--reaction", 0, "--stiffness", 100,
            "--dt", 0.1, "--vmax", 0.05,
        )
        self.assertEqual(servo["velocity"], 0.05)
        self.assertTrue(servo["clamped"])
        with tempfile.TemporaryDirectory() as raw:
            case = Path(raw) / "solve.json"
            case.write_text(json.dumps({
                "parameters": [1, 2],
                "residual": [1, -2],
                "jacobian": [[1, 0], [0, 2]],
                "bounds": [[0, 2], [0, 4]],
            }), encoding="utf-8")
            _, solved = run_script(
                "skills/pfc5-servo-calibration/scripts/dual_target_solver.py", case
            )
            self.assertEqual(solved["proposed_parameters"], [0.0, 3.0])
            self.assertEqual(solved["condition_inf"], 2.0)

            case.write_text(json.dumps({
                "parameters": [1, 2],
                "residual": [1, 1],
                "jacobian": [[1, 1], [1, 1.000001]],
            }), encoding="utf-8")
            rejected = subprocess.run(
                [sys.executable, str(ROOT / "skills/pfc5-servo-calibration/scripts/dual_target_solver.py"),
                 str(case), "--cond-max", "1000"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("condition_inf", rejected.stderr)

    def test_geometry_and_standard_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            nodes = base / "nodes.csv"
            nodes.write_text("id,x,y\n1,0,0\n2,1,0\n3,0,1\n", encoding="utf-8")
            elements = base / "elements.csv"
            elements.write_text("id,n1,n2,n3\n1,1,2,3\n", encoding="utf-8")
            _, geometry = run_script(
                "skills/pfc5-geometry-import/scripts/validate_geometry_csv.py",
                "--nodes", nodes, "--elements", elements, "--dimension", 2,
            )
            self.assertTrue(geometry["ok"])
            self.assertEqual(geometry["elements"], 1)

            curve = base / "curve.csv"
            curve.write_text(
                "strain,stress_mpa,load_n\n0,0,0\n0.002,2,100\n0.004,4,200\n0.006,3,150\n",
                encoding="utf-8",
            )
            _, metrics = run_script(
                "skills/pfc5-standard-tests/scripts/extract_test_metrics.py",
                curve, "--fit-min", 0, "--fit-max", 0.004,
                "--load-col", "load_n", "--diameter", 0.1, "--thickness", 0.05,
            )
            self.assertEqual(metrics["peak_y"], 4.0)
            self.assertAlmostEqual(float(metrics["linear_slope"]), 1000.0)
            self.assertGreater(float(metrics["diametral_strength"]), 0)

    def test_dynamic_resolution_accepts_and_rejects(self) -> None:
        _, valid = run_script(
            "skills/pfc5-dynamics-wave/scripts/check_dynamic_resolution.py",
            "--dimension", 2, "--direction", "x", "--spacing", 0.001,
            "--wave-speed", 2500, "--f-max", 100000, "--dt", 0.0000001,
        )
        self.assertTrue(valid["ok"])
        _, invalid = run_script(
            "skills/pfc5-dynamics-wave/scripts/check_dynamic_resolution.py",
            "--dimension", 2, "--direction", "z", "--spacing", 0.003,
            "--wave-speed", 2500, "--f-max", 100000, expected=1,
        )
        self.assertFalse(invalid["ok"])
        self.assertEqual(len(invalid["errors"]), 2)

    def test_ae_cluster_and_energy(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            hits = base / "hits.csv"
            hits.write_text(
                "hit_id,time,x,y,mode\na,0,0,0,tension\nb,0.1,0.1,0,shear\nc,1,5,5,tension\n",
                encoding="utf-8",
            )
            events = base / "events.csv"
            _, clustered = run_script(
                "skills/pfc5-ae-energy/scripts/cluster_ae_events.py", hits, events,
                "--time-window", 0.2, "--space-window", 0.2, "--dimension", 2,
            )
            self.assertEqual(clustered["events"], 2)
            with events.open("r", encoding="utf-8", newline="") as handle:
                event_rows = list(csv.DictReader(handle))
            self.assertEqual(event_rows[0]["hit_count"], "2")

            curve = base / "energy.csv"
            curve.write_text("strain,stress_mpa\n0,0\n0.001,1\n0.002,2\n", encoding="utf-8")
            energy_out = base / "energy-out.csv"
            _, energy = run_script(
                "skills/pfc5-ae-energy/scripts/ae_energy_metrics.py", curve, energy_out,
                "--modulus-mpa", 1000,
            )
            self.assertAlmostEqual(float(energy["final_input_mj_m3"]), 0.002)
            self.assertTrue(energy_out.is_file())

    def test_coupling_contract(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            nodes = base / "mesh.csv"
            nodes.write_text("id,x,y\n1,0,0\n", encoding="utf-8")
            contract = base / "contract.json"
            contract.write_text(json.dumps({
                "coupling_type": "seepage",
                "dimension": 2,
                "length_unit": "m",
                "time_unit": "s",
                "force_unit": "N",
                "exchange_interval_cycles": 10,
                "fluid": {"density": 1000, "viscosity": 0.001},
                "mesh": {"nodes": "mesh.csv"},
                "runtime_validated": False,
            }), encoding="utf-8")
            _, report = run_script(
                "skills/pfc5-coupling/scripts/validate_coupling_contract.py", contract
            )
            self.assertTrue(report["ok"])
            self.assertFalse(report["runtime_validated"])

            unsafe = base / "unsafe.json"
            unsafe.write_text(json.dumps({
                "coupling_type": "pfc-flac",
                "dimension": 2,
                "length_unit": "m",
                "time_unit": "s",
                "force_unit": "N",
                "exchange_interval_cycles": 1,
                "mesh": {"nodes": "../outside.csv"},
            }), encoding="utf-8")
            _, rejected = run_script(
                "skills/pfc5-coupling/scripts/validate_coupling_contract.py",
                unsafe,
                expected=1,
            )
            self.assertFalse(rejected["ok"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
