# Algorithm Route — VQE H2

## Encoding
Bravyi-Kitaev superfast parity mapping → 2 qubits for H2 in STO-3G minimal basis (frozen core, 2 electrons in 2 spin-orbitals).

## Hamiltonian
Pre-computed Pauli terms at equilibrium bond distance (0.735 Å):

```python
H2_HAMILTONIAN = [
    (-1.052373245772859, []),                           # identity
    (0.39793742484318045, [(0, "Z")]),                   # Z0
    (-0.39793742484318045, [(1, "Z")]),                  # Z1
    (-0.01128010425623538, [(0, "Z"), (1, "Z")]),       # Z0 Z1
    (0.18093119978423156, [(0, "X"), (1, "X")]),        # X0 X1
]
```

Reference exact ground-state energy: -1.137275 Hartree (at this Hamiltonian).

## Ansatz
Hardware-efficient ansatz: alternating RY-RZ layers with CNOT entanglement.

```python
# 2 qubits, 2 layers → 8 parameters
circuit.ry(q, Parameter(f"ry_{layer}_{q}"))
circuit.rz(q, Parameter(f"rz_{layer}_{q}"))
circuit.cx(q, q+1)
```

Hartree-Fock initialization: X gate on qubit 0 to prepare |01⟩ (occupied orbital).

## Optimizer
scipy.optimize.minimize with COBYLA method, maxiter=500, tol=1e-6.

## Measurement
Basis rotation per Pauli term → StatevectorSimulator.measure() → parity-based expectation.

## Backend
cqlib.StatevectorSimulator (simulator only).

## Result Schema
quantum_report.json: task, data, primary_metric, higher_is_better, value, command, artifact_paths, seed, backend, qubits, circuit_depth, limitations.
