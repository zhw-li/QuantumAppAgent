"""Deterministic 3+2 repair policy for failed scientific validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence import write_json_atomic


@dataclass(frozen=True)
class RepairPolicy:
    atomic_attempt_limit: int = 3
    route_redesign_limit: int = 2

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> RepairPolicy:
        raw = config.get("repair_policy")
        if not isinstance(raw, dict):
            return cls()
        atomic = raw.get("atomic_attempt_limit", 3)
        route = raw.get("route_redesign_limit", 2)
        if not isinstance(atomic, int) or isinstance(atomic, bool):
            atomic = 3
        if not isinstance(route, int) or isinstance(route, bool):
            route = 2
        return cls(
            atomic_attempt_limit=max(1, min(atomic, 10)),
            route_redesign_limit=max(1, min(route, 5)),
        )


def _state_path(app_path: Path) -> Path:
    return app_path / ".tyqa" / "scientific_repair_state.json"


def _load_state(app_path: Path) -> dict[str, Any]:
    path = _state_path(app_path)
    if not path.is_file():
        return {}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return state if isinstance(state, dict) else {}


def update_repair_state(
    app_path: Path,
    *,
    scientific_status: str,
    source_hash: str,
    spec_hash: str,
    failure_codes: list[str],
    policy: RepairPolicy,
) -> dict[str, Any]:
    """Update attempts only when code/spec evidence changed between validations."""
    previous = _load_state(app_path)
    atomic_attempts = int(previous.get("atomic_attempts", 0) or 0)
    route_redesigns = int(previous.get("route_redesigns", 0) or 0)

    if scientific_status == "passed":
        action = "none"
        atomic_attempts = 0
        route_redesigns = 0
    else:
        previous_source = previous.get("last_source_hash")
        previous_spec = previous.get("last_spec_hash")
        if previous_source and previous_source != source_hash:
            if previous_spec and previous_spec != spec_hash:
                route_redesigns += 1
                atomic_attempts = 0
            else:
                atomic_attempts += 1

        if route_redesigns >= policy.route_redesign_limit:
            action = "manual_review"
        elif atomic_attempts >= policy.atomic_attempt_limit:
            action = "route_redesign"
        else:
            action = "repair"

    state = {
        "status": scientific_status,
        "action": action,
        "atomic_attempts": atomic_attempts,
        "atomic_attempt_limit": policy.atomic_attempt_limit,
        "route_redesigns": route_redesigns,
        "route_redesign_limit": policy.route_redesign_limit,
        "last_source_hash": source_hash,
        "last_spec_hash": spec_hash,
        "failure_codes": failure_codes,
    }
    write_json_atomic(_state_path(app_path), state)
    return state
