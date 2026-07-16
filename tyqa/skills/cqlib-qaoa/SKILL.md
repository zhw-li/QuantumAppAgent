---
name: cqlib-qaoa
description: "Guides Cqlib QAOA implementation and evidence generation for quantum optimization applications. Use when the task involves QAOA, QUBO/Ising, MaxCut, portfolio selection, scheduling, unit commitment, knapsack/TSP-like binary optimization, constraint penalties, top-k feasible decoding, simulator/cloud execution evidence, or quantum_report.json for application-pipeline. Trigger after cqlib-sdk selects the QAOA route. Do NOT use for VQE chemistry, QML classification/regression, hybrid neural models, standalone qccp packaging, or final delivery readiness decisions."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: TYQA
  version: '1.1.0'
  tags: [quantum, cqlib, qaoa, qubo, optimization, application, evidence]
---

# cqlib QAOA

Use after `cqlib-sdk` selects the QAOA route. This skill owns the algorithm layer for binary optimization: model, circuit, optimizer, decoding, validation evidence, and `quantum_report.json`. It does not own UI/API packaging or final delivery readiness; hand those artifacts to `application-pipeline`, `qccp-service`, or `qccp-frontend`.

## When to Use

- User needs a QAOA, QUBO, or Ising solution for MaxCut, portfolio selection, scheduling, unit commitment, knapsack/TSP-like binary optimization, or another combinatorial problem.
- User needs binary-variable encoding, constraint penalties, coefficient normalization, bitstring decoding, top-k feasible solution search, or small-instance brute-force comparison.
- User needs simulator or authorized cloud execution evidence for `quantum_report.json` inside `application-pipeline`.
- User asks whether an optimization application is ready for quantum-algorithm evidence, not whether the whole application is delivery-ready.

## When NOT to Use

- **Hamiltonian ground-state energy or molecular simulation** -> use `cqlib-vqe`.
- **Quantum classifier, regressor, feature map, or VQC/QML training** -> use `cqlib-qml`.
- **Hybrid deep-learning architectures such as CNN/RNN plus quantum layers** -> use `cqlib-hybrid`.
- **Standalone backend/API, QCCP page, local FastAPI packaging, or final delivery readiness** -> use `qccp-service`, `qccp-frontend`, `qccp-ui`, or `application-pipeline`.

## First checks before editing code

1. Inspect the active repository or installed cqlib version before using an API that is not already confirmed by `cqlib-sdk`.
2. Keep these modules separate: problem data loading, QUBO/Ising modeling, QAOA circuit construction, backend execution, optimizer loop, decoding, and report generation.
3. Record objective direction. A QUBO minimization value, a MaxCut value, and an optimality gap are different metrics and must not be mixed.
4. Use normalized coefficients only for circuit stability. Always evaluate and report the original business objective or the agreed primary metric on decoded bitstrings.
5. Do not run TianYan/GuoDun hardware jobs unless the user explicitly authorizes the run and credentials are provided through environment variables or ignored local config.
6. Create the `qaoa` scientific contract first: objective direction, variable-to-qubit and
   bitstring conventions, original constraints, QUBO/Ising mapping including offsets and penalty
   semantics, a brute-force or trusted classical oracle for small instances, tolerances, and claims.

## Required outputs for application delivery

When this skill is used inside `application-pipeline`, produce machine-readable algorithm evidence in the caller-provided or current project artifact location:

- `qaoa_model.json`: variables, variable-to-qubit map, objective direction, raw coefficients, normalized coefficients, offset, constraints, penalty weights, normalization factor, and bitstring convention.
- `qaoa_trace.csv` or `qaoa_trace.json`: optimizer, seed, restart id, iteration, parameters, expectation value, best decoded metric, and feasibility rate when available.
- `qaoa_samples.json`: backend, shots or exact-probability mode, top-k bitstrings, decoded variables, probability/count, original objective value, feasibility, and violations.
- `quantum_report.json`: same `task`, `data`, `primary_metric`, and `higher_is_better` as `baseline_report.json`; numeric `value`; `command`; `artifact_paths`; plus backend, shots, seed, qubits, circuit depth, optimizer settings, best feasible solution, limitations, and reproducibility notes.
- `verification_report.md` inputs: commands run, tests passed/failed, brute-force comparison, metric comparison, and known blockers so `application-pipeline` can assemble final verification evidence.
- If `application_manifest.json` already exists, update only the actual paths to the QAOA evidence. Do not invent fixed directories.

A minimal `quantum_report.json` must include the validator-required fields: `task`, `data`, `primary_metric`, `higher_is_better`, `value`, `command`, and `artifact_paths`.

## End-to-end workflow

1. Define binary variables and a stable variable-to-qubit map.
2. Write the original objective and constraints before converting them.
3. Convert to QUBO or Ising with explicit offset and penalty terms.
4. Choose penalty weights and coefficient normalization; preserve raw and normalized coefficients separately.
5. Build the QAOA ansatz with declared cqlib parameters and a documented parameter order.
6. Optimize on a local simulator first, with deterministic seeds, restart count, optimizer name, and max iterations recorded.
7. Decode top-k samples/probabilities; check feasibility against the original constraints; compute the original business metric.
8. Compare against brute force for small cases, or against a documented classical baseline for larger cases using the same task/data/metric.
9. Write artifacts and hand them to `application-pipeline` for staged validation.
10. Run route-specific supplementary tests and require a current `qaoa` scientific pass before
    packaging. Never edit the machine report, repair state, oracle, or tolerance to force a pass.

## QUBO modeling contract

Use a single convention and document it in code and `qaoa_model.json`. Prefer the upper-triangular QUBO convention:

```text
f(x) = offset + sum_i linear[i] * x_i + sum_{i<j} quadratic[(i,j)] * x_i * x_j
x_i in {0, 1}
```

Rules:

- Keep `variable_to_qubit` as a named dict, for example `{("unit_A", 0): 0}` or `{asset_id: qubit}`.
- State whether the original problem is minimization or maximization.
- Convert maximization to minimization only inside the QUBO if needed; report the user-facing metric in its original direction.
- Penalty weights are part of the model. Record the formula or chosen value and why it dominates constraint violations.
- Include the offset even when it is zero. Missing offsets make brute-force checks and reports ambiguous.
- For constrained problems, implement `is_feasible(x)` and `violation_summary(x)` separately from the QUBO value.
- Highest probability bitstring is not necessarily the best feasible solution. Search top-k decoded candidates by the original metric.

## Common application templates

- **MaxCut**: variable `x_i` is the partition assignment. The user-facing metric can be `cut_value` with `higher_is_better=true`, or `cost_gap_percent` with `higher_is_better=false`. State which one is used.
- **Portfolio selection**: encode asset selection and cardinality. Report selected assets, return, risk, Sharpe or objective value from the raw financial model, not the normalized QUBO value.
- **Unit commitment / scheduling**: use a clear `(unit, time)` or `(job, slot)` map. Report load/capacity feasibility, violation count/rate, actual cost/emission, and optimality gap when a baseline exists.
- **Generic constrained QUBO**: keep constraint penalties and objective terms in separate fields so penalties can be tuned without changing the business objective evaluator.

## Cqlib circuit pattern

cqlib has confirmed `cx` and `rz`; use CNOT-RZ-CNOT for ZZ evolution unless the active cqlib version has a verified native RZZ gate.

```python
from cqlib import Circuit, Parameter


def add_zz(circuit, qi, qj, coeff, gamma):
    circuit.cx(qi, qj)
    circuit.rz(qj, 2.0 * coeff * gamma)
    circuit.cx(qi, qj)


def add_z(circuit, qi, coeff, gamma):
    circuit.rz(qi, 2.0 * coeff * gamma)


def build_qaoa(n_qubits, linear, quadratic, depth):
    param_names = []
    for layer in range(depth):
        param_names.extend([f"gamma_{layer}", f"beta_{layer}"])

    circuit = Circuit(n_qubits, parameters=param_names)

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
    return circuit, param_names
```

Important cqlib rules:

- `Circuit(..., parameters=...)` should declare all QAOA parameters before binding.
- `assign_parameters(...)` returns a copied circuit by default; do not mutate the template unintentionally.
- Explicitly call `measure_all()` before `StatevectorSimulator(...).measure()` for measurement semantics.
- Existing cqlib examples typically map qubit `i` from `bitstring[-1 - i]`. Keep this bitstring convention explicit in code, tests, and reports.

## Expectation, decoding, and top-k scoring

```python
from cqlib.simulator import StatevectorSimulator


def bitstring_to_binary(bitstring, n_qubits):
    return [int(bitstring[-1 - i]) for i in range(n_qubits)]


def qubo_value(x, linear, quadratic, offset=0.0):
    value = offset + sum(coeff * x[i] for i, coeff in linear.items())
    value += sum(coeff * x[i] * x[j] for (i, j), coeff in quadratic.items())
    return float(value)


def expectation(params, circuit, param_names, n_qubits, linear, quadratic, offset=0.0):
    bound = circuit.assign_parameters(dict(zip(param_names, params)))
    probs = StatevectorSimulator(circuit=bound).measure()
    return sum(
        prob * qubo_value(bitstring_to_binary(bits, n_qubits), linear, quadratic, offset)
        for bits, prob in probs.items()
    )


def rank_topk(probs, n_qubits, score_fn, is_feasible_fn, top_k=50, higher_is_better=True):
    ranked = []
    for bits, prob in sorted(probs.items(), key=lambda item: -item[1])[:top_k]:
        x = bitstring_to_binary(bits, n_qubits)
        feasible = bool(is_feasible_fn(x))
        metric = score_fn(x)
        ranked.append({
            "bitstring": bits,
            "x": x,
            "probability": float(prob),
            "metric": float(metric),
            "feasible": feasible,
        })

    feasible_rows = [row for row in ranked if row["feasible"]]
    key = (lambda row: row["metric"]) if higher_is_better else (lambda row: -row["metric"])
    best = max(feasible_rows, key=key) if feasible_rows else None
    return best, ranked
```

For constrained problems, `score_fn(x)` must evaluate the original objective or agreed metric. Do not use the normalized penalized QUBO as the final business score unless the user explicitly chose that metric.

## Optimization protocol

- Start with local simulator execution before cloud or hardware execution.
- Use deterministic seeds for random initial parameters, random graph/data generation, and shot sampling.
- Record `depth`, `optimizer`, `restarts`, `maxiter`, initial parameter rule, final parameters, and convergence trace.
- Use multiple restarts for non-convex landscapes. Include at least one deterministic initialization, such as zeros or a known warm start, when appropriate.
- Keep optimizer objective and reported metric separate: the optimizer may minimize normalized QUBO expectation, while the report may maximize cut value or minimize actual cost.
- For shot-based backends, record `shots`, `rng_seed` or backend seed if supported, and aggregate counts with tolerant comparisons.

## Baseline and validation rules

- For small instances, run brute force over all bitstrings and compare best feasible solutions.
- For larger instances, compare with a documented classical baseline using the same task, dataset, constraints, and metric direction.
- Produce the same `task`, `data`, `primary_metric`, and `higher_is_better` in `baseline_report.json` and `quantum_report.json` so `application-pipeline` can compare them.
- Include limitations honestly: simulator scale, shot noise, penalty sensitivity, unsupported constraints, hardware topology, or unavailable credentials.
- If the quantum result does not beat the baseline, report the gap and useful diagnostic data instead of hiding the failure.

## Cloud and hardware boundaries

- Never hardcode `login_key`, tokens, account identifiers, or private endpoints.
- Do not silently fall back from hardware/cloud to simulator. If a backend fails, report it and ask for authorization before rerouting to another backend.
- Before cloud submission, validate parameter binding, measurement gates, shot count, machine name, unsupported gates, QCIS/OpenQASM language, qubit availability, and topology/transpilation needs.
- For TianYan/GuoDun execution, preserve query IDs, backend name, machine name, shot count, language, transpilation settings, and raw result schema in artifacts.
- Real hardware evidence should be treated as optional unless explicitly required by `requirements.json` or the user.

## Validation checklist

- [ ] Variable-to-qubit map is documented and tested.
- [ ] Objective direction and final metric are explicit.
- [ ] QUBO/Ising terms, offset, constraints, penalty weights, and normalization factor are recorded.
- [ ] Raw objective evaluator and normalized circuit coefficients are separated.
- [ ] `Circuit(..., parameters=...)` declares all QAOA parameters.
- [ ] Bitstring convention is consistent in decoding, tests, and reports.
- [ ] Top-k decoded candidates are checked for feasibility and original objective value.
- [ ] Small instance has brute-force or known-optimum validation.
- [ ] Optimizer settings, seeds, restarts, max iterations, backend, shots, and command are recorded.
- [ ] `quantum_report.json` contains validator-required fields and comparable task/data/metric fields.
- [ ] Cloud/hardware calls are authorized and credentials are not committed.

## Application handoff

For application delivery, hand `qaoa_model.json`, `qaoa_trace`, `qaoa_samples.json`, and `quantum_report.json` to `application-pipeline`. This skill may update existing manifest artifact paths, but it must not decide final delivery readiness. `application-pipeline` owns staged comparison, `validate_quantum_application`, packaging checks, and final blocker reporting.
