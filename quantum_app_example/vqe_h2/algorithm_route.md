# Algorithm Route: H2 VQE

## Hamiltonian and Energy Convention

The application uses a fixed two-qubit electronic Hamiltonian at 0.735 angstrom:

```text
H_e = -1.052373245773 I
    + 0.397937424843 Z0 - 0.397937424843 Z1
    - 0.011280104256 Z0 Z1 + 0.180931199784 X0 X1.
```

The exact electronic energy is `-1.857275030202 Ha`. Adding the nuclear-repulsion constant `0.719968994449 Ha` gives the exact molecular total energy `-1.137306035753 Ha`.

## Reference and Ansatz

The HF determinant is `|01>` in Cqlib's `|q1 q0>` convention and has total energy `-1.116998996754 Ha`. The circuit

```text
X(q0) -> RY(q1, theta) -> CX(q1, q0)
```

spans `cos(theta/2)|01> + sin(theta/2)|10>`, the two-dimensional sector coupled by this reduced Hamiltonian. COBYLA minimizes the exact statevector expectation value from a seed-controlled random initial angle.

## Measurement and Validation

Each Pauli term is measured after the required basis rotation and combined with its coefficient. An independent dense-matrix implementation verifies the same expectation values at multiple angles. Exact diagonalization provides the oracle; HF provides the classical baseline.
