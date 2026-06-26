---
name: cqlib-qml
description: "Guides Cqlib quantum machine learning implementation for application datasets. Use when the task involves VQC classifiers/regressors, angle/amplitude/basis encoding decisions, quantum probability or expectation layers, feature maps, trainable ansatz, quantum classification, quantum regression, or PyTorch integration boundaries. Trigger after cqlib-sdk selects the QML route. Do NOT use for QAOA/QUBO optimization, VQE Hamiltonians, large hybrid neural architectures better handled by cqlib-hybrid, qccp packaging, or final delivery readiness decisions."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: EvoScientist
  version: '1.0.0'
  tags: [quantum, cqlib, qml, vqc, application]
---

# cqlib QML

Use after `cqlib-sdk`. QML work must distinguish state preparation, encoding, ansatz, measurement, loss, optimizer, and backend.

## When to Use

- User needs a VQC classifier/regressor, quantum feature map, quantum probability/expectation layer, or QML baseline comparison.
- User needs encoding, ansatz, measurement output, loss, optimizer, and backend assumptions documented separately.
- User needs QML evidence for `quantum_report.json` inside `experiment-pipeline`.

## When NOT to Use

- **QAOA/QUBO/Ising optimization** -> use `cqlib-qaoa`.
- **VQE or Pauli Hamiltonian expectation** -> use `cqlib-vqe`.
- **Hybrid deep learning architecture with classical backbones** -> use `cqlib-hybrid`.
- **UI/API/deployment packaging or final verification** -> use `qccp-frontend`, `qccp-service`, or `experiment-pipeline`.

## Workflow

1. Define task type: classification, regression, sequence prediction, anomaly detection, or embedding.
2. Normalize classical features and choose encoding.
3. Build a parameterized circuit with explicit cqlib parameter names.
4. Choose output: probability vector, selected basis probabilities, or Z expectations.
5. Integrate with classical code while documenting differentiability limits.
6. Validate on a tiny known dataset before scaling.

## Encoding guidance

- Angle encoding is the default PoC path because it is simple and hardware-compatible.
- Use one feature per rotation where possible; when features exceed qubits, add classical projection first.
- Scale features into a bounded angle range, usually through normalization or `tanh(x) * pi`.
- Do not claim cqlib simulator execution is differentiable through PyTorch unless the active implementation provides a custom gradient path. Standard `.item()` based loops break autograd through quantum execution.

## VQC circuit pattern

```python
from cqlib import Circuit, Parameter

def build_vqc(n_qubits, n_features, layers):
    enc_names = []
    var_names = []
    for i in range(min(n_qubits, n_features)):
        enc_names.extend([f"enc_ry_{i}", f"enc_rz_{i}"])
    for layer in range(layers):
        for q in range(n_qubits):
            var_names.extend([f"var_ry_{layer}_{q}", f"var_rz_{layer}_{q}"])

    circuit = Circuit(n_qubits, parameters=enc_names + var_names)
    for i in range(min(n_qubits, n_features)):
        circuit.ry(i, Parameter(f"enc_ry_{i}"))
        circuit.rz(i, Parameter(f"enc_rz_{i}"))
    for layer in range(layers):
        for q in range(n_qubits):
            circuit.ry(q, Parameter(f"var_ry_{layer}_{q}"))
            circuit.rz(q, Parameter(f"var_rz_{layer}_{q}"))
        for q in range(n_qubits - 1):
            circuit.cx(q, q + 1)
    circuit.measure_all()
    return circuit, enc_names, var_names
```

## Output helpers

```python
import torch
from cqlib.simulator import StatevectorSimulator

def probs_to_tensor(probs, n_qubits):
    values = torch.zeros(2 ** n_qubits, dtype=torch.float32)
    for bits, prob in probs.items():
        values[int(bits, 2)] = float(prob)
    return values

def z_expectations(probs, n_qubits):
    values = []
    for q in range(n_qubits):
        exp_q = sum((1 - 2 * int(bits[-1 - q])) * float(prob) for bits, prob in probs.items())
        values.append(exp_q)
    return torch.tensor(values, dtype=torch.float32)

def run_vqc_sample(circuit, enc_names, var_names, x_angles, var_values, output="expectation"):
    params = {}
    for i, name in enumerate(enc_names):
        params[name] = float(x_angles[i])
    for i, name in enumerate(var_names):
        params[name] = float(var_values[i])
    bound = circuit.assign_parameters(params)
    probs = StatevectorSimulator(circuit=bound).measure()
    if output == "probability":
        return probs_to_tensor(probs, circuit.num_qubits)
    return z_expectations(probs, circuit.num_qubits)
```

## Engineering rules

- Keep quantum simulation batch loops small; statevector cost grows as `2 ** n_qubits`.
- Prefer expectation outputs for larger qubit counts; full probability output grows exponentially.
- Keep data preprocessing outside the quantum circuit builder.
- Use fixed seeds for train/test split and optimizer initialization.
- Compare against a classical baseline with the same input features.
- Report runtime, qubit count, layer count, number of parameters, and backend.

## Validation checklist

- [ ] Encoding range and feature-to-qubit mapping are documented.
- [ ] Ansatz depth and entanglement pattern are justified.
- [ ] Measurement output shape is explicit.
- [ ] Bit order is handled consistently.
- [ ] Training loop records seeds and metrics.
- [ ] Tiny smoke test runs in seconds.
- [ ] Claims distinguish architecture scaffold, simulator result, and real-device result.

## Application handoff

For application delivery, write QML metrics into `quantum_report.json` using the `cqlib-sdk` artifact contract. Include dataset split, feature preprocessing, feature-to-qubit map, encoding range, ansatz depth, output mapping, loss, optimizer, metric, backend, shots/seed, command, and artifact paths.

Do not decide delivery readiness from this skill. Hand the reports to `experiment-pipeline` for baseline comparison and staged verification.
