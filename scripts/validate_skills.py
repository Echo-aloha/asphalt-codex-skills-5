#!/usr/bin/env python3
"""Validate publication readiness for the PFC Codex skill repository."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
README_PATH = ROOT / "README.md"
REQUIRED_SKILLS_PATH = ROOT / "references" / "pfc5-skill-set.json"
PORTABLE_REQUIRED_SKILLS_PATH = SKILLS_DIR / "pfc-skill-pack" / "references" / "pfc5-skill-set.json"
PORTABLE_SKILL_INDEX_PATH = SKILLS_DIR / "pfc-skill-pack" / "references" / "skill-index.md"
PLUGIN_MANIFEST_PATH = ROOT / ".codex-plugin" / "plugin.json"
SKILL_COUNT_START = "<!-- skill-count:start -->"
SKILL_COUNT_END = "<!-- skill-count:end -->"

ABS_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/]|/mnt/[A-Za-z0-9._-]+(?:/|$)")
EXCLUDED_DIRS = {".git", ".tmp", ".pytest_cache", "__pycache__", ".venv", "venv"}
SECRET_RE = re.compile(
    r"(?:ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,})"
)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"(?<!`)`([^`\r\n]+)`(?!`)")
INLINE_PFC_REFERENCE_RE = re.compile(r"pfc[a-z0-9]*(?:-[a-z0-9]+)+")
INLINE_LOCAL_ROOTS = ("references/", "scripts/", "templates/", "agents/", "assets/")
# Lowercase inline-code tokens that begin with pfc but intentionally are not skills.
INLINE_PFC_REFERENCE_ALLOWLIST = frozenset({"pfc-flac"})
BINARY_RISK_SUFFIXES = {".exe", ".dll", ".sav", ".p2sav", ".p3sav", ".p2prj", ".p3prj"}
OVERSIZE_BYTES = 5_000_000
UNSUPPORTED_VERSION_RE = re.compile(
    r"\bPFC\s*(?:6(?:\.0)?|7(?:\.0)?)\b|\bPFC(?:6|7)\b", re.IGNORECASE
)
UNSUPPORTED_COMMAND_RE = re.compile(r"\bcontact\s+cmat\b", re.IGNORECASE)
UNSAFE_PYTHON_PATTERNS = {
    re.compile(r"\ballow_pickle\s*=\s*True\b"): "unsafe NumPy pickle loading",
    re.compile(r"\bshell\s*=\s*True\b"): "shell=True command execution",
}
AGENT_SHORT_DESCRIPTION_MAX = 64
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
REQUIRED_REQUIREMENTS = {
    "requirements.txt": {
        "numpy", "pandas", "matplotlib", "scipy", "imageio", "pillow",
    },
    "requirements-visualization.txt": {
        "imageio-ffmpeg", "opencv-python-headless", "vedo",
    },
    "requirements-dev.txt": {"pytest"},
}


@dataclass
class Finding:
    level: str
    path: Path
    message: str
    line: int | None = None

    def format(self) -> str:
        rel = self.path.relative_to(ROOT) if self.path.is_absolute() else self.path
        loc = f":{self.line}" if self.line else ""
        return f"{self.level}: {rel}{loc} - {self.message}"


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    data: dict[str, str] = {}
    current_key: str | None = None
    for raw in text[4:end].splitlines():
        if raw.startswith((" ", "\t")) and current_key:
            data[current_key] = (data[current_key] + " " + raw.strip()).strip()
            continue
        if ":" not in raw:
            current_key = None
            continue
        key, value = raw.split(":", 1)
        current_key = key.strip()
        data[current_key] = value.strip().strip('"').strip(">|- ")
    return data


def local_link_target(source: Path, raw: str) -> Path | None:
    target = raw.split("#", 1)[0].strip()
    if not target or re.match(r"(?:https?://|mailto:)", target):
        return None
    return (source.parent / target).resolve()


def validate_skill(skill_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        findings.append(Finding("ERROR", skill_dir, "missing SKILL.md"))
        return findings

    text = read_text(skill_file)
    if text is None:
        findings.append(Finding("ERROR", skill_file, "SKILL.md must be UTF-8 text"))
        return findings

    fm = frontmatter(text)
    if fm is None:
        findings.append(Finding("ERROR", skill_file, "missing YAML frontmatter"))
    else:
        if not fm.get("name"):
            findings.append(Finding("ERROR", skill_file, "frontmatter missing name"))
        elif fm["name"] != skill_dir.name:
            findings.append(
                Finding(
                    "ERROR",
                    skill_file,
                    f"frontmatter name must match directory: {skill_dir.name}",
                )
            )
        if not fm.get("description"):
            findings.append(Finding("ERROR", skill_file, "frontmatter missing description"))
        elif len(fm["description"]) < 40:
            findings.append(Finding("WARN", skill_file, "description is very short; add trigger/use-case detail"))

    body = text.split("---", 2)[-1] if text.startswith("---") else text
    checks = {
        "When to use": ("when to use", "use this skill", "when the user"),
        "Required inputs": ("required inputs", "inputs"),
        "Workflow": ("workflow", "checklist", "lifecycle"),
        "Output contract": ("output contract", "outputs", "deliver"),
        "Local contents": ("local contents", "contents"),
    }
    lower = body.lower()
    for label, needles in checks.items():
        if not any(n in lower for n in needles):
            findings.append(Finding("WARN", skill_file, f"missing or weak section: {label}"))

    if len(text.splitlines()) > 500:
        findings.append(
            Finding(
                "WARN",
                skill_file,
                "SKILL.md exceeds 500 lines; move detailed material to references/",
            )
        )

    return findings


def validate_agent_metadata(skill_dir: Path) -> list[Finding]:
    path = skill_dir / "agents" / "openai.yaml"
    if not path.exists():
        return []
    text = read_text(path)
    if text is None:
        return [Finding("ERROR", path, "agent metadata must be UTF-8 text")]
    match = re.search(
        r"^\s*short_description:\s*[\"']?(.*?)[\"']?\s*$",
        text,
        flags=re.MULTILINE,
    )
    if match is None:
        return [Finding("ERROR", path, "missing short_description")]
    value = match.group(1).strip().strip("\"'")
    if len(value) > AGENT_SHORT_DESCRIPTION_MAX:
        return [
            Finding(
                "ERROR",
                path,
                f"short_description exceeds {AGENT_SHORT_DESCRIPTION_MAX} characters",
            )
        ]
    return []


def validate_inline_skill_references(
    skill_dir: Path,
    known_skills: set[str] | None = None,
    allowlist: set[str] | frozenset[str] | None = None,
) -> list[Finding]:
    """Require inline `pfc...` skill-like tokens in SKILL.md to resolve."""
    path = skill_dir / "SKILL.md"
    text = read_text(path)
    if text is None:
        return []
    body_start = 0
    if text.startswith("---\n"):
        frontmatter_end = text.find("\n---", 4)
        if frontmatter_end >= 0:
            body_start = frontmatter_end + len("\n---")
    body = text[body_start:]
    approved = (
        (known_skills if known_skills is not None else {item.name for item in skill_directories()})
        | set(INLINE_PFC_REFERENCE_ALLOWLIST if allowlist is None else allowlist)
    )
    findings: list[Finding] = []
    for match in INLINE_CODE_RE.finditer(body):
        token = match.group(1)
        if INLINE_PFC_REFERENCE_RE.fullmatch(token) and token not in approved:
            line = text[: body_start + match.start()].count("\n") + 1
            findings.append(
                Finding(
                    "ERROR",
                    path,
                    f"unknown inline PFC skill reference: {token}",
                    line,
                )
            )
    return findings


def validate_inline_local_paths(skill_dir: Path, allowed_root: Path | None = None) -> list[Finding]:
    """Require local-looking inline-code paths in SKILL.md to exist and stay portable."""
    path = skill_dir / "SKILL.md"
    text = read_text(path)
    if text is None:
        return []
    root = (ROOT if allowed_root is None else allowed_root).resolve()
    findings: list[Finding] = []
    for match in INLINE_CODE_RE.finditer(text):
        raw = match.group(1).strip()
        normalized = raw.split("#", 1)[0].replace("\\", "/")
        if (
            not normalized
            or any(marker in normalized for marker in ("<", ">", "*", "?", "://"))
        ):
            continue
        is_local = (
            normalized.startswith(("./", "../", *INLINE_LOCAL_ROOTS))
        )
        if not is_local:
            continue
        line = text[: match.start()].count("\n") + 1
        if normalized.startswith("../../"):
            findings.append(
                Finding(
                    "ERROR",
                    path,
                    f"inline local path escapes the portable skills directory: {raw}",
                    line,
                )
            )
            continue
        candidate = (path.parent / normalized).resolve()
        if candidate != root and root not in candidate.parents:
            findings.append(Finding("ERROR", path, f"unsafe inline local path: {raw}", line))
        elif not candidate.exists():
            findings.append(Finding("ERROR", path, f"broken inline local path: {raw}", line))
    return findings


def validate_cross_skill_dependency_references(
    skill_dir: Path,
    skills_root: Path | None = None,
) -> list[Finding]:
    """Require every referenced sibling-skill asset to be declared in dependencies.json."""
    root = (SKILLS_DIR if skills_root is None else skills_root).resolve()
    manifest_path = skill_dir / "dependencies.json"
    declared: dict[str, set[str]] = {}
    if manifest_path.is_file():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            data = {}
        for entry in data.get("requires", []) if isinstance(data, dict) else []:
            if not isinstance(entry, dict) or not isinstance(entry.get("skill"), str):
                continue
            paths = entry.get("paths", [])
            if isinstance(paths, list):
                declared.setdefault(entry["skill"], set()).update(
                    item.replace("\\", "/") for item in paths if isinstance(item, str)
                )

    findings: list[Finding] = []
    seen: set[tuple[str, int, str, str]] = set()
    markdown_files = sorted(path for path in skill_dir.rglob("*.md") if path.is_file())
    for source in markdown_files:
        text = read_text(source)
        if text is None:
            continue
        raw_references: list[tuple[str, int]] = []
        for match in INLINE_CODE_RE.finditer(text):
            raw = match.group(1).strip()
            normalized = raw.split("#", 1)[0].replace("\\", "/")
            if (
                normalized
                and not any(marker in normalized for marker in ("<", ">", "*", "?", "://"))
                and normalized.startswith(("./", "../", *INLINE_LOCAL_ROOTS))
            ):
                raw_references.append((normalized, text[: match.start()].count("\n") + 1))
        for match in LINK_RE.finditer(text):
            raw = match.group(1).split("#", 1)[0].strip().replace("\\", "/")
            if raw and not re.match(r"(?:https?://|mailto:)", raw):
                raw_references.append((raw, text[: match.start()].count("\n") + 1))

        for raw, line in raw_references:
            candidate = (source.parent / raw).resolve()
            if candidate != root and root not in candidate.parents:
                continue
            try:
                relative_to_skills = candidate.relative_to(root)
            except ValueError:
                continue
            if len(relative_to_skills.parts) < 2:
                continue
            target_skill = relative_to_skills.parts[0]
            if target_skill == skill_dir.name:
                continue
            target_relative = Path(*relative_to_skills.parts[1:]).as_posix()
            key = (str(source), line, target_skill, target_relative)
            if key in seen:
                continue
            seen.add(key)
            if target_relative not in declared.get(target_skill, set()):
                findings.append(
                    Finding(
                        "ERROR",
                        source,
                        "undeclared cross-skill dependency: "
                        f"{target_skill}/{target_relative}",
                        line,
                    )
                )
    return findings


def skill_directories() -> list[Path]:
    return sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())


def validate_dependency_contract(skill_dir: Path) -> list[Finding]:
    """Validate optional, package-level sibling-skill dependencies."""
    manifest_path = skill_dir / "dependencies.json"
    if not manifest_path.exists():
        return []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [Finding("ERROR", manifest_path, f"invalid dependency manifest: {exc}")]
    if not isinstance(data, dict) or not isinstance(data.get("requires"), list):
        return [Finding("ERROR", manifest_path, "dependency manifest must contain a requires array")]

    findings: list[Finding] = []
    for index, entry in enumerate(data["requires"]):
        if not isinstance(entry, dict) or not isinstance(entry.get("skill"), str):
            findings.append(Finding("ERROR", manifest_path, f"requires[{index}] must name a skill"))
            continue
        required = SKILLS_DIR / entry["skill"]
        if not (required / "SKILL.md").is_file():
            findings.append(Finding("ERROR", manifest_path, f"missing required skill: {entry['skill']}"))
            continue
        paths = entry.get("paths", [])
        if not isinstance(paths, list) or not all(isinstance(item, str) for item in paths):
            findings.append(Finding("ERROR", manifest_path, f"requires[{index}].paths must be a string array"))
            continue
        for relative in paths:
            candidate = required / relative
            if candidate.resolve() != required.resolve() and required.resolve() not in candidate.resolve().parents:
                findings.append(Finding("ERROR", manifest_path, f"unsafe dependency path: {relative}"))
            elif not candidate.exists():
                findings.append(Finding("ERROR", manifest_path, f"missing dependency asset: {entry['skill']}/{relative}"))
    return findings


def validate_required_skill_set() -> list[Finding]:
    """Enforce the declared PFC5 functional-coverage inventory."""
    if not REQUIRED_SKILLS_PATH.is_file():
        return [Finding("ERROR", REQUIRED_SKILLS_PATH, "missing required-skill manifest")]
    try:
        data = json.loads(REQUIRED_SKILLS_PATH.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [Finding("ERROR", REQUIRED_SKILLS_PATH, f"invalid required-skill manifest: {exc}")]
    required = data.get("required_skills") if isinstance(data, dict) else None
    if not isinstance(required, list) or not required or not all(isinstance(item, str) for item in required):
        return [Finding("ERROR", REQUIRED_SKILLS_PATH, "required_skills must be a non-empty string array")]
    if len(required) != len(set(required)):
        return [Finding("ERROR", REQUIRED_SKILLS_PATH, "required_skills contains duplicate slugs")]

    actual = {path.name for path in skill_directories()}
    findings: list[Finding] = []
    for slug in sorted(set(required) - actual):
        findings.append(Finding("ERROR", REQUIRED_SKILLS_PATH, f"required skill is missing: {slug}"))
    for slug in sorted(actual - set(required)):
        findings.append(Finding("ERROR", REQUIRED_SKILLS_PATH, f"undeclared skill directory: {slug}"))
    return findings


def validate_portable_required_skill_set() -> list[Finding]:
    """Keep the repository and self-contained governance-skill manifests identical."""
    if not PORTABLE_REQUIRED_SKILLS_PATH.is_file():
        return [Finding("ERROR", PORTABLE_REQUIRED_SKILLS_PATH, "missing portable required-skill manifest")]
    try:
        repository_data = json.loads(REQUIRED_SKILLS_PATH.read_text(encoding="utf-8"))
        portable_data = json.loads(PORTABLE_REQUIRED_SKILLS_PATH.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [Finding("ERROR", PORTABLE_REQUIRED_SKILLS_PATH, f"invalid portable required-skill manifest: {exc}")]
    if portable_data != repository_data:
        return [Finding("ERROR", PORTABLE_REQUIRED_SKILLS_PATH, "portable required-skill manifest differs from repository manifest")]
    return []


def validate_portable_skill_index() -> list[Finding]:
    """Keep the single-skill installation index identical to the release index."""
    repository_index = ROOT / "references" / "skill-index.md"
    if not PORTABLE_SKILL_INDEX_PATH.is_file():
        return [Finding("ERROR", PORTABLE_SKILL_INDEX_PATH, "missing portable skill index")]
    if read_text(PORTABLE_SKILL_INDEX_PATH) != read_text(repository_index):
        return [Finding("ERROR", PORTABLE_SKILL_INDEX_PATH, "portable skill index is stale; run validator with --write-index")]
    return []


def validate_plugin_manifest(plugin_root: Path = ROOT) -> list[Finding]:
    path = plugin_root / ".codex-plugin" / "plugin.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [Finding("ERROR", path, "missing plugin manifest")]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [Finding("ERROR", path, f"invalid plugin manifest: {exc}")]
    if not isinstance(data, dict):
        return [Finding("ERROR", path, "plugin manifest must contain an object")]

    findings: list[Finding] = []
    required_strings = ("name", "version", "description", "skills")
    for field in required_strings:
        if not isinstance(data.get(field), str) or not data[field].strip():
            findings.append(Finding("ERROR", path, f"plugin field must be non-empty: {field}"))
    if isinstance(data.get("name"), str) and data["name"] != plugin_root.name:
        findings.append(Finding("ERROR", path, "plugin name must match its root directory"))
    if isinstance(data.get("version"), str) and not SEMVER_RE.fullmatch(data["version"]):
        findings.append(Finding("ERROR", path, "plugin version must be strict semver"))
    if isinstance(data.get("skills"), str) and data["skills"].replace("\\", "/").strip("./") != "skills":
        findings.append(Finding("ERROR", path, "plugin skills path must resolve to ./skills/"))

    author = data.get("author")
    if not isinstance(author, dict) or not isinstance(author.get("name"), str) or not author["name"].strip():
        findings.append(Finding("ERROR", path, "plugin author.name must be non-empty"))
    interface = data.get("interface")
    if not isinstance(interface, dict):
        findings.append(Finding("ERROR", path, "plugin interface must be an object"))
    else:
        for field in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
            if not isinstance(interface.get(field), str) or not interface[field].strip():
                findings.append(Finding("ERROR", path, f"plugin interface field must be non-empty: {field}"))
        capabilities = interface.get("capabilities")
        if not isinstance(capabilities, list) or not all(isinstance(item, str) and item.strip() for item in capabilities):
            findings.append(Finding("ERROR", path, "plugin capabilities must be a string array"))
        prompts = interface.get("defaultPrompt")
        if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
            findings.append(Finding("ERROR", path, "plugin defaultPrompt must contain one to three prompts"))
        elif not all(isinstance(item, str) and item.strip() and len(item) <= 128 for item in prompts):
            findings.append(Finding("ERROR", path, "plugin prompts must be non-empty and at most 128 characters"))
    if "[TODO:" in json.dumps(data, ensure_ascii=False):
        findings.append(Finding("ERROR", path, "plugin manifest contains an unfinished TODO marker"))
    return findings


def requirement_names(path: Path) -> tuple[set[str], set[str]]:
    names: set[str] = set()
    includes: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("-r "):
            includes.add(line[3:].strip())
            continue
        match = re.match(r"([A-Za-z0-9_.-]+)", line)
        if match:
            names.add(match.group(1).lower().replace("_", "-"))
    return names, includes


def validate_requirement_contract(root: Path = ROOT) -> list[Finding]:
    findings: list[Finding] = []
    for filename, required in REQUIRED_REQUIREMENTS.items():
        path = root / filename
        if not path.is_file():
            findings.append(Finding("ERROR", path, "missing release requirements file"))
            continue
        names, includes = requirement_names(path)
        for package in sorted(required - names):
            findings.append(Finding("ERROR", path, f"missing declared dependency: {package}"))
        if filename != "requirements.txt" and "requirements.txt" not in includes:
            findings.append(Finding("ERROR", path, "optional/test requirements must include requirements.txt"))
    return findings


def iter_repository_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        yield path


def validate_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    suffix = path.suffix.lower()
    size = path.stat().st_size
    if size > OVERSIZE_BYTES:
        findings.append(Finding("WARN", path, f"large file ({size} bytes); confirm it is source/reference, not output"))
    if suffix in BINARY_RISK_SUFFIXES:
        findings.append(Finding("ERROR", path, "publication-risk binary or generated PFC state; remove or document externally"))

    text = read_text(path)
    if text is None:
        return findings

    relative = path.relative_to(ROOT)
    is_validator = path.resolve() == Path(__file__).resolve()
    is_test = "tests" in relative.parts
    if suffix in {".p2dat", ".p3dat", ".fis", ".p2fis", ".p3fis"} and not re.search(
        r"\b(?:static_validated|runtime_validated)\s*:", text, re.IGNORECASE
    ):
        findings.append(Finding("ERROR", path, "PFC source must declare static_validated or runtime_validated"))
    skip_absolute_path_scan = is_validator
    for i, line in enumerate(text.splitlines(), 1):
        if not skip_absolute_path_scan and ABS_PATH_RE.search(line):
            findings.append(Finding("ERROR", path, "private absolute path; replace with relative path or placeholder", i))
        if SECRET_RE.search(line):
            findings.append(Finding("ERROR", path, "possible leaked credential/token", i))
        if not is_validator and not is_test:
            if UNSUPPORTED_VERSION_RE.search(line):
                findings.append(
                    Finding(
                        "ERROR",
                        path,
                        "unsupported PFC major-version content in PFC5-only package",
                        i,
                    )
                )
            if UNSUPPORTED_COMMAND_RE.search(line):
                findings.append(
                    Finding(
                        "ERROR",
                        path,
                        "unsupported newer-major command family in PFC5-only package",
                        i,
                    )
                )
        if not is_test and not is_validator:
            for pattern, label in UNSAFE_PYTHON_PATTERNS.items():
                if pattern.search(line):
                    findings.append(Finding("ERROR", path, label, i))

    if suffix in {".md", ".markdown"}:
        for match in LINK_RE.finditer(text):
            target = local_link_target(path, match.group(1))
            if target is not None and not target.exists():
                line = text[: match.start()].count("\n") + 1
                findings.append(Finding("ERROR", path, f"broken local Markdown link: {match.group(1)}", line))

    return findings


def validate_generated_artifacts() -> list[Finding]:
    findings: list[Finding] = []
    for path in ROOT.rglob("*"):
        if path.name == "__pycache__" and path.is_dir():
            findings.append(Finding("ERROR", path, "generated __pycache__ directory"))
        elif path.is_file() and path.suffix.lower() == ".pyc":
            findings.append(Finding("ERROR", path, "generated Python bytecode"))
    return findings


def generate_index(skills_dir: Path = SKILLS_DIR) -> str:
    rows = []
    for skill_dir in sorted(
        p for p in skills_dir.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()
    ):
        skill_file = skill_dir / "SKILL.md"
        text = read_text(skill_file) or ""
        fm = frontmatter(text) or {}
        desc = fm.get("description", "").replace("\n", " ").strip()
        indexed_files = list(iter_repository_files(skill_dir))
        references_dir = skill_dir / "references"
        scripts_dir = skill_dir / "scripts"
        files = len(indexed_files)
        refs = sum(1 for path in indexed_files if references_dir in path.parents)
        scripts = sum(1 for path in indexed_files if scripts_dir in path.parents)
        rows.append((skill_dir.name, fm.get("name", ""), files, refs, scripts, desc))

    lines = [
        "# Skill Index",
        "",
        "Generated by `scripts/validate_skills.py --write-index`.",
        "",
        "| Slug | Name | Files | References | Scripts | Description |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for slug, name, files, refs, scripts, desc in rows:
        desc = desc.replace("|", r"\|")
        lines.append(f"| `{slug}` | `{name}` | {files} | {refs} | {scripts} | {desc} |")
    lines.append("")
    return "\n".join(lines)


def skill_count_block() -> str:
    return (
        f"{SKILL_COUNT_START}\n"
        f"当前包包含 **{len(skill_directories())} 个技能**；数量由 "
        "`scripts/validate_skills.py --write-index` 自动维护。\n"
        f"{SKILL_COUNT_END}"
    )


def update_readme_skill_count() -> None:
    text = README_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"{re.escape(SKILL_COUNT_START)}.*?{re.escape(SKILL_COUNT_END)}",
        flags=re.DOTALL,
    )
    replacement = skill_count_block()
    if pattern.search(text):
        text = pattern.sub(replacement, text, count=1)
    else:
        anchor = "完整清单见 [`references/skill-index.md`](references/skill-index.md)。"
        if anchor not in text:
            raise ValueError("README skill-index anchor is missing")
        text = text.replace(anchor, f"{anchor}\n\n{replacement}", 1)
    README_PATH.write_text(text, encoding="utf-8")


def validate_readme_skill_count() -> list[Finding]:
    text = read_text(README_PATH) or ""
    expected = skill_count_block()
    if expected not in text:
        return [Finding("ERROR", README_PATH, "generated skill count is stale; run validator with --write-index")]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-index", action="store_true", help="rewrite references/skill-index.md")
    args = parser.parse_args()

    if args.write_index:
        index_path = ROOT / "references" / "skill-index.md"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        generated_index = generate_index()
        index_path.write_text(generated_index, encoding="utf-8")
        PORTABLE_SKILL_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        PORTABLE_SKILL_INDEX_PATH.write_text(generated_index, encoding="utf-8")
        print(f"wrote {index_path.relative_to(ROOT)}")
        print(f"wrote {PORTABLE_SKILL_INDEX_PATH.relative_to(ROOT)}")
        update_readme_skill_count()
        print(f"updated {README_PATH.relative_to(ROOT)} skill count")

    findings: list[Finding] = []
    if not SKILLS_DIR.exists():
        print(f"ERROR: missing skills directory: {SKILLS_DIR}", file=sys.stderr)
        return 2

    findings.extend(validate_readme_skill_count())
    findings.extend(validate_plugin_manifest())
    findings.extend(validate_requirement_contract())
    findings.extend(validate_required_skill_set())
    findings.extend(validate_portable_required_skill_set())
    findings.extend(validate_portable_skill_index())
    skills = skill_directories()
    known_skills = {skill_dir.name for skill_dir in skills}
    for skill_dir in skills:
        findings.extend(validate_skill(skill_dir))
        findings.extend(validate_agent_metadata(skill_dir))
        findings.extend(validate_inline_skill_references(skill_dir, known_skills))
        findings.extend(validate_inline_local_paths(skill_dir))
        findings.extend(validate_dependency_contract(skill_dir))
        findings.extend(validate_cross_skill_dependency_references(skill_dir))
    for path in sorted(iter_repository_files(ROOT)):
        findings.extend(validate_file(path))
    findings.extend(validate_generated_artifacts())

    errors = [f for f in findings if f.level == "ERROR"]
    warnings = [f for f in findings if f.level == "WARN"]
    for finding in findings:
        print(finding.format())
    print(f"\nValidation summary: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
