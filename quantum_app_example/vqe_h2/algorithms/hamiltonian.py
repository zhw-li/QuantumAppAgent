"""Two-qubit electronic Hamiltonian for H2 in the STO-3G basis.

The coefficients match the public Qiskit Algorithms H2 example at an
interatomic distance of 0.735 angstrom.  The qubit Hamiltonian contains only
the electronic contribution.  The nuclear-repulsion constant must be added to
obtain the molecular total energy.

Bitstrings and dense matrices use the Cqlib convention ``|q1 q0>``: qubit 0 is
the least-significant (rightmost) bit.
"""

from __future__ import annotations

import numpy as np

BOND_DISTANCE_ANGSTROM = 0.735
N_QUBITS = 2
HF_BITSTRING = "01"
NUCLEAR_REPULSION_ENERGY_HARTREE = 0.7199689944489797

# Public two-qubit H2 electronic Hamiltonian at 0.735 angstrom.
# Each term is (coefficient, [(qubit_index, Pauli), ...]).
H2_HAMILTONIAN = [
    (-1.052373245772859, []),
    (0.39793742484318045, [(0, "Z")]),
    (-0.39793742484318045, [(1, "Z")]),
    (-0.01128010425623538, [(0, "Z"), (1, "Z")]),
    (0.18093119978423156, [(0, "X"), (1, "X")]),
]

_I = np.array([[1, 0], [0, 1]], dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_PAULI_MAP = {"I": _I, "X": _X, "Y": _Y, "Z": _Z}


def hamiltonian_to_matrix(hamiltonian=H2_HAMILTONIAN, n_qubits=N_QUBITS):
    """Return a dense Hamiltonian matrix in the ``|q[n-1] ... q0>`` basis."""
    if not isinstance(n_qubits, int) or n_qubits <= 0:
        raise ValueError("n_qubits must be a positive integer")

    dimension = 2**n_qubits
    matrix = np.zeros((dimension, dimension), dtype=complex)

    for coefficient, pauli_list in hamiltonian:
        operators = [_I for _ in range(n_qubits)]
        seen_qubits: set[int] = set()
        for qubit, pauli in pauli_list:
            if qubit < 0 or qubit >= n_qubits:
                raise ValueError(f"qubit index {qubit} is outside 0..{n_qubits - 1}")
            if qubit in seen_qubits:
                raise ValueError(f"qubit {qubit} appears more than once in a Pauli term")
            if pauli not in _PAULI_MAP:
                raise ValueError(f"unsupported Pauli operator: {pauli}")
            seen_qubits.add(qubit)
            operators[qubit] = _PAULI_MAP[pauli]

        # Qubit 0 is the least-significant bit, so it is the rightmost factor.
        term = operators[-1]
        for qubit in range(n_qubits - 2, -1, -1):
            term = np.kron(term, operators[qubit])
        matrix += float(coefficient) * term

    return matrix


def electronic_to_total_energy(electronic_energy_hartree: float) -> float:
    """Add the fixed nuclear-repulsion energy for the 0.735 angstrom geometry."""
    return float(electronic_energy_hartree + NUCLEAR_REPULSION_ENERGY_HARTREE)


def basis_state(bitstring: str) -> np.ndarray:
    """Return a computational-basis statevector for a ``|q1 q0>`` bitstring."""
    if len(bitstring) != N_QUBITS or set(bitstring) - {"0", "1"}:
        raise ValueError(f"bitstring must contain exactly {N_QUBITS} binary digits")
    state = np.zeros(2**N_QUBITS, dtype=complex)
    state[int(bitstring, 2)] = 1.0
    return state
