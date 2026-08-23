#!/usr/bin/env python3
"""Read-only portability and integrity audit for a private PFC5 case handoff."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


EXECUTABLE_SUFFIXES = {
    ".dat", ".fis", ".dvr", ".p2dat", ".p3dat", ".p2fis", ".p3fis",
    ".p2dvr", ".p3dvr",
}
SAVE_SUFFIXES = {".sav", ".p2sav", ".p3sav"}
PROJECT_SUFFIXES = {".prj", ".p2prj", ".p3prj"}
CALL_SUFFIXES = ("", ".fis", ".p2fis", ".p3fis", ".dat", ".p2dat", ".p3dat")
RESTORE_SUFFIXES = ("", ".sav", ".p2sav", ".p3sav")
ABSOLUTE_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:[A-Za-z]:[\\/]|\\\\[^\\\s]+[\\/][^\s]+|/(?:home|Users|mnt|opt|var)/)"
)
LOCALDIR_RE = re.compile(r"(?im)^\s*(?:model\s+)?save\b[^\r\n]*\blocaldir\b")
UNSUPPORTED_VERSION_RE = re.compile(r"\bPFC\s*(?:6(?:\.0)?|7(?:\.0)?|9(?:\.0)?)\b", re.I)
UNSUPPORTED_COMMAND_RE = re.compile(r"\bcontact\s+cmat\b", re.I)
REFERENCE_RE = re.compile(
    r"(?im)^\s*(?:model\s+)?(?P<kind>call|restore)\s+"
    r"(?P<target>'[^'\r\n]+'|\"[^\"\r\n]+\"|[^\s;]+)"
)
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
MAX_TEXT_BYTES = 2_000_000


def relative(path: Path, root: Path, redact: bool) -> str:
    if redact:
        return "<redacted>"
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return "<outside-root>"


def finding(
    level: str,
    code: str,
    path: str,
    detail: str,
    line: int | None = None,
) -> dict[str, object]:
    item: dict[str, object] = {
        "level": level,
        "code": code,
        "path": path,
        "detail": detail,
    }
    if line is not None:
        item["line"] = line
    return item


def decode_text(path: Path) -> str | None:
    if path.stat().st_size > MAX_TEXT_BYTES:
        return None
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def target_candidates(root: Path, source: Path, target: str, kind: str) -> list[Path]:
    cleaned = target.strip().strip("'\"").replace("\\", "/")
    if not cleaned or "@" in cleaned or ABSOLUTE_PATH_RE.search(cleaned):
        return []
    raw = Path(cleaned)
    suffixes = CALL_SUFFIXES if kind.lower() == "call" else RESTORE_SUFFIXES
    candidates: list[Path] = []
    for base in (source.parent, root):
        for suffix in suffixes:
            candidate = base / raw
            if suffix and not raw.suffix:
                candidate = Path(str(candidate) + suffix)
            candidates.append(candidate.resolve())
    return candidates


def scan_executable(
    root: Path,
    path: Path,
    redact: bool,
) -> tuple[list[dict[str, object]], int]:
    findings: list[dict[str, object]] = []
    text = decode_text(path)
    shown = relative(path, root, redact)
    if text is None:
        return [finding("WARN", "unreadable_executable_text", shown, "not scanned as text")], 0

    checks = (
        (ABSOLUTE_PATH_RE, "private_absolute_path", "absolute path in executable source"),
        (LOCALDIR_RE, "ambiguous_save_localdir", "save destination depends on localdir behavior"),
        (UNSUPPORTED_VERSION_RE, "unsupported_major_marker", "newer-major PFC marker in PFC5 source"),
        (
            UNSUPPORTED_COMMAND_RE,
            "unsupported_command_family",
            "unsupported contact-model-assignment command family",
        ),
    )
    for regex, code, detail in checks:
        for match in regex.finditer(text):
            findings.append(
                finding("ERROR", code, shown, detail, text[:match.start()].count("\n") + 1)
            )

    references = 0
    for match in REFERENCE_RE.finditer(text):
        references += 1
        kind = match.group("kind").lower()
        target = match.group("target")
        line = text[:match.start()].count("\n") + 1
        if "@" in target:
            findings.append(
                finding(
                    "WARN",
                    "dynamic_dependency",
                    shown,
                    f"dynamic {kind} target requires runtime verification",
                    line,
                )
            )
            continue
        candidates = target_candidates(root, path, target, kind)
        if candidates and not any(candidate.is_file() for candidate in candidates):
            findings.append(
                finding(
                    "ERROR",
                    "missing_dependency",
                    shown,
                    f"unresolved relative {kind} target",
                    line,
                )
            )
    return findings, references


def parse_checksum_manifest(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        try:
            has_header = csv.Sniffer().has_header(sample)
        except csv.Error:
            has_header = True
        if has_header:
            reader = csv.DictReader(handle)
            fields = {field.strip().lower(): field for field in (reader.fieldnames or [])}
            path_key = next(
                (fields[key] for key in ("relative_path", "path", "file", "filename") if key in fields),
                None,
            )
            hash_key = next(
                (fields[key] for key in ("sha256", "hash", "digest") if key in fields),
                None,
            )
            if path_key is None or hash_key is None:
                raise ValueError("checksum CSV needs path and sha256 columns")
            for row in reader:
                rows.append((str(row[path_key]).strip(), str(row[hash_key]).strip()))
        else:
            for row in csv.reader(handle):
                if len(row) < 2:
                    continue
                first, second = row[0].strip(), row[1].strip()
                rows.append((second, first) if SHA256_RE.fullmatch(first) else (first, second))
    return rows


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_checksums(
    root: Path,
    manifest: Path,
    redact: bool,
    require_complete: bool,
) -> tuple[list[dict[str, object]], int]:
    findings: list[dict[str, object]] = []
    listed: set[Path] = set()
    rows = parse_checksum_manifest(manifest)
    for raw_path, expected in rows:
        candidate = (root / raw_path.replace("\\", "/")).resolve()
        shown = "<redacted>" if redact else raw_path.replace("\\", "/")
        if candidate != root and root not in candidate.parents:
            findings.append(
                finding("ERROR", "checksum_path_escape", shown, "manifest path escapes case root")
            )
            continue
        listed.add(candidate)
        if not SHA256_RE.fullmatch(expected):
            findings.append(
                finding("ERROR", "invalid_checksum", shown, "expected digest is not SHA-256")
            )
        elif not candidate.is_file():
            findings.append(
                finding("ERROR", "checksum_file_missing", shown, "manifest file is missing")
            )
        elif sha256(candidate).lower() != expected.lower():
            findings.append(
                finding("ERROR", "checksum_mismatch", shown, "file digest does not match")
            )
    if require_complete:
        for candidate in sorted(path for path in root.rglob("*") if path.is_file()):
            if candidate.resolve() == manifest.resolve():
                continue
            if candidate.resolve() not in listed:
                findings.append(
                    finding(
                        "ERROR",
                        "checksum_unlisted_file",
                        relative(candidate, root, redact),
                        "file is absent from checksum manifest",
                    )
                )
    return findings, len(rows)


def audit(args: argparse.Namespace) -> dict[str, object]:
    root = args.root.resolve()
    findings: list[dict[str, object]] = []
    if not root.is_dir():
        raise ValueError("case root is not a directory")

    files = sorted(path for path in root.rglob("*") if path.is_file())
    suffix_counts = Counter((path.suffix.lower() or "<none>") for path in files)
    executable_files = [path for path in files if path.suffix.lower() in EXECUTABLE_SUFFIXES]
    references_checked = 0
    for path in executable_files:
        new_findings, count = scan_executable(root, path, args.redact_paths)
        findings.extend(new_findings)
        references_checked += count

    checksum_rows = 0
    if args.checksums:
        manifest = args.checksums.resolve()
        if not manifest.is_file():
            shown = "<redacted>" if args.redact_paths else str(args.checksums)
            findings.append(
                finding("ERROR", "checksum_manifest_missing", shown, "checksum manifest not found")
            )
        else:
            checksum_findings, checksum_rows = verify_checksums(
                root,
                manifest,
                args.redact_paths,
                args.require_complete_manifest,
            )
            findings.extend(checksum_findings)

    errors = sum(item["level"] == "ERROR" for item in findings)
    warnings = sum(item["level"] == "WARN" for item in findings)
    return {
        "schema_version": 1,
        "ok": errors == 0,
        "evidence_level": "static_only",
        "expected_pfc_major": args.expected_major,
        "inventory": {
            "files": len(files),
            "executable_sources": len(executable_files),
            "saved_states": sum(path.suffix.lower() in SAVE_SUFFIXES for path in files),
            "project_files": sum(path.suffix.lower() in PROJECT_SUFFIXES for path in files),
            "suffix_counts": dict(sorted(suffix_counts.items())),
        },
        "references_checked": references_checked,
        "checksum_rows": checksum_rows,
        "errors": errors,
        "warnings": warnings,
        "findings": findings,
        "runtime_validated": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="private case root to audit read-only")
    parser.add_argument(
        "--expected-major",
        default="5",
        choices=("5",),
        help="supported PFC major",
    )
    parser.add_argument("--checksums", type=Path, help="optional CSV digest manifest")
    parser.add_argument(
        "--require-complete-manifest",
        action="store_true",
        help="error on files absent from the digest manifest",
    )
    parser.add_argument(
        "--redact-paths",
        action="store_true",
        help="hide relative file paths in JSON findings",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        report = audit(args)
    except (OSError, ValueError, csv.Error) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
