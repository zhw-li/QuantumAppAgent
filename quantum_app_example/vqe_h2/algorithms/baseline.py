"""Classical references for the two-qubit H2 VQE application."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

import numpy as np

from algorithms.hamiltonian import (
    BOND_DISTANCE_ANGSTROM,
    HF_BITSTRING,
    H2_HAMILTONIAN,
    N_QUBITS,
    NUCLEAR_REPULSION_ENERGY_HARTREE,
    basis_state,
    electronic_to_total_energy,
    hamiltonian_to_matrix,
)

REPORT_PATH = Path(__file__).resolve().parent.parent / "baseline_report.json"


@dataclass(frozen=True)
class ClassicalReference:
    hf_electronic_energy_hartree: float
    hf_total_energy_hartree: float
    exact_electronic_energy_hartree: float
    exact_total_energy_hartree: float
    nuclear_repulsion_energy_hartree: float
    hf_error_mhartree: float


def compute_hf_energy() -> float:
    """Return ``<01|H_electronic|01>`` in the Cqlib ``|q1 q0>`` convention."""
    hamiltonian = hamiltonian_to_matrix(H2_HAMILTONIAN, N_QUBITS)
    hf_state = basis_state(HF_BITSTRING)
    energy = np.vdot(hf_state, hamiltonian @ hf_state)
    return float(np.real_if_close(energy))


def compute_reference() -> ClassicalReference:
    """Compute Hartree-Fock and exact energies for the same Hamiltonian."""
    hamiltonian = hamiltonian_to_matrix(H2_HAMILTONIAN, N_QUBITS)
    exact_electronic = float(np.linalg.eigvalsh(hamiltonian)[0])
    hf_electronic = compute_hf_energy()
    return ClassicalReference(
        hf_electronic_energy_hartree=hf_electronic,
        hf_total_energy_hartree=electronic_to_total_energy(hf_electronic),
        exact_electronic_energy_hartree=exact_electronic,
        exact_total_energy_hartree=electronic_to_total_energy(exact_electronic),
        nuclear_repulsion_energy_hartree=NUCLEAR_REPULSION_ENERGY_HARTREE,
        hf_error_mhartree=abs(hf_electronic - exact_electronic) * 1000.0,
    )


def run_baseline() -> float:
    """Return the exact electronic ground-state energy for compatibility."""
    return compute_reference().exact_electronic_energy_hartree


def get_exact_energy() -> float:
    """Return the exact electronic ground-state energy."""
    return run_baseline()


def main() -> None:
    reference = compute_reference()

    print("=" * 72)
    print("H2 STO-3G at 0.735 angstrom -- classical reference")
    print("=" * 72)
    print(f"  HF bitstring             : |{HF_BITSTRING}> (Cqlib |q1 q0>)")
    print(f"  HF electronic energy     : {reference.hf_electronic_energy_hartree:.12f} Ha")
    print(f"  Exact electronic energy  : {reference.exact_electronic_energy_hartree:.12f} Ha")
    print(f"  Nuclear repulsion        : {reference.nuclear_repulsion_energy_hartree:.12f} Ha")
    print(f"  HF total energy          : {reference.hf_total_energy_hartree:.12f} Ha")
    print(f"  Exact total energy       : {reference.exact_total_energy_hartree:.12f} Ha")
    print(f"  HF error                 : {reference.hf_error_mhartree:.6f} mHa")
    print("=" * 72)

    report = {
        "task": "vqe_h2_ground_state",
        "data": "H2 STO-3G at 0.735 angstrom; fixed two-qubit Hamiltonian",
        "primary_metric": "absolute_energy_error_mhartree",
        "higher_is_better": False,
        "value": round(reference.hf_error_mhartree, 9),
        "energy_hartree": reference.hf_total_energy_hartree,
        "exact_energy_hartree": reference.exact_total_energy_hartree,
        **asdict(reference),
        "hf_bitstring": HF_BITSTRING,
        "bitstring_convention": "|q1 q0>; qubit 0 is the least-significant bit",
        "command": "python -m algorithms.baseline",
        "artifact_paths": ["baseline_report.json"],
        "backend": "numpy.linalg.eigvalsh exact diagonalization",
        "qubits": N_QUBITS,
        "bond_distance_angstrom": BOND_DISTANCE_ANGSTROM,
        "limitations": [
            "The two-qubit Hamiltonian is a fixed, precomputed minimal-basis instance",
            "Exact diagonalization is practical for this demonstration-scale system",
            "The result is a simulator/reference check, not evidence of quantum advantage",
        ],
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Baseline report saved to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
