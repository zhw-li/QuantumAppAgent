---
name: cqlib-sdk
description: "Guides Cqlib SDK usage for quantum application development: circuit construction, parameter binding, simulation, QCIS/QASM conversion, transpilation, result parsing, TianYan/GuoDun workflow boundaries, and algorithm skill routing. Use when writing or reviewing cqlib code, producing quantum_report.json evidence, or deciding whether to use cqlib-qaoa, cqlib-vqe, cqlib-qml, or cqlib-hybrid. Do NOT use for standalone frontend/backend packaging (use qccp-ui, qccp-frontend, or qccp-service), literature planning, or final delivery readiness decisions (use experiment-pipeline)."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: EvoScientist
  version: '1.0.0'
  tags: [quantum, cqlib, sdk, application, routing]
---

# cqlib SDK

Use this skill as the root cqlib workflow. Treat cqlib as a framework with clear boundaries, not a script helper.

## When to Use

- User is writing, reviewing, or debugging Cqlib circuits, simulators, QCIS/QASM conversion, transpilation, or result parsing.
- User needs to choose the correct cqlib algorithm skill for QAOA, VQE, QML, or hybrid quantum-classical work.
- User needs comparable `quantum_report.json` evidence for `experiment-pipeline`.
- User mentions TianYan or GuoDun execution and needs safe cloud/hardware boundaries.

## When NOT to Use

- **Frontend or visual design work** -> use `qccp-ui` and `qccp-frontend`.
- **Backend/API/deployment packaging** -> use `qccp-service`.
- **Literature survey, ideation, or planning only** -> use the relevant research/planning skill.
- **Final stage advancement or delivery readiness** -> use `experiment-pipeline`.

## First checks

1. Inspect the repository before using an API that is not already confirmed.
2. Keep circuit construction, IR/export, simulator execution, cloud execution, transpilation, and visualization separate.
3. Do not invent backend names, cloud parameters, tokens, endpoints, result fields, or hardware constraints.
4. Do not run TianYan/GuoDun hardware jobs unless the user explicitly authorizes the run and provides credentials through environment variables or ignored local config.
5. For behavior changes, add focused tests or runnable examples when the target project has tests/examples.

## Skill routing

- QAOA, QUBO, Ising, MaxCut, portfolio, scheduling, unit commitment: use `cqlib-qaoa`.
- VQE, molecular energy, Pauli Hamiltonian, eigenvalue optimization: use `cqlib-vqe`.
- VQC, QML classifier/regressor, quantum layer, quantum feature map: use `cqlib-qml`.
- PyTorch plus cqlib, hybrid neural network, QLSTM/HQNN/CNN plus quantum layer: use `cqlib-hybrid`.

## Confirmed public entry points

Verify these imports in the active repository or installed cqlib version before use:

```python
from cqlib import Circuit, Parameter, Qubit, Measure, Barrier
from cqlib import TianYanPlatform, GuoDunPlatform, QuantumLanguage
from cqlib.circuits import gates
from cqlib.mapping import transpile_qcis
from cqlib.simulator import StatevectorSimulator, SimpleSimulator
```

If an import fails in the active repo, inspect its installed cqlib version before changing code. Do not hardcode user-machine paths or assume a private checkout layout.

## Application artifact contract

When cqlib work is part of application delivery, produce artifacts that `experiment-pipeline` can compare against the classical baseline during later stages.

This skill owns the `algorithm` layer and comparable algorithm evidence only. It does not own local demo, backend contracts, qccp UI evidence, or delivery readiness. Update `application_manifest.json` only with the actual paths to algorithm artifacts and relevant execution metadata when that manifest exists.

`baseline_report.json` and `quantum_report.json` should include:

- `task`
- `data`
- `primary_metric`
- `higher_is_better`
- `value`
- `command`
- `artifact_paths`
- `seed` when stochastic
- `backend`
- `shots` when shot-based
- `qubits`
- `circuit_depth` when available
- `limitations`

Do not decide delivery readiness from this skill. Produce comparable evidence and let `experiment-pipeline` and `validate_quantum_application` advance or block the next stage.

## Circuit contract

```python
from cqlib import Circuit, Parameter

theta = Parameter("theta")
phi = Parameter("phi")
circuit = Circuit(2, parameters=[theta, phi])
circuit.h(0)
circuit.rx(0, theta)
circuit.rz(1, phi)
circuit.cx(0, 1)
circuit.measure_all()

bound = circuit.assign_parameters({"theta": 0.2, "phi": 1.0})
qcis = bound.qcis
qasm2 = bound.to_qasm2()
```

Important details:

- `Circuit(qubits, parameters=...)` accepts an integer qubit count, a `Qubit`, or a list/tuple of int/`Qubit`.
- Parameters can be declared at construction or added later with `add_parameter`, but parameterized gate code should declare them explicitly before binding.
- `assign_parameters(...)` returns a copied circuit by default. Use `inplace=True` only when mutation is intended.
- `assign_parameters` accepts dict keys as strings or `Parameter` objects, keyword arguments, or a sequence matching parameter order.
- `circuit.qcis` exports QCIS-compliant text and normalizes numeric QCIS parameters into `[-pi, pi)`.
- `Circuit.load(qcis)` loads QCIS text. Do not assume it loads arbitrary OpenQASM.
- `c1 + c2` returns a new concatenated circuit; `c1 += c2` mutates `c1`.
- `draw(category="text")` and `draw(category="mpl")` are the confirmed draw categories.

Common gates confirmed in `Circuit`: `h`, `x`, `y`, `z`, `s`, `sd`, `t`, `td`, `rx`, `ry`, `rz`, `rxy`, `u`, `cx`, `cy`, `cz`, `swap`, `ccx`, `barrier`, `barrier_all`, `measure`, `measure_all`.

## Simulator contract

```python
from cqlib.simulator import StatevectorSimulator

sim = StatevectorSimulator(circuit=bound)
state = sim.statevector()
probs = sim.probs()
measured_probs = sim.measure()
counts = sim.sample(shots=1024, rng_seed=123)
```

Measurement and ordering:

- `measure()` raises if no measurement gates exist.
- `sample()` will measure all qubits if no measurement gates exist, but prefer explicit `measure_all()` for reproducible semantics.
- State/probability keys are bitstrings. Existing examples use `bitstring[-1 - qubit_index]` when mapping key bits back to qubit indices; keep this convention explicit in code and tests.
- For shot-based results, use seeds and tolerant assertions. Do not assert exact sampling frequencies.

## Cloud and hardware workflow

```python
from cqlib import TianYanPlatform, QuantumLanguage

platform = TianYanPlatform(login_key=token, machine_name="simulator")
query_ids = platform.submit_experiment(
    circuit=bound.qcis,
    language=QuantumLanguage.QCIS,
    num_shots=12000,
    machine_name="simulator",
)
results = platform.query_experiment(query_ids)
```

Rules:

- Never hardcode `login_key`, tokens, account identifiers, or private endpoints.
- Do not silently fall back from hardware/cloud to simulator.
- Before cloud submission, validate circuit language, shot count, machine name, unsupported gates, parameter binding, and measurement intent.
- `submit_experiment` returns query IDs; `query_experiment` returns result data after polling. Preserve query IDs and metadata in outputs.
- `transpile_qcis(qcis, platform, initial_layout=None, objective="size")` is available for mapping/transpilation. Inspect platform topology/config before relying on a layout.

## Implementation checklist

- State the qubit indexing, bitstring interpretation, and measurement mapping.
- Keep ansatz, cost/observable, optimizer, backend execution, and result analysis in separate functions/classes.
- Validate numeric dtype, parameter count/order, shot count, and result schema.
- Use local simulators or mocks for tests; avoid real cloud calls in tests.
- For user-facing examples, include expected output shape and limitations.
- When producing application artifacts, hand off `baseline_report.json` and `quantum_report.json` to `experiment-pipeline` for staged comparison and verification.
