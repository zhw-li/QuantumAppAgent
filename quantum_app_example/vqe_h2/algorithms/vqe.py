"""VQE algorithm for H2 ground-state energy using cqlib.

Implements a hardware-efficient ansatz with RY-RZ-CX layers,
Pauli expectation estimation via basis rotation and measurement,
and COBYLA classical optimization.
"""

import json
import os

import numpy as np
from scipy.optimize import minimize

from cqlib import Circuit, Parameter
from cqlib.simulator import StatevectorSimulator

from algorithms.hamiltonian import H2_HAMILTONIAN
from algorithms.baseline import get_exact_energy

N_QUBITS = 2
DEFAULT_LAYERS = 2
OPTIMIZER = "COBYLA"
MAXITER = 500
TOL = 1e-6
SEEDS = [42, 123, 456]

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
QUANTUM_REPORT_PATH = os.path.join(BASE_DIR, "quantum_report.json")
CONVERGENCE_PATH = os.path.join(BASE_DIR, "convergence.json")


# ---------------------------------------------------------------------------
# Ansatz
# ---------------------------------------------------------------------------

def build_ansatz(n_qubits=N_QUBITS, layers=DEFAULT_LAYERS):
    """Build a hardware-efficient ansatz: RY-RZ-CX per layer.

    Returns:
        circuit: cqlib Circuit with parameterized gates.
        param_names: list of parameter name strings in order.
    """
    param_names = []
    for layer in range(layers):
        for q in range(n_qubits):
            param_names.append(f"ry_l{layer}_q{q}")
        for q in range(n_qubits):
            param_names.append(f"rz_l{layer}_q{q}")

    circuit = Circuit(n_qubits, parameters=param_names)

    idx = 0
    for layer in range(layers):
        # RY on each qubit
        for q in range(n_qubits):
            circuit.ry(q, Parameter(param_names[idx]))
            idx += 1
        # RZ on each qubit
        for q in range(n_qubits):
            circuit.rz(q, Parameter(param_names[idx]))
            idx += 1
        # CX ladder
        for q in range(n_qubits - 1):
            circuit.cx(q, q + 1)

    return circuit, param_names


# ---------------------------------------------------------------------------
# Measurement helpers
# ---------------------------------------------------------------------------

def add_basis_rotations(circuit, pauli_list):
    """Add basis rotation gates before measurement for a Pauli term.

    X -> H, Y -> RX(π/2), Z -> no rotation.
    """
    circ = circuit.copy()
    for qubit, op in pauli_list:
        if op == "X":
            circ.h(qubit)
        elif op == "Y":
            circ.rx(qubit, np.pi / 2)
        # Z needs no rotation
    return circ


def compute_pauli_expectation(bound_circuit, pauli_list):
    """Compute <ψ|P|ψ> for a Pauli string P via sampling.

    Uses basis rotation + measure_all() with StatevectorSimulator.
    Bitstring convention: bits[-1 - qubit_index] maps qubit_index.
    """
    if not pauli_list:
        # Identity term
        return 1.0

    rotated = add_basis_rotations(bound_circuit, pauli_list)
    rotated.measure_all()

    sim = StatevectorSimulator(circuit=rotated)
    probs = sim.measure()

    expectation = 0.0
    for bitstring, prob in probs.items():
        # Compute parity of the measured bits at the pauli qubit positions
        parity = sum(int(bitstring[-1 - q]) for q, _ in pauli_list)
        expectation += ((-1) ** parity) * prob

    return expectation


# ---------------------------------------------------------------------------
# Energy evaluation
# ---------------------------------------------------------------------------

def compute_energy(circuit, param_dict, hamiltonian):
    """Compute VQE energy = Σ coeff * <P> for all Hamiltonian terms."""
    bound = circuit.assign_parameters(param_dict)
    energy = 0.0
    for coeff, pauli_list in hamiltonian:
        energy += coeff * compute_pauli_expectation(bound, pauli_list)
    return energy


# ---------------------------------------------------------------------------
# Optimization
# ---------------------------------------------------------------------------

def run_vqe(seed, layers=DEFAULT_LAYERS):
    """Run a single VQE optimization with the given random seed.

    Returns:
        result_energy: optimized energy (float)
        convergence: list of (iteration, energy) pairs
    """
    np.random.seed(seed)
    circuit, param_names = build_ansatz(layers=layers)
    n_params = len(param_names)
    initial_params = np.zeros(n_params)

    convergence = []
    iteration = [0]

    def cost_fn(params):
        param_dict = dict(zip(param_names, params))
        e = compute_energy(circuit, param_dict, H2_HAMILTONIAN)
        convergence.append((iteration[0], float(e)))
        iteration[0] += 1
        return e

    result = minimize(
        cost_fn,
        initial_params,
        method=OPTIMIZER,
        options={"maxiter": MAXITER, "tol": TOL},
    )

    # Final energy from the optimizer result
    final_params = result.x
    param_dict = dict(zip(param_names, final_params))
    final_energy = compute_energy(circuit, param_dict, H2_HAMILTONIAN)

    return float(final_energy), convergence


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    exact_energy = get_exact_energy()
    print("=" * 60)
    print("H2 Ground-State Energy — VQE Quantum Algorithm")
    print("=" * 60)
    print(f"  Exact energy  : {exact_energy:.10f} Hartree")
    print(f"  Ansatz        : hardware_efficient ({DEFAULT_LAYERS} layers)")
    print(f"  Optimizer     : {OPTIMIZER} (maxiter={MAXITER}, tol={TOL})")
    print(f"  Seeds         : {SEEDS}")
    print("-" * 60)

    energies = []
    all_convergence = {}

    for seed in SEEDS:
        energy, convergence = run_vqe(seed)
        energies.append(energy)
        all_convergence[str(seed)] = convergence
        error_mhartree = (energy - exact_energy) * 1000
        print(f"  Seed {seed:>3d}: energy = {energy:.10f} Ha, "
              f"error = {error_mhartree:.4f} mHa")

    mean_energy = float(np.mean(energies))
    std_energy = float(np.std(energies))
    mean_error = float((mean_energy - exact_energy) * 1000)
    std_error = float(np.std([(e - exact_energy) * 1000 for e in energies]))

    # Circuit info
    circuit, _ = build_ansatz()
    circuit_depth = circuit.depth()

    print("-" * 60)
    print(f"  Mean VQE energy : {mean_energy:.10f} Hartree")
    print(f"  Mean error      : {mean_error:.4f} mHartree")
    print(f"  Std error       : {std_error:.4f} mHartree")
    print(f"  Circuit depth   : {circuit_depth}")
    print("=" * 60)

    # Save quantum_report.json
    quantum_report = {
        "task": "vqe_molecular_energy",
        "data": "H2 STO-3G at 0.735 Å",
        "primary_metric": "energy_error",
        "higher_is_better": False,
        "value": round(mean_error, 6),
        "energy_hartree": round(mean_energy, 10),
        "exact_energy_hartree": round(exact_energy, 10),
        "energy_error_mhartree": round(mean_error, 6),
        "energy_error_std_mhartree": round(std_error, 6),
        "seeds": SEEDS,
        "command": "python -m algorithms.vqe",
        "artifact_paths": ["quantum_report.json", "convergence.json"],
        "backend": "cqlib.StatevectorSimulator",
        "qubits": N_QUBITS,
        "circuit_depth": circuit_depth,
        "ansatz": "hardware_efficient",
        "layers": DEFAULT_LAYERS,
        "optimizer": OPTIMIZER,
        "limitations": [
            "Simulator-only results",
            "H2 minimal basis only",
        ],
    }

    with open(QUANTUM_REPORT_PATH, "w") as f:
        json.dump(quantum_report, f, indent=2)
    print(f"\nQuantum report saved to: {QUANTUM_REPORT_PATH}")

    # Save convergence.json
    with open(CONVERGENCE_PATH, "w") as f:
        json.dump(all_convergence, f, indent=2)
    print(f"Convergence data saved to: {CONVERGENCE_PATH}")


if __name__ == "__main__":
    main()
