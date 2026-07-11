"""Cqlib VQE for the fixed two-qubit H2 electronic Hamiltonian."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

from cqlib import Circuit, Parameter
from cqlib.simulator import StatevectorSimulator

from algorithms.baseline import compute_reference
from algorithms.hamiltonian import (
    BOND_DISTANCE_ANGSTROM,
    H2_HAMILTONIAN,
    N_QUBITS,
    electronic_to_total_energy,
)

PARAMETER_NAME = "theta"
OPTIMIZER = "COBYLA"
MAXITER = 200
TOL = 1e-10
REPORT_SEEDS = [42, 123, 456]

BASE_DIR = Path(__file__).resolve().parent.parent
QUANTUM_REPORT_PATH = BASE_DIR / "quantum_report.json"
CONVERGENCE_PATH = BASE_DIR / "convergence.json"


@dataclass(frozen=True)
class VQEResult:
    seed: int
    initial_theta: float
    optimal_theta: float
    electronic_energy_hartree: float
    total_energy_hartree: float
    energy_error_mhartree: float
    correlation_energy_recovered_percent: float
    evaluations: int
    optimizer_success: bool
    optimizer_message: str
    convergence: list[tuple[int, float]]

    @property
    def optimal_parameters(self) -> dict[str, float]:
        return {PARAMETER_NAME: self.optimal_theta}


def build_ansatz() -> tuple[Circuit, list[str]]:
    """Prepare ``cos(theta/2)|01> + sin(theta/2)|10>``.

    The fixed X gate prepares the Hartree-Fock determinant ``|01>`` in Cqlib's
    ``|q1 q0>`` convention.  The RY-CX pair spans the two-dimensional sector
    coupled by the reduced H2 Hamiltonian with one variational parameter.
    """
    circuit = Circuit(N_QUBITS, parameters=[PARAMETER_NAME])
    circuit.x(0)
    circuit.ry(1, Parameter(PARAMETER_NAME))
    circuit.cx(1, 0)
    return circuit, [PARAMETER_NAME]


def add_basis_rotations(circuit: Circuit, pauli_list: list[tuple[int, str]]) -> Circuit:
    """Rotate a Pauli measurement into the computational basis."""
    rotated = circuit.copy()
    for qubit, operator in pauli_list:
        if operator == "X":
            rotated.h(qubit)
        elif operator == "Y":
            rotated.rx(qubit, np.pi / 2)
        elif operator != "Z":
            raise ValueError(f"unsupported Pauli operator: {operator}")
    return rotated


def compute_pauli_expectation(
    bound_circuit: Circuit,
    pauli_list: list[tuple[int, str]],
) -> float:
    """Evaluate a Pauli expectation exactly with Cqlib's statevector backend."""
    if not pauli_list:
        return 1.0

    rotated = add_basis_rotations(bound_circuit, pauli_list)
    rotated.measure_all()
    probabilities = StatevectorSimulator(circuit=rotated).measure()

    expectation = 0.0
    for bitstring, probability in probabilities.items():
        parity = sum(int(bitstring[-1 - qubit]) for qubit, _ in pauli_list)
        expectation += ((-1) ** parity) * float(probability)
    return float(expectation)


def compute_energy(
    circuit: Circuit,
    parameter_values: dict[str, float],
    hamiltonian=H2_HAMILTONIAN,
) -> float:
    """Evaluate the electronic energy for a bound variational circuit."""
    bound = circuit.assign_parameters(parameter_values)
    return float(
        sum(
            coefficient * compute_pauli_expectation(bound, pauli_list)
            for coefficient, pauli_list in hamiltonian
        )
    )


def run_vqe(seed: int = 42) -> VQEResult:
    """Run one reproducible one-parameter VQE optimization."""
    if not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be a non-negative integer")

    reference = compute_reference()
    circuit, _ = build_ansatz()
    rng = np.random.default_rng(seed)
    initial_theta = float(rng.uniform(-0.25, 0.25))
    convergence: list[tuple[int, float]] = []

    def cost_fn(parameters: np.ndarray) -> float:
        energy = compute_energy(circuit, {PARAMETER_NAME: float(parameters[0])})
        convergence.append((len(convergence), energy))
        return energy

    optimizer_result = minimize(
        cost_fn,
        np.array([initial_theta], dtype=float),
        method=OPTIMIZER,
        options={"maxiter": MAXITER, "tol": TOL},
    )

    optimal_theta = float(optimizer_result.x[0])
    electronic_energy = compute_energy(circuit, {PARAMETER_NAME: optimal_theta})
    error_mhartree = abs(electronic_energy - reference.exact_electronic_energy_hartree) * 1000.0
    correlation_energy = (
        reference.hf_electronic_energy_hartree
        - reference.exact_electronic_energy_hartree
    )
    recovered = (
        reference.hf_electronic_energy_hartree - electronic_energy
    ) / correlation_energy * 100.0

    return VQEResult(
        seed=seed,
        initial_theta=initial_theta,
        optimal_theta=optimal_theta,
        electronic_energy_hartree=electronic_energy,
        total_energy_hartree=electronic_to_total_energy(electronic_energy),
        energy_error_mhartree=error_mhartree,
        correlation_energy_recovered_percent=float(np.clip(recovered, 0.0, 100.0)),
        evaluations=int(optimizer_result.nfev),
        optimizer_success=bool(optimizer_result.success),
        optimizer_message=str(optimizer_result.message),
        convergence=convergence,
    )


def main() -> None:
    reference = compute_reference()
    results = [run_vqe(seed) for seed in REPORT_SEEDS]

    print("=" * 72)
    print("H2 STO-3G at 0.735 angstrom -- Cqlib VQE")
    print("=" * 72)
    print(f"  Exact electronic energy  : {reference.exact_electronic_energy_hartree:.12f} Ha")
    print(f"  Exact total energy       : {reference.exact_total_energy_hartree:.12f} Ha")
    print("  Ansatz                   : one-parameter |01>/<10> subspace")
    print(f"  Optimizer                : {OPTIMIZER} (maxiter={MAXITER}, tol={TOL})")
    print("-" * 72)
    for result in results:
        print(
            f"  Seed {result.seed:>3d}: E_total={result.total_energy_hartree:.12f} Ha, "
            f"error={result.energy_error_mhartree:.6e} mHa, evals={result.evaluations}"
        )

    electronic_energies = np.array([result.electronic_energy_hartree for result in results])
    total_energies = np.array([result.total_energy_hartree for result in results])
    errors = np.array([result.energy_error_mhartree for result in results])
    recovered = np.array([result.correlation_energy_recovered_percent for result in results])
    circuit, _ = build_ansatz()

    print("-" * 72)
    print(f"  Mean total energy        : {np.mean(total_energies):.12f} Ha")
    print(f"  Mean absolute error      : {np.mean(errors):.6e} mHa")
    print(f"  Max absolute error       : {np.max(errors):.6e} mHa")
    print(f"  Circuit depth            : {circuit.depth()}")
    print("=" * 72)

    per_seed = [
        {
            "seed": result.seed,
            "initial_theta": result.initial_theta,
            "optimal_theta": result.optimal_theta,
            "electronic_energy_hartree": result.electronic_energy_hartree,
            "total_energy_hartree": result.total_energy_hartree,
            "energy_error_mhartree": result.energy_error_mhartree,
            "correlation_energy_recovered_percent": result.correlation_energy_recovered_percent,
            "evaluations": result.evaluations,
            "optimizer_success": result.optimizer_success,
        }
        for result in results
    ]
    quantum_report = {
        "task": "vqe_h2_ground_state",
        "data": "H2 STO-3G at 0.735 angstrom; fixed two-qubit Hamiltonian",
        "primary_metric": "absolute_energy_error_mhartree",
        "higher_is_better": False,
        "value": round(float(np.mean(errors)), 12),
        "energy_hartree": float(np.mean(total_energies)),
        "exact_energy_hartree": reference.exact_total_energy_hartree,
        "electronic_energy_hartree": float(np.mean(electronic_energies)),
        "total_energy_hartree": float(np.mean(total_energies)),
        "exact_electronic_energy_hartree": reference.exact_electronic_energy_hartree,
        "exact_total_energy_hartree": reference.exact_total_energy_hartree,
        "nuclear_repulsion_energy_hartree": reference.nuclear_repulsion_energy_hartree,
        "energy_error_mhartree": float(np.mean(errors)),
        "max_energy_error_mhartree": float(np.max(errors)),
        "energy_error_std_mhartree": float(np.std(errors)),
        "correlation_energy_recovered_percent": float(np.mean(recovered)),
        "seeds": REPORT_SEEDS,
        "per_seed_results": per_seed,
        "command": "python -m algorithms.vqe",
        "artifact_paths": ["quantum_report.json", "convergence.json"],
        "backend": "cqlib.StatevectorSimulator",
        "qubits": N_QUBITS,
        "circuit_depth": circuit.depth(),
        "parameters": 1,
        "ansatz": "particle_conserving_h2_subspace",
        "optimizer": OPTIMIZER,
        "bond_distance_angstrom": BOND_DISTANCE_ANGSTROM,
        "limitations": [
            "Exact statevector simulation; no sampling or device noise",
            "Fixed H2/STO-3G two-qubit instance",
            "The example validates the TYQA workflow and does not establish quantum advantage",
        ],
    }
    QUANTUM_REPORT_PATH.write_text(
        json.dumps(quantum_report, indent=2), encoding="utf-8"
    )

    convergence_report = {
        str(result.seed): [
            {
                "evaluation": evaluation,
                "electronic_energy_hartree": electronic_energy,
                "total_energy_hartree": electronic_to_total_energy(electronic_energy),
            }
            for evaluation, electronic_energy in result.convergence
        ]
        for result in results
    }
    CONVERGENCE_PATH.write_text(
        json.dumps(convergence_report, indent=2), encoding="utf-8"
    )
    print(f"Quantum report saved to: {QUANTUM_REPORT_PATH}")
    print(f"Convergence data saved to: {CONVERGENCE_PATH}")


if __name__ == "__main__":
    main()
