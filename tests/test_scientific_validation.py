"""Regression tests for fail-closed scientific validation and repair routing."""

from __future__ import annotations

import json
from pathlib import Path

from tyqa.scientific_validation.engine import (
    validate_scientific_application,
    validate_scientific_plan,
)
from tyqa.scientific_validation.profiles import validate_vqe
from tyqa.scientific_validation.repair import RepairPolicy, update_repair_state
from tyqa.scientific_validation.runner import run_supplementary_tests

EXACT_ELECTRONIC = -1.8572750302023795
NUCLEAR_REPULSION = 0.7199689944489797
EXACT_TOTAL = EXACT_ELECTRONIC + NUCLEAR_REPULSION
HF_ELECTRONIC = -1.8369679912029844
HF_TOTAL = HF_ELECTRONIC + NUCLEAR_REPULSION


def _spec() -> dict:
    return {
        "contract_version": "1.0",
        "profile": "vqe",
        "problem": {
            "hamiltonian_kind": "electronic",
            "energy_convention": "total = electronic + nuclear repulsion",
            "reference_instance": "H2 STO-3G at 0.735 angstrom",
        },
        "conventions": {
            "qubit_order": "q0 least-significant",
            "bitstring_order": "|q1 q0>",
            "hf_bitstring": "01",
        },
        "references": [{"name": "independent dense diagonalization"}],
        "reference_values": {
            "exact_electronic_energy_hartree": EXACT_ELECTRONIC,
            "exact_total_energy_hartree": EXACT_TOTAL,
            "nuclear_repulsion_energy_hartree": NUCLEAR_REPULSION,
            "hf_electronic_energy_hartree": HF_ELECTRONIC,
        },
        "required_checks": [
            "energy_convention",
            "hf_state",
            "variational_bound",
            "reference_oracle",
        ],
        "tolerances": {"energy_hartree": 1e-9},
        "claims": {"allowed": ["fixture"], "forbidden": ["quantum advantage"]},
    }


def _baseline() -> dict:
    return {
        "task": "vqe_h2_ground_state",
        "data": "H2 fixture",
        "primary_metric": "absolute_energy_error_mhartree",
        "higher_is_better": False,
        "value": 20.307,
        "command": "python baseline.py",
        "hf_electronic_energy_hartree": HF_ELECTRONIC,
        "hf_total_energy_hartree": HF_TOTAL,
        "exact_electronic_energy_hartree": EXACT_ELECTRONIC,
        "exact_total_energy_hartree": EXACT_TOTAL,
        "nuclear_repulsion_energy_hartree": NUCLEAR_REPULSION,
        "hf_bitstring": "01",
    }


def _quantum() -> dict:
    electronic = EXACT_ELECTRONIC + 1e-10
    return {
        "task": "vqe_h2_ground_state",
        "data": "H2 fixture",
        "primary_metric": "absolute_energy_error_mhartree",
        "higher_is_better": False,
        "value": 1e-7,
        "command": "python vqe.py",
        "electronic_energy_hartree": electronic,
        "total_energy_hartree": electronic + NUCLEAR_REPULSION,
        "exact_electronic_energy_hartree": EXACT_ELECTRONIC,
        "exact_total_energy_hartree": EXACT_TOTAL,
        "nuclear_repulsion_energy_hartree": NUCLEAR_REPULSION,
        "energy_error_mhartree": abs(electronic - EXACT_ELECTRONIC) * 1000,
        "seeds": [11, 22],
        "per_seed_results": [
            {"seed": 11, "initial_theta": 0.1},
            {"seed": 22, "initial_theta": 0.2},
        ],
    }


def _codes(checks) -> set[str]:
    return {check.code for check in checks if check.status != "passed"}


def test_correct_vqe_contract_passes_profile_checks() -> None:
    checks = validate_vqe({}, _spec(), _baseline(), _quantum())

    assert _codes(checks) == set()


def test_valid_scientific_plan_allows_implementation_without_runtime_reports(
    tmp_path: Path,
) -> None:
    (tmp_path / "scientific_spec.json").write_text(
        json.dumps(_spec()), encoding="utf-8"
    )
    manifest = {
        "scientific_validation": {
            "profile": "vqe",
            "spec": "scientific_spec.json",
            "report": "scientific_report.json",
        }
    }

    result = validate_scientific_plan(tmp_path, manifest)

    assert result["status"] == "passed"
    assert result["implementation_allowed"] is True
    assert (tmp_path / "scientific_plan_report.json").is_file()


def test_incomplete_scientific_plan_blocks_implementation(tmp_path: Path) -> None:
    spec = _spec()
    del spec["conventions"]["hf_bitstring"]
    (tmp_path / "scientific_spec.json").write_text(json.dumps(spec), encoding="utf-8")
    manifest = {
        "scientific_validation": {
            "profile": "vqe",
            "spec": "scientific_spec.json",
            "report": "scientific_report.json",
        }
    }

    result = validate_scientific_plan(tmp_path, manifest)

    assert result["status"] == "failed"
    assert result["implementation_allowed"] is False
    assert "VQE.CONVENTIONS_MISSING" in result["failure_codes"]


def test_glm_vqe_h2_regression_is_rejected() -> None:
    baseline = _baseline()
    baseline.update(
        {
            "hf_bitstring": "10",
            "hf_electronic_energy_hartree": -1.063653350029,
            "hf_total_energy_hartree": -1.063653350029,
        }
    )
    quantum = _quantum()
    quantum.update(
        {
            "electronic_energy_hartree": -1.063653350029,
            "total_energy_hartree": -1.063653350029,
            "energy_error_mhartree": 0.0,
        }
    )

    codes = _codes(validate_vqe({}, _spec(), baseline, quantum))

    assert "VQE.ENERGY_CONVENTION_MISMATCH" in codes
    assert "VQE.HF_STATE_MISMATCH" in codes
    assert "VQE.REFERENCE_ORACLE_MISMATCH" in codes
    assert "VQE.ABSOLUTE_ERROR_MISMATCH" in codes


def test_vqe_variational_bound_and_seed_effect_are_enforced() -> None:
    quantum = _quantum()
    quantum["electronic_energy_hartree"] = EXACT_ELECTRONIC - 0.01
    quantum["total_energy_hartree"] = (
        quantum["electronic_energy_hartree"] + NUCLEAR_REPULSION
    )
    quantum["energy_error_mhartree"] = 10.0
    quantum["per_seed_results"] = [
        {"seed": 11, "initial_theta": 0.1},
        {"seed": 22, "initial_theta": 0.1},
    ]

    codes = _codes(validate_vqe({}, _spec(), _baseline(), quantum))

    assert "VQE.VARIATIONAL_BOUND_VIOLATION" in codes
    assert "COMMON.SEED_NO_EFFECT" in codes


def test_missing_scientific_contract_blocks_and_generates_report(
    tmp_path: Path,
) -> None:
    result = validate_scientific_application(tmp_path, {}, _baseline(), _quantum())

    assert result["status"] == "failed"
    assert result["delivery_allowed"] is False
    assert "SCIENTIFIC.CONTRACT_MISSING" in result["failure_codes"]
    assert (tmp_path / "scientific_report.json").is_file()


def test_missing_application_directory_is_not_created(tmp_path: Path) -> None:
    missing = tmp_path / "missing-app"

    plan_result = validate_scientific_plan(missing, None)
    application_result = validate_scientific_application(missing, None, None, None)

    assert plan_result["implementation_allowed"] is False
    assert application_result["delivery_allowed"] is False
    assert "SCIENTIFIC.APPLICATION_DIR_MISSING" in plan_result["failure_codes"]
    assert not missing.exists()


def test_report_path_cannot_escape_application(tmp_path: Path) -> None:
    (tmp_path / "scientific_spec.json").write_text(
        json.dumps(_spec()), encoding="utf-8"
    )
    manifest = {
        "scientific_validation": {
            "profile": "vqe",
            "spec": "scientific_spec.json",
            "report": "../escaped.json",
            "supplementary_tests": ["test_science.py"],
        }
    }
    (tmp_path / "test_science.py").write_text(
        "def test_ok():\n    assert True\n", encoding="utf-8"
    )

    result = validate_scientific_application(
        tmp_path, manifest, _baseline(), _quantum()
    )

    assert result["status"] == "failed"
    assert result["delivery_allowed"] is False
    assert "SCIENTIFIC.REPORT_PATH_INVALID" in result["failure_codes"]
    assert not (tmp_path.parent / "escaped.json").exists()


def test_supplementary_test_runner_rejects_shell_payload(tmp_path: Path) -> None:
    marker = tmp_path / "should-not-exist"
    result = run_supplementary_tests(
        tmp_path,
        [f"test_science.py; touch {marker.name}"],
    )

    assert result is not None
    assert result.status == "failed"
    assert result.code == "SCIENTIFIC.TEST_TARGET_INVALID"
    assert not marker.exists()


def test_repair_policy_routes_three_atomic_then_two_redesigns(tmp_path: Path) -> None:
    policy = RepairPolicy(atomic_attempt_limit=3, route_redesign_limit=2)

    state = update_repair_state(
        tmp_path,
        scientific_status="failed",
        source_hash="source-0",
        spec_hash="spec-0",
        failure_codes=["VQE.HF_STATE_MISMATCH"],
        policy=policy,
    )
    assert state["action"] == "repair"

    for attempt in range(1, 4):
        state = update_repair_state(
            tmp_path,
            scientific_status="failed",
            source_hash=f"source-{attempt}",
            spec_hash="spec-0",
            failure_codes=["VQE.HF_STATE_MISMATCH"],
            policy=policy,
        )
    assert state["atomic_attempts"] == 3
    assert state["action"] == "route_redesign"

    state = update_repair_state(
        tmp_path,
        scientific_status="failed",
        source_hash="route-1",
        spec_hash="spec-1",
        failure_codes=["VQE.REFERENCE_ORACLE_MISMATCH"],
        policy=policy,
    )
    assert state["route_redesigns"] == 1
    assert state["action"] == "repair"

    state = update_repair_state(
        tmp_path,
        scientific_status="failed",
        source_hash="route-2",
        spec_hash="spec-2",
        failure_codes=["VQE.REFERENCE_ORACLE_MISMATCH"],
        policy=policy,
    )
    assert state["route_redesigns"] == 2
    assert state["action"] == "manual_review"

    state = update_repair_state(
        tmp_path,
        scientific_status="passed",
        source_hash="fixed",
        spec_hash="spec-2",
        failure_codes=[],
        policy=policy,
    )
    assert state["action"] == "none"
    assert state["atomic_attempts"] == 0
    assert state["route_redesigns"] == 0
