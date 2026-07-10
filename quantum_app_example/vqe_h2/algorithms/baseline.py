"""Classical baseline for H2 ground-state energy.

Computes the Hartree-Fock (mean-field) energy as the classical baseline,
and the exact ground-state energy via full diagonalization for reference.
The VQE quantum algorithm should improve on the HF energy by capturing
electron correlation.
"""

import json
import os

import numpy as np

from algorithms.hamiltonian import H2_HAMILTONIAN, hamiltonian_to_matrix

N_QUBITS = 2
REPORT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "baseline_report.json")


def compute_hf_energy():
    """Compute the Hartree-Fock (mean-field) energy.

    The HF state is |00⟩ (both electrons in the lowest orbital).
    Energy = <00|H|00>, which omits the X0X1 correlation term.
    """
    # For |00⟩, Z eigenvalues are both +1, X0X1 gives 0
    hf_energy = 0.0
    for coeff, pauli_list in H2_HAMILTONIAN:
        if not pauli_list:
            hf_energy += coeff
        else:
            # In |00⟩, Z operators give +1, X operators give 0
            all_z = all(op == "Z" for _, op in pauli_list)
            if all_z:
                hf_energy += coeff  # all +1 eigenvalues
            # X or Y terms have zero expectation in |00⟩
    return hf_energy


def run_baseline():
    """Run exact diagonalization and return the ground-state energy.

    Also computes the HF energy as the classical baseline metric.
    """
    H = hamiltonian_to_matrix(H2_HAMILTONIAN, N_QUBITS)
    eigenvalues = np.linalg.eigh(H)[0]
    exact_energy = float(eigenvalues[0])
    return exact_energy


def get_exact_energy():
    """Return the exact ground-state energy for reference."""
    return run_baseline()


def main():
    exact_energy = run_baseline()
    hf_energy = compute_hf_energy()
    hf_error_mhartree = (hf_energy - exact_energy) * 1000

    print("=" * 60)
    print("H2 Ground-State Energy — Classical Baseline")
    print("=" * 60)
    print(f"  Molecule           : H2 (STO-3G, bond=0.735 Å)")
    print(f"  Qubits             : {N_QUBITS}")
    print(f"  HF energy          : {hf_energy:.10f} Hartree")
    print(f"  Exact energy       : {exact_energy:.10f} Hartree")
    print(f"  HF error           : {hf_error_mhartree:.4f} mHartree")
    print(f"  Backend            : numpy.linalg.eigh (exact) + HF (classical)")
    print("=" * 60)

    # The baseline metric is the HF energy error (classical mean-field).
    # VQE should beat this by capturing correlation.
    report = {
        "task": "vqe_molecular_energy",
        "data": "H2 STO-3G at 0.735 Å",
        "primary_metric": "energy_error",
        "higher_is_better": False,
        "value": round(hf_error_mhartree, 6),
        "energy_hartree": hf_energy,
        "exact_energy_hartree": exact_energy,
        "hf_energy_hartree": hf_energy,
        "hf_error_mhartree": round(hf_error_mhartree, 6),
        "command": "python -m algorithms.baseline",
        "artifact_paths": ["baseline_report.json"],
        "backend": "Hartree-Fock (numpy.linalg.eigh for exact reference)",
        "qubits": N_QUBITS,
        "limitations": [
            "Hartree-Fock is a mean-field approximation that ignores electron correlation",
            "Exact diagonalization is used only for reference, not as the baseline metric",
        ],
    }

    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nBaseline report saved to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
