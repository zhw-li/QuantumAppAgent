"""Scientific and application-contract tests for the H2 VQE case."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from algorithms.baseline import compute_hf_energy, compute_reference
from algorithms.hamiltonian import (
    HF_BITSTRING,
    H2_HAMILTONIAN,
    NUCLEAR_REPULSION_ENERGY_HARTREE,
    hamiltonian_to_matrix,
)
from algorithms.vqe import build_ansatz, compute_energy, run_vqe
from app.main import app

APP_DIR = Path(__file__).resolve().parent.parent


def test_hamiltonian_matches_public_h2_reference() -> None:
    matrix = hamiltonian_to_matrix(H2_HAMILTONIAN, 2)
    assert np.allclose(matrix, matrix.conj().T)
    eigenvalues = np.linalg.eigvalsh(matrix)
    assert eigenvalues[0] == pytest.approx(-1.857275030202, abs=1e-12)
    assert NUCLEAR_REPULSION_ENERGY_HARTREE == pytest.approx(
        0.719968994449, abs=1e-12
    )
    assert eigenvalues[0] + NUCLEAR_REPULSION_ENERGY_HARTREE == pytest.approx(
        -1.137306035753, abs=1e-12
    )


def test_hartree_fock_reference_uses_correct_bitstring() -> None:
    reference = compute_reference()
    assert HF_BITSTRING == "01"
    assert compute_hf_energy() == pytest.approx(-1.836967991203, abs=1e-12)
    assert reference.hf_total_energy_hartree == pytest.approx(-1.116998996754, abs=1e-12)
    assert reference.hf_error_mhartree == pytest.approx(20.307038999, abs=1e-9)


@pytest.mark.parametrize("theta", [-1.2, -0.2, 0.0, 0.7, 2.1])
def test_cqlib_energy_matches_dense_matrix(theta: float) -> None:
    circuit, _ = build_ansatz()
    cqlib_energy = compute_energy(circuit, {"theta": theta})

    # The ansatz prepares cos(theta/2)|01> + sin(theta/2)|10>.
    state = np.zeros(4, dtype=complex)
    state[1] = np.cos(theta / 2)
    state[2] = np.sin(theta / 2)
    matrix = hamiltonian_to_matrix(H2_HAMILTONIAN, 2)
    dense_energy = float(np.real(np.vdot(state, matrix @ state)))
    assert cqlib_energy == pytest.approx(dense_energy, abs=1e-10)


@pytest.mark.parametrize("seed", [42, 123, 456])
def test_vqe_obeys_variational_bound_and_reaches_chemical_accuracy(seed: int) -> None:
    reference = compute_reference()
    result = run_vqe(seed)
    assert result.optimizer_success
    assert result.electronic_energy_hartree >= (
        reference.exact_electronic_energy_hartree - 1e-9
    )
    assert result.energy_error_mhartree <= 1.6
    assert result.correlation_energy_recovered_percent >= 99.99
    assert result.total_energy_hartree == pytest.approx(
        result.electronic_energy_hartree + NUCLEAR_REPULSION_ENERGY_HARTREE,
        abs=1e-12,
    )


def test_api_contract_and_energy_semantics() -> None:
    client = TestClient(app)
    info = client.get("/api/info")
    baseline = client.get("/api/baseline")
    vqe = client.get("/api/vqe", params={"seed": 42})
    comparison = client.get("/api/compare")

    assert info.status_code == baseline.status_code == vqe.status_code == 200
    assert comparison.status_code == 200
    assert info.json()["energy_convention"] == "electronic_plus_nuclear_repulsion"

    baseline_data = baseline.json()
    assert baseline_data["hf_bitstring"] == "01"
    assert baseline_data["exact_total_energy_hartree"] == pytest.approx(
        -1.137306035753, abs=1e-10
    )

    vqe_data = vqe.json()
    assert vqe_data["energy_error_mhartree"] <= 1.6
    assert vqe_data["parameters"] == 1
    assert vqe_data["qcis"]
    assert vqe_data["convergence"]
    assert set(vqe_data["convergence"][0]) == {
        "evaluation",
        "electronic_energy_hartree",
        "total_energy_hartree",
    }

    comparison_data = comparison.json()
    assert comparison_data["baseline"]["hf_error_mhartree"] == pytest.approx(
        20.307038999, abs=1e-6
    )
    assert comparison_data["vqe"]["energy_error_mhartree"] <= 1.6
    assert comparison_data["correlation_energy_recovered_percent"] >= 99.99


def test_reports_use_total_and_electronic_energy_explicitly() -> None:
    baseline_report = json.loads((APP_DIR / "baseline_report.json").read_text())
    quantum_report = json.loads((APP_DIR / "quantum_report.json").read_text())
    for report in (baseline_report, quantum_report):
        assert report["task"] == "vqe_h2_ground_state"
        assert report["primary_metric"] == "absolute_energy_error_mhartree"
        assert report["higher_is_better"] is False
    assert "exact_electronic_energy_hartree" in baseline_report
    assert "exact_total_energy_hartree" in baseline_report
    assert "electronic_energy_hartree" in quantum_report
    assert "total_energy_hartree" in quantum_report


def test_manifest_and_frontends_follow_the_api_contract() -> None:
    manifest = json.loads((APP_DIR / "application_manifest.json").read_text())
    assert manifest["scientific_scope"]["energy_convention"].startswith(
        "molecular total energy"
    )
    assert manifest["algorithm"]["parameters"] == 1
    assert "layers" not in manifest["algorithm"]

    standalone = (APP_DIR / "app/static/index.html").read_text()
    assert "vqe-layers" not in standalone
    assert "total_energy_hartree" in standalone
    assert "electronic_energy_hartree" in standalone

    qccp_root = APP_DIR / "qccp_page/project-files/src/views/solution/vqeH2"
    vqe_panel = (qccp_root / "components/VqePanel.vue").read_text()
    compare_panel = (qccp_root / "components/ComparePanel.vue").read_text()
    assert "layers" not in vqe_panel
    assert "p.total_energy_hartree" in vqe_panel
    assert "d.baseline.hf_total_energy_hartree" in compare_panel
    assert "d.vqe.total_energy_hartree" in compare_panel
