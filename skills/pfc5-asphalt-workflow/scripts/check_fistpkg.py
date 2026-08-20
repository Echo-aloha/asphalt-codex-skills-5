#!/usr/bin/env python3
"""Compatibility entry point for the checker owned by pfc-fishtank-tests."""
from __future__ import annotations

import importlib.util
from pathlib import Path

CANONICAL = (
    Path(__file__).resolve().parents[2]
    / "pfc-fishtank-tests"
    / "scripts"
    / "check_fistpkg.py"
)
spec = importlib.util.spec_from_file_location("pfc_fishtank_check_fistpkg", CANONICAL)
if spec is None or spec.loader is None:
    raise ImportError(f"cannot load canonical checker: {CANONICAL}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

inspect = module.inspect
main = module.main

if __name__ == "__main__":
    raise SystemExit(main())
