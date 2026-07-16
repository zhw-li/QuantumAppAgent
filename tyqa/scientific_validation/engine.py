"""Fail-closed scientific validation engine for generated quantum applications."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .evidence import (
    application_source_hash,
    file_hash,
    safe_app_path,
    write_json_atomic,
)
from .models import ScientificCheck, aggregate_status, failed, passed
from .profiles import (
    PROFILE_VALIDATORS,
    SPEC_VALIDATORS,
    validate_common_contract,
    validate_common_spec_contract,
)
from .repair import RepairPolicy, update_repair_state
from .runner import run_supplementary_tests


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _read_json_object(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def _missing_application_result(*, phase: str) -> dict[str, Any]:
    code = "SCIENTIFIC.APPLICATION_DIR_MISSING"
    result = {
        "contract_version": "1.0",
        "status": "failed",
        "profile": "unknown",
        "source_hash": "missing",
        "spec_hash": "missing",
        "checks": [
            failed(
                "application_directory",
                code,
                "application directory does not exist",
            ).to_dict()
        ],
        "failure_codes": [code],
    }
    if phase == "plan":
        result["implementation_allowed"] = False
    else:
        result["delivery_allowed"] = False
        result["repair"] = {"status": "failed", "action": "repair"}
    return result


def _contract_check(
    app_path: Path,
    manifest: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any], Path | None, list[ScientificCheck]]:
    checks: list[ScientificCheck] = []
    manifest_obj = _as_dict(manifest)
    config = _as_dict(manifest_obj.get("scientific_validation"))
    if not config:
        checks.append(
            failed(
                "scientific_contract",
                "SCIENTIFIC.CONTRACT_MISSING",
                "application_manifest.json must define scientific_validation",
            )
        )
        return config, {}, None, checks

    required = ("profile", "spec", "report")
    missing = [field for field in required if not config.get(field)]
    if missing:
        checks.append(
            failed(
                "scientific_contract",
                "SCIENTIFIC.CONTRACT_INVALID",
                f"scientific_validation is missing: {', '.join(missing)}",
                expected=list(required),
                actual=sorted(config),
            )
        )

    spec_path: Path | None = None
    spec: dict[str, Any] = {}
    raw_spec_path = config.get("spec")
    if isinstance(raw_spec_path, str):
        try:
            spec_path = safe_app_path(app_path, raw_spec_path)
        except ValueError as exc:
            checks.append(
                failed(
                    "scientific_spec.path",
                    "SCIENTIFIC.SPEC_PATH_INVALID",
                    str(exc),
                    actual=raw_spec_path,
                )
            )
        else:
            if not spec_path.is_file():
                checks.append(
                    failed(
                        "scientific_spec.path",
                        "SCIENTIFIC.SPEC_MISSING",
                        "scientific spec file does not exist",
                        actual=raw_spec_path,
                    )
                )
            else:
                loaded = _read_json_object(spec_path)
                if loaded is None:
                    checks.append(
                        failed(
                            "scientific_spec.schema",
                            "SCIENTIFIC.SPEC_JSON_INVALID",
                            "scientific spec must be a JSON object",
                            actual=raw_spec_path,
                        )
                    )
                else:
                    spec = loaded
                    checks.append(
                        passed(
                            "scientific_spec.path",
                            "SCIENTIFIC.SPEC_LOADED",
                            "scientific spec was loaded from the application",
                            path=raw_spec_path,
                        )
                    )
    return config, spec, spec_path, checks


def validate_scientific_plan(
    app_path: Path,
    manifest: dict[str, Any] | None,
) -> dict[str, Any]:
    """Validate the scientific plan before candidate algorithm code is written."""
    app_path = app_path.resolve()
    if not app_path.is_dir():
        return _missing_application_result(phase="plan")
    manifest_obj = _as_dict(manifest)
    config, spec, spec_path, checks = _contract_check(app_path, manifest)
    if spec:
        checks.extend(validate_common_spec_contract(manifest_obj, spec))
        profile = config.get("profile")
        validator = SPEC_VALIDATORS.get(profile)
        if validator is None:
            checks.append(
                failed(
                    "scientific_profile",
                    "SCIENTIFIC.PROFILE_UNSUPPORTED",
                    "no scientific plan profile is registered",
                    actual=profile,
                    supported=sorted(SPEC_VALIDATORS),
                )
            )
        else:
            checks.extend(validator(spec))

    status = aggregate_status(checks)
    profile = config.get("profile") or spec.get("profile") or "unknown"
    failure_codes = list(
        dict.fromkeys(check.code for check in checks if check.status != "passed")
    )
    source_hash = application_source_hash(app_path) if app_path.is_dir() else "missing"
    spec_hash = (
        file_hash(spec_path)
        if spec_path is not None and spec_path.is_file()
        else "missing"
    )
    report = {
        "contract_version": "1.0",
        "status": status,
        "profile": profile,
        "source_hash": source_hash,
        "spec_hash": spec_hash,
        "checks": [check.to_dict() for check in checks],
        "failure_codes": failure_codes,
        "implementation_allowed": status == "passed",
    }
    raw_report_path = config.get("plan_report", "scientific_plan_report.json")
    try:
        report_path = safe_app_path(app_path, raw_report_path)
    except ValueError:
        report_path = app_path / "scientific_plan_report.json"
        report["failure_codes"] = list(
            dict.fromkeys([*failure_codes, "SCIENTIFIC.PLAN_REPORT_PATH_INVALID"])
        )
        report["status"] = "failed"
        report["implementation_allowed"] = False
    write_json_atomic(report_path, report)
    report["report_path"] = report_path.relative_to(app_path).as_posix()
    return report


def validate_scientific_application(
    app_path: Path,
    manifest: dict[str, Any] | None,
    baseline: dict[str, Any] | None,
    quantum: dict[str, Any] | None,
) -> dict[str, Any]:
    """Validate scientific semantics and regenerate machine-owned evidence."""
    app_path = app_path.resolve()
    if not app_path.is_dir():
        return _missing_application_result(phase="application")
    source_hash = application_source_hash(app_path) if app_path.is_dir() else "missing"
    manifest_obj = _as_dict(manifest)
    baseline_obj = _as_dict(baseline)
    quantum_obj = _as_dict(quantum)
    config, spec, spec_path, checks = _contract_check(app_path, manifest)

    if spec:
        checks.extend(
            validate_common_contract(manifest_obj, spec, baseline_obj, quantum_obj)
        )
        profile = config.get("profile")
        validator = PROFILE_VALIDATORS.get(profile)
        if validator is None:
            checks.append(
                failed(
                    "scientific_profile",
                    "SCIENTIFIC.PROFILE_UNSUPPORTED",
                    "no deterministic scientific profile is registered",
                    actual=profile,
                    supported=sorted(PROFILE_VALIDATORS),
                )
            )
        else:
            checks.extend(validator(manifest_obj, spec, baseline_obj, quantum_obj))

        targets = config.get("supplementary_tests")
        if profile != "generic" and not targets:
            checks.append(
                failed(
                    "supplementary_tests",
                    "SCIENTIFIC.TESTS_REQUIRED",
                    f"{profile} applications must provide supplementary "
                    "scientific tests",
                )
            )
        test_check = run_supplementary_tests(
            app_path,
            targets,
            timeout_seconds=config.get("test_timeout_seconds", 120),
        )
        if test_check is not None:
            checks.append(test_check)

    status = aggregate_status(checks)
    failure_codes = list(
        dict.fromkeys(check.code for check in checks if check.status != "passed")
    )
    spec_hash = (
        file_hash(spec_path)
        if spec_path is not None and spec_path.is_file()
        else "missing"
    )
    repair_state = update_repair_state(
        app_path,
        scientific_status=status,
        source_hash=source_hash,
        spec_hash=spec_hash,
        failure_codes=failure_codes,
        policy=RepairPolicy.from_config(config),
    )
    if repair_state["action"] == "manual_review" and status != "passed":
        status = "manual_review"

    profile = config.get("profile") or spec.get("profile") or "unknown"
    report: dict[str, Any] = {
        "contract_version": "1.0",
        "status": status,
        "profile": profile,
        "run_id": f"{profile}-{source_hash[:16]}",
        "source_hash": source_hash,
        "spec_hash": spec_hash,
        "checks": [check.to_dict() for check in checks],
        "failure_codes": failure_codes,
        "repair": repair_state,
        "delivery_allowed": status == "passed",
    }

    raw_report_path = config.get("report", "scientific_report.json")
    try:
        report_path = safe_app_path(app_path, raw_report_path)
    except ValueError:
        report_path = app_path / "scientific_report.json"
        report["failure_codes"] = list(
            dict.fromkeys([*failure_codes, "SCIENTIFIC.REPORT_PATH_INVALID"])
        )
        report["status"] = "failed"
        report["delivery_allowed"] = False
    write_json_atomic(report_path, report)
    report["report_path"] = report_path.relative_to(app_path).as_posix()
    return report
