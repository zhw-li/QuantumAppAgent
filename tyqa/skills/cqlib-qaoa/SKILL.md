---
name: cqlib-qaoa
description: "Guides Cqlib QAOA implementation for combinatorial optimization applications. Use when the task involves QAOA, QUBO, Ising, MaxCut, portfolio optimization, scheduling, unit commitment, constraint penalties, variational optimization, top-k feasible solution search, or simulator/cloud execution evidence for optimization circuits. Trigger after cqlib-sdk selects the QAOA route. Do NOT use for VQE chemistry, QML classification/regression, hybrid neural models, qccp packaging, or final delivery readiness decisions."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: TYQA
  version: '1.0.0'
  tags: [quantum, cqlib, qaoa, optimization, application]
---

# cqlib QAOA

Use after `cqlib-sdk`. QAOA work must make the business objective, binary encoding, constraints, penalty weights, circuit, backend, and decoder explicit.

## When to Use

- User needs a QAOA/QUBO/Ising solution for optimization, scheduling, portfolio, unit commitment, MaxCut, or similar binary decision tasks.
- User needs feasibility checks, bitstring decoding, penalty design, or small-instance brute-force comparison.
- User needs QAOA evidence for `quantum_report.json` inside `application-pipeline`.

## When NOT to Use

- **Hamiltonian ground-state energy or molecular simulation** -> use `cqlib-vqe`.
- **Quantum classifier/regressor or feature map work** -> use `cqlib-qml`.
- **Hybrid deep learning architecture** -> use `cqlib-hybrid`.
- **UI/API/deployment packaging or final verification** -> use `qccp-frontend`, `qccp-service`, or `application-pipeline`.

## Workflow

1. Define binary variables and objective in classical form.
2. Convert to QUBO or Ising with documented penalty terms.
3. Normalize coefficients when needed so angles remain numerically stable.
4. Build QAOA ansatz with declared cqlib parameters.
5. Optimize expectation on a simulator first.
6. Decode top-k sampled bitstrings and validate feasibility against the original constraints.
7. Compare against brute force or a classical baseline for small cases.

## Modeling rules

- Do not claim QAOA quality before checking feasible decoded solutions.
- Highest probability bitstring is not necessarily the best feasible solution.
- Keep qubit index to business variable mapping in a named structure.
- State the bitstring convention. Existing cqlib examples typically read qubit `i` from `bitstring[-1 - i]`.
- Penalty weights are part of the model. Record how they were chosen.

## Circuit pattern

cqlib has confirmed `cx` and `rz`; use CNOT-RZ-CNOT for ZZ evolution unless the active version has a native RZZ gate.

```python
import numpy as np
from cqlib import Circuit, Parameter

def add_zz(circuit, qi, qj, coeff, gamma):
    circuit.cx(qi, qj)
    circuit.rz(qj, 2.0 * coeff * gamma)
    circuit.cx(qi, qj)

def add_z(circuit, qi, coeff, gamma):
    circuit.rz(qi, 2.0 * coeff * gamma)

def build_qaoa(n_qubits, linear, quadratic, depth):
    names = [name for layer in range(depth) for name in (f"gamma_{layer}", f"beta_{layer}")]
    circuit = Circuit(n_qubits, parameters=names)

    for q in range(n_qubits):
        circuit.h(q)

    for layer in range(depth):
        gamma = Parameter(f"gamma_{layer}")
        beta = Parameter(f"beta_{layer}")

        for qi, coeff in linear.items():
            add_z(circuit, qi, coeff, gamma)
        for (qi, qj), coeff in quadratic.items():
            add_zz(circuit, qi, qj, coeff, gamma)
        for q in range(n_qubits):
            circuit.rx(q, 2.0 * beta)

    circuit.measure_all()
    return circuit, names
```

## Expectation and decoding

```python
from cqlib.simulator import StatevectorSimulator

def bitstring_to_spin(bitstring, n_qubits):
    return [1 - 2 * int(bitstring[-1 - i]) for i in range(n_qubits)]

def bitstring_to_binary(bitstring, n_qubits):
    return [int(bitstring[-1 - i]) for i in range(n_qubits)]

def qubo_value(x, linear, quadratic, offset=0.0):
    value = offset + sum(coeff * x[i] for i, coeff in linear.items())
    value += sum(coeff * x[i] * x[j] for (i, j), coeff in quadratic.items())
    return value

def expectation(params, circuit, param_names, n_qubits, linear, quadratic, offset=0.0):
    bound = circuit.assign_parameters(dict(zip(param_names, params)))
    probs = StatevectorSimulator(circuit=bound).measure()
    return sum(
        prob * qubo_value(bitstring_to_binary(bits, n_qubits), linear, quadratic, offset)
        for bits, prob in probs.items()
    )
```

For constrained problems, write a separate `is_feasible(x)` and `repair_or_score(x)` function. Do not hide penalties inside decoding.

## Validation checklist

- [ ] Variable-to-qubit map is documented.
- [ ] QUBO/Ising terms match the original objective and constraints.
- [ ] Penalty weights and coefficient normalization are recorded.
- [ ] `Circuit(..., parameters=...)` declares all QAOA parameters.
- [ ] Measurement mapping uses the chosen bit order consistently.
- [ ] Small instance is checked against brute force or a known optimum.
- [ ] Optimizer seed/restarts/max iterations are recorded.
- [ ] If cloud execution is proposed, hardware cost/quota and credentials are explicitly authorized first.

## Application handoff

For application delivery, write the QAOA result into `quantum_report.json` using the `cqlib-sdk` artifact contract. Include objective direction, decoded best feasible solution, feasibility rate, variable-to-qubit map, bitstring convention, optimizer settings, backend, shots/seed, command, and artifact paths.

Do not decide delivery readiness from this skill. Hand the reports to `application-pipeline` for baseline comparison and staged verification.
