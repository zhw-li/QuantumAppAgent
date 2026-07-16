"""Algorithm-specific deterministic scientific validation profiles."""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

from .models import ScientificCheck, failed, passed

ProfileValidator = Callable[
    [dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]],
    list[ScientificCheck],
]
SpecValidator = Callable[[dict[str, Any]], list[ScientificCheck]]

SUPPORTED_PROFILES = {"generic", "vqe", "qaoa", "qml", "hybrid"}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _number(mapping: dict[str, Any], key: str) -> float | None:
    value = mapping.get(key)
    if (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    ):
        return float(value)
    return None


def _close(left: float, right: float, tolerance: float) -> bool:
    return math.isclose(left, right, rel_tol=0.0, abs_tol=tolerance)


def _require_fields(
    name: str,
    code: str,
    mapping: dict[str, Any],
    fields: tuple[str, ...],
) -> ScientificCheck:
    missing = [field for field in fields if mapping.get(field) in (None, "", [], {})]
    if missing:
        return failed(
            name,
            code,
            f"missing required scientific fields: {', '.join(missing)}",
            expected=list(fields),
            actual=sorted(mapping),
        )
    return passed(name, f"{code}.PASSED", "required scientific fields are present")


def validate_common_spec_contract(
    manifest: dict[str, Any],
    spec: dict[str, Any],
) -> list[ScientificCheck]:
    checks: list[ScientificCheck] = []
    checks.append(
        _require_fields(
            "scientific_spec.schema",
            "SCIENTIFIC.SPEC_SCHEMA_INVALID",
            spec,
            (
                "contract_version",
                "profile",
                "problem",
                "conventions",
                "references",
                "required_checks",
                "claims",
            ),
        )
    )
    if spec.get("contract_version") != "1.0":
        checks.append(
            failed(
                "scientific_spec.version",
                "SCIENTIFIC.SPEC_VERSION_UNSUPPORTED",
                "scientific contract version is unsupported",
                expected="1.0",
                actual=spec.get("contract_version"),
            )
        )
    else:
        checks.append(
            passed(
                "scientific_spec.version",
                "SCIENTIFIC.SPEC_VERSION_SUPPORTED",
                "scientific contract version is supported",
            )
        )

    scientific_config = _as_dict(manifest.get("scientific_validation"))
    declared_profile = scientific_config.get("profile")
    spec_profile = spec.get("profile")
    if declared_profile != spec_profile or declared_profile not in SUPPORTED_PROFILES:
        checks.append(
            failed(
                "scientific_spec.profile",
                "SCIENTIFIC.PROFILE_MISMATCH",
                "manifest and scientific spec profiles must match a supported profile",
                expected=declared_profile,
                actual=spec_profile,
                supported=sorted(SUPPORTED_PROFILES),
            )
        )
    else:
        checks.append(
            passed(
                "scientific_spec.profile",
                "SCIENTIFIC.PROFILE_MATCHED",
                "scientific profile is supported and consistent",
                profile=declared_profile,
            )
        )

    return checks


def validate_common_contract(
    manifest: dict[str, Any],
    spec: dict[str, Any],
    baseline: dict[str, Any],
    quantum: dict[str, Any],
) -> list[ScientificCheck]:
    checks = validate_common_spec_contract(manifest, spec)
    for report_name, report in (("baseline", baseline), ("quantum", quantum)):
        checks.append(
            _require_fields(
                f"{report_name}_report.provenance",
                f"SCIENTIFIC.{report_name.upper()}_PROVENANCE_MISSING",
                report,
                (
                    "task",
                    "data",
                    "primary_metric",
                    "higher_is_better",
                    "value",
                    "command",
                ),
            )
        )
    return checks


def validate_vqe_spec(spec: dict[str, Any]) -> list[ScientificCheck]:
    problem = _as_dict(spec.get("problem"))
    conventions = _as_dict(spec.get("conventions"))
    references = _as_dict(spec.get("reference_values"))
    return [
        _require_fields(
            "vqe.problem_contract",
            "VQE.PROBLEM_CONTRACT_INVALID",
            problem,
            ("hamiltonian_kind", "energy_convention", "reference_instance"),
        ),
        _require_fields(
            "vqe.conventions",
            "VQE.CONVENTIONS_MISSING",
            conventions,
            ("qubit_order", "bitstring_order", "hf_bitstring"),
        ),
        _require_fields(
            "vqe.reference_values",
            "VQE.REFERENCE_ORACLE_MISSING",
            references,
            (
                "exact_electronic_energy_hartree",
                "exact_total_energy_hartree",
                "nuclear_repulsion_energy_hartree",
                "hf_electronic_energy_hartree",
            ),
        ),
    ]


def validate_generic(
    manifest: dict[str, Any],
    spec: dict[str, Any],
    baseline: dict[str, Any],
    quantum: dict[str, Any],
) -> list[ScientificCheck]:
    return []


def validate_vqe(
    manifest: dict[str, Any],
    spec: dict[str, Any],
    baseline: dict[str, Any],
    quantum: dict[str, Any],
) -> list[ScientificCheck]:
    checks = validate_vqe_spec(spec)
    conventions = _as_dict(spec.get("conventions"))
    references = _as_dict(spec.get("reference_values"))
    tolerances = _as_dict(spec.get("tolerances"))
    tolerance = _number(tolerances, "energy_hartree") or 1e-9

    baseline_fields = (
        "hf_electronic_energy_hartree",
        "hf_total_energy_hartree",
        "exact_electronic_energy_hartree",
        "exact_total_energy_hartree",
        "nuclear_repulsion_energy_hartree",
        "hf_bitstring",
    )
    quantum_fields = (
        "electronic_energy_hartree",
        "total_energy_hartree",
        "exact_electronic_energy_hartree",
        "exact_total_energy_hartree",
        "nuclear_repulsion_energy_hartree",
        "energy_error_mhartree",
    )
    checks.append(
        _require_fields(
            "vqe.baseline_energy_semantics",
            "VQE.BASELINE_ENERGY_FIELDS_MISSING",
            baseline,
            baseline_fields,
        )
    )
    checks.append(
        _require_fields(
            "vqe.quantum_energy_semantics",
            "VQE.QUANTUM_ENERGY_FIELDS_MISSING",
            quantum,
            quantum_fields,
        )
    )

    exact_electronic = _number(baseline, "exact_electronic_energy_hartree")
    exact_total = _number(baseline, "exact_total_energy_hartree")
    nuclear = _number(baseline, "nuclear_repulsion_energy_hartree")
    hf_electronic = _number(baseline, "hf_electronic_energy_hartree")
    hf_total = _number(baseline, "hf_total_energy_hartree")
    quantum_electronic = _number(quantum, "electronic_energy_hartree")
    quantum_total = _number(quantum, "total_energy_hartree")

    energy_values = (
        exact_electronic,
        exact_total,
        nuclear,
        hf_electronic,
        hf_total,
        quantum_electronic,
        quantum_total,
    )
    if all(value is not None for value in energy_values):
        assert exact_electronic is not None
        assert exact_total is not None
        assert nuclear is not None
        assert hf_electronic is not None
        assert hf_total is not None
        assert quantum_electronic is not None
        assert quantum_total is not None
        relations_ok = (
            _close(exact_electronic + nuclear, exact_total, tolerance)
            and _close(hf_electronic + nuclear, hf_total, tolerance)
            and _close(quantum_electronic + nuclear, quantum_total, tolerance)
        )
        checks.append(
            passed(
                "vqe.energy_convention",
                "VQE.ENERGY_CONVENTION_VALID",
                "electronic and total energies use one consistent convention",
                tolerance=tolerance,
            )
            if relations_ok
            else failed(
                "vqe.energy_convention",
                "VQE.ENERGY_CONVENTION_MISMATCH",
                "total energy must equal electronic energy plus nuclear repulsion",
                expected={
                    "exact_total": exact_electronic + nuclear,
                    "hf_total": hf_electronic + nuclear,
                    "quantum_total": quantum_electronic + nuclear,
                },
                actual={
                    "exact_total": exact_total,
                    "hf_total": hf_total,
                    "quantum_total": quantum_total,
                },
            )
        )

        variational_ok = quantum_electronic >= exact_electronic - tolerance
        checks.append(
            passed(
                "vqe.variational_bound",
                "VQE.VARIATIONAL_BOUND_VALID",
                "VQE energy respects the variational lower bound",
                tolerance=tolerance,
            )
            if variational_ok
            else failed(
                "vqe.variational_bound",
                "VQE.VARIATIONAL_BOUND_VIOLATION",
                "VQE energy is below the exact ground-state energy beyond tolerance",
                expected=f">= {exact_electronic - tolerance}",
                actual=quantum_electronic,
            )
        )

        reported_error = _number(quantum, "energy_error_mhartree")
        expected_error = abs(quantum_electronic - exact_electronic) * 1000.0
        error_ok = reported_error is not None and _close(
            reported_error, expected_error, tolerance * 1000.0
        )
        checks.append(
            passed(
                "vqe.absolute_error",
                "VQE.ABSOLUTE_ERROR_VALID",
                "reported VQE error is an absolute error against the exact "
                "electronic energy",
            )
            if error_ok
            else failed(
                "vqe.absolute_error",
                "VQE.ABSOLUTE_ERROR_MISMATCH",
                "reported energy error does not match the independently "
                "recomputed absolute error",
                expected=expected_error,
                actual=reported_error,
            )
        )

    expected_hf = conventions.get("hf_bitstring")
    actual_hf = baseline.get("hf_bitstring")
    checks.append(
        passed(
            "vqe.hf_state",
            "VQE.HF_STATE_VALID",
            "Hartree-Fock determinant matches the scientific contract",
        )
        if expected_hf and actual_hf == expected_hf
        else failed(
            "vqe.hf_state",
            "VQE.HF_STATE_MISMATCH",
            "Hartree-Fock determinant does not match the declared mapping",
            expected=expected_hf,
            actual=actual_hf,
        )
    )

    reference_pairs = (
        ("exact_electronic_energy_hartree", exact_electronic),
        ("exact_total_energy_hartree", exact_total),
        ("nuclear_repulsion_energy_hartree", nuclear),
        ("hf_electronic_energy_hartree", hf_electronic),
    )
    mismatched_references: dict[str, Any] = {}
    for key, actual in reference_pairs:
        expected = _number(references, key)
        if (
            expected is None
            or actual is None
            or not _close(expected, actual, tolerance)
        ):
            mismatched_references[key] = {"expected": expected, "actual": actual}
    checks.append(
        passed(
            "vqe.reference_oracle",
            "VQE.REFERENCE_ORACLE_MATCHED",
            "computed reference values match the independent scientific contract",
        )
        if not mismatched_references
        else failed(
            "vqe.reference_oracle",
            "VQE.REFERENCE_ORACLE_MISMATCH",
            "computed values disagree with the independent reference values",
            expected=references,
            actual=mismatched_references,
        )
    )

    seeds = _as_list(quantum.get("seeds"))
    per_seed = _as_list(quantum.get("per_seed_results"))
    if len(seeds) > 1:
        initial_values = [
            row.get("initial_theta")
            for row in per_seed
            if isinstance(row, dict)
            and isinstance(row.get("initial_theta"), (int, float))
        ]
        seed_ok = (
            len(initial_values) == len(seeds)
            and len({round(float(v), 14) for v in initial_values}) > 1
        )
        checks.append(
            passed(
                "vqe.seed_effectiveness",
                "COMMON.SEED_EFFECTIVE",
                "multiple seeds produce distinct recorded initial values",
            )
            if seed_ok
            else failed(
                "vqe.seed_effectiveness",
                "COMMON.SEED_NO_EFFECT",
                "multiple seeds were declared but did not produce distinct "
                "initial values",
                expected=(
                    f"{len(seeds)} per-seed rows with at least two distinct "
                    "initial values"
                ),
                actual=initial_values,
            )
        )
    return checks


def validate_qaoa_spec(spec: dict[str, Any]) -> list[ScientificCheck]:
    problem = _as_dict(spec.get("problem"))
    conventions = _as_dict(spec.get("conventions"))
    oracle = _as_dict(spec.get("oracle"))
    return [
        _require_fields(
            "qaoa.problem_contract",
            "QAOA.PROBLEM_CONTRACT_INVALID",
            problem,
            ("objective_direction", "original_objective", "constraints"),
        ),
        _require_fields(
            "qaoa.mapping_contract",
            "QAOA.MAPPING_CONTRACT_INVALID",
            conventions,
            ("variable_to_qubit", "bitstring_order", "qubo_convention"),
        ),
        _require_fields(
            "qaoa.oracle",
            "QAOA.ORACLE_MISSING",
            oracle,
            ("type", "reference_artifact"),
        ),
    ]


def validate_qaoa(
    manifest: dict[str, Any],
    spec: dict[str, Any],
    baseline: dict[str, Any],
    quantum: dict[str, Any],
) -> list[ScientificCheck]:
    return validate_qaoa_spec(spec)


def validate_qml_spec(spec: dict[str, Any]) -> list[ScientificCheck]:
    problem = _as_dict(spec.get("problem"))
    conventions = _as_dict(spec.get("conventions"))
    data = _as_dict(spec.get("data"))
    return [
        _require_fields(
            "qml.problem_contract",
            "QML.PROBLEM_CONTRACT_INVALID",
            problem,
            ("task_type", "loss", "metric"),
        ),
        _require_fields(
            "qml.data_contract",
            "QML.DATA_CONTRACT_INVALID",
            data,
            ("dataset", "split_hash", "preprocessing"),
        ),
        _require_fields(
            "qml.quantum_contract",
            "QML.QUANTUM_CONTRACT_INVALID",
            conventions,
            ("encoding", "output_mapping", "bitstring_order"),
        ),
    ]


def validate_qml(
    manifest: dict[str, Any],
    spec: dict[str, Any],
    baseline: dict[str, Any],
    quantum: dict[str, Any],
) -> list[ScientificCheck]:
    return validate_qml_spec(spec)


def validate_hybrid(
    manifest: dict[str, Any],
    spec: dict[str, Any],
    baseline: dict[str, Any],
    quantum: dict[str, Any],
) -> list[ScientificCheck]:
    checks = validate_qml_spec(spec)
    hybrid = _as_dict(spec.get("hybrid"))
    checks.append(
        _require_fields(
            "hybrid.training_contract",
            "HYBRID.TRAINING_CONTRACT_INVALID",
            hybrid,
            ("autograd_boundary", "quantum_parameter_update_check", "ablations"),
        )
    )
    return checks


PROFILE_VALIDATORS: dict[str, ProfileValidator] = {
    "generic": validate_generic,
    "vqe": validate_vqe,
    "qaoa": validate_qaoa,
    "qml": validate_qml,
    "hybrid": validate_hybrid,
}

SPEC_VALIDATORS: dict[str, SpecValidator] = {
    "generic": lambda spec: [],
    "vqe": validate_vqe_spec,
    "qaoa": validate_qaoa_spec,
    "qml": validate_qml_spec,
    "hybrid": lambda spec: validate_hybrid({}, spec, {}, {}),
}
