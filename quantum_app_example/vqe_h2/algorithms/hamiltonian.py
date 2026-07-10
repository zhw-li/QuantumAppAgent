"""H2 molecule Hamiltonian in the STO-3G minimal basis at equilibrium bond distance.

Uses Bravyi-Kitaev parity mapping to reduce to 2 qubits.
Bond distance: 0.735 Å
"""

import numpy as np

# H2 STO-3G Hamiltonian at 0.735 Å, Bravyi-Kitaev parity mapping, 2 qubits
# Each term: (coefficient, [(qubit_index, pauli_operator), ...])
# Identity term has empty pauli list.
H2_HAMILTONIAN = [
    (-1.052373245772859, []),                            # identity
    (0.39793742484318045, [(0, "Z")]),                   # Z0
    (-0.39793742484318045, [(1, "Z")]),                  # Z1
    (-0.01128010425623538, [(0, "Z"), (1, "Z")]),        # Z0 Z1
    (0.18093119978423156, [(0, "X"), (1, "X")]),         # X0 X1
]

# Pauli matrices
_I = np.array([[1, 0], [0, 1]], dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)

_PAULI_MAP = {"I": _I, "X": _X, "Y": _Y, "Z": _Z}


def hamiltonian_to_matrix(hamiltonian, n_qubits):
    """Convert a Pauli Hamiltonian to a dense 2^n_qubits x 2^n_qubits matrix.

    Args:
        hamiltonian: List of (coefficient, [(qubit, pauli_op), ...]) tuples.
        n_qubits: Number of qubits.

    Returns:
        numpy.ndarray: The Hamiltonian as a dense matrix.
    """
    dim = 2 ** n_qubits
    H = np.zeros((dim, dim), dtype=complex)

    for coeff, pauli_list in hamiltonian:
        if not pauli_list:
            # Identity term
            term = coeff * np.eye(dim, dtype=complex)
        else:
            # Build tensor product of Pauli operators
            ops = [_I] * n_qubits
            for qubit, op in pauli_list:
                ops[qubit] = _PAULI_MAP[op]
            term_matrix = ops[0]
            for i in range(1, n_qubits):
                term_matrix = np.kron(term_matrix, ops[i])
            term = coeff * term_matrix
        H += term

    return H
