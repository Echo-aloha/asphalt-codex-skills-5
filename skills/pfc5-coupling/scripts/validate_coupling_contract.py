from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ALLOWED = {"buoyancy", "seepage", "pore-pressure", "pfc-flac"}


def csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return next(csv.reader(handle), [])


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a portable PFC5 coupling JSON contract")
    parser.add_argument("contract", type=Path)
    args = parser.parse_args()
    data = json.loads(args.contract.read_text(encoding="utf-8"))
    errors: list[str] = []
    if data.get("coupling_type") not in ALLOWED:
        errors.append(f"coupling_type must be one of {sorted(ALLOWED)}")
    if data.get("dimension") not in (2, 3):
        errors.append("dimension must be 2 or 3")
    for key in ("length_unit", "time_unit", "force_unit"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"{key} is required")
    interval = data.get("exchange_interval_cycles")
    if not isinstance(interval, int) or interval <= 0:
        errors.append("exchange_interval_cycles must be a positive integer")
    if data.get("coupling_type") in {"buoyancy", "seepage", "pore-pressure"}:
        fluid = data.get("fluid", {})
        for key in ("density", "viscosity"):
            try:
                if float(fluid[key]) <= 0:
                    errors.append(f"fluid.{key} must be positive")
            except (KeyError, TypeError, ValueError):
                errors.append(f"fluid.{key} is required and numeric")
    mesh_report: dict[str, object] = {}
    contract_root = args.contract.parent.resolve()
    mesh = data.get("mesh", {})
    if not isinstance(mesh, dict):
        errors.append("mesh must be an object of named relative CSV paths")
        mesh = {}
    for kind, raw in mesh.items():
        if not isinstance(raw, str) or not raw.strip():
            errors.append(f"mesh.{kind} must be a relative file path")
            continue
        candidate = Path(raw)
        path = (contract_root / candidate).resolve()
        if candidate.is_absolute() or (path != contract_root and contract_root not in path.parents):
            errors.append(f"mesh.{kind} must stay within the contract directory")
        elif not path.is_file():
            errors.append(f"missing mesh file: {raw}")
        else:
            mesh_report[kind] = {"path": str(path), "columns": csv_header(path)}
    print(json.dumps({
        "ok": not errors,
        "errors": errors,
        "mesh": mesh_report,
        "runtime_validated": bool(data.get("runtime_validated", False)),
    }, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
