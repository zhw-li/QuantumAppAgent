---
name: cqlib-hybrid
description: "Guides hybrid quantum-classical application systems with Cqlib plus classical ML or optimization code. Use when the task involves PyTorch models with cqlib quantum layers, HQNN, QLSTM, CNN/RNN/Transformer plus quantum circuit, hybrid training loops, quantum feature extraction, parallel quantum channels, classical-only ablations, or end-to-end PoC validation evidence. Trigger after cqlib-sdk selects the hybrid route. Do NOT use for pure QAOA, pure VQE, simple VQC/QML tasks, qccp packaging, or final delivery readiness decisions."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: TYQA
  version: '1.0.0'
  tags: [quantum, cqlib, hybrid, qlstm, application]
---

# cqlib Hybrid

Use after `cqlib-sdk`; often also use `cqlib-qml`. Hybrid work must keep classical model, quantum circuit, backend execution, optimizer, and evaluation separately testable.

## When to Use

- User needs a hybrid quantum-classical model with classical feature extractor, projection, quantum layer, and classical head.
- User asks for HQNN, QLSTM, sequence forecasting/classification with a quantum circuit, or PyTorch plus cqlib integration.
- User needs hybrid model evidence for `quantum_report.json` inside `application-pipeline`.

## When NOT to Use

- **Pure QAOA/QUBO/Ising optimization** -> use `cqlib-qaoa`.
- **Pure VQE/Hamiltonian work** -> use `cqlib-vqe`.
- **Simple VQC/QML classifier/regressor without larger hybrid architecture** -> use `cqlib-qml`.
- **UI/API/deployment packaging or final verification** -> use `qccp-frontend`, `qccp-service`, or `application-pipeline`.

## Architecture workflow

1. Define the business or ML task and baseline metric.
2. Build or reuse a classical feature extractor.
3. Add a projection layer to match `n_qubits` or quantum feature count.
4. Build a cqlib quantum layer with explicit encoding, ansatz, and measurement.
5. Add a classical head and training loop.
6. Validate against a classical-only ablation and a tiny deterministic smoke test.

## Recommended patterns

- Serial: classical encoder -> projection -> quantum layer -> classical head.
- Parallel: shared classical features -> multiple small quantum channels -> concatenate -> head.
- Residual: classical path plus quantum features; useful when quantum layer is slow or noisy.
- Sequence: RNN/GRU/LSTM/Transformer encoder -> final hidden state projection -> quantum layer -> forecast/classifier head.

Avoid large quantum layers inside every token/time-step unless the user explicitly accepts the runtime cost.

## Quantum layer skeleton

This skeleton is intentionally explicit about the autograd boundary. Parameters are trainable in PyTorch, but cqlib execution itself is called sample by sample.

```python
import numpy as np
import torch
import torch.nn as nn
from cqlib import Circuit, Parameter
from cqlib.simulator import StatevectorSimulator

class CqlibExpectationLayer(nn.Module):
    def __init__(self, n_qubits, n_features, layers=2):
        super().__init__()
        self.n_qubits = n_qubits
        self.n_features = n_features
        self.circuit, self.enc_names, self.var_names = self._build_circuit(layers)
        self.var_values = nn.Parameter(torch.randn(len(self.var_names)) * 0.05)
        self.input_scale = nn.Parameter(torch.ones(min(n_qubits, n_features)))

    def _build_circuit(self, layers):
        enc_names = [f"enc_{i}" for i in range(min(self.n_qubits, self.n_features))]
        var_names = [
            f"theta_{layer}_{q}_{axis}"
            for layer in range(layers)
            for q in range(self.n_qubits)
            for axis in ("ry", "rz")
        ]
        circuit = Circuit(self.n_qubits, parameters=enc_names + var_names)
        for i, name in enumerate(enc_names):
            circuit.ry(i, Parameter(name))
        idx = 0
        for layer in range(layers):
            for q in range(self.n_qubits):
                circuit.ry(q, Parameter(var_names[idx])); idx += 1
                circuit.rz(q, Parameter(var_names[idx])); idx += 1
            for q in range(self.n_qubits - 1):
                circuit.cx(q, q + 1)
        circuit.measure_all()
        return circuit, enc_names, var_names

    def _run_one(self, features):
        scaled = torch.tanh(features[:len(self.enc_names)] * self.input_scale) * np.pi
        params = {name: float(scaled[i].detach().cpu()) for i, name in enumerate(self.enc_names)}
        params.update({
            name: float(self.var_values[i].detach().cpu())
            for i, name in enumerate(self.var_names)
        })
        bound = self.circuit.assign_parameters(params)
        probs = StatevectorSimulator(circuit=bound).measure()
        return torch.tensor([
            sum((1 - 2 * int(bits[-1 - q])) * float(prob) for bits, prob in probs.items())
            for q in range(self.n_qubits)
        ], dtype=features.dtype, device=features.device)

    def forward(self, x):
        return torch.stack([self._run_one(sample) for sample in x], dim=0)
```

If true gradient-through-quantum execution is required, implement and validate a parameter-shift or finite-difference estimator explicitly. Do not imply `.detach().cpu()` code is end-to-end differentiable through the quantum simulator.

## Training rules

- Use a smaller learning rate for pretrained classical backbones and a separate group for quantum parameters.
- Cache or precompute classical features when the quantum layer is the bottleneck.
- Keep `n_qubits <= 10` for local statevector PoCs unless performance is already measured.
- Use mini-batches that finish predictably; report per-epoch runtime.
- Include classical-only, quantum-only if meaningful, and hybrid metrics.

## Validation checklist

- [ ] Feature extractor, projection, quantum layer, and head are separate modules.
- [ ] Quantum input shape and output shape are tested.
- [ ] Qubit count, layers, parameter count, and runtime are reported.
- [ ] Autograd boundary is explicitly documented.
- [ ] Seeds, split, metric, and baseline are recorded.
- [ ] No cloud/hardware call is made without explicit authorization.

## Application handoff

For application delivery, write hybrid metrics into `quantum_report.json` using the `cqlib-sdk` artifact contract. Include classical baseline or ablation reference, dataset split, feature extractor, projection, quantum layer, head, optimizer, metric, runtime, backend, shots/seed, command, and artifact paths.

Do not decide delivery readiness from this skill. Hand the reports to `application-pipeline` for baseline comparison and staged verification.
