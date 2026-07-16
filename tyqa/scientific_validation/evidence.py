"""Evidence hashing and safe path helpers for scientific validation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

SCIENTIFIC_SOURCE_SUFFIXES = {".py", ".json", ".toml", ".yaml", ".yml"}
GENERATED_SCIENTIFIC_FILES = {
    "scientific_plan_report.json",
    "scientific_report.json",
}


def safe_app_path(app_path: Path, relative_path: str) -> Path:
    """Resolve a manifest path and reject traversal outside the application."""
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise ValueError("path must be a non-empty string")
    raw = Path(relative_path)
    if raw.is_absolute():
        raise ValueError("absolute paths are not allowed")
    resolved_app = app_path.resolve()
    resolved = (resolved_app / raw).resolve()
    try:
        resolved.relative_to(resolved_app)
    except ValueError as exc:
        raise ValueError("path escapes the application directory") from exc
    return resolved


def _iter_scientific_files(app_path: Path) -> list[Path]:
    files: list[Path] = []
    for path in app_path.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(app_path)
        if ".tyqa" in relative.parts or "__pycache__" in relative.parts:
            continue
        if path.name in GENERATED_SCIENTIFIC_FILES or path.suffix == ".pyc":
            continue
        if path.suffix.lower() in SCIENTIFIC_SOURCE_SUFFIXES:
            files.append(path)
    return sorted(files, key=lambda path: path.relative_to(app_path).as_posix())


def application_source_hash(app_path: Path) -> str:
    """Hash scientific source, specs, reports, and dependency metadata."""
    digest = hashlib.sha256()
    for path in _iter_scientific_files(app_path):
        relative = path.relative_to(app_path).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
