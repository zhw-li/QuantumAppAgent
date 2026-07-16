---
name: cqlib-qml
description: "Guides Cqlib quantum machine learning engineering implementation for application datasets. Use when the task involves generating runnable VQC classifier/regressor code, angle/amplitude/basis encoding decisions, quantum probability or expectation outputs, feature maps, trainable ansatz, PyTorch or simulator integration, QML train/evaluate scripts, smoke tests, baseline comparisons, or quantum_report.json artifacts. Trigger after cqlib-sdk selects the QML route. Do NOT use for QAOA/QUBO optimization, VQE Hamiltonians, large hybrid neural architectures better handled by cqlib-hybrid, qccp packaging, or final delivery readiness decisions."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: TYQA
  version: '1.1.0'
  tags: [quantum, cqlib, qml, vqc, application]
---

# cqlib QML

Use after `cqlib-sdk`. QML work must produce task-specific engineering code, not only circuit snippets. Keep state preparation, encoding, ansatz, measurement, output mapping, loss, optimizer, backend, validation, and report artifacts separate.

Before implementation, create the `qml` scientific contract with dataset identity and immutable
split, preprocessing/normalization fit boundary, label and metric conventions, feature-to-qubit
mapping, measurement and prediction semantics, classical oracle/baseline, tolerances, leakage
checks, and allowed claims. Require focused supplementary tests and a current scientific pass
before packaging. Candidate training metrics are not an independent correctness oracle; never edit
the machine report, repair state, reference values, or tolerances to force a pass.

## When to Use

- User needs runnable VQC classifier/regressor code, a quantum feature map, a quantum probability/expectation layer, or a QML baseline comparison.
- User needs dataset preprocessing, encoding, circuit construction, model wrapping, train/evaluate scripts, and smoke tests for a QML task.
- User needs encoding, ansatz, measurement output, loss, optimizer, backend assumptions, and reproducibility evidence documented separately.
- User needs QML evidence for `quantum_report.json` inside `application-pipeline`.

## When NOT to Use

- **QAOA/QUBO/Ising optimization** -> use `cqlib-qaoa`.
- **VQE or Pauli Hamiltonian expectation** -> use `cqlib-vqe`.
- **Hybrid deep learning architecture with classical backbones** -> use `cqlib-hybrid`.
- **UI/API/deployment packaging or final verification** -> use `qccp-frontend`, `qccp-service`, or `application-pipeline`.

## Workflow

1. Define task type: binary classification, multiclass classification, regression, sequence prediction, anomaly detection, embedding, or baseline comparison.
2. Inspect the project dependency pins and active cqlib API before assuming simulator names, Python requirements, or differentiability support. Record the discovered cqlib version in reports.
3. Inspect dataset shape, target semantics, feature columns, and train/test split requirements.
4. Normalize or project classical features and choose encoding.
5. Build a parameterized circuit with explicit cqlib parameter names and a returned parameter map.
6. Choose output: probability vector, selected basis probabilities, Z expectations, or expectations followed by a small classical head.
7. Integrate with classical code while documenting differentiability limits and simulator/backend choices.
8. Add train/evaluate entrypoints, a tiny smoke test, and a classical baseline using the same processed features.
9. Validate on a tiny known dataset before scaling.

## Encoding guidance

- Angle encoding is the default PoC path because it is simple and hardware-compatible.
- Use one feature per rotation where possible; when features exceed available rotations, add classical projection first.
- Scale features into a bounded angle range, usually `[0, pi]`, `[-pi, pi]`, or `tanh(x) * pi`; document the selected range.
- Make feature-to-parameter mapping explicit. If each qubit uses both `RY` and `RZ`, the encoded vector has up to `2 * n_qubits` rotation values.
- Use basis encoding only when discrete or categorical states naturally map to bitstrings.
- Use amplitude encoding only when the implementation explicitly handles vector length, padding, normalization, and state-preparation assumptions.
- Do not claim cqlib simulator execution is differentiable through PyTorch unless the active implementation returns tensors connected to autograd. Standard `.item()`, `float(...)`, NumPy conversion, or dict-to-float loops break autograd through quantum execution.

## VQC circuit pattern

```python
from cqlib import Circuit, Parameter


def build_vqc(n_qubits, encoded_dim, layers):
    enc_names = [f"enc_{i}" for i in range(encoded_dim)]
    var_names = [
        f"var_{layer}_{axis}_{q}"
        for layer in range(layers)
        for q in range(n_qubits)
        for axis in ("ry", "rz")
    ]

    circuit = Circuit(n_qubits, parameters=enc_names + var_names)

    for q in range(n_qubits):
        i = 2 * q
        if i < encoded_dim:
            circuit.ry(q, Parameter(enc_names[i]))
        if i + 1 < encoded_dim:
            circuit.rz(q, Parameter(enc_names[i + 1]))

    for layer in range(layers):
        for q in range(n_qubits):
            circuit.ry(q, Parameter(f"var_{layer}_ry_{q}"))
            circuit.rz(q, Parameter(f"var_{layer}_rz_{q}"))
        for q in range(n_qubits - 1):
            circuit.cx(q, q + 1)

    circuit.measure_all()
    return circuit, {"encoding": enc_names, "variational": var_names}
```

Keep data loading, preprocessing, optimizer creation, and metric logging outside the circuit builder. If the installed cqlib API differs, adapt this pattern to the local `Circuit`, `Parameter`, gate, measurement, and parameter-binding interfaces.

## Output helpers

```python
import torch
from cqlib.simulator import StatevectorSimulator


def probs_to_tensor(probs, n_qubits, *, dtype=torch.float32):
    values = torch.zeros(2 ** n_qubits, dtype=dtype)
    for bits, prob in probs.items():
        values[int(bits, 2)] = torch.as_tensor(prob, dtype=dtype)
    return values


def z_expectations(probs, n_qubits):
    values = []
    for q in range(n_qubits):
        exp_q = sum((1 - 2 * int(bits[-1 - q])) * float(prob) for bits, prob in probs.items())
        values.append(exp_q)
    return torch.tensor(values, dtype=torch.float32)


def run_vqc_sample(circuit, param_values, output="expectation"):
    bound = circuit.assign_parameters(param_values)
    probs = StatevectorSimulator(circuit=bound).measure()
    if output == "probability":
        return probs_to_tensor(probs, circuit.num_qubits)
    return z_expectations(probs, circuit.num_qubits)
```

Use these helpers for non-differentiable verification and reporting. For PyTorch training, prefer a cqlib simulator path that preserves tensors when available, such as a torch-backed simulator in the active cqlib installation. Keep trainable values as tensors until after loss computation. If the active cqlib install exposes only non-differentiable probability dictionaries, train with an explicit derivative-free or finite-difference optimizer instead of pretending autograd is connected.

## Engineering rules

- Follow the repository's existing module layout. If no layout exists, prefer `src/qml/encoding.py`, `src/qml/circuit.py`, `src/qml/model.py`, `scripts/train_qml.py`, `scripts/evaluate_qml.py`, and `tests/test_qml_smoke.py`.
- Keep quantum simulation batch loops small; statevector cost grows as `2 ** n_qubits`.
- Start with a shallow circuit and a small qubit count unless the dataset and runtime budget justify more.
- Prefer expectation outputs for larger qubit counts; full probability output grows exponentially.
- Keep data preprocessing outside the quantum circuit builder.
- Use fixed seeds for train/test split and optimizer initialization.
- For binary classification, map one probability or one Z expectation to the target and use BCE, CE, or MSE consistently.
- For multiclass classification, document which basis states map to classes and what happens to unused states.
- For regression, use one or more expectations directly or attach a small classical linear head.
- Compare against a classical baseline with the same processed input features.
- Report runtime, cqlib version, Python version, qubit count, layer count, number of parameters, backend, optimizer, metric, command, and artifact paths.

## Validation checklist

- [ ] Active cqlib version, Python version, backend, and dependency pins are recorded.
- [ ] Encoding range and feature-to-parameter mapping are documented.
- [ ] Ansatz depth and entanglement pattern are justified.
- [ ] Measurement output shape is explicit for the selected task.
- [ ] Bit order is handled consistently and tested with a known one- or two-qubit circuit.
- [ ] Training loop records seeds, splits, optimizer, losses, metrics, runtime, and command.
- [ ] Tiny smoke test runs in seconds and checks import, parameter binding, output shape, and metric calculation.
- [ ] Classical baseline result is produced or the reason for skipping it is documented.
- [ ] Claims distinguish architecture scaffold, simulator result, and real-device result.

## Application handoff

For application delivery, write QML metrics into `quantum_report.json` using the `cqlib-sdk` artifact contract. Include dataset split, active cqlib version, Python version, feature preprocessing, feature-to-parameter map, encoding range, ansatz depth, output mapping, loss, optimizer, metric, backend, shots/seed if applicable, command, baseline metrics, and artifact paths.

Do not decide delivery readiness from this skill. Hand the reports to `application-pipeline` for baseline comparison and staged verification.
