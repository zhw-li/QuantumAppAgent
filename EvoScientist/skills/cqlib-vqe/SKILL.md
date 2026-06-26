---
name: cqlib-vqe
description: "Guides Cqlib VQE implementation for molecular energy and Pauli Hamiltonian applications. Use when the task involves VQE, variational eigensolvers, ground-state energy, molecular energy, Pauli Hamiltonian expectation, hardware-efficient ansatz, UCC-inspired ansatz, basis rotation measurements, optimizer loops, or simulator/cloud evidence for VQE circuits. Trigger after cqlib-sdk selects the VQE route. Do NOT use for QUBO/QAOA optimization, VQC/QML models, hybrid neural architectures, qccp packaging, or final delivery readiness decisions."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: EvoScientist
  version: '1.0.0'
  tags: [quantum, cqlib, vqe, chemistry, hamiltonian]
---

# cqlib VQE

Use after `cqlib-sdk`. VQE work must separate Hamiltonian definition, ansatz, measurement strategy, optimizer, backend, and validation.

## When to Use

- User needs molecular ground-state energy, Pauli Hamiltonian expectation, or variational eigensolver implementation.
- User needs ansatz, measurement basis rotation, optimizer, backend, and reference-value validation separated.
- User needs VQE evidence for `quantum_report.json` inside `experiment-pipeline`.

## When NOT to Use

- **QUBO/Ising/combinatorial optimization** -> use `cqlib-qaoa`.
- **Classification, regression, or quantum feature maps** -> use `cqlib-qml`.
- **Hybrid deep learning systems** -> use `cqlib-hybrid`.
- **UI/API/deployment packaging or final verification** -> use `qccp-frontend`, `qccp-service`, or `experiment-pipeline`.

## Workflow

1. Define Hamiltonian as explicit Pauli terms: `(coefficient, [(qubit, "X"|"Y"|"Z")])`.
2. Choose ansatz: hardware-efficient for PoC, chemistry-inspired only when the mapping is known.
3. Declare all cqlib parameters before adding parameterized gates.
4. Compute expectation term by term, or group commuting terms when the implementation supports it.
5. Optimize with deterministic initial values or recorded random seed.
6. Validate against a small exact diagonalization or known reference value when possible.

## Hamiltonian representation

Prefer parsed terms over compact strings in production code.

```python
H2_MINIMAL = [
    (-1.052373245772859, []),
    (0.39793742484318045, [(0, "Z")]),
    (-0.39793742484318045, [(1, "Z")]),
    (-0.01128010425623538, [(0, "Z"), (1, "Z")]),
    (0.18093119978423156, [(0, "X"), (1, "X")]),
]
```

If the input uses strings such as `Z0 Z1`, parse and validate them before execution.

## Ansatz pattern

```python
from cqlib import Circuit, Parameter

def hardware_efficient_ansatz(n_qubits, layers):
    names = []
    for layer in range(layers):
        for q in range(n_qubits):
            names.extend([f"ry_{layer}_{q}", f"rz_{layer}_{q}"])

    circuit = Circuit(n_qubits, parameters=names)
    for layer in range(layers):
        for q in range(n_qubits):
            circuit.ry(q, Parameter(f"ry_{layer}_{q}"))
            circuit.rz(q, Parameter(f"rz_{layer}_{q}"))
        for q in range(n_qubits - 1):
            circuit.cx(q, q + 1)
    return circuit, names
```

For Hartree-Fock style initialization, document the orbital-to-qubit convention and use `x(i)` only for occupied spin orbitals under that convention.

## Pauli expectation

```python
import numpy as np
from cqlib.simulator import StatevectorSimulator

def copy_with_basis_rotation(circuit, pauli_ops):
    measured = circuit.copy()
    for qubit, op in pauli_ops:
        if op == "X":
            measured.h(qubit)
        elif op == "Y":
            measured.rx(qubit, np.pi / 2)
        elif op != "Z":
            raise ValueError(f"Unsupported Pauli operator: {op}")
    measured.measure_all()
    return measured

def pauli_expectation(circuit, pauli_ops):
    measured = copy_with_basis_rotation(circuit, pauli_ops)
    probs = StatevectorSimulator(circuit=measured).measure()
    value = 0.0
    for bits, prob in probs.items():
        parity = sum(int(bits[-1 - qubit]) for qubit, _ in pauli_ops)
        value += ((-1) ** parity) * prob
    return value

def energy(params, circuit, param_names, hamiltonian):
    bound = circuit.assign_parameters(dict(zip(param_names, params)))
    return sum(coeff * pauli_expectation(bound, ops) for coeff, ops in hamiltonian)
```

Check the Y-basis convention against a known single-qubit case if changing rotations. Do not change basis rotations casually.

## Validation checklist

- [ ] Hamiltonian coefficients, units, and qubit mapping are stated.
- [ ] Ansatz parameter count equals optimizer vector length.
- [ ] Basis rotations are covered by simple known-state tests.
- [ ] Measurement bit order is explicit.
- [ ] Optimizer method, tolerance, max iterations, and seed are recorded.
- [ ] Result reports final energy, parameter vector, iterations, and convergence trace.
- [ ] Hardware execution, if any, uses shot-based estimates and never assumes exact simulator agreement.

## Application handoff

For application delivery, write the VQE result into `quantum_report.json` using the `cqlib-sdk` artifact contract. Include Hamiltonian source, units, qubit mapping, ansatz depth, measurement strategy, optimizer settings, final energy, convergence trace path, backend, shots/seed, command, and limitations.

Do not decide delivery readiness from this skill. Hand the reports to `experiment-pipeline` for baseline comparison and staged verification.
