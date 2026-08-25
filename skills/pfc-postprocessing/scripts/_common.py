from __future__ import annotations

from pathlib import Path
import argparse
import csv
import re
from typing import Iterable

import numpy as np
import pandas as pd


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_csv_required(path: Path, required: Iterable[str]) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    df = pd.read_csv(path)
    missing = [name for name in required if name not in df.columns]
    if missing:
        raise ValueError(f"{path.name} missing required columns: {missing}")
    return df


def find_first_existing(base: Path, candidates: list[str]) -> Path | None:
    for name in candidates:
        path = base / name
        if path.exists():
            return path
    return None


def find_column(df: pd.DataFrame, candidates: list[str], *, required: bool = True) -> str | None:
    lowered = {str(col).lower(): str(col) for col in df.columns}
    for candidate in candidates:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    if required:
        raise ValueError(f"Could not find any column from {candidates}. Available columns: {list(df.columns)}")
    return None


def make_argument_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--input-dir", type=Path, required=True, help="Directory containing input files")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory to write outputs")
    parser.add_argument("--case-name", default="case", help="Display name for titles")
    parser.add_argument("--stage", default="final", help="Stage label for output naming")
    return parser


def slugify(text: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9]+", "_", text.strip())
    return safe.strip("_").lower() or "case"
