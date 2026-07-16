"""Restricted command runner for supplementary scientific tests."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from .evidence import safe_app_path
from .models import ScientificCheck, failed, inconclusive, passed

MAX_TEST_TIMEOUT_SECONDS = 300


def _validated_test_targets(app_path: Path, targets: Any) -> list[str]:
    if targets is None:
        return []
    if not isinstance(targets, list) or not all(
        isinstance(item, str) for item in targets
    ):
        raise ValueError("supplementary_tests must be a list of relative paths")

    validated: list[str] = []
    for item in targets:
        target = safe_app_path(app_path, item)
        if not target.exists():
            raise ValueError(f"supplementary test target does not exist: {item}")
        validated.append(target.relative_to(app_path.resolve()).as_posix())
    return validated


def run_supplementary_tests(
    app_path: Path,
    targets: Any,
    *,
    timeout_seconds: int = 120,
) -> ScientificCheck | None:
    """Run pytest without a shell and without accepting arbitrary arguments."""
    try:
        validated = _validated_test_targets(app_path, targets)
    except ValueError as exc:
        return failed(
            "supplementary_tests",
            "SCIENTIFIC.TEST_TARGET_INVALID",
            str(exc),
        )
    if not validated:
        return None

    timeout = max(1, min(int(timeout_seconds), MAX_TEST_TIMEOUT_SECONDS))
    command = [sys.executable, "-m", "pytest", "-q", *validated]
    environment = os.environ.copy()
    existing_pythonpath = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        str(app_path)
        if not existing_pythonpath
        else os.pathsep.join((str(app_path), existing_pythonpath))
    )
    try:
        completed = subprocess.run(
            command,
            cwd=app_path,
            env=environment,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return failed(
            "supplementary_tests",
            "SCIENTIFIC.TEST_TIMEOUT",
            f"scientific tests exceeded {timeout} seconds",
            actual=exc.stdout or "",
            timeout_seconds=timeout,
        )
    except OSError as exc:
        return inconclusive(
            "supplementary_tests",
            "SCIENTIFIC.TEST_RUNNER_UNAVAILABLE",
            f"could not start scientific tests: {exc}",
        )

    output = "\n".join(
        part for part in (completed.stdout, completed.stderr) if part
    ).strip()
    evidence = {
        "command": command,
        "exit_code": completed.returncode,
        "timeout_seconds": timeout,
    }
    if completed.returncode != 0:
        return failed(
            "supplementary_tests",
            "SCIENTIFIC.TESTS_FAILED",
            "supplementary scientific tests failed",
            expected=0,
            actual=completed.returncode,
            output_tail=output[-6000:],
            **evidence,
        )
    return passed(
        "supplementary_tests",
        "SCIENTIFIC.TESTS_PASSED",
        "supplementary scientific tests passed",
        **evidence,
    )
